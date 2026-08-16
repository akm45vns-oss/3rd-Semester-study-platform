"""
Database engine and session management.
Supports both SQLite + aiosqlite (local dev) and Supabase / PostgreSQL + asyncpg (production).
Automatically normalizes connection strings, safely encodes passwords with special characters,
handles connection pooling, WAL mode, and auto-adds new columns.
"""
import urllib.parse
import re
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import text
from app.core.config import settings


def get_normalized_database_url(url: str) -> str:
    """Normalize database URL for SQLAlchemy asyncpg engine, safely encoding special characters in password."""
    if not url:
        return "sqlite+aiosqlite:///./semester_os.db"
    
    url = url.strip().strip("'\"")
    if "sqlite" in url:
        return url
    
    # Match scheme, user, password, host, port, db
    pattern = r"^(?:postgresql|postgres|postgresql\+asyncpg)://([^:]+):(.+)@([^:/]+)(?::(\d+))?/(.+)$"
    match = re.match(pattern, url)
    if match:
        user, raw_password, host, port, db_name = match.groups()
        decoded_password = urllib.parse.unquote(raw_password)
        encoded_password = urllib.parse.quote_plus(decoded_password)
        port_str = f":{port}" if port else ""
        return f"postgresql+asyncpg://{user}:{encoded_password}@{host}{port_str}/{db_name}"

    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+asyncpg://", 1)
    elif url.startswith("postgresql://") and not url.startswith("postgresql+asyncpg://"):
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
    
    return url


db_url = get_normalized_database_url(settings.DATABASE_URL)
is_sqlite = "sqlite" in db_url

engine_kwargs = {
    "echo": False,
}

if is_sqlite:
    engine_kwargs["connect_args"] = {"check_same_thread": False}
else:
    # Production PostgreSQL / Supabase connection pooling configuration
    engine_kwargs.update({
        "pool_size": 10,
        "max_overflow": 20,
        "pool_pre_ping": True,
        "pool_recycle": 300,
    })

engine = create_async_engine(db_url, **engine_kwargs)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def create_tables():
    """Create all tables, configure SQLite concurrency PRAGMAs, and ensure schema sync."""
    async with engine.begin() as conn:
        if is_sqlite:
            # Enable WAL mode and 5000ms busy timeout to prevent database lock contention
            try:
                await conn.execute(text("PRAGMA journal_mode=WAL;"))
                await conn.execute(text("PRAGMA busy_timeout=5000;"))
            except Exception:
                pass

        await conn.run_sync(Base.metadata.create_all)
        
        # If SQLite, ensure newly added columns are present
        if is_sqlite:
            try:
                await conn.execute(text("ALTER TABLE practicals ADD COLUMN code_template TEXT"))
            except Exception:
                pass
