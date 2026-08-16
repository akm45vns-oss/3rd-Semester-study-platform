"""Pydantic schemas for the Exam Preparation and Simulator system."""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from app.models.practice import Difficulty


class ExamBlueprintOut(BaseModel):
    exam_type: str
    title: str
    description: str
    coverage_units: List[int]
    mcq_count: int
    descriptive_count: int
    descriptive_marks_per_q: int
    duration_minutes: int
    total_marks: int
    part_a_title: str
    part_b_title: str


class ExamReadinessUnit(BaseModel):
    unit_number: int
    title: str
    mastery_percent: float
    topics_count: int
    topics_mastered: int
    mcq_accuracy: float


class ExamReadinessSubject(BaseModel):
    subject_id: int
    course_code: str
    subject_name: str
    midterm_readiness_percent: float
    endterm_readiness_percent: float
    units: List[ExamReadinessUnit]
    weak_topics: List[str]


class ExamReadinessOut(BaseModel):
    overall_midterm_readiness: float
    overall_endterm_readiness: float
    upcoming_exam: str  # "MIDTERM" or "END_TERM"
    days_remaining: Optional[int] = None
    target_date: Optional[str] = None
    subjects: List[ExamReadinessSubject]
    weakest_subject: Optional[str] = None
    weakest_unit_info: Optional[str] = None


class DescriptiveQuestionOut(BaseModel):
    id: int
    subject_id: int
    course_code: Optional[str] = None
    unit_id: int
    unit_number: Optional[int] = None
    topic_id: int
    topic_name: Optional[str] = None
    question_text: str
    marks: int = 10
    difficulty: Difficulty
    question_type: str
    answer_outline: List[str] = []
    model_answer: str
    key_points: List[str] = []
    exam_tips: List[str] = []
    important_terms: List[str] = []
    diagram_guidance: Optional[str] = None
    code_guidance: Optional[str] = None
    is_solved: bool = False
    latest_score: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)


class DescriptiveSubmissionCreate(BaseModel):
    question_id: int
    user_answer: str
    self_score: float = Field(ge=0.0, le=10.0)
    checklist_completed: List[str] = []
    status: str = "UNDERSTOOD"  # UNDERSTOOD, NEEDS_REVISION


class DescriptiveSubmissionOut(BaseModel):
    id: int
    question_id: int
    self_score: float
    status: str
    checklist_completed: List[str]
    submitted_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ExamMCQOptionOut(BaseModel):
    id: int
    option_text: str
    sort_order: int

    model_config = ConfigDict(from_attributes=True)


class ExamMCQQuestionOut(BaseModel):
    id: int
    topic_id: int
    topic_name: Optional[str] = None
    unit_number: Optional[int] = None
    course_code: Optional[str] = None
    question_text: str
    difficulty: Difficulty
    options: List[ExamMCQOptionOut]

    model_config = ConfigDict(from_attributes=True)


class ExamSessionOut(BaseModel):
    session_id: str
    exam_type: str  # "MIDTERM" or "END_TERM"
    subject_id: Optional[int] = None
    subject_name: Optional[str] = None
    course_code: Optional[str] = None
    duration_minutes: int
    total_marks: int
    mcqs: List[ExamMCQQuestionOut]
    descriptive_questions: List[DescriptiveQuestionOut] = []
    created_at: datetime
    expires_at: datetime


class ExamMCQAnswer(BaseModel):
    question_id: int
    selected_option_id: Optional[int] = None
    marked_for_review: bool = False


class ExamDescriptiveAnswer(BaseModel):
    question_id: int
    user_answer: str
    self_score: Optional[float] = None
    marked_for_review: bool = False


class ExamSubmissionCreate(BaseModel):
    session_id: str
    exam_type: str
    subject_id: Optional[int] = None
    time_taken_seconds: int
    mcq_answers: List[ExamMCQAnswer]
    descriptive_answers: List[ExamDescriptiveAnswer] = []


class UnitScoreBreakdown(BaseModel):
    unit_number: int
    questions_count: int
    correct_count: int
    accuracy_percent: float


class ExamReviewQuestion(BaseModel):
    question_id: int
    question_text: str
    topic_name: Optional[str] = None
    unit_number: Optional[int] = None
    user_selected_option_id: Optional[int] = None
    user_selected_option_text: Optional[str] = None
    correct_option_id: int
    correct_option_text: str
    is_correct: bool
    explanation: Optional[str] = None


class ExamResultOut(BaseModel):
    session_id: str
    exam_type: str
    score: float
    total_marks: int
    percentage: float
    mcqs_total: int
    mcqs_correct: int
    mcqs_incorrect: int
    mcqs_unanswered: int
    accuracy_percent: float
    descriptive_total: int = 0
    descriptive_attempted: int = 0
    unit_breakdown: List[UnitScoreBreakdown]
    weak_topics: List[str]
    mistakes_logged_count: int
    review_mcqs: List[ExamReviewQuestion]
    submitted_at: datetime
