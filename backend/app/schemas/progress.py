"""Pydantic schemas for progress tracking, dashboard, notes, and study sessions."""
from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel
from app.models.progress import TopicStatus
from app.models.curriculum import PracticalStatus


class TopicProgressUpdate(BaseModel):
    status: Optional[TopicStatus] = None
    theory_completion: Optional[float] = None
    practice_completion: Optional[float] = None
    assessment_completion: Optional[float] = None
    revision_completion: Optional[float] = None
    notes_read: Optional[bool] = None
    practice_completed: Optional[bool] = None
    quiz_completed: Optional[bool] = None
    coding_completed: Optional[bool] = None
    practical_completed: Optional[bool] = None
    confidence_level: Optional[int] = None


class TopicProgressOut(BaseModel):
    id: int
    user_id: int
    topic_id: int
    status: TopicStatus
    theory_completion: float
    practice_completion: float
    assessment_completion: float
    revision_completion: float
    notes_read: bool
    practice_completed: bool
    quiz_completed: bool
    coding_completed: bool
    practical_completed: bool
    confidence_level: int
    mastery_percent: float
    last_studied_at: Optional[datetime]
    revision_count: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PracticalProgressUpdate(BaseModel):
    status: Optional[PracticalStatus] = None
    code_content: Optional[str] = None
    output_notes: Optional[str] = None
    notes: Optional[str] = None


class PracticalProgressOut(BaseModel):
    id: int
    user_id: int
    practical_id: int
    status: PracticalStatus
    code_content: Optional[str]
    output_notes: Optional[str]
    notes: Optional[str]
    completed_at: Optional[datetime]
    updated_at: datetime

    model_config = {"from_attributes": True}


class SubjectProgressOut(BaseModel):
    subject_id: int
    course_code: str
    subject_name: str
    total_topics: int
    learned_topics: int
    learning_topics: int
    needs_revision_topics: int
    not_started_topics: int
    completion_percent: float
    average_mastery: float
    total_practicals: int
    completed_practicals: int
    practical_completion_percent: float

    model_config = {"from_attributes": True}


class DashboardOut(BaseModel):
    overall_completion_percent: float
    total_topics: int
    learned_topics: int
    needs_revision_topics: int
    total_practicals: int
    completed_practicals: int
    subjects: list[SubjectProgressOut]
    study_streak_days: int
    total_study_minutes: int
    today_study_minutes: int = 0
    recent_topics: list[dict]
    weak_topics: list[dict]
    revision_due_count: int
    continue_studying: Optional[dict] = None
    recommended_action: Optional[dict] = None


class NoteCreate(BaseModel):
    content: str


class NoteOut(BaseModel):
    id: int
    topic_id: int
    content: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class StudySessionStart(BaseModel):
    topic_id: Optional[int] = None
    session_type: str = "THEORY"


class StudySessionFinish(BaseModel):
    notes: Optional[str] = None
    topics_studied: int = 1
    mcqs_attempted: int = 0


class StudySessionOut(BaseModel):
    id: int
    user_id: int
    topic_id: Optional[int] = None
    session_type: str
    duration_minutes: int
    notes: Optional[str] = None
    started_at: datetime
    ended_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class TopicWorkspaceOut(BaseModel):
    topic: dict
    unit: dict
    subject: dict
    progress: TopicProgressOut
    notes: list[NoteOut]
    questions_count: int
    coding_problem: Optional[dict] = None
    next_topic: Optional[dict] = None
    prev_topic: Optional[dict] = None
