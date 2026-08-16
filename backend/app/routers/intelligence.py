"""Revision, Smart Recommendations, Practicals, Analytics, and Global Search router."""
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from sqlalchemy.orm import selectinload
from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.curriculum import Subject, Unit, Topic, Practical, PracticalStatus
from app.models.progress import TopicProgress, TopicStatus, PracticalProgress, Mistake, Note
from app.models.practice import Question, CodingProblem, PracticeAttempt

router = APIRouter(tags=["intelligence"])


# ── Revision System ───────────────────────────────────────────────────────────

@router.get("/revision/queue")
async def get_revision_queue(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Calculate revision queue with HIGH, MEDIUM, LOW priorities based on:
    - Status == NEEDS_REVISION
    - Low quiz score / mastery
    - Gap in study time (> 5 days)
    - Active unresolved mistakes
    """
    stmt = (
        select(TopicProgress)
        .options(selectinload(TopicProgress.topic).selectinload(Topic.unit).selectinload(Unit.subject))
        .where(TopicProgress.user_id == current_user.id)
    )
    res = await db.execute(stmt)
    progs = res.scalars().all()

    now = datetime.now(timezone.utc)
    queue = []

    for p in progs:
        if not p.topic or not p.topic.unit or not p.topic.unit.subject:
            continue

        priority = "LOW"
        reason = "Routine periodic review"

        # Check mistake count
        mistake_cnt = await db.execute(
            select(func.count(Mistake.id)).where(
                Mistake.user_id == current_user.id,
                Mistake.topic_id == p.topic_id,
                Mistake.is_resolved == False,
            )
        )
        has_unresolved_mistakes = (mistake_cnt.scalar() or 0) > 0

        days_since_study = (now - p.last_studied_at).days if p.last_studied_at else 999

        if p.status == TopicStatus.NEEDS_REVISION or (p.mastery_percent < 40 and p.status != TopicStatus.NOT_STARTED):
            priority = "HIGH"
            reason = "Marked for revision or low mastery (< 40%)"
        elif has_unresolved_mistakes:
            priority = "HIGH"
            reason = "Has unresolved mistakes from recent practice/test"
        elif days_since_study > 7 and p.status == TopicStatus.LEARNED:
            priority = "MEDIUM"
            reason = f"Studied {days_since_study} days ago without revision"
        elif p.confidence_level < 3 and p.status in [TopicStatus.LEARNING, TopicStatus.LEARNED]:
            priority = "MEDIUM"
            reason = "Low user-rated confidence score"

        if priority in ["HIGH", "MEDIUM"] or p.status == TopicStatus.NEEDS_REVISION:
            queue.append({
                "topic_id": p.topic.id,
                "topic_name": p.topic.name,
                "course_code": p.topic.unit.subject.course_code,
                "unit_number": p.topic.unit.unit_number,
                "unit_name": p.topic.unit.name,
                "priority": priority,
                "mastery_percent": p.mastery_percent,
                "status": p.status,
                "reason": reason,
                "last_studied_at": p.last_studied_at.isoformat() if p.last_studied_at else None,
            })

    # Sort: HIGH first, then lowest mastery
    priority_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
    queue.sort(key=lambda x: (priority_order.get(x["priority"], 3), x["mastery_percent"]))
    return queue


@router.post("/revision/{topic_id}/complete")
async def complete_revision(
    topic_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Mark a revision session complete for a topic."""
    res = await db.execute(
        select(TopicProgress).where(
            TopicProgress.user_id == current_user.id,
            TopicProgress.topic_id == topic_id,
        )
    )
    p = res.scalar_one_or_none()
    if not p:
        p = TopicProgress(user_id=current_user.id, topic_id=topic_id)
        db.add(p)

    now = datetime.now(timezone.utc)
    p.revision_count += 1
    p.revision_completion = min(1.0, p.revision_completion + 0.5)
    p.last_revised_at = now
    p.last_studied_at = now
    if p.status == TopicStatus.NEEDS_REVISION:
        p.status = TopicStatus.LEARNED
    p.calculate_mastery()

    await db.commit()
    return {"status": "success", "mastery_percent": p.mastery_percent}


# ── Smart "What should I study now?" Recommender ─────────────────────────────

@router.get("/recommendations/what-to-study")
async def get_what_to_study_now(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Analyzes:
    1. Weak topics (< 50% mastery)
    2. High priority revision due
    3. Next unstarted topic in curriculum progression
    4. Pending coding or practical experiment
    Returns an actionable 60-minute session breakdown.
    """
    # 1. Look for urgent revision / weak topic
    weak_res = await db.execute(
        select(TopicProgress)
        .options(selectinload(TopicProgress.topic).selectinload(Topic.unit).selectinload(Unit.subject))
        .where(
            TopicProgress.user_id == current_user.id,
            or_(
                TopicProgress.status == TopicStatus.NEEDS_REVISION,
                TopicProgress.mastery_percent < 50,
            ),
            TopicProgress.status != TopicStatus.NOT_STARTED,
        )
        .order_by(TopicProgress.mastery_percent.asc())
        .limit(2)
    )
    weak_progs = weak_res.scalars().all()

    # 2. Next unstarted topic in a subject that needs work
    subj_res = await db.execute(select(Subject).where(Subject.is_active == True).order_by(Subject.sort_order))
    subjects = subj_res.scalars().all()

    next_new_topic = None
    for s in subjects:
        top_res = await db.execute(
            select(Topic)
            .join(Unit, Topic.unit_id == Unit.id)
            .options(selectinload(Topic.unit).selectinload(Unit.subject))
            .where(Unit.subject_id == s.id)
            .order_by(Unit.unit_number, Topic.sort_order)
        )
        topics = top_res.scalars().all()
        for t in topics:
            p_check = await db.execute(
                select(TopicProgress).where(
                    TopicProgress.user_id == current_user.id,
                    TopicProgress.topic_id == t.id,
                )
            )
            prog = p_check.scalar_one_or_none()
            if not prog or prog.status == TopicStatus.NOT_STARTED:
                next_new_topic = t
                break
        if next_new_topic:
            break

    # 3. Next pending practical or coding problem
    coding_res = await db.execute(
        select(CodingProblem)
        .options(selectinload(CodingProblem.topic).selectinload(Topic.unit).selectinload(Unit.subject))
        .limit(1)
    )
    next_coding = coding_res.scalar_one_or_none()

    # Build 60-Minute Plan
    plan_blocks = []
    total_minutes = 0

    if weak_progs:
        wp = weak_progs[0]
        plan_blocks.append({
            "duration_minutes": 20,
            "title": f"Revise & Strengthen: {wp.topic.name}",
            "subject": wp.topic.unit.subject.course_code,
            "unit": f"Unit {wp.topic.unit.unit_number}",
            "topic_id": wp.topic.id,
            "type": "REVISION",
            "reason": f"Current mastery is {wp.mastery_percent:.0f}%. High-priority review required.",
        })
        total_minutes += 20

    if next_new_topic:
        plan_blocks.append({
            "duration_minutes": 25,
            "title": f"Learn New Core Concept: {next_new_topic.name}",
            "subject": next_new_topic.unit.subject.course_code,
            "unit": f"Unit {next_new_topic.unit.unit_number}: {next_new_topic.unit.name}",
            "topic_id": next_new_topic.id,
            "type": "NEW_THEORY",
            "reason": "Next topic in your structured syllabus roadmap.",
        })
        total_minutes += 25

    if next_coding:
        rem_min = 60 - total_minutes
        plan_blocks.append({
            "duration_minutes": rem_min,
            "title": f"Coding Lab: {next_coding.title}",
            "subject": next_coding.topic.unit.subject.course_code,
            "unit": f"Unit {next_coding.topic.unit.unit_number}",
            "topic_id": next_coding.topic.id,
            "type": "CODING",
            "reason": f"Practical application in {next_coding.language}.",
        })
    else:
        plan_blocks.append({
            "duration_minutes": 15,
            "title": "Practice Quiz & Knowledge Check",
            "subject": "All Subjects",
            "unit": "Mixed Scope",
            "topic_id": None,
            "type": "QUIZ",
            "reason": "Reinforce memory retention through active retrieval.",
        })

    return {
        "session_title": "🎯 Focused 60-Minute Study Session",
        "total_minutes": 60,
        "blocks": plan_blocks,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


# ── Practical Tracker ─────────────────────────────────────────────────────────

@router.get("/practicals")
async def list_all_practicals(
    subject_id: int = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all official syllabus practical experiments with status and notes."""
    stmt = (
        select(Practical)
        .options(selectinload(Practical.subject))
        .order_by(Practical.subject_id, Practical.practical_number)
    )
    if subject_id:
        stmt = stmt.where(Practical.subject_id == subject_id)

    res = await db.execute(stmt)
    practicals = res.scalars().all()

    # Pull user progress for all practicals
    prog_res = await db.execute(
        select(PracticalProgress).where(PracticalProgress.user_id == current_user.id)
    )
    prog_map = {p.practical_id: p for p in prog_res.scalars().all()}

    out = []
    for p in practicals:
        up = prog_map.get(p.id)
        out.append({
            "id": p.id,
            "subject_id": p.subject_id,
            "course_code": p.subject.course_code,
            "subject_name": p.subject.name,
            "practical_number": p.practical_number,
            "title": p.title,
            "objective": p.objective,
            "description": p.description,
            "status": up.status if up else "NOT_STARTED",
            "code_content": up.code_content if up else None,
            "output_notes": up.output_notes if up else None,
            "notes": up.notes if up else None,
            "completed_at": up.completed_at.isoformat() if (up and up.completed_at) else None,
        })
    return out


# ── Deep Analytics ────────────────────────────────────────────────────────────

@router.get("/analytics/detailed")
async def get_detailed_analytics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Detailed analytics for charts: subject masteries, question attempt accuracy, streaks."""
    subjects_res = await db.execute(
        select(Subject).options(selectinload(Subject.units).selectinload(Unit.topics)).where(Subject.is_active == True)
    )
    subjects = subjects_res.scalars().all()

    all_topic_ids = [t.id for s in subjects for u in s.units for t in u.topics]
    prog_res = await db.execute(
        select(TopicProgress).where(TopicProgress.user_id == current_user.id, TopicProgress.topic_id.in_(all_topic_ids))
    )
    prog_map = {p.topic_id: p for p in prog_res.scalars().all()}

    subject_chart_data = []
    for s in subjects:
        s_tids = [t.id for u in s.units for t in u.topics]
        total = len(s_tids)
        learned = sum(1 for tid in s_tids if prog_map.get(tid) and prog_map[tid].status == TopicStatus.LEARNED)
        learning = sum(1 for tid in s_tids if prog_map.get(tid) and prog_map[tid].status == TopicStatus.LEARNING)
        rev = sum(1 for tid in s_tids if prog_map.get(tid) and prog_map[tid].status == TopicStatus.NEEDS_REVISION)
        not_st = total - learned - learning - rev

        masteries = [prog_map[tid].mastery_percent for tid in s_tids if tid in prog_map]
        avg_m = sum(masteries) / len(masteries) if masteries else 0.0

        subject_chart_data.append({
            "course_code": s.course_code,
            "name": s.name[:18] + ("…" if len(s.name) > 18 else ""),
            "learned": learned,
            "learning": learning,
            "needs_revision": rev,
            "not_started": not_st,
            "average_mastery": round(avg_m, 1),
            "completion_pct": round((learned / total * 100) if total > 0 else 0, 1),
        })

    # Total questions attempted & accuracy
    attempt_res = await db.execute(
        select(
            func.count(PracticeAttempt.id),
            func.sum(func.case((PracticeAttempt.is_correct == True, 1), else_=0))
        ).where(PracticeAttempt.user_id == current_user.id)
    )
    total_att, total_corr = attempt_res.one()
    total_att = total_att or 0
    total_corr = total_corr or 0
    accuracy = round((total_corr / total_att * 100) if total_att > 0 else 0, 1)

    return {
        "subject_breakdown": subject_chart_data,
        "total_attempts": total_att,
        "correct_attempts": total_corr,
        "overall_accuracy_percent": accuracy,
        "study_streak_days": 1,
    }


# ── Global Search ─────────────────────────────────────────────────────────────

@router.get("/search")
async def global_search(
    q: str = Query(..., min_length=1),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """
    Search across:
    - Subjects
    - Units
    - Topics
    - Practicals
    - Coding Problems
    """
    pattern = f"%{q}%"
    results = []

    # Subjects
    sub_res = await db.execute(
        select(Subject).where(or_(Subject.course_code.ilike(pattern), Subject.name.ilike(pattern)))
    )
    for s in sub_res.scalars().all():
        results.append({
            "type": "SUBJECT",
            "title": f"{s.course_code} - {s.name}",
            "subtitle": f"{s.credits} Credits",
            "url": f"/subjects/{s.id}",
        })

    # Units
    unit_res = await db.execute(
        select(Unit).options(selectinload(Unit.subject)).where(Unit.name.ilike(pattern))
    )
    for u in unit_res.scalars().all():
        results.append({
            "type": "UNIT",
            "title": f"{u.subject.course_code} Unit {u.unit_number}: {u.name}",
            "subtitle": u.subject.name,
            "url": f"/subjects/{u.subject_id}",
        })

    # Topics
    top_res = await db.execute(
        select(Topic)
        .options(selectinload(Topic.unit).selectinload(Unit.subject))
        .where(Topic.name.ilike(pattern))
        .limit(10)
    )
    for t in top_res.scalars().all():
        results.append({
            "type": "TOPIC",
            "title": t.name,
            "subtitle": f"{t.unit.subject.course_code} • Unit {t.unit.unit_number}: {t.unit.name}",
            "url": f"/topics/{t.id}",
        })

    # Practicals
    prac_res = await db.execute(
        select(Practical).options(selectinload(Practical.subject)).where(Practical.title.ilike(pattern)).limit(5)
    )
    for p in prac_res.scalars().all():
        results.append({
            "type": "PRACTICAL",
            "title": f"Practical {p.practical_number}: {p.title}",
            "subtitle": f"{p.subject.course_code} - {p.subject.name}",
            "url": f"/practicals",
        })

    # Coding
    code_res = await db.execute(
        select(CodingProblem).options(selectinload(CodingProblem.topic)).where(CodingProblem.title.ilike(pattern)).limit(5)
    )
    for c in code_res.scalars().all():
        results.append({
            "type": "CODING",
            "title": c.title,
            "subtitle": f"{c.language} • {c.difficulty}",
            "url": f"/coding",
        })

    return results
