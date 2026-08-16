"""Pydantic schemas for curriculum data."""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from app.models.curriculum import SourceType


class TopicOut(BaseModel):
    id: int
    unit_id: int
    name: str
    description: Optional[str] = None
    sort_order: int = 0
    source_type: SourceType = SourceType.OFFICIAL_SYLLABUS
    has_coding: bool = False
    has_practical: bool = False

    model_config = {"from_attributes": True}


class UnitOut(BaseModel):
    id: int
    subject_id: int
    unit_number: int
    name: str
    description: Optional[str] = None
    sort_order: int = 0
    topics: List[TopicOut] = []

    model_config = {"from_attributes": True}


class PracticalOut(BaseModel):
    id: int
    subject_id: int
    practical_number: int
    title: str
    objective: Optional[str] = None
    description: Optional[str] = None
    code_template: Optional[str] = None
    sort_order: int = 0

    model_config = {"from_attributes": True}


class SubjectOut(BaseModel):
    id: int
    course_code: str
    name: str
    credits: int
    description: Optional[str] = None
    sort_order: int = 0
    units: List[UnitOut] = []

    model_config = {"from_attributes": True}


class SubjectSummary(BaseModel):
    """Lightweight subject without units (for list views)."""
    id: int
    course_code: str
    name: str
    credits: int
    description: Optional[str] = None
    sort_order: int = 0

    model_config = {"from_attributes": True}


class UnitSummary(BaseModel):
    """Lightweight unit without topics (for breadcrumbs)."""
    id: int
    subject_id: int
    unit_number: int
    name: str
    description: Optional[str] = None

    model_config = {"from_attributes": True}


class CurriculumAuditReport(BaseModel):
    valid: bool
    subject_count: int
    total_units: int
    course_codes: List[str]
    errors: List[str]
    warnings: List[str]
    subjects: List[dict]
    stats: Optional[dict] = None

