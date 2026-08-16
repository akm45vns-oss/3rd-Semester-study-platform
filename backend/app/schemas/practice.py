"""Pydantic schemas for practice, quizzes, and tests."""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from app.models.practice import QuestionType, Difficulty


class OptionOut(BaseModel):
    id: int
    option_text: str
    is_correct: Optional[bool] = None  # Hidden during test mode
    sort_order: int

    model_config = {"from_attributes": True}


class QuestionOut(BaseModel):
    id: int
    topic_id: int
    question_text: str
    question_type: QuestionType
    difficulty: Difficulty
    explanation: Optional[str] = None
    source_type: str
    options: List[OptionOut] = []

    model_config = {"from_attributes": True}


class PracticeAttemptCreate(BaseModel):
    question_id: int
    selected_option_id: Optional[int] = None
    answer_text: Optional[str] = None
    time_taken_seconds: Optional[int] = None
    session_id: Optional[str] = None


class PracticeAttemptOut(BaseModel):
    id: int
    question_id: int
    topic_id: Optional[int]
    is_correct: bool
    score: float
    explanation: Optional[str]
    correct_option_id: Optional[int]
    attempted_at: datetime


class TestGenerateRequest(BaseModel):
    scope: str = Field("TOPIC", description="TOPIC | UNIT | SUBJECT | FULL_MOCK")
    topic_id: Optional[int] = None
    unit_id: Optional[int] = None
    subject_id: Optional[int] = None
    question_count: int = Field(5, ge=1, le=50)
    difficulty: Optional[Difficulty] = None


class TestSessionOut(BaseModel):
    session_id: str
    scope: str
    scope_title: str
    time_limit_minutes: int
    questions: List[QuestionOut]


class AnswerItem(BaseModel):
    question_id: int
    selected_option_id: Optional[int] = None
    answer_text: Optional[str] = None
    time_taken_seconds: Optional[int] = None


class TestSubmitRequest(BaseModel):
    session_id: str
    scope: str
    answers: List[AnswerItem]


class TestResultOut(BaseModel):
    session_id: str
    total_questions: int
    correct_count: int
    incorrect_count: int
    skipped_count: int
    score_percentage: float
    passed: bool
    weak_topics: List[dict]
    recommended_revision: List[str]
    details: List[dict]


class MistakeOut(BaseModel):
    id: int
    topic_id: int
    topic_name: Optional[str] = None
    course_code: Optional[str] = None
    description: str
    correction: Optional[str]
    source_type: str
    is_resolved: bool
    created_at: datetime

    model_config = {"from_attributes": True}
