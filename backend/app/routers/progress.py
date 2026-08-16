"""Progress tracking router — topic progress, practical progress, notes, study sessions, workspace."""
from datetime import datetime, timezone, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, desc
from sqlalchemy.orm import selectinload
from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.curriculum import Subject, Unit, Topic, Practical
from app.models.practice import Question, CodingProblem
from app.models.progress import (
    TopicProgress, PracticalProgress, Note, StudySession, DailyGoal, Mistake,
    TopicStatus,
)
from app.models.curriculum import PracticalStatus
from app.schemas.progress import (
    TopicProgressUpdate, TopicProgressOut,
    PracticalProgressUpdate, PracticalProgressOut,
    SubjectProgressOut, DashboardOut, NoteCreate, NoteOut,
    StudySessionStart, StudySessionFinish, StudySessionOut,
    TopicWorkspaceOut,
)

router = APIRouter(tags=["progress"])


# ── Topic Progress ────────────────────────────────────────────────────────────

@router.get("/progress/topics/{topic_id}", response_model=TopicProgressOut)
async def get_topic_progress(
    topic_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get current user's progress for a topic. Creates record if none exists."""
    result = await db.execute(
        select(TopicProgress).where(
            TopicProgress.user_id == current_user.id,
            TopicProgress.topic_id == topic_id,
        )
    )
    progress = result.scalar_one_or_none()
    if not progress:
        progress = TopicProgress(user_id=current_user.id, topic_id=topic_id)
        db.add(progress)
        await db.commit()
        await db.refresh(progress)
    return progress


@router.post("/progress/topics/{topic_id}", response_model=TopicProgressOut)
async def update_topic_progress(
    topic_id: int,
    data: TopicProgressUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update topic progress. Recalculates mastery automatically."""
    topic_check = await db.execute(select(Topic).where(Topic.id == topic_id))
    if not topic_check.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Topic not found")

    result = await db.execute(
        select(TopicProgress).where(
            TopicProgress.user_id == current_user.id,
            TopicProgress.topic_id == topic_id,
        )
    )
    progress = result.scalar_one_or_none()
    if not progress:
        progress = TopicProgress(user_id=current_user.id, topic_id=topic_id)
        db.add(progress)

    now = datetime.now(timezone.utc)

    if data.status is not None:
        progress.status = data.status
        if data.status == TopicStatus.LEARNED and not progress.first_learned_at:
            progress.first_learned_at = now
            progress.theory_completion = max(progress.theory_completion or 0.0, 1.0)
        if data.status == TopicStatus.NEEDS_REVISION:
            progress.revision_count = (progress.revision_count or 0) + 1

    if data.theory_completion is not None:
        progress.theory_completion = min(1.0, max(0.0, data.theory_completion))
    if data.practice_completion is not None:
        progress.practice_completion = min(1.0, max(0.0, data.practice_completion))
    if data.assessment_completion is not None:
        progress.assessment_completion = min(1.0, max(0.0, data.assessment_completion))
    if data.revision_completion is not None:
        progress.revision_completion = min(1.0, max(0.0, data.revision_completion))

    if data.notes_read is not None:
        progress.notes_read = data.notes_read
        if data.notes_read and (progress.theory_completion or 0.0) < 1.0:
            progress.theory_completion = 1.0

    if data.practice_completed is not None:
        progress.practice_completed = data.practice_completed
        if data.practice_completed and (progress.practice_completion or 0.0) < 1.0:
            progress.practice_completion = 1.0

    if data.quiz_completed is not None:
        progress.quiz_completed = data.quiz_completed
        if data.quiz_completed and (progress.assessment_completion or 0.0) < 1.0:
            progress.assessment_completion = 1.0

    if data.coding_completed is not None:
        progress.coding_completed = data.coding_completed

    if data.practical_completed is not None:
        progress.practical_completed = data.practical_completed

    if data.confidence_level is not None:
        progress.confidence_level = min(5, max(1, data.confidence_level))

    progress.last_studied_at = now
    progress.calculate_mastery()

    await db.commit()
    await db.refresh(progress)
    return progress


# ── Practical Progress ────────────────────────────────────────────────────────

@router.get("/progress/practicals/{practical_id}", response_model=PracticalProgressOut)
async def get_practical_progress(
    practical_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(PracticalProgress).where(
            PracticalProgress.user_id == current_user.id,
            PracticalProgress.practical_id == practical_id,
        )
    )
    progress = result.scalar_one_or_none()
    if not progress:
        progress = PracticalProgress(user_id=current_user.id, practical_id=practical_id)
        db.add(progress)
        await db.commit()
        await db.refresh(progress)
    return progress


@router.post("/progress/practicals/{practical_id}", response_model=PracticalProgressOut)
async def update_practical_progress(
    practical_id: int,
    data: PracticalProgressUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(PracticalProgress).where(
            PracticalProgress.user_id == current_user.id,
            PracticalProgress.practical_id == practical_id,
        )
    )
    progress = result.scalar_one_or_none()
    if not progress:
        progress = PracticalProgress(user_id=current_user.id, practical_id=practical_id)
        db.add(progress)

    if data.status is not None:
        progress.status = data.status
        if data.status == PracticalStatus.COMPLETED and not progress.completed_at:
            progress.completed_at = datetime.now(timezone.utc)
    if data.code_content is not None:
        progress.code_content = data.code_content
    if data.output_notes is not None:
        progress.output_notes = data.output_notes
    if data.notes is not None:
        progress.notes = data.notes

    await db.commit()
    await db.refresh(progress)
    return progress


# ── Subject Progress ──────────────────────────────────────────────────────────

@router.get("/progress/subjects/{subject_id}", response_model=SubjectProgressOut)
async def get_subject_progress(
    subject_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    subject_result = await db.execute(
        select(Subject)
        .options(selectinload(Subject.units).selectinload(Unit.topics))
        .where(Subject.id == subject_id)
    )
    subject = subject_result.scalar_one_or_none()
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")

    all_topic_ids = [t.id for u in subject.units for t in u.topics]

    progress_result = await db.execute(
        select(TopicProgress).where(
            TopicProgress.user_id == current_user.id,
            TopicProgress.topic_id.in_(all_topic_ids),
        )
    )
    progress_records = {p.topic_id: p for p in progress_result.scalars().all()}

    total = len(all_topic_ids)
    learned = sum(
        1 for tid in all_topic_ids
        if progress_records.get(tid) and progress_records[tid].status == TopicStatus.LEARNED
    )
    learning = sum(
        1 for tid in all_topic_ids
        if progress_records.get(tid) and progress_records[tid].status == TopicStatus.LEARNING
    )
    needs_rev = sum(
        1 for tid in all_topic_ids
        if progress_records.get(tid) and progress_records[tid].status == TopicStatus.NEEDS_REVISION
    )
    not_started = total - learned - learning - needs_rev

    masteries = [progress_records[tid].mastery_percent for tid in all_topic_ids if tid in progress_records]
    avg_mastery = sum(masteries) / len(masteries) if masteries else 0.0
    completion_pct = (learned / total * 100) if total > 0 else 0.0

    practicals_result = await db.execute(
        select(Practical).where(Practical.subject_id == subject_id)
    )
    practicals = practicals_result.scalars().all()
    prac_ids = [p.id for p in practicals]

    prac_prog_result = await db.execute(
        select(PracticalProgress).where(
            PracticalProgress.user_id == current_user.id,
            PracticalProgress.practical_id.in_(prac_ids),
        )
    )
    prac_progs = {pp.practical_id: pp for pp in prac_prog_result.scalars().all()}
    completed_pracs = sum(
        1 for pid in prac_ids
        if prac_progs.get(pid) and prac_progs[pid].status == PracticalStatus.COMPLETED
    )

    return SubjectProgressOut(
        subject_id=subject.id,
        course_code=subject.course_code,
        subject_name=subject.name,
        total_topics=total,
        learned_topics=learned,
        learning_topics=learning,
        needs_revision_topics=needs_rev,
        not_started_topics=not_started,
        completion_percent=round(completion_pct, 1),
        average_mastery=round(avg_mastery, 1),
        total_practicals=len(prac_ids),
        completed_practicals=completed_pracs,
        practical_completion_percent=round(completed_pracs / len(prac_ids) * 100 if prac_ids else 0.0, 1),
    )


# ── Dashboard (Aggregated & Action-Oriented) ──────────────────────────────────

@router.get("/dashboard", response_model=DashboardOut)
async def get_dashboard(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Compute action-oriented semester progress, continue-studying target, and smart weak areas."""
    subjects_result = await db.execute(
        select(Subject)
        .options(selectinload(Subject.units).selectinload(Unit.topics))
        .where(Subject.is_active == True)
        .order_by(Subject.sort_order)
    )
    subjects = subjects_result.scalars().all()

    all_topic_ids = [t.id for s in subjects for u in s.units for t in u.topics]

    progress_result = await db.execute(
        select(TopicProgress).where(
            TopicProgress.user_id == current_user.id,
            TopicProgress.topic_id.in_(all_topic_ids),
        )
    )
    progress_map = {p.topic_id: p for p in progress_result.scalars().all()}

    total_topics = len(all_topic_ids)
    learned = sum(1 for tid in all_topic_ids if progress_map.get(tid) and progress_map[tid].status == TopicStatus.LEARNED)
    needs_rev = sum(1 for tid in all_topic_ids if progress_map.get(tid) and progress_map[tid].status == TopicStatus.NEEDS_REVISION)
    overall_pct = round(learned / total_topics * 100, 1) if total_topics else 0.0

    prac_result = await db.execute(select(Practical))
    all_practicals = prac_result.scalars().all()
    prac_ids = [p.id for p in all_practicals]

    prac_prog_result = await db.execute(
        select(PracticalProgress).where(
            PracticalProgress.user_id == current_user.id,
            PracticalProgress.practical_id.in_(prac_ids),
        )
    )
    prac_progs = {pp.practical_id: pp for pp in prac_prog_result.scalars().all()}
    completed_pracs = sum(
        1 for pid in prac_ids
        if prac_progs.get(pid) and prac_progs[pid].status == PracticalStatus.COMPLETED
    )

    subject_progress_list = []
    topic_meta = {}
    for s in subjects:
        s_topic_ids = [t.id for u in s.units for t in u.topics]
        for u in s.units:
            for t in u.topics:
                topic_meta[t.id] = {
                    "topic_id": t.id,
                    "topic_name": t.name,
                    "unit_id": u.id,
                    "unit_number": u.unit_number,
                    "unit_name": u.name,
                    "subject_id": s.id,
                    "subject_name": s.name,
                    "course_code": s.course_code,
                    "has_coding": t.has_coding,
                }
        s_total = len(s_topic_ids)
        s_learned = sum(1 for tid in s_topic_ids if progress_map.get(tid) and progress_map[tid].status == TopicStatus.LEARNED)
        s_learning = sum(1 for tid in s_topic_ids if progress_map.get(tid) and progress_map[tid].status == TopicStatus.LEARNING)
        s_needs_rev = sum(1 for tid in s_topic_ids if progress_map.get(tid) and progress_map[tid].status == TopicStatus.NEEDS_REVISION)
        s_not_started = s_total - s_learned - s_learning - s_needs_rev
        s_masteries = [progress_map[tid].mastery_percent for tid in s_topic_ids if tid in progress_map]
        s_avg = sum(s_masteries) / len(s_masteries) if s_masteries else 0.0

        s_prac_ids = [p.id for p in all_practicals if p.subject_id == s.id]
        s_comp_pracs = sum(1 for pid in s_prac_ids if prac_progs.get(pid) and prac_progs[pid].status == PracticalStatus.COMPLETED)

        subject_progress_list.append(SubjectProgressOut(
            subject_id=s.id,
            course_code=s.course_code,
            subject_name=s.name,
            total_topics=s_total,
            learned_topics=s_learned,
            learning_topics=s_learning,
            needs_revision_topics=s_needs_rev,
            not_started_topics=s_not_started,
            completion_percent=round(s_learned / s_total * 100, 1) if s_total else 0.0,
            average_mastery=round(s_avg, 1),
            total_practicals=len(s_prac_ids),
            completed_practicals=s_comp_pracs,
            practical_completion_percent=round(s_comp_pracs / len(s_prac_ids) * 100 if s_prac_ids else 0.0, 1),
        ))

    # Recent studied topics
    recent_result = await db.execute(
        select(TopicProgress)
        .where(
            TopicProgress.user_id == current_user.id,
            TopicProgress.last_studied_at.isnot(None),
        )
        .order_by(TopicProgress.last_studied_at.desc())
        .limit(5)
    )
    recent_progs = recent_result.scalars().all()
    recent_topics = []
    for rp in recent_progs:
        meta = topic_meta.get(rp.topic_id)
        if meta:
            recent_topics.append({
                "topic_id": meta["topic_id"],
                "topic_name": meta["topic_name"],
                "unit_id": meta["unit_id"],
                "unit_number": meta["unit_number"],
                "subject_id": meta["subject_id"],
                "course_code": meta["course_code"],
                "status": rp.status,
                "mastery_percent": rp.mastery_percent,
                "last_studied_at": rp.last_studied_at.isoformat() if rp.last_studied_at else None,
            })

    # Continue Studying Target (Primary Hero Card)
    continue_studying = None
    if recent_topics:
        latest = recent_topics[0]
        # Calculate human friendly time ago
        time_ago_str = "Recently"
        if latest["last_studied_at"]:
            try:
                dt = datetime.fromisoformat(latest["last_studied_at"].replace("Z", "+00:00"))
                mins = max(1, int((datetime.now(timezone.utc) - dt).total_seconds() / 60))
                time_ago_str = f"{mins} minutes ago" if mins < 60 else f"{mins // 60} hours ago" if mins < 1440 else f"{mins // 1440} days ago"
            except Exception:
                pass
        
        # Determine next action for continuation
        prog = progress_map.get(latest["topic_id"])
        next_action_label = "Read Notes"
        if prog:
            if not prog.notes_read:
                next_action_label = "Read Academic Notes"
            elif not prog.practice_completed:
                next_action_label = "Solve Practice MCQs"
            elif latest.get("has_coding") and not prog.coding_completed:
                next_action_label = "Solve Coding Challenge"
            elif prog.mastery_percent < 80:
                next_action_label = "Quick Recall & Revision"
            else:
                next_action_label = "Review Topic Mastery"

        continue_studying = {
            "topic_id": latest["topic_id"],
            "topic_name": latest["topic_name"],
            "unit_number": latest["unit_number"],
            "course_code": latest["course_code"],
            "subject_name": latest.get("subject_name", latest["course_code"]),
            "mastery_percent": latest["mastery_percent"],
            "last_studied_ago": time_ago_str,
            "next_action_label": next_action_label,
            "to": f"/topics/{latest['topic_id']}",
        }
    elif all_topic_ids:
        # Fallback to the very first topic of the first subject
        first_tid = all_topic_ids[0]
        meta = topic_meta.get(first_tid, {})
        continue_studying = {
            "topic_id": first_tid,
            "topic_name": meta.get("topic_name", "Getting Started"),
            "unit_number": meta.get("unit_number", 1),
            "course_code": meta.get("course_code", "CAP392"),
            "subject_name": meta.get("subject_name", "Java Programming"),
            "mastery_percent": 0.0,
            "last_studied_ago": "Not started yet",
            "next_action_label": "Start Unit 1 Notes",
            "to": f"/topics/{first_tid}",
        }

    # Weak Topics (Smart Priority Ranking with mistake frequencies)
    # Fetch mistakes count grouped by topic
    mistakes_result = await db.execute(
        select(Mistake.topic_id, func.count(Mistake.id))
        .where(Mistake.user_id == current_user.id, Mistake.is_resolved == False)
        .group_by(Mistake.topic_id)
    )
    mistake_counts = dict(mistakes_result.all())

    candidate_weak = []
    for tid, p in progress_map.items():
        if p.mastery_percent < 75 or p.status == TopicStatus.NEEDS_REVISION:
            meta = topic_meta.get(tid)
            if meta:
                m_count = mistake_counts.get(tid, 0)
                # Smart Priority Formula:
                # Priority Score = (100 - mastery) * 0.4 + (m_count * 15) + (20 if NEEDS_REVISION else 0)
                urgency = 20 if p.status == TopicStatus.NEEDS_REVISION else 0
                priority_score = (100 - p.mastery_percent) * 0.4 + (m_count * 15) + urgency

                reason = "Needs urgent revision" if p.status == TopicStatus.NEEDS_REVISION else f"{m_count} recorded mistakes" if m_count > 0 else f"Mastery only {p.mastery_percent:.0f}%"

                candidate_weak.append({
                    "topic_id": tid,
                    "topic_name": meta["topic_name"],
                    "unit_id": meta["unit_id"],
                    "unit_number": meta["unit_number"],
                    "course_code": meta["course_code"],
                    "subject_name": meta["subject_name"],
                    "mastery_percent": p.mastery_percent,
                    "reason": reason,
                    "priority_score": round(priority_score, 1),
                    "mistake_count": m_count,
                    "to": f"/topics/{tid}?tab=practice" if m_count > 0 else f"/topics/{tid}",
                })

    candidate_weak.sort(key=lambda x: x["priority_score"], reverse=True)
    top_weak_topics = candidate_weak[:3]

    # Calculate Today's Study Progress Minutes
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    sessions_result = await db.execute(
        select(func.sum(StudySession.duration_minutes))
        .where(
            StudySession.user_id == current_user.id,
            StudySession.started_at >= today_start,
        )
    )
    today_mins = sessions_result.scalar_one_or_none() or 0

    # Recommended Action
    recommended_action = None
    if top_weak_topics:
        target = top_weak_topics[0]
        recommended_action = {
            "title": f"Strengthen: {target['topic_name']}",
            "subtitle": f"{target['course_code']} · Unit {target['unit_number']} · {target['reason']}",
            "action_text": "Fix Weakness",
            "to": target["to"],
        }
    elif continue_studying:
        recommended_action = {
            "title": f"Continue: {continue_studying['topic_name']}",
            "subtitle": f"{continue_studying['course_code']} · Unit {continue_studying['unit_number']} · {continue_studying['next_action_label']}",
            "action_text": "Resume Study",
            "to": continue_studying["to"],
        }

    return DashboardOut(
        overall_completion_percent=overall_pct,
        total_topics=total_topics,
        learned_topics=learned,
        needs_revision_topics=needs_rev,
        total_practicals=len(all_practicals),
        completed_practicals=completed_pracs,
        subjects=subject_progress_list,
        study_streak_days=1,
        total_study_minutes=today_mins + (learned * 15),
        today_study_minutes=today_mins,
        recent_topics=recent_topics,
        weak_topics=top_weak_topics,
        revision_due_count=len(candidate_weak),
        continue_studying=continue_studying,
        recommended_action=recommended_action,
    )


# ── Aggregated Topic Workspace (High-Speed Single Fetch) ──────────────────────

@router.get("/topics/{topic_id}/workspace", response_model=TopicWorkspaceOut)
async def get_topic_workspace(
    topic_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Aggregate read endpoint for Topic Page to eliminate multiple round trips."""
    topic_res = await db.execute(
        select(Topic)
        .options(selectinload(Topic.unit).selectinload(Unit.subject))
        .where(Topic.id == topic_id)
    )
    topic = topic_res.scalar_one_or_none()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")

    unit = topic.unit
    subject = unit.subject

    # Topic Progress
    prog_res = await db.execute(
        select(TopicProgress).where(
            TopicProgress.user_id == current_user.id,
            TopicProgress.topic_id == topic_id,
        )
    )
    progress = prog_res.scalar_one_or_none()
    if not progress:
        progress = TopicProgress(user_id=current_user.id, topic_id=topic_id)
        db.add(progress)
        await db.commit()
        await db.refresh(progress)

    # Notes
    notes_res = await db.execute(
        select(Note)
        .where(
            Note.topic_id == topic_id,
            or_(Note.user_id == current_user.id, Note.user_id == 3),
        )
        .order_by(Note.created_at.asc())
    )
    notes = notes_res.scalars().all()

    # Questions count
    q_count_res = await db.execute(
        select(func.count(Question.id)).where(Question.topic_id == topic_id)
    )
    q_count = q_count_res.scalar_one_or_none() or 0

    # Coding problem (if any)
    cp_res = await db.execute(
        select(CodingProblem).where(CodingProblem.topic_id == topic_id)
    )
    cp = cp_res.scalar_one_or_none()
    cp_dict = None
    if cp:
        cp_dict = {
            "id": cp.id,
            "title": cp.title,
            "description": cp.description,
            "language": cp.language,
            "difficulty": cp.difficulty,
            "starter_code": cp.starter_code,
            "hints": cp.hints,
        }

    # Prev / Next topic in unit
    unit_topics_res = await db.execute(
        select(Topic).where(Topic.unit_id == unit.id).order_by(Topic.sort_order)
    )
    unit_topics = unit_topics_res.scalars().all()
    curr_idx = next((i for i, t in enumerate(unit_topics) if t.id == topic_id), -1)
    prev_topic = None
    next_topic = None
    if curr_idx > 0:
        prev_topic = {"id": unit_topics[curr_idx - 1].id, "name": unit_topics[curr_idx - 1].name}
    if curr_idx != -1 and curr_idx < len(unit_topics) - 1:
        next_topic = {"id": unit_topics[curr_idx + 1].id, "name": unit_topics[curr_idx + 1].name}

    return TopicWorkspaceOut(
        topic={"id": topic.id, "name": topic.name, "description": topic.description, "has_coding": topic.has_coding},
        unit={"id": unit.id, "unit_number": unit.unit_number, "name": unit.name},
        subject={"id": subject.id, "course_code": subject.course_code, "name": subject.name},
        progress=progress,
        notes=notes,
        questions_count=q_count,
        coding_problem=cp_dict,
        next_topic=next_topic,
        prev_topic=prev_topic,
    )


# ── Study Sessions & Timers ───────────────────────────────────────────────────

@router.post("/progress/study-sessions/start", response_model=StudySessionOut)
async def start_study_session(
    data: StudySessionStart,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Start an active study session or resume the currently running session."""
    active_res = await db.execute(
        select(StudySession).where(
            StudySession.user_id == current_user.id,
            StudySession.ended_at.is_(None),
        ).order_by(desc(StudySession.started_at))
    )
    active_session = active_res.scalar_one_or_none()
    if active_session:
        return active_session

    new_session = StudySession(
        user_id=current_user.id,
        topic_id=data.topic_id,
        session_type=data.session_type,
        started_at=datetime.now(timezone.utc),
    )
    db.add(new_session)
    await db.commit()
    await db.refresh(new_session)
    return new_session


@router.post("/progress/study-sessions/{session_id}/finish", response_model=StudySessionOut)
async def finish_study_session(
    session_id: int,
    data: StudySessionFinish,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Finish an active study session and update duration."""
    session_res = await db.execute(
        select(StudySession).where(
            StudySession.id == session_id,
            StudySession.user_id == current_user.id,
        )
    )
    session = session_res.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Study session not found")

    now = datetime.now(timezone.utc)
    session.ended_at = now
    if session.started_at:
        delta_mins = max(1, int((now - session.started_at).total_seconds() / 60))
        session.duration_minutes = delta_mins
    if data.notes:
        session.notes = data.notes

    # Update daily goals
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    goal_res = await db.execute(
        select(DailyGoal).where(
            DailyGoal.user_id == current_user.id,
            DailyGoal.target_date >= today_start,
        )
    )
    goal = goal_res.scalar_one_or_none()
    if not goal:
        goal = DailyGoal(
            user_id=current_user.id,
            target_date=today_start,
            minutes_completed=session.duration_minutes,
            topics_completed=data.topics_studied,
        )
        db.add(goal)
    else:
        goal.minutes_completed += session.duration_minutes
        goal.topics_completed += data.topics_studied
        if goal.minutes_completed >= goal.minutes_goal:
            goal.is_completed = True

    await db.commit()
    await db.refresh(session)
    return session


@router.get("/progress/study-sessions/active", response_model=Optional[StudySessionOut])
async def get_active_study_session(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Check if there is an in-progress study session."""
    active_res = await db.execute(
        select(StudySession).where(
            StudySession.user_id == current_user.id,
            StudySession.ended_at.is_(None),
        ).order_by(desc(StudySession.started_at))
    )
    return active_res.scalar_one_or_none()


# ── Notes CRUD ────────────────────────────────────────────────────────────────

@router.get("/topics/{topic_id}/notes", response_model=list[NoteOut])
async def get_topic_notes(
    topic_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Note)
        .where(
            Note.topic_id == topic_id,
            or_(Note.user_id == current_user.id, Note.user_id == 3),
        )
        .order_by(Note.created_at.asc())
    )
    return result.scalars().all()


@router.post("/topics/{topic_id}/notes", response_model=NoteOut)
async def create_topic_note(
    topic_id: int,
    data: NoteCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    note = Note(
        user_id=current_user.id,
        topic_id=topic_id,
        content=data.content,
    )
    db.add(note)
    await db.commit()
    await db.refresh(note)
    return note
