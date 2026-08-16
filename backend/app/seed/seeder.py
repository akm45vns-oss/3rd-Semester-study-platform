"""
Idempotent database seeder.
Seeds:
1. Official Curriculum (5 Subjects, 30 Units, Topics, Practicals)
2. Question Bank (MCQs with answers and detailed explanations)
3. Coding Problems (Java, SQL, Python, JS with test cases)
Safe to run multiple times.
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from sqlalchemy import select
from app.core.database import AsyncSessionLocal, create_tables
import app.models  # noqa: F401
from app.models.curriculum import Subject, Unit, Topic, Practical
from app.models.practice import Question, QuestionOption, CodingProblem, QuestionType, Difficulty
from app.seed.curriculum_data import CURRICULUM, validate_curriculum
from app.seed.questions_data import QUESTION_BANK
from app.seed.coding_data import CODING_PROBLEMS


async def seed_curriculum(db):
    """Seed all subjects, units, topics, and practicals."""
    print("[*] Validating curriculum data...")
    result = validate_curriculum()
    if not result["valid"]:
        print("[FAIL] Curriculum validation FAILED:")
        for error in result["errors"]:
            print(f"  [ERROR] {error}")
        sys.exit(1)

    print(f"[OK] Curriculum valid: {result['subject_count']} subjects, {result['total_units']} units")

    for subj_data in CURRICULUM:
        existing_subj = await db.execute(
            select(Subject).where(Subject.course_code == subj_data["course_code"])
        )
        subject = existing_subj.scalar_one_or_none()

        if subject is None:
            subject = Subject(
                course_code=subj_data["course_code"],
                name=subj_data["name"],
                credits=subj_data["credits"],
                description=subj_data.get("description"),
                sort_order=list(d["course_code"] for d in CURRICULUM).index(subj_data["course_code"]),
            )
            db.add(subject)
            await db.flush()
            print(f"  [+] Added subject: {subject.course_code} - {subject.name}")

        for unit_data in subj_data["units"]:
            existing_unit = await db.execute(
                select(Unit).where(
                    Unit.subject_id == subject.id,
                    Unit.unit_number == unit_data["unit_number"],
                )
            )
            unit = existing_unit.scalar_one_or_none()

            if unit is None:
                unit = Unit(
                    subject_id=subject.id,
                    unit_number=unit_data["unit_number"],
                    name=unit_data["name"],
                    description=unit_data.get("description"),
                    sort_order=unit_data["unit_number"],
                )
                db.add(unit)
                await db.flush()
                print(f"    [+] Added unit {unit.unit_number}: {unit.name}")

            for idx, topic_name in enumerate(unit_data["topics"]):
                existing_topic = await db.execute(
                    select(Topic).where(
                        Topic.unit_id == unit.id,
                        Topic.name == topic_name,
                    )
                )
                topic = existing_topic.scalar_one_or_none()
                if topic is None:
                    topic = Topic(
                        unit_id=unit.id,
                        name=topic_name,
                        sort_order=idx,
                    )
                    db.add(topic)

        for idx, prac_title in enumerate(subj_data.get("practicals", [])):
            existing_prac = await db.execute(
                select(Practical).where(
                    Practical.subject_id == subject.id,
                    Practical.title == prac_title,
                )
            )
            practical = existing_prac.scalar_one_or_none()
            if practical is None:
                practical = Practical(
                    subject_id=subject.id,
                    practical_number=idx + 1,
                    title=prac_title,
                    sort_order=idx,
                )
                db.add(practical)

    await db.commit()


async def seed_questions(db):
    """Seed Question Bank."""
    print("[*] Seeding questions...")
    added_count = 0
    for q_data in QUESTION_BANK:
        # Find the topic
        stmt = (
            select(Topic)
            .join(Unit, Topic.unit_id == Unit.id)
            .join(Subject, Unit.subject_id == Subject.id)
            .where(
                Subject.course_code == q_data["course_code"],
                Unit.unit_number == q_data["unit_number"],
                Topic.name == q_data["topic_name"],
            )
        )
        res = await db.execute(stmt)
        topic = res.scalar_one_or_none()
        if not topic:
            # Fallback: look up by partial topic name in that subject & unit
            stmt_fallback = (
                select(Topic)
                .join(Unit, Topic.unit_id == Unit.id)
                .join(Subject, Unit.subject_id == Subject.id)
                .where(
                    Subject.course_code == q_data["course_code"],
                    Unit.unit_number == q_data["unit_number"],
                )
            )
            res_fallback = await db.execute(stmt_fallback)
            all_topics = res_fallback.scalars().all()
            for t in all_topics:
                if q_data["topic_name"].lower() in t.name.lower() or t.name.lower() in q_data["topic_name"].lower():
                    topic = t
                    break

        if not topic:
            continue

        existing_q = await db.execute(
            select(Question).where(
                Question.topic_id == topic.id,
                Question.question_text == q_data["question_text"],
            )
        )
        if existing_q.scalar_one_or_none() is not None:
            continue

        q = Question(
            topic_id=topic.id,
            question_text=q_data["question_text"],
            question_type=QuestionType(q_data.get("question_type", "MCQ")),
            difficulty=Difficulty(q_data.get("difficulty", "MEDIUM")),
            explanation=q_data.get("explanation"),
            source_type="ADDITIONAL_LEARNING",
        )
        db.add(q)
        await db.flush()

        for idx, opt in enumerate(q_data["options"]):
            o = QuestionOption(
                question_id=q.id,
                option_text=opt["text"],
                is_correct=opt["is_correct"],
                sort_order=idx,
            )
            db.add(o)
        added_count += 1

    await db.commit()
    print(f"[OK] Seeded {added_count} new questions into the question bank.")


async def seed_coding_problems(db):
    """Seed Coding and SQL challenges."""
    print("[*] Seeding coding problems...")
    added_count = 0
    for p_data in CODING_PROBLEMS:
        stmt = (
            select(Topic)
            .join(Unit, Topic.unit_id == Unit.id)
            .join(Subject, Unit.subject_id == Subject.id)
            .where(
                Subject.course_code == p_data["course_code"],
                Unit.unit_number == p_data["unit_number"],
            )
        )
        res = await db.execute(stmt)
        topics = res.scalars().all()
        topic = None
        for t in topics:
            if p_data["topic_name"].lower() in t.name.lower() or t.name.lower() in p_data["topic_name"].lower():
                topic = t
                break
        if not topic and topics:
            topic = topics[0]

        if not topic:
            continue

        existing = await db.execute(
            select(CodingProblem).where(
                CodingProblem.topic_id == topic.id,
                CodingProblem.title == p_data["title"],
            )
        )
        if existing.scalar_one_or_none() is not None:
            continue

        topic.has_coding = True
        prob = CodingProblem(
            topic_id=topic.id,
            title=p_data["title"],
            description=p_data["description"],
            language=p_data["language"],
            difficulty=Difficulty(p_data.get("difficulty", "MEDIUM")),
            starter_code=p_data.get("starter_code"),
            expected_output=p_data.get("expected_output"),
            hints=p_data.get("hints"),
            examples=p_data.get("examples"),
            source_type="OFFICIAL_SYLLABUS",
        )
        db.add(prob)
        added_count += 1

    await db.commit()
    print(f"[OK] Seeded {added_count} new coding problems.")


async def main():
    print("Semester OS - Database Seeder")
    print("=" * 50)
    await create_tables()
    async with AsyncSessionLocal() as db:
        await seed_curriculum(db)
        await seed_questions(db)
        await seed_coding_problems(db)
    print("\n[DONE] All seed operations completed successfully!")


if __name__ == "__main__":
    asyncio.run(main())
