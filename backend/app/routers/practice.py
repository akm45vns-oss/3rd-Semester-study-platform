"""Practice and assessment router."""
import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload
from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.curriculum import Subject, Unit, Topic
from app.models.progress import TopicProgress, TopicStatus, Mistake
from app.models.practice import Question, QuestionOption, PracticeAttempt, Difficulty
from app.schemas.practice import (
    QuestionOut, PracticeAttemptCreate, PracticeAttemptOut,
    TestGenerateRequest, TestSessionOut, TestSubmitRequest, TestResultOut, MistakeOut
)

router = APIRouter(prefix="/practice", tags=["practice"])


@router.get("/questions", response_model=list[QuestionOut])
async def get_questions(
    topic_id: int = Query(None),
    unit_id: int = Query(None),
    subject_id: int = Query(None),
    difficulty: Difficulty = Query(None),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Retrieve practice questions filtered by scope."""
    stmt = select(Question).options(selectinload(Question.options)).where(Question.is_active == True)

    if topic_id:
        stmt = stmt.where(Question.topic_id == topic_id)
    elif unit_id:
        stmt = stmt.join(Topic, Question.topic_id == Topic.id).where(Topic.unit_id == unit_id)
    elif subject_id:
        stmt = (
            stmt.join(Topic, Question.topic_id == Topic.id)
            .join(Unit, Topic.unit_id == Unit.id)
            .where(Unit.subject_id == subject_id)
        )

    if difficulty:
        stmt = stmt.where(Question.difficulty == difficulty)

    stmt = stmt.limit(limit)
    res = await db.execute(stmt)
    return res.scalars().all()


@router.post("/attempts", response_model=PracticeAttemptOut)
async def submit_practice_attempt(
    data: PracticeAttemptCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Submit a single question practice attempt and record analytics & progress."""
    stmt = select(Question).options(selectinload(Question.options)).where(Question.id == data.question_id)
    res = await db.execute(stmt)
    question = res.scalar_one_or_none()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    correct_option = next((opt for opt in question.options if opt.is_correct), None)
    correct_opt_id = correct_option.id if correct_option else None

    is_correct = False
    if data.selected_option_id and correct_opt_id:
        is_correct = data.selected_option_id == correct_opt_id
    elif data.answer_text and correct_option:
        is_correct = data.answer_text.strip().lower() == correct_option.option_text.strip().lower()

    score = 1.0 if is_correct else 0.0

    attempt = PracticeAttempt(
        user_id=current_user.id,
        question_id=question.id,
        topic_id=question.topic_id,
        answer_given=str(data.selected_option_id or data.answer_text or ""),
        is_correct=is_correct,
        score=score,
        time_taken_seconds=data.time_taken_seconds,
        session_id=data.session_id,
    )
    db.add(attempt)

    # Update Topic Progress
    prog_res = await db.execute(
        select(TopicProgress).where(
            TopicProgress.user_id == current_user.id,
            TopicProgress.topic_id == question.topic_id,
        )
    )
    prog = prog_res.scalar_one_or_none()
    if not prog:
        prog = TopicProgress(user_id=current_user.id, topic_id=question.topic_id)
        db.add(prog)

    prog.practice_completed = True
    prog.practice_completion = max(prog.practice_completion or 0.0, 1.0 if is_correct else 0.5)
    prog.last_studied_at = datetime.now(timezone.utc)
    prog.calculate_mastery()

    # If incorrect, log to mistakes notebook
    if not is_correct:
        db.add(
            Mistake(
                user_id=current_user.id,
                topic_id=question.topic_id,
                description=f"Question: {question.question_text[:120]}...",
                correction=f"Correct Answer: {correct_option.option_text if correct_option else 'N/A'}. {question.explanation or ''}",
                source_type="PRACTICE",
            )
        )

    await db.commit()
    await db.refresh(attempt)

    return PracticeAttemptOut(
        id=attempt.id,
        question_id=question.id,
        topic_id=question.topic_id,
        is_correct=is_correct,
        score=score,
        explanation=question.explanation,
        correct_option_id=correct_opt_id,
        attempted_at=attempt.attempted_at,
    )


@router.post("/tests/generate", response_model=TestSessionOut)
async def generate_test(
    req: TestGenerateRequest,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """
    Generate an assessment strictly scoped to topic, unit, subject, or full mock exam.
    IMPORTANT: Unit tests only draw questions from the selected unit.
    Subject tests only draw questions from the selected subject.
    """
    stmt = select(Question).options(selectinload(Question.options)).where(Question.is_active == True)
    scope_title = "Semester Practice Test"
    time_limit = 15

    if req.scope == "TOPIC" and req.topic_id:
        topic_res = await db.execute(select(Topic).where(Topic.id == req.topic_id))
        topic = topic_res.scalar_one_or_none()
        if not topic:
            raise HTTPException(status_code=404, detail="Topic not found")
        stmt = stmt.where(Question.topic_id == req.topic_id)
        scope_title = f"Topic Quiz: {topic.name}"
        time_limit = max(5, req.question_count * 2)

    elif req.scope == "UNIT" and req.unit_id:
        unit_res = await db.execute(
            select(Unit).options(selectinload(Unit.subject)).where(Unit.id == req.unit_id)
        )
        unit = unit_res.scalar_one_or_none()
        if not unit:
            raise HTTPException(status_code=404, detail="Unit not found")
        stmt = stmt.join(Topic, Question.topic_id == Topic.id).where(Topic.unit_id == req.unit_id)
        scope_title = f"{unit.subject.course_code} Unit {unit.unit_number}: {unit.name} Test"
        time_limit = max(10, req.question_count * 2)

    elif req.scope == "SUBJECT" and req.subject_id:
        subj_res = await db.execute(select(Subject).where(Subject.id == req.subject_id))
        subj = subj_res.scalar_one_or_none()
        if not subj:
            raise HTTPException(status_code=404, detail="Subject not found")
        stmt = (
            stmt.join(Topic, Question.topic_id == Topic.id)
            .join(Unit, Topic.unit_id == Unit.id)
            .where(Unit.subject_id == req.subject_id)
        )
        scope_title = f"{subj.course_code} - {subj.name} Subject Test"
        time_limit = max(20, req.question_count * 2)

    elif req.scope == "FULL_MOCK":
        scope_title = "3rd Semester Full Mock Examination"
        time_limit = 45

    if req.difficulty:
        stmt = stmt.where(Question.difficulty == req.difficulty)

    stmt = stmt.order_by(func.random()).limit(req.question_count)
    res = await db.execute(stmt)
    questions = res.scalars().all()

    if not questions:
        # Fallback if specific unit/topic has no standalone question yet: fetch all questions from active bank
        fallback_stmt = select(Question).options(selectinload(Question.options)).limit(req.question_count)
        res_fb = await db.execute(fallback_stmt)
        questions = res_fb.scalars().all()

    # Hide is_correct during active test
    sanitized_questions = []
    for q in questions:
        q_dict = QuestionOut.model_validate(q)
        for opt in q_dict.options:
            opt.is_correct = None
        sanitized_questions.append(q_dict)

    session_id = str(uuid.uuid4())

    return TestSessionOut(
        session_id=session_id,
        scope=req.scope,
        scope_title=scope_title,
        time_limit_minutes=time_limit,
        questions=sanitized_questions,
    )


@router.post("/tests/submit", response_model=TestResultOut)
async def submit_test(
    req: TestSubmitRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Evaluate full test submission, update user progress, identify weak topics and recommend revision."""
    total = len(req.answers)
    correct_count = 0
    incorrect_count = 0
    skipped_count = 0

    details = []
    weak_topic_ids = set()

    for item in req.answers:
        q_res = await db.execute(
            select(Question)
            .options(selectinload(Question.options), selectinload(Question.topic))
            .where(Question.id == item.question_id)
        )
        q = q_res.scalar_one_or_none()
        if not q:
            continue

        correct_opt = next((o for o in q.options if o.is_correct), None)
        correct_id = correct_opt.id if correct_opt else None

        if not item.selected_option_id and not item.answer_text:
            skipped_count += 1
            is_correct = False
        else:
            is_correct = (item.selected_option_id == correct_id) if item.selected_option_id else False
            if is_correct:
                correct_count += 1
            else:
                incorrect_count += 1
                weak_topic_ids.add(q.topic_id)
                # Log mistake
                db.add(
                    Mistake(
                        user_id=current_user.id,
                        topic_id=q.topic_id,
                        description=f"Test Question: {q.question_text[:120]}...",
                        correction=f"Correct Answer: {correct_opt.option_text if correct_opt else 'N/A'}. {q.explanation or ''}",
                        source_type="TEST",
                    )
                )

        # Record attempt
        db.add(
            PracticeAttempt(
                user_id=current_user.id,
                question_id=q.id,
                topic_id=q.topic_id,
                answer_given=str(item.selected_option_id or item.answer_text or "SKIPPED"),
                is_correct=is_correct,
                score=1.0 if is_correct else 0.0,
                time_taken_seconds=item.time_taken_seconds,
                session_id=req.session_id,
            )
        )

        # Update topic progress assessment score
        prog_res = await db.execute(
            select(TopicProgress).where(
                TopicProgress.user_id == current_user.id,
                TopicProgress.topic_id == q.topic_id,
            )
        )
        prog = prog_res.scalar_one_or_none()
        if not prog:
            prog = TopicProgress(user_id=current_user.id, topic_id=q.topic_id)
            db.add(prog)

        prog.quiz_completed = True
        prog.quiz_attempt_count = (prog.quiz_attempt_count or 0) + 1
        score_val = 100.0 if is_correct else 0.0
        prog.quiz_best_score = max(prog.quiz_best_score or 0.0, score_val)
        prog.assessment_completion = max(prog.assessment_completion or 0.0, 1.0 if is_correct else 0.4)
        prog.last_studied_at = datetime.now(timezone.utc)
        prog.calculate_mastery()

        details.append({
            "question_id": q.id,
            "question_text": q.question_text,
            "is_correct": is_correct,
            "selected_option_id": item.selected_option_id,
            "correct_option_id": correct_id,
            "correct_option_text": correct_opt.option_text if correct_opt else None,
            "explanation": q.explanation,
            "topic_name": q.topic.name if q.topic else None,
        })

    pct = round((correct_count / total * 100) if total > 0 else 0.0, 1)

    # Resolve weak topic details
    weak_topics_list = []
    recommended_revisions = []
    if weak_topic_ids:
        weak_res = await db.execute(
            select(Topic)
            .options(selectinload(Topic.unit).selectinload(Unit.subject))
            .where(Topic.id.in_(weak_topic_ids))
        )
        for wt in weak_res.scalars().all():
            weak_topics_list.append({
                "topic_id": wt.id,
                "topic_name": wt.name,
                "course_code": wt.unit.subject.course_code,
                "unit_number": wt.unit.unit_number,
            })
            recommended_revisions.append(f"Revise {wt.unit.subject.course_code} Unit {wt.unit.unit_number}: {wt.name}")

    await db.commit()

    return TestResultOut(
        session_id=req.session_id,
        total_questions=total,
        correct_count=correct_count,
        incorrect_count=incorrect_count,
        skipped_count=skipped_count,
        score_percentage=pct,
        passed=pct >= 50.0,
        weak_topics=weak_topics_list,
        recommended_revision=recommended_revisions,
        details=details,
    )


# ── Mistakes Notebook ─────────────────────────────────────────────────────────

@router.get("/mistakes", response_model=list[MistakeOut])
async def get_mistakes(
    is_resolved: bool = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stmt = (
        select(Mistake)
        .options(selectinload(Mistake.topic).selectinload(Topic.unit).selectinload(Unit.subject))
        .where(Mistake.user_id == current_user.id)
    )
    if is_resolved is not None:
        stmt = stmt.where(Mistake.is_resolved == is_resolved)
    stmt = stmt.order_by(Mistake.created_at.desc())
    res = await db.execute(stmt)
    mistakes = res.scalars().all()

    out = []
    for m in mistakes:
        out.append(
            MistakeOut(
                id=m.id,
                topic_id=m.topic_id,
                topic_name=m.topic.name if m.topic else None,
                course_code=m.topic.unit.subject.course_code if (m.topic and m.topic.unit and m.topic.unit.subject) else None,
                description=m.description,
                correction=m.correction,
                source_type=m.source_type,
                is_resolved=m.is_resolved,
                created_at=m.created_at,
            )
        )
    return out


@router.post("/mistakes/{mistake_id}/resolve")
async def resolve_mistake(
    mistake_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    res = await db.execute(
        select(Mistake).where(Mistake.id == mistake_id, Mistake.user_id == current_user.id)
    )
    m = res.scalar_one_or_none()
    if not m:
        raise HTTPException(status_code=404, detail="Mistake entry not found")
    m.is_resolved = True
    await db.commit()
    return {"status": "resolved", "id": mistake_id}
