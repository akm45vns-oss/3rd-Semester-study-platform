"""SQLAlchemy practice and assessment models."""
from datetime import datetime, timezone
from sqlalchemy import Integer, String, Text, Boolean, DateTime, ForeignKey, Float, Enum, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
import enum


class QuestionType(str, enum.Enum):
    MCQ = "MCQ"
    MULTIPLE_ANSWER = "MULTIPLE_ANSWER"
    TRUE_FALSE = "TRUE_FALSE"
    FILL_BLANK = "FILL_BLANK"
    SHORT_ANSWER = "SHORT_ANSWER"
    OUTPUT_PREDICTION = "OUTPUT_PREDICTION"
    DEBUGGING = "DEBUGGING"
    CODING = "CODING"
    SQL = "SQL"


class Difficulty(str, enum.Enum):
    EASY = "EASY"
    MEDIUM = "MEDIUM"
    HARD = "HARD"


class Question(Base):
    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    topic_id: Mapped[int] = mapped_column(Integer, ForeignKey("topics.id"), nullable=False)
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    question_type: Mapped[QuestionType] = mapped_column(
        Enum(QuestionType, native_enum=False), nullable=False
    )
    difficulty: Mapped[Difficulty] = mapped_column(
        Enum(Difficulty, native_enum=False), default=Difficulty.MEDIUM
    )
    explanation: Mapped[str] = mapped_column(Text, nullable=True)
    source_type: Mapped[str] = mapped_column(String(50), default="ADDITIONAL_LEARNING")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    topic = relationship("Topic", back_populates="questions", lazy="noload")
    options = relationship("QuestionOption", back_populates="question", lazy="noload")
    practice_attempts = relationship("PracticeAttempt", back_populates="question", lazy="noload")


class QuestionOption(Base):
    __tablename__ = "question_options"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    question_id: Mapped[int] = mapped_column(Integer, ForeignKey("questions.id"), nullable=False)
    option_text: Mapped[str] = mapped_column(Text, nullable=False)
    is_correct: Mapped[bool] = mapped_column(Boolean, default=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    question = relationship("Question", back_populates="options", lazy="noload")


class PracticeAttempt(Base):
    __tablename__ = "practice_attempts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    question_id: Mapped[int] = mapped_column(Integer, ForeignKey("questions.id"), nullable=False)
    topic_id: Mapped[int] = mapped_column(Integer, ForeignKey("topics.id"), nullable=True)
    answer_given: Mapped[str] = mapped_column(Text, nullable=True)
    is_correct: Mapped[bool] = mapped_column(Boolean, nullable=True)
    score: Mapped[float] = mapped_column(Float, default=0.0)
    time_taken_seconds: Mapped[int] = mapped_column(Integer, nullable=True)
    attempted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    session_id: Mapped[str] = mapped_column(String(100), nullable=True)  # group attempts in a test

    user = relationship("User", back_populates="practice_attempts", lazy="noload")
    question = relationship("Question", back_populates="practice_attempts", lazy="noload")


class CodingProblem(Base):
    __tablename__ = "coding_problems"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    topic_id: Mapped[int] = mapped_column(Integer, ForeignKey("topics.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    language: Mapped[str] = mapped_column(String(50), nullable=False)  # JAVA, SQL, HTML, JS, PYTHON
    difficulty: Mapped[Difficulty] = mapped_column(
        Enum(Difficulty, native_enum=False), default=Difficulty.MEDIUM
    )
    starter_code: Mapped[str] = mapped_column(Text, nullable=True)
    expected_output: Mapped[str] = mapped_column(Text, nullable=True)
    hints: Mapped[str] = mapped_column(Text, nullable=True)
    examples: Mapped[str] = mapped_column(Text, nullable=True)
    source_type: Mapped[str] = mapped_column(String(50), default="OFFICIAL_SYLLABUS")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    topic = relationship("Topic", back_populates="coding_problems", lazy="noload")
    submissions = relationship("CodingSubmission", back_populates="problem", lazy="noload")


class CodingSubmission(Base):
    __tablename__ = "coding_submissions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    problem_id: Mapped[int] = mapped_column(Integer, ForeignKey("coding_problems.id"), nullable=False)
    code: Mapped[str] = mapped_column(Text, nullable=False)
    language: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="PENDING")  # PASSED, FAILED, ERROR
    output: Mapped[str] = mapped_column(Text, nullable=True)
    submitted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    user = relationship("User", back_populates="coding_submissions", lazy="noload")
    problem = relationship("CodingProblem", back_populates="submissions", lazy="noload")


class SqlProblem(Base):
    __tablename__ = "sql_problems"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    topic_id: Mapped[int] = mapped_column(Integer, ForeignKey("topics.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    schema_sql: Mapped[str] = mapped_column(Text, nullable=False)
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    expected_query: Mapped[str] = mapped_column(Text, nullable=False)
    difficulty: Mapped[Difficulty] = mapped_column(
        Enum(Difficulty, native_enum=False), default=Difficulty.MEDIUM
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )


class DescriptiveQuestion(Base):
    __tablename__ = "descriptive_questions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    subject_id: Mapped[int] = mapped_column(Integer, ForeignKey("subjects.id"), nullable=False)
    unit_id: Mapped[int] = mapped_column(Integer, ForeignKey("units.id"), nullable=False)
    topic_id: Mapped[int] = mapped_column(Integer, ForeignKey("topics.id"), nullable=False)
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    marks: Mapped[int] = mapped_column(Integer, default=10)
    difficulty: Mapped[Difficulty] = mapped_column(
        Enum(Difficulty, native_enum=False), default=Difficulty.MEDIUM
    )
    question_type: Mapped[str] = mapped_column(String(100), default="THEORY_EXPLANATION")
    answer_outline: Mapped[dict | list] = mapped_column(JSON, default=list)
    model_answer: Mapped[str] = mapped_column(Text, nullable=False)
    key_points: Mapped[dict | list] = mapped_column(JSON, default=list)
    exam_tips: Mapped[dict | list] = mapped_column(JSON, default=list)
    important_terms: Mapped[dict | list] = mapped_column(JSON, default=list)
    diagram_guidance: Mapped[str] = mapped_column(Text, nullable=True)
    code_guidance: Mapped[str] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    subject = relationship("Subject", lazy="noload")
    unit = relationship("Unit", lazy="noload")
    topic = relationship("Topic", lazy="noload")
    submissions = relationship("DescriptiveSubmission", back_populates="question", lazy="noload")


class DescriptiveSubmission(Base):
    __tablename__ = "descriptive_submissions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    question_id: Mapped[int] = mapped_column(Integer, ForeignKey("descriptive_questions.id"), nullable=False)
    user_answer: Mapped[str] = mapped_column(Text, nullable=False)
    self_score: Mapped[float] = mapped_column(Float, default=0.0)
    checklist_completed: Mapped[dict | list] = mapped_column(JSON, default=list)
    status: Mapped[str] = mapped_column(String(50), default="UNDERSTOOD")  # UNDERSTOOD, NEEDS_REVISION
    submitted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    user = relationship("User", lazy="noload")
    question = relationship("DescriptiveQuestion", back_populates="submissions", lazy="noload")
