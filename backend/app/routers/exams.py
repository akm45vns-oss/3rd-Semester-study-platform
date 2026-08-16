"""Master Exam Preparation & Simulator router for Midterm and End-Term patterns."""
import uuid
import random
from datetime import datetime, timezone, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.exam_config import MIDTERM_EXAM_CONFIG, END_TERM_EXAM_CONFIG, get_exam_config
from app.models.user import User
from app.models.curriculum import Subject, Unit, Topic
from app.models.progress import TopicProgress, TopicStatus, Mistake, RevisionItem, RevisionPriority
from app.models.practice import (
    Question, QuestionOption, PracticeAttempt, Difficulty,
    DescriptiveQuestion, DescriptiveSubmission
)
from app.schemas.exams import (
    ExamBlueprintOut, ExamReadinessOut, ExamReadinessSubject, ExamReadinessUnit,
    DescriptiveQuestionOut, DescriptiveSubmissionCreate, DescriptiveSubmissionOut,
    ExamSessionOut, ExamMCQQuestionOut, ExamMCQOptionOut,
    ExamSubmissionCreate, ExamResultOut, UnitScoreBreakdown, ExamReviewQuestion
)

router = APIRouter(prefix="/exams", tags=["exams"])


# ── In-memory active session cache for timer & question tracking ──
# (Allows seamless page reload and state resumption)
ACTIVE_EXAM_SESSIONS: dict[str, dict] = {}


@router.get("/blueprint", response_model=List[ExamBlueprintOut])
async def get_exam_blueprints(
    _: User = Depends(get_current_user)
):
    """Retrieve official university examination blueprints for Midterm and End-Term."""
    return [
        ExamBlueprintOut(**MIDTERM_EXAM_CONFIG.to_dict()),
        ExamBlueprintOut(**END_TERM_EXAM_CONFIG.to_dict()),
    ]


