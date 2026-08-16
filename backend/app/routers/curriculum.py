"""Subjects, Units, and Topics router."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.curriculum import Subject, Unit, Topic, Practical
from app.schemas.curriculum import (
    SubjectOut, SubjectSummary, UnitOut, TopicOut, PracticalOut, CurriculumAuditReport
)
from app.seed.curriculum_data import validate_curriculum, CURRICULUM

router = APIRouter(tags=["curriculum"])


# ── Subjects ────────────────────────────────────────────────────────────────

@router.get("/subjects", response_model=list[SubjectSummary])
async def list_subjects(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Subject).where(Subject.is_active == True).order_by(Subject.sort_order)
    )
    return result.scalars().all()


@router.get("/subjects/{subject_id}", response_model=SubjectOut)
async def get_subject(
    subject_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Subject)
        .options(
            selectinload(Subject.units).selectinload(Unit.topics)
        )
        .where(Subject.id == subject_id, Subject.is_active == True)
    )
    subject = result.scalar_one_or_none()
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    return subject


@router.get("/subjects/{subject_id}/units", response_model=list[UnitOut])
async def get_subject_units(
    subject_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Unit)
        .options(selectinload(Unit.topics))
        .where(Unit.subject_id == subject_id)
        .order_by(Unit.unit_number)
    )
    return result.scalars().all()


@router.get("/subjects/{subject_id}/practicals", response_model=list[PracticalOut])
async def get_subject_practicals(
    subject_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Practical)
        .where(Practical.subject_id == subject_id)
        .order_by(Practical.sort_order)
    )
    return result.scalars().all()


# ── Units ────────────────────────────────────────────────────────────────────

@router.get("/units/{unit_id}", response_model=UnitOut)
async def get_unit(
    unit_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Unit)
        .options(selectinload(Unit.topics))
        .where(Unit.id == unit_id)
    )
    unit = result.scalar_one_or_none()
    if not unit:
        raise HTTPException(status_code=404, detail="Unit not found")
    return unit


# ── Topics ────────────────────────────────────────────────────────────────────

@router.get("/topics/{topic_id}", response_model=TopicOut)
async def get_topic(
    topic_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    result = await db.execute(select(Topic).where(Topic.id == topic_id))
    topic = result.scalar_one_or_none()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    return topic


# ── Curriculum Audit ─────────────────────────────────────────────────────────

@router.get("/curriculum/audit", response_model=CurriculumAuditReport)
async def curriculum_audit(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Validate and audit the curriculum and database integrity."""
    from app.services.integrity_audit import run_full_system_integrity_audit

    audit_res = await run_full_system_integrity_audit(db)
    validation = validate_curriculum()

    # Combine static validation + live DB audit
    all_errors = list(set(validation.get("errors", []) + audit_res.get("errors", [])))
    all_warnings = list(set(validation.get("warnings", []) + audit_res.get("warnings", [])))

    subjects_summary = audit_res["stats"].get("subjects_summary", [])
    subjects_detail = [
        {
            "course_code": s["course_code"],
            "name": s["name"],
            "unit_count": s["units"],
            "topic_count": s["topics"],
        }
        for s in subjects_summary
    ]

    return CurriculumAuditReport(
        valid=len(all_errors) == 0,
        subject_count=audit_res["stats"]["subject_count"],
        total_units=audit_res["stats"]["total_units"],
        course_codes=audit_res["stats"]["course_codes"],
        errors=all_errors,
        warnings=all_warnings,
        subjects=subjects_detail,
        stats=audit_res["stats"],
    )

