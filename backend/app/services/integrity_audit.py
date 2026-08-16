"""Automated Data Integrity Audit Service for Semester OS."""
from typing import Dict, Any, List
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.curriculum import Subject, Unit, Topic, Practical
from app.models.progress import Note
from app.models.practice import Question, QuestionOption, CodingProblem, DescriptiveQuestion

EXPECTED_COURSE_CODES = {"CAP392", "CAP206", "CAP135", "CAB213", "CAB114"}
FORBIDDEN_COURSE_CODES = {"CAP138", "PES209"}
EXPECTED_SUBJECT_COUNT = 5
EXPECTED_UNITS_PER_SUBJECT = 6
EXPECTED_TOTAL_UNITS = 30
EXPECTED_TOPIC_COUNT = 344


async def run_full_system_integrity_audit(db: AsyncSession) -> Dict[str, Any]:
    """Perform a deep scan of all curriculum, content, and data integrity invariants."""
    errors: List[str] = []
    warnings: List[str] = []
    stats: Dict[str, Any] = {}

    # 1. Subjects & Units Check
    subjects_res = await db.execute(
        select(Subject).options(selectinload(Subject.units).selectinload(Unit.topics))
    )
    subjects = subjects_res.scalars().all()
    actual_codes = {s.course_code for s in subjects}

    stats["subject_count"] = len(subjects)
    stats["course_codes"] = sorted(list(actual_codes))

    for forbidden in FORBIDDEN_COURSE_CODES:
        if forbidden in actual_codes:
            errors.append(f"CRITICAL: Forbidden course code found in database: {forbidden}")

    for expected in EXPECTED_COURSE_CODES:
        if expected not in actual_codes:
            errors.append(f"Missing expected course code: {expected}")

    if len(subjects) != EXPECTED_SUBJECT_COUNT:
        errors.append(f"Expected {EXPECTED_SUBJECT_COUNT} subjects, found {len(subjects)}")

    total_units = 0
    total_topics = 0
    subjects_summary = []

    for s in subjects:
        u_count = len(s.units)
        total_units += u_count
        s_topics = sum(len(u.topics) for u in s.units)
        total_topics += s_topics

        if u_count != EXPECTED_UNITS_PER_SUBJECT:
            errors.append(f"Subject {s.course_code} has {u_count} units (expected {EXPECTED_UNITS_PER_SUBJECT})")

        subjects_summary.append({
            "course_code": s.course_code,
            "name": s.name,
            "units": u_count,
            "topics": s_topics,
        })

    stats["total_units"] = total_units
    stats["total_topics"] = total_topics
    stats["subjects_summary"] = subjects_summary

    if total_units != EXPECTED_TOTAL_UNITS:
        errors.append(f"Expected {EXPECTED_TOTAL_UNITS} total units, found {total_units}")

    if total_topics != EXPECTED_TOPIC_COUNT:
        warnings.append(f"Found {total_topics} topics (expected {EXPECTED_TOPIC_COUNT})")

    # 2. Topic Notes Coverage Check
    notes_topic_count = await db.scalar(select(func.count(Note.topic_id.distinct())))
    stats["topics_with_notes"] = notes_topic_count
    stats["notes_coverage_percent"] = round((notes_topic_count / max(1, total_topics)) * 100, 1)

    if notes_topic_count < total_topics:
        warnings.append(f"{total_topics - notes_topic_count} topics do not have notes seeded.")

    # 3. MCQ Option Validation (Exactly 4 options, Exactly 1 correct)
    mcqs_res = await db.execute(
        select(Question).options(selectinload(Question.options))
    )
    all_mcqs = mcqs_res.scalars().all()
    stats["total_mcqs"] = len(all_mcqs)

    invalid_option_counts = 0
    invalid_correct_counts = 0

    for q in all_mcqs:
        opt_len = len(q.options)
        if opt_len != 4:
            invalid_option_counts += 1
        correct_count = sum(1 for o in q.options if o.is_correct)
        if correct_count != 1:
            invalid_correct_counts += 1

    stats["mcqs_with_4_options"] = len(all_mcqs) - invalid_option_counts
    stats["mcqs_with_1_correct"] = len(all_mcqs) - invalid_correct_counts

    if invalid_option_counts > 0:
        errors.append(f"{invalid_option_counts} MCQs do not have exactly 4 options.")
    if invalid_correct_counts > 0:
        errors.append(f"{invalid_correct_counts} MCQs do not have exactly 1 correct answer.")

    # 4. Coding Problems & Practicals
    coding_count = await db.scalar(select(func.count(CodingProblem.id)))
    practical_count = await db.scalar(select(func.count(Practical.id)))
    desc_count = await db.scalar(select(func.count(DescriptiveQuestion.id)))

    stats["total_coding_problems"] = coding_count
    stats["total_practicals"] = practical_count
    stats["total_descriptive_questions"] = desc_count

    return {
        "healthy": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "stats": stats,
    }