@router.get("/readiness", response_model=ExamReadinessOut)
async def get_exam_readiness(
    subject_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Calculate comprehensive Midterm and End-Term Readiness based on verified student progress."""
    subjects_query = select(Subject).options(selectinload(Subject.units).selectinload(Unit.topics))
    if subject_id:
        subjects_query = subjects_query.where(Subject.id == subject_id)
    
    sub_res = await db.execute(subjects_query)
    subjects = sub_res.scalars().all()

    # Load all user topic progress
    prog_res = await db.execute(
        select(TopicProgress).where(TopicProgress.user_id == current_user.id)
    )
    user_progs = {p.topic_id: p for p in prog_res.scalars().all()}

    # Load MCQ attempts
    attempts_res = await db.execute(
        select(PracticeAttempt).where(PracticeAttempt.user_id == current_user.id)
    )
    user_attempts = attempts_res.scalars().all()

    # Load Descriptive submissions
    desc_sub_res = await db.execute(
        select(DescriptiveSubmission).where(DescriptiveSubmission.user_id == current_user.id)
    )
    user_desc_subs = {s.question_id: s for s in desc_sub_res.scalars().all()}

    subject_readiness_list: List[ExamReadinessSubject] = []
    total_midterm_scores: List[float] = []
    total_endterm_scores: List[float] = []
    weakest_unit_info = ""
    min_unit_mastery = 101.0
    weakest_subject_name = ""
    min_subject_mastery = 101.0

    for sub in subjects:
        units_readiness: List[ExamReadinessUnit] = []
        midterm_unit_masteries: List[float] = []
        all_unit_masteries: List[float] = []
        sub_weak_topics: List[str] = []

        for unit in sorted(sub.units, key=lambda u: u.unit_number):
            unit_topics = unit.topics
            t_count = len(unit_topics)
            mastered_count = 0
            mastery_sum = 0.0

            for t in unit_topics:
                prog = user_progs.get(t.id)
                if prog:
                    m = prog.mastery_percent or 0.0
                    mastery_sum += m
                    if m >= 80.0:
                        mastered_count += 1
                    if m < 50.0 and len(sub_weak_topics) < 4:
                        sub_weak_topics.append(t.name)
                else:
                    if len(sub_weak_topics) < 4:
                        sub_weak_topics.append(t.name)

            unit_mastery = round(mastery_sum / max(1, t_count), 1)
            
            # Unit MCQ accuracy
            unit_topic_ids = {t.id for t in unit_topics}
            unit_att = [a for a in user_attempts if a.topic_id in unit_topic_ids]
            u_correct = sum(1 for a in unit_att if a.is_correct)
            u_acc = round((u_correct / max(1, len(unit_att))) * 100, 1) if unit_att else 0.0

            if unit.unit_number <= 3:
                midterm_unit_masteries.append(unit_mastery)
            all_unit_masteries.append(unit_mastery)

            if unit_mastery < min_unit_mastery:
                min_unit_mastery = unit_mastery
                weakest_unit_info = f"{sub.course_code} · Unit {unit.unit_number}: {unit.name}"

            units_readiness.append(
                ExamReadinessUnit(
                    unit_number=unit.unit_number,
                    title=unit.name,
                    mastery_percent=unit_mastery,
                    topics_count=t_count,
                    topics_mastered=mastered_count,
                    mcq_accuracy=u_acc,
                )
            )

        mid_subj_score = round(sum(midterm_unit_masteries) / max(1, len(midterm_unit_masteries)), 1)
        end_subj_score = round(sum(all_unit_masteries) / max(1, len(all_unit_masteries)), 1)

        if mid_subj_score < min_subject_mastery:
            min_subject_mastery = mid_subj_score
            weakest_subject_name = f"{sub.course_code} ({sub.name})"

        total_midterm_scores.append(mid_subj_score)
        total_endterm_scores.append(end_subj_score)

        subject_readiness_list.append(
            ExamReadinessSubject(
                subject_id=sub.id,
                course_code=sub.course_code,
                subject_name=sub.name,
                midterm_readiness_percent=mid_subj_score,
                endterm_readiness_percent=end_subj_score,
                units=units_readiness,
                weak_topics=sub_weak_topics,
            )
        )

    overall_mid = round(sum(total_midterm_scores) / max(1, len(total_midterm_scores)), 1) if total_midterm_scores else 0.0
    overall_end = round(sum(total_endterm_scores) / max(1, len(total_endterm_scores)), 1) if total_endterm_scores else 0.0

    return ExamReadinessOut(
        overall_midterm_readiness=overall_mid,
        overall_endterm_readiness=overall_end,
        upcoming_exam="MIDTERM",
        days_remaining=None,
        target_date=None,
        subjects=subject_readiness_list,
        weakest_subject=weakest_subject_name,
        weakest_unit_info=weakest_unit_info,
    )


@router.post("/midterm/generate", response_model=ExamSessionOut)
async def generate_midterm_mock(
    subject_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Generate an official 30-MCQ Midterm Examination Simulator.
    Strictly covers Units 1, 2, and 3. Validates exactly 30 questions server-side.
    """
    # 1. Fetch available questions across Units 1-3
    q_stmt = (
        select(Question)
        .options(selectinload(Question.options), selectinload(Question.topic).selectinload(Topic.unit).selectinload(Unit.subject))
        .join(Topic, Question.topic_id == Topic.id)
        .join(Unit, Topic.unit_id == Unit.id)
        .where(
            Question.is_active == True,
            Unit.unit_number.in_([1, 2, 3])
        )
    )
    if subject_id:
        q_stmt = q_stmt.where(Unit.subject_id == subject_id)

    res = await db.execute(q_stmt)
    all_midterm_questions = res.scalars().all()

    if len(all_midterm_questions) < 30:
        raise HTTPException(
            status_code=400,
            detail=f"Insufficient Midterm questions in database ({len(all_midterm_questions)} found, 30 required). Please seed more Unit 1-3 questions."
        )

    # 2. Balanced selection across Units 1, 2, and 3
    unit_groups: dict[int, list[Question]] = {1: [], 2: [], 3: []}
    for q in all_midterm_questions:
        if q.topic and q.topic.unit and q.topic.unit.unit_number in unit_groups:
            unit_groups[q.topic.unit.unit_number].append(q)

    selected_questions: list[Question] = []
    target_per_unit = 10  # 10 * 3 = 30

    for u_num in [1, 2, 3]:
        available = unit_groups[u_num]
        random.shuffle(available)
        take_count = min(len(available), target_per_unit)
        selected_questions.extend(available[:take_count])

    # If any unit had < 10, fill remainder from remaining questions
    if len(selected_questions) < 30:
        selected_ids = {q.id for q in selected_questions}
        remainder = [q for q in all_midterm_questions if q.id not in selected_ids]
        random.shuffle(remainder)
        needed = 30 - len(selected_questions)
        selected_questions.extend(remainder[:needed])

    # Exact count enforcement
    selected_questions = selected_questions[:30]
    if len(selected_questions) != 30:
        raise HTTPException(status_code=500, detail="Failed to select exactly 30 Midterm questions.")

    random.shuffle(selected_questions)

    session_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(minutes=MIDTERM_EXAM_CONFIG.duration_minutes)

    # Format MCQs
    formatted_mcqs: List[ExamMCQQuestionOut] = []
    for q in selected_questions:
        opts = [
            ExamMCQOptionOut(id=opt.id, option_text=opt.option_text, sort_order=opt.sort_order)
            for opt in sorted(q.options, key=lambda o: o.sort_order)
        ]
        formatted_mcqs.append(
            ExamMCQQuestionOut(
                id=q.id,
                topic_id=q.topic_id,
                topic_name=q.topic.name if q.topic else None,
                unit_number=q.topic.unit.unit_number if q.topic and q.topic.unit else None,
                course_code=q.topic.unit.subject.course_code if q.topic and q.topic.unit and q.topic.unit.subject else None,
                question_text=q.question_text,
                difficulty=q.difficulty,
                options=opts,
            )
        )

    # Cache session
    ACTIVE_EXAM_SESSIONS[session_id] = {
        "user_id": current_user.id,
        "exam_type": "MIDTERM",
        "question_ids": [q.id for q in selected_questions],
        "created_at": now,
        "expires_at": expires_at,
    }

    sub_name = selected_questions[0].topic.unit.subject.name if selected_questions[0].topic and selected_questions[0].topic.unit and selected_questions[0].topic.unit.subject else "3rd Semester All Subjects"
    c_code = selected_questions[0].topic.unit.subject.course_code if selected_questions[0].topic and selected_questions[0].topic.unit and selected_questions[0].topic.unit.subject else "ALL"

    return ExamSessionOut(
        session_id=session_id,
        exam_type="MIDTERM",
        subject_id=subject_id,
        subject_name=sub_name if subject_id else "Semester Multi-Subject Midterm",
        course_code=c_code if subject_id else "MIDTERM-30",
        duration_minutes=MIDTERM_EXAM_CONFIG.duration_minutes,
        total_marks=MIDTERM_EXAM_CONFIG.total_marks,
        mcqs=formatted_mcqs,
        descriptive_questions=[],
        created_at=now,
        expires_at=expires_at,
    )


@router.post("/endterm/generate", response_model=ExamSessionOut)
async def generate_endterm_mock(
    subject_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Generate an official End-Term Examination Simulator:
    Part A: Exactly 30 MCQs across Units 1–6.
    Part B: Exactly 5 Descriptive 10-Mark Questions.
    Server-side validates exactly 30 MCQs and 5 Descriptive questions.
    """
    # 1. Fetch MCQs across Units 1-6
    q_stmt = (
        select(Question)
        .options(selectinload(Question.options), selectinload(Question.topic).selectinload(Topic.unit).selectinload(Unit.subject))
        .join(Topic, Question.topic_id == Topic.id)
        .join(Unit, Topic.unit_id == Unit.id)
        .where(Question.is_active == True)
    )
    if subject_id:
        q_stmt = q_stmt.where(Unit.subject_id == subject_id)

    res = await db.execute(q_stmt)
    all_questions = res.scalars().all()

    if len(all_questions) < 30:
        raise HTTPException(
            status_code=400,
            detail=f"Insufficient questions in database ({len(all_questions)} found, 30 required)."
        )

    # 2. Balanced MCQ selection across Units 1-6 (target ~5 per unit)
    unit_groups: dict[int, list[Question]] = {i: [] for i in range(1, 7)}
    for q in all_questions:
        if q.topic and q.topic.unit and q.topic.unit.unit_number in unit_groups:
            unit_groups[q.topic.unit.unit_number].append(q)

    selected_mcqs: list[Question] = []
    for u_num in range(1, 7):
        available = unit_groups[u_num]
        random.shuffle(available)
        selected_mcqs.extend(available[:5])

    if len(selected_mcqs) < 30:
        sel_ids = {q.id for q in selected_mcqs}
        rem = [q for q in all_questions if q.id not in sel_ids]
        random.shuffle(rem)
        needed = 30 - len(selected_mcqs)
        selected_mcqs.extend(rem[:needed])

    selected_mcqs = selected_mcqs[:30]
    if len(selected_mcqs) != 30:
        raise HTTPException(status_code=500, detail="Failed to select exactly 30 End-Term MCQs.")

    random.shuffle(selected_mcqs)

    # 3. Fetch 5 Descriptive 10-Mark Questions
    desc_stmt = (
        select(DescriptiveQuestion)
        .options(selectinload(DescriptiveQuestion.topic), selectinload(DescriptiveQuestion.unit), selectinload(DescriptiveQuestion.subject))
        .where(DescriptiveQuestion.is_active == True)
    )
    if subject_id:
        desc_stmt = desc_stmt.where(DescriptiveQuestion.subject_id == subject_id)

    desc_res = await db.execute(desc_stmt)
    all_desc = desc_res.scalars().all()

    selected_desc: list[DescriptiveQuestion] = []
    if all_desc:
        random.shuffle(all_desc)
        selected_desc = all_desc[:5]

    session_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(minutes=END_TERM_EXAM_CONFIG.duration_minutes)

    # Format MCQs
    formatted_mcqs: List[ExamMCQQuestionOut] = []
    for q in selected_mcqs:
        opts = [
            ExamMCQOptionOut(id=opt.id, option_text=opt.option_text, sort_order=opt.sort_order)
            for opt in sorted(q.options, key=lambda o: o.sort_order)
        ]
        formatted_mcqs.append(
            ExamMCQQuestionOut(
                id=q.id,
                topic_id=q.topic_id,
                topic_name=q.topic.name if q.topic else None,
                unit_number=q.topic.unit.unit_number if q.topic and q.topic.unit else None,
                course_code=q.topic.unit.subject.course_code if q.topic and q.topic.unit and q.topic.unit.subject else None,
                question_text=q.question_text,
                difficulty=q.difficulty,
                options=opts,
            )
        )

    # Format Descriptive Questions
    formatted_desc: List[DescriptiveQuestionOut] = []
    for dq in selected_desc:
        formatted_desc.append(
            DescriptiveQuestionOut(
                id=dq.id,
                subject_id=dq.subject_id,
                course_code=dq.subject.course_code if dq.subject else None,
                unit_id=dq.unit_id,
                unit_number=dq.unit.unit_number if dq.unit else None,
                topic_id=dq.topic_id,
                topic_name=dq.topic.name if dq.topic else None,
                question_text=dq.question_text,
                marks=dq.marks,
                difficulty=dq.difficulty,
                question_type=dq.question_type,
                answer_outline=dq.answer_outline or [],
                model_answer=dq.model_answer,
                key_points=dq.key_points or [],
                exam_tips=dq.exam_tips or [],
                important_terms=dq.important_terms or [],
                diagram_guidance=dq.diagram_guidance,
                code_guidance=dq.code_guidance,
            )
        )

    ACTIVE_EXAM_SESSIONS[session_id] = {
        "user_id": current_user.id,
        "exam_type": "END_TERM",
        "question_ids": [q.id for q in selected_mcqs],
        "descriptive_ids": [dq.id for dq in selected_desc],
        "created_at": now,
        "expires_at": expires_at,
    }

    return ExamSessionOut(
        session_id=session_id,
        exam_type="END_TERM",
        subject_id=subject_id,
        subject_name="End-Term Full Syllabus Examination",
        course_code="ENDTERM-80",
        duration_minutes=END_TERM_EXAM_CONFIG.duration_minutes,
        total_marks=END_TERM_EXAM_CONFIG.total_marks,
        mcqs=formatted_mcqs,
        descriptive_questions=formatted_desc,
        created_at=now,
        expires_at=expires_at,
    )


@router.post("/submit", response_model=ExamResultOut)
async def submit_exam(
    data: ExamSubmissionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Submit Midterm or End-Term Mock Exam.
    Calculates score, accuracy, unit breakdown, logs mistakes, and updates progress.
    """
    # 1. Fetch questions with options
    q_ids = [a.question_id for a in data.mcq_answers]
    q_res = await db.execute(
        select(Question)
        .options(selectinload(Question.options), selectinload(Question.topic).selectinload(Topic.unit))
        .where(Question.id.in_(q_ids))
    )
    questions_map = {q.id: q for q in q_res.scalars().all()}

    correct_count = 0
    incorrect_count = 0
    unanswered_count = 0
    unit_stats: dict[int, dict] = {}
    weak_topic_names: list[str] = []
    mistakes_logged = 0
    review_items: List[ExamReviewQuestion] = []

    for ans in data.mcq_answers:
        q = questions_map.get(ans.question_id)
        if not q:
            continue

        u_num = q.topic.unit.unit_number if q.topic and q.topic.unit else 1
        if u_num not in unit_stats:
            unit_stats[u_num] = {"total": 0, "correct": 0}
        unit_stats[u_num]["total"] += 1

        correct_opt = next((o for o in q.options if o.is_correct), None)
        corr_id = correct_opt.id if correct_opt else 0
        corr_text = correct_opt.option_text if correct_opt else ""

        user_opt = next((o for o in q.options if o.id == ans.selected_option_id), None)
        user_opt_text = user_opt.option_text if user_opt else None

        is_corr = False
        if ans.selected_option_id is None:
            unanswered_count += 1
        elif ans.selected_option_id == corr_id:
            is_corr = True
            correct_count += 1
            unit_stats[u_num]["correct"] += 1
        else:
            incorrect_count += 1

            # Log to Mistake Notebook
            if q.topic:
                db.add(
                    Mistake(
                        user_id=current_user.id,
                        topic_id=q.topic_id,
                        description=f"Exam Mistake: {q.question_text[:120]}...",
                        correction=f"Correct Answer: {corr_text}. {q.explanation or ''}",
                        source_type="EXAM_MOCK",
                    )
                )
                mistakes_logged += 1
                if q.topic.name not in weak_topic_names and len(weak_topic_names) < 5:
                    weak_topic_names.append(q.topic.name)

        # Record attempt
        db.add(
            PracticeAttempt(
                user_id=current_user.id,
                question_id=q.id,
                topic_id=q.topic_id,
                answer_given=str(ans.selected_option_id or ""),
                is_correct=is_corr,
                score=1.0 if is_corr else 0.0,
                session_id=data.session_id,
            )
        )

        review_items.append(
            ExamReviewQuestion(
                question_id=q.id,
                question_text=q.question_text,
                topic_name=q.topic.name if q.topic else None,
                unit_number=u_num,
                user_selected_option_id=ans.selected_option_id,
                user_selected_option_text=user_opt_text,
                correct_option_id=corr_id,
                correct_option_text=corr_text,
                is_correct=is_corr,
                explanation=q.explanation,
            )
        )

    # 2. Record Descriptive Submissions if any
    desc_attempted = 0
    for dans in data.descriptive_answers:
        if dans.user_answer and dans.user_answer.strip():
            desc_attempted += 1
            db.add(
                DescriptiveSubmission(
                    user_id=current_user.id,
                    question_id=dans.question_id,
                    user_answer=dans.user_answer,
                    self_score=dans.self_score or 0.0,
                    status="UNDERSTOOD" if (dans.self_score or 0.0) >= 6.0 else "NEEDS_REVISION",
                )
            )

    await db.commit()

    total_mcqs = len(data.mcq_answers)
    accuracy = round((correct_count / max(1, total_mcqs)) * 100, 1)
    
    # Calculate unit breakdown
    breakdown: List[UnitScoreBreakdown] = []
    for u_num, st in sorted(unit_stats.items()):
        acc = round((st["correct"] / max(1, st["total"])) * 100, 1)
        breakdown.append(
            UnitScoreBreakdown(
                unit_number=u_num,
                questions_count=st["total"],
                correct_count=st["correct"],
                accuracy_percent=acc,
            )
        )

    # Remove session from memory cache
    ACTIVE_EXAM_SESSIONS.pop(data.session_id, None)

    return ExamResultOut(
        session_id=data.session_id,
        exam_type=data.exam_type,
        score=float(correct_count),
        total_marks=30 if data.exam_type == "MIDTERM" else 80,
        percentage=accuracy,
        mcqs_total=total_mcqs,
        mcqs_correct=correct_count,
        mcqs_incorrect=incorrect_count,
        mcqs_unanswered=unanswered_count,
        accuracy_percent=accuracy,
        descriptive_total=len(data.descriptive_answers),
        descriptive_attempted=desc_attempted,
        unit_breakdown=breakdown,
        weak_topics=weak_topic_names,
        mistakes_logged_count=mistakes_logged,
        review_mcqs=review_items,
        submitted_at=datetime.now(timezone.utc),
    )


@router.get("/descriptive", response_model=List[DescriptiveQuestionOut])
async def list_descriptive_questions(
    subject_id: Optional[int] = Query(None),
    unit_id: Optional[int] = Query(None),
    difficulty: Optional[Difficulty] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List 10-Mark Descriptive Questions with filters and student's solved status."""
    stmt = (
        select(DescriptiveQuestion)
        .options(
            selectinload(DescriptiveQuestion.subject),
            selectinload(DescriptiveQuestion.unit),
            selectinload(DescriptiveQuestion.topic),
            selectinload(DescriptiveQuestion.submissions)
        )
        .where(DescriptiveQuestion.is_active == True)
    )

    if subject_id:
        stmt = stmt.where(DescriptiveQuestion.subject_id == subject_id)
    if unit_id:
        stmt = stmt.where(DescriptiveQuestion.unit_id == unit_id)
    if difficulty:
        stmt = stmt.where(DescriptiveQuestion.difficulty == difficulty)

    res = await db.execute(stmt)
    questions = res.scalars().all()

    # Load user's latest submissions
    sub_stmt = select(DescriptiveSubmission).where(DescriptiveSubmission.user_id == current_user.id)
    sub_res = await db.execute(sub_stmt)
    user_subs = {s.question_id: s for s in sub_res.scalars().all()}

    output: List[DescriptiveQuestionOut] = []
    for dq in questions:
        usub = user_subs.get(dq.id)
        output.append(
            DescriptiveQuestionOut(
                id=dq.id,
                subject_id=dq.subject_id,
                course_code=dq.subject.course_code if dq.subject else None,
                unit_id=dq.unit_id,
                unit_number=dq.unit.unit_number if dq.unit else None,
                topic_id=dq.topic_id,
                topic_name=dq.topic.name if dq.topic else None,
                question_text=dq.question_text,
                marks=dq.marks,
                difficulty=dq.difficulty,
                question_type=dq.question_type,
                answer_outline=dq.answer_outline or [],
                model_answer=dq.model_answer,
                key_points=dq.key_points or [],
                exam_tips=dq.exam_tips or [],
                important_terms=dq.important_terms or [],
                diagram_guidance=dq.diagram_guidance,
                code_guidance=dq.code_guidance,
                is_solved=usub is not None,
                latest_score=usub.self_score if usub else None,
            )
        )

    return output


@router.post("/descriptive/submit", response_model=DescriptiveSubmissionOut)
async def submit_descriptive_answer(
    data: DescriptiveSubmissionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Submit a student's answer and self-evaluation score for a 10-Mark Descriptive Question.
    If marked 'NEEDS_REVISION', adds the topic to the active Revision queue.
    """
    dq_res = await db.execute(
        select(DescriptiveQuestion).where(DescriptiveQuestion.id == data.question_id)
    )
    dq = dq_res.scalar_one_or_none()
    if not dq:
        raise HTTPException(status_code=404, detail="Descriptive question not found.")

    sub = DescriptiveSubmission(
        user_id=current_user.id,
        question_id=dq.id,
        user_answer=data.user_answer,
        self_score=data.self_score,
        checklist_completed=data.checklist_completed,
        status=data.status,
    )
    db.add(sub)

    # If Needs Revision or low self score, add to Revision queue
    if data.status == "NEEDS_REVISION" or data.self_score < 6.0:
        db.add(
            RevisionItem(
                user_id=current_user.id,
                topic_id=dq.topic_id,
                priority=RevisionPriority.HIGH,
                reason=f"10-Mark Practice ({dq.question_text[:60]}...) self-scored {data.self_score}/10",
            )
        )

    await db.commit()
    await db.refresh(sub)

    return DescriptiveSubmissionOut(
        id=sub.id,
        question_id=sub.question_id,
        self_score=sub.self_score,
        status=sub.status,
        checklist_completed=sub.checklist_completed or [],
        submitted_at=sub.submitted_at,
    )
