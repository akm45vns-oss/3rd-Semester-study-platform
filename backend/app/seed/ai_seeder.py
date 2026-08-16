"""
AI-Powered Curriculum Seeder for Semester OS.
Uses Groq API (Llama 3.3 70B) with automatic 5-key pool load balancing and failover
to generate comprehensive notes, question bank, and coding challenges for all 5 subjects.

Usage:
  python -m app.seed.ai_seeder --all
  python -m app.seed.ai_seeder --subject CAP392
  python -m app.seed.ai_seeder --subject CAP206 --unit 1
"""
import asyncio
import argparse
import sys
import os
import json
from sqlalchemy import select
from sqlalchemy.orm import selectinload

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from app.core.database import AsyncSessionLocal, create_tables
import app.models  # noqa: F401
from app.models.user import User
from app.models.curriculum import Subject, Unit, Topic
from app.models.progress import Note
from app.models.practice import Question, QuestionOption, CodingProblem, QuestionType, Difficulty
from app.services.ai_generator import GroqAIGenerator


def to_str(val) -> str:
    """Ensure JSON fields are properly serialized strings for SQLite."""
    if val is None:
        return ""
    if isinstance(val, (dict, list)):
        return json.dumps(val, indent=2)
    return str(val)


async def get_or_create_system_user(db) -> User:
    """Ensure a default user exists to attach global notes to."""
    res = await db.execute(select(User).where(User.username == "semester_admin"))
    user = res.scalar_one_or_none()
    if not user:
        from app.core.security import get_password_hash
        user = User(
            username="semester_admin",
            email="admin@semester-os.local",
            hashed_password=get_password_hash("AdminPass123!"),
            full_name="Semester OS AI Assistant",
            is_admin=True,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
    return user


async def seed_with_ai(
    subject_code: str = None,
    unit_number: int = None,
    api_key: str = None,
    questions_per_topic: int = 3,
    generate_notes: bool = True,
    generate_questions: bool = True,
    generate_coding: bool = True,
):
    ai = GroqAIGenerator(api_key=api_key)
    if not ai.is_configured():
        print("\n[ERROR] Groq API Key pool is empty!")
        print("Please provide it via --api-key or set GROQ_API_KEY in backend/.env")
        print("Get your free Groq key at: https://console.groq.com/keys\n")
        return

    print("=" * 60)
    print("  Semester OS — AI Curriculum & Assessment Seeder")
    print(f"  Model: {ai.model}")
    print(f"  Key Pool Size: {len(ai.keys)} keys active")
    print("=" * 60)

    await create_tables()

    # 1. Fetch metadata snapshot to detach from DB session during generation
    async with AsyncSessionLocal() as db:
        admin_user = await get_or_create_system_user(db)
        admin_user_id = admin_user.id

        stmt = (
            select(Topic)
            .join(Unit, Topic.unit_id == Unit.id)
            .join(Subject, Unit.subject_id == Subject.id)
            .options(selectinload(Topic.unit).selectinload(Unit.subject))
            .where(Subject.is_active == True)
        )

        if subject_code:
            stmt = stmt.where(Subject.course_code == subject_code.upper())
        if unit_number:
            stmt = stmt.where(Unit.unit_number == unit_number)

        stmt = stmt.order_by(Subject.sort_order, Unit.unit_number, Topic.sort_order)
        res = await db.execute(stmt)
        topics = res.scalars().all()

        topic_items = []
        for t in topics:
            topic_items.append({
                "id": t.id,
                "name": t.name,
                "has_coding": t.has_coding,
                "unit_number": t.unit.unit_number,
                "unit_name": t.unit.name,
                "course_code": t.unit.subject.course_code,
                "subject_name": t.unit.subject.name,
            })

    if not topic_items:
        print(f"[!] No matching topics found for Subject={subject_code}, Unit={unit_number}")
        return

    print(f"\n[*] Found {len(topic_items)} topic(s) to process.\n")

    notes_count = 0
    questions_count = 0
    coding_count = 0

    for idx, item in enumerate(topic_items, 1):
        t_id = item["id"]
        t_name = item["name"]
        u_num = item["unit_number"]
        u_name = item["unit_name"]
        c_code = item["course_code"]
        s_name = item["subject_name"]

        print(f"[{idx}/{len(topic_items)}] Processing: {c_code} Unit {u_num} -> {t_name}")

        async with AsyncSessionLocal() as db:
            # 1. Generate Academic Notes
            if generate_notes:
                try:
                    existing_notes = await db.execute(
                        select(Note).where(Note.topic_id == t_id)
                    )
                    if not existing_notes.scalars().first():
                        print("    [+] Generating comprehensive academic notes...")
                        notes_md = await ai.generate_academic_notes(
                            course_code=c_code,
                            subject_name=s_name,
                            unit_number=u_num,
                            unit_name=u_name,
                            topic_name=t_name,
                        )
                        note = Note(
                            user_id=admin_user_id,
                            topic_id=t_id,
                            content=notes_md,
                        )
                        db.add(note)
                        await db.commit()
                        notes_count += 1
                        print("    [OK] Notes saved.")
                        await asyncio.sleep(0.5)
                except Exception as e:
                    await db.rollback()
                    print(f"    [!] Error generating notes: {e}")

            # 2. Generate Questions
            if generate_questions:
                try:
                    existing_q = await db.execute(
                        select(Question).where(Question.topic_id == t_id)
                    )
                    if len(existing_q.scalars().all()) < questions_per_topic:
                        print(f"    [+] Generating {questions_per_topic} assessment questions...")
                        q_list = await ai.generate_topic_questions(
                            course_code=c_code,
                            subject_name=s_name,
                            unit_number=u_num,
                            unit_name=u_name,
                            topic_name=t_name,
                            count=questions_per_topic,
                        )
                        for q_item in q_list:
                            q_type_str = q_item.get("question_type", "MCQ")
                            q_type = QuestionType.MCQ
                            if q_type_str in QuestionType.__members__:
                                q_type = QuestionType[q_type_str]

                            diff_str = q_item.get("difficulty", "MEDIUM").upper()
                            diff = Difficulty.MEDIUM
                            if diff_str in Difficulty.__members__:
                                diff = Difficulty[diff_str]

                            q_obj = Question(
                                topic_id=t_id,
                                question_text=to_str(q_item.get("question_text", "")),
                                question_type=q_type,
                                difficulty=diff,
                                explanation=to_str(q_item.get("explanation", "")),
                                source_type="ADDITIONAL_LEARNING",
                            )
                            db.add(q_obj)
                            await db.flush()

                            for opt_idx, opt in enumerate(q_item.get("options", [])):
                                opt_obj = QuestionOption(
                                    question_id=q_obj.id,
                                    option_text=to_str(opt.get("text", "")),
                                    is_correct=bool(opt.get("is_correct", False)),
                                    sort_order=opt_idx,
                                )
                                db.add(opt_obj)

                            questions_count += 1

                        await db.commit()
                        print(f"    [OK] Added {len(q_list)} questions to question bank.")
                        await asyncio.sleep(0.5)
                except Exception as e:
                    await db.rollback()
                    print(f"    [!] Error generating questions: {e}")

            # 3. Generate Coding Challenge if applicable
            if generate_coding and (item["has_coding"] or idx % 3 == 0):
                try:
                    existing_cp = await db.execute(
                        select(CodingProblem).where(CodingProblem.topic_id == t_id)
                    )
                    if not existing_cp.scalars().first():
                        print("    [+] Generating coding problem challenge...")
                        prob_data = await ai.generate_coding_problem(
                            course_code=c_code,
                            unit_number=u_num,
                            topic_name=t_name,
                        )
                        if prob_data and prob_data.get("title"):
                            top_update = await db.execute(select(Topic).where(Topic.id == t_id))
                            top_obj = top_update.scalar_one_or_none()
                            if top_obj:
                                top_obj.has_coding = True

                            cp = CodingProblem(
                                topic_id=t_id,
                                title=to_str(prob_data.get("title")),
                                description=to_str(prob_data.get("description", "")),
                                language=to_str(prob_data.get("language", "PYTHON")),
                                difficulty=Difficulty.MEDIUM,
                                starter_code=to_str(prob_data.get("starter_code", "")),
                                expected_output=to_str(prob_data.get("expected_output", "")),
                                hints=to_str(prob_data.get("hints", "")),
                                examples=to_str(prob_data.get("examples", "")),
                                source_type="OFFICIAL_SYLLABUS",
                            )
                            db.add(cp)
                            await db.commit()
                            coding_count += 1
                            print(f"    [OK] Coding problem '{cp.title}' saved.")
                        await asyncio.sleep(0.5)
                except Exception as e:
                    await db.rollback()
                    print(f"    [!] Error generating coding challenge: {e}")

    print("\n" + "=" * 60)
    print("  AI SEEDING COMPLETED SUCCESSFULLY!")
    print(f"  • Notes Generated:    {notes_count}")
    print(f"  • Questions Created:  {questions_count}")
    print(f"  • Coding Challenges:  {coding_count}")
    print("=" * 60 + "\n")


def main():
    parser = argparse.ArgumentParser(description="Semester OS AI Curriculum Seeder")
    parser.add_argument("--subject", type=str, help="Subject code (e.g. CAP392, CAP206, CAP135, CAB213, CAB114)")
    parser.add_argument("--unit", type=int, help="Unit number (1-6)")
    parser.add_argument("--api-key", type=str, help="Groq API Key (overrides .env)")
    parser.add_argument("--count", type=int, default=3, help="Questions per topic (default 3)")
    parser.add_argument("--all", action="store_true", help="Seed all subjects and units")
    args = parser.parse_args()

    asyncio.run(
        seed_with_ai(
            subject_code=args.subject,
            unit_number=args.unit,
            api_key=args.api_key,
            questions_per_topic=args.count,
        )
    )


if __name__ == "__main__":
    main()
