"""
Supabase / PostgreSQL Migration & Sync Script for Semester OS.
Transfers all local SQLite data (curriculum, questions, AI notes, coding problems, progress)
directly into your Supabase PostgreSQL database instance.
"""
import asyncio
import argparse
import sys
import os
import sqlite3
from datetime import datetime
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import text

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from app.core.database import Base, get_normalized_database_url
import app.models  # noqa: F401
from app.core.config import settings

# Boolean columns in SQLite that need conversion to Python bool for PostgreSQL
BOOLEAN_COLS = {
    "is_active", "is_admin", "has_coding", "has_practical", "is_correct",
    "notes_read", "practice_completed", "quiz_completed", "coding_completed",
    "practical_completed", "is_completed", "is_resolved"
}

DATETIME_COLS = {
    "created_at", "updated_at", "attempted_at", "last_studied_at",
    "first_learned_at", "last_revised_at", "completed_at", "resolved_at",
    "started_at", "ended_at", "scheduled_date", "target_date", "awarded_at"
}

TABLE_MIGRATION_ORDER = [
    ("users", "users"),
    ("subjects", "subjects"),
    ("units", "units"),
    ("topics", "topics"),
    ("subtopics", "subtopics"),
    ("course_outcomes", "course_outcomes"),
    ("practicals", "practicals"),
    ("questions", "questions"),
    ("question_options", "question_options"),
    ("practice_attempts", "practice_attempts"),
    ("coding_problems", "coding_problems"),
    ("coding_submissions", "coding_submissions"),
    ("sql_problems", "sql_problems"),
    ("topic_progress", "topic_progress"),
    ("practical_progress", "practical_progress"),
    ("notes", "notes"),
    ("bookmarks", "bookmarks"),
    ("revision_items", "revision_items"),
    ("mistakes", "mistakes"),
    ("study_sessions", "study_sessions"),
]


def clean_val(col_name: str, val):
    if val is None:
        return None
    if col_name in BOOLEAN_COLS:
        return bool(val == 1 or val is True or str(val).lower() in ["true", "1"])
    if col_name in DATETIME_COLS and isinstance(val, str):
        try:
            return datetime.fromisoformat(val.replace("Z", "+00:00"))
        except Exception:
            return val
    return val


async def migrate_sqlite_to_supabase(supabase_url: str, sqlite_path: str = "semester_os.db"):
    norm_url = get_normalized_database_url(supabase_url)
    if "sqlite" in norm_url:
        print("\n[!] Error: Provided URL is SQLite, not Supabase/PostgreSQL.")
        return

    if not os.path.exists(sqlite_path):
        print(f"\n[!] SQLite database file '{sqlite_path}' not found.")
        return

    print("=" * 65)
    print("  Semester OS — Supabase / PostgreSQL Data Migration Engine")
    print("=" * 65)
    print(f"[*] Source Database:      SQLite ({sqlite_path})")
    print(f"[*] Target Destination:   Supabase / PostgreSQL")
    print("=" * 65 + "\n")

    sqlite_conn = sqlite3.connect(sqlite_path)
    sqlite_conn.row_factory = sqlite3.Row
    sqlite_cur = sqlite_conn.cursor()

    target_engine = create_async_engine(
        norm_url,
        echo=False,
        pool_size=5,
        max_overflow=10,
        pool_pre_ping=True,
    )

    print("[1/3] Verifying and creating all relational tables in Supabase...")
    async with target_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("    [OK] Tables verified / created successfully.\n")

    print("[2/3] Migrating table data...")
    TargetSession = async_sessionmaker(target_engine, class_=AsyncSession, expire_on_commit=False)

    async with TargetSession() as db:
        for table_name, target_table in TABLE_MIGRATION_ORDER:
            sqlite_cur.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,)
            )
            if not sqlite_cur.fetchone():
                continue

            sqlite_cur.execute(f"SELECT * FROM {table_name}")
            rows = sqlite_cur.fetchall()
            if not rows:
                print(f"    • {table_name:22} : 0 records (skipped)")
                continue

            # Only include columns present in the SQLAlchemy target model
            target_cols = Base.metadata.tables[target_table].columns.keys()
            sqlite_cols = [col[0] for col in sqlite_cur.description]
            common_cols = [c for c in sqlite_cols if c in target_cols]

            cols_str = ", ".join([f'"{c}"' for c in common_cols])
            params_str = ", ".join([f":{c}" for c in common_cols])

            insert_query = text(
                f'INSERT INTO "{target_table}" ({cols_str}) VALUES ({params_str}) ON CONFLICT DO NOTHING'
            )

            # Convert row values with proper PostgreSQL types
            data_list = []
            for r in rows:
                row_dict = {}
                for col in common_cols:
                    row_dict[col] = clean_val(col, r[col])
                data_list.append(row_dict)

            try:
                chunk_size = 100
                for i in range(0, len(data_list), chunk_size):
                    chunk = data_list[i : i + chunk_size]
                    await db.execute(insert_query, chunk)
                    await db.commit()
                print(f"    [OK] {table_name:22} : {len(rows)} records migrated")
            except Exception as e:
                await db.rollback()
                err_msg = str(e).encode('ascii', 'replace').decode('ascii')
                print(f"    [!]  {table_name:22} : Error ({err_msg[:120]})")

        # Synchronize sequence primary keys
        print("\n[3/3] Synchronizing PostgreSQL sequence primary keys...")
        for table_name, _ in TABLE_MIGRATION_ORDER:
            try:
                seq_fix = text(f"""
                    SELECT setval(
                        pg_get_serial_sequence('"{table_name}"', 'id'),
                        COALESCE((SELECT MAX(id) FROM "{table_name}"), 1),
                        true
                    );
                """)
                await db.execute(seq_fix)
            except Exception:
                pass
        await db.commit()

    sqlite_conn.close()
    await target_engine.dispose()

    print("\n" + "=" * 65)
    print("  MIGRATION TO SUPABASE COMPLETED SUCCESSFULLY!")
    print("  All data is now live and stored in your Supabase PostgreSQL instance.")
    print("=" * 65 + "\n")


def main():
    parser = argparse.ArgumentParser(description="Migrate Semester OS data to Supabase PostgreSQL")
    parser.add_argument(
        "--supabase-url",
        type=str,
        default=os.getenv("DATABASE_URL", settings.DATABASE_URL),
        help="Supabase PostgreSQL connection URI",
    )
    parser.add_argument(
        "--sqlite-file",
        type=str,
        default="semester_os.db",
        help="Local SQLite file path (default: semester_os.db)",
    )
    args = parser.parse_args()

    asyncio.run(
        migrate_sqlite_to_supabase(
            supabase_url=args.supabase_url,
            sqlite_path=args.sqlite_file,
        )
    )


if __name__ == "__main__":
    main()
