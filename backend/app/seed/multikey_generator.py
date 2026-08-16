"""
Semester OS — Topic-by-Topic Resumable Content Generation Runner (CLI).

Usage Examples:
  # Check live status across all 268 topics
  python -m app.seed.multikey_generator --status

  # Seed all 268 topics sequentially/concurrently with 5 keys
  python -m app.seed.multikey_generator --all

  # Seed only Java (CAP392)
  python -m app.seed.multikey_generator --subject CAP392

  # Seed a sample of 10 topics to verify resume behavior
  python -m app.seed.multikey_generator --max-topics 10

  # Custom concurrency and MCQ targets
  python -m app.seed.multikey_generator --workers 3 --target-mcqs 5
"""
import sys
import os
import asyncio
import argparse
import logging

# Ensure backend path is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.core.database import AsyncSessionLocal, create_tables
from app.services.groq_content_engine.topic_seeder import TopicContentSeeder, TopicJobState

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("MultiKeyRunner")


async def main():
    parser = argparse.ArgumentParser(description="Semester OS Topic-by-Topic Resumable Content Seeder")
    parser.add_argument("--all", action="store_true", help="Process all pending topics in curriculum")
    parser.add_argument("--subject", type=str, default=None, help="Filter by course code (e.g. CAP392, CAP206, CAP135, CAB213, CAB114)")
    parser.add_argument("--unit", type=int, default=None, help="Filter by unit number (1-6)")
    parser.add_argument("--max-topics", type=int, default=None, help="Limit number of topics to process in this run")
    parser.add_argument("--target-mcqs", type=int, default=5, help="Target MCQs per topic (default: 5)")
    parser.add_argument("--workers", type=int, default=5, help="Number of concurrent workers (1-5)")
    parser.add_argument("--status", action="store_true", help="Print current state summary across all topics and exit")
    parser.add_argument("--reset-state", action="store_true", help="Reset local state file and re-audit directly from database")
    args = parser.parse_args()

    # Ensure tables exist
    await create_tables()

    state_file = "groq_seeding_state.json"
    if args.reset_state and os.path.exists(state_file):
        os.remove(state_file)
        logger.info(f"Removed {state_file}. State will be cleanly re-audited from database.")

    seeder = TopicContentSeeder(
        state_file_path=state_file,
        max_workers=args.workers,
        target_mcqs_per_topic=args.target_mcqs,
    )

    async with AsyncSessionLocal() as db:
        await seeder.initialize_tasks_and_audit_db(db)

    if args.status:
        total = len(seeder.tasks)
        complete = sum(1 for t in seeder.tasks.values() if t.state == TopicJobState.COMPLETE)
        notes_saved = sum(1 for t in seeder.tasks.values() if t.note_status == "SAVED")
        total_mcqs = sum(t.mcq_count_saved for t in seeder.tasks.values())
        failed = sum(1 for t in seeder.tasks.values() if t.state in [TopicJobState.FAILED, TopicJobState.RETRY_REQUIRED])
        pending = sum(1 for t in seeder.tasks.values() if t.state == TopicJobState.PENDING)

        print("\n" + "=" * 65)
        print("SEMESTER OS — CONTENT SEEDING STATUS")
        print("=" * 65)
        print(f"Total Curriculum Topics:    {total}")
        print(f"Completed Topics:           {complete} ({(complete/total)*100:.1f}%)")
        print(f"Pending Topics:             {pending}")
        print(f"Official Theory Notes Saved: {notes_saved} / {total}")
        print(f"Validated MCQs in DB:       {total_mcqs}")
        print(f"Duplicates Prevented:       {seeder.duplicate_detector.duplicates_prevented_count}")
        print(f"Failed / Needs Retry:       {failed}")
        print(f"Configured Groq Keys:       {seeder.key_manager.key_count}/5")
        print("=" * 65 + "\n")
        return

    # Run the topic-by-topic seeding pipeline
    await seeder.run_seeding(
        subject_filter=args.subject,
        unit_filter=args.unit,
        max_topics=args.max_topics,
    )

    # Print final summary
    seeder.print_summary_report()


if __name__ == "__main__":
    asyncio.run(main())
