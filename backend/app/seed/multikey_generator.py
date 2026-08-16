"""
Semester OS — Groq Multi-Key Content Generation Runner (CLI).

Usage:
  python -m app.seed.multikey_generator --all
  python -m app.seed.multikey_generator --subject CAP392
  python -m app.seed.multikey_generator --type mcq
  python -m app.seed.multikey_generator --type notes
  python -m app.seed.multikey_generator --status
  python -m app.seed.multikey_generator --dry-run
"""
import sys
import os
import asyncio
import argparse
import logging

# Ensure backend path is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.core.database import AsyncSessionLocal, create_tables
from app.services.groq_content_engine.engine import GroqContentEngine
from app.services.groq_content_engine.job_queue import ContentType

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("MultiKeyRunner")


async def main():
    parser = argparse.ArgumentParser(description="Groq Multi-Key Content Generation System for Semester OS")
    parser.add_argument("--all", action="store_true", help="Generate all pending notes and MCQs")
    parser.add_argument("--subject", type=str, default=None, help="Filter by course code (e.g. CAP392, CAP206)")
    parser.add_argument("--type", type=str, choices=["notes", "mcq", "all"], default="all", help="Content type filter")
    parser.add_argument("--workers", type=int, default=5, help="Number of concurrent workers (1-5)")
    parser.add_argument("--status", action="store_true", help="Print current job queue status and exit")
    parser.add_argument("--dry-run", action="store_true", help="Execute without committing to database")
    parser.add_argument("--sync-only", action="store_true", help="Sync already approved jobs to DB without making new API calls")
    args = parser.parse_args()

    # Ensure DB tables exist
    await create_tables()

    engine = GroqContentEngine(max_workers=args.workers)

    async with AsyncSessionLocal() as db:
        await engine.initialize_and_preload(db)
        before_user_snapshot = await engine.capture_user_data_snapshot(db)

        if args.status:
            print("\n" + "=" * 50)
            print("GROQ MULTI-KEY GENERATION QUEUE STATUS")
            print("=" * 50)
            summary = engine.job_queue.get_summary()
            print(f"Configured Groq Keys: {engine.key_manager.key_count}/5")
            print(f"Total Jobs:           {summary['total']}")
            print(f"Pending Jobs:         {summary['pending']}")
            print(f"Generating Jobs:      {summary['generating']}")
            print(f"Approved Notes:       {summary['notes_approved']}")
            print(f"Approved MCQ Batches: {summary['mcqs_approved']}")
            print(f"Rejected:             {summary['rejected']}")
            print(f"Failed:               {summary['failed']}")
            print("=" * 50)
            return

        if args.sync_only:
            logger.info("Syncing approved jobs to database...")
            sync_res = await engine.sync_approved_jobs_to_db(db)
            logger.info(f"Sync complete: {sync_res}")
            report = await engine.generate_final_report(db, before_user_snapshot)
            print("\n" + report)
            return

        # Determine ContentType filter
        c_type = None
        if args.type == "notes":
            c_type = ContentType.NOTE
        elif args.type == "mcq":
            c_type = ContentType.MCQ

        pending_jobs = engine.job_queue.get_pending_jobs(content_type=c_type, subject_code=args.subject)
        logger.info(f"Found {len(pending_jobs)} pending jobs to process.")

        if pending_jobs and not args.dry_run:
            def on_progress(job, success):
                status_str = "APPROVED" if success else "FAILED"
                print(f"[{job.job_id}] -> {status_str} (Assigned: {job.assigned_key})")

            await engine.worker_pool.run_worker_pool(pending_jobs, progress_callback=on_progress)
            logger.info("Worker pool execution finished. Committing to database...")
            await engine.sync_approved_jobs_to_db(db)

        # Print Final Report
        report = await engine.generate_final_report(db, before_user_snapshot)
        print("\n" + report)


if __name__ == "__main__":
    asyncio.run(main())
