"""SQLAlchemy curriculum models: Subject, Unit, Topic, Subtopic, CourseOutcome, Practical."""
from datetime import datetime, timezone
from sqlalchemy import Integer, String, Text, Boolean, DateTime, ForeignKey, Float, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
import enum


class SourceType(str, enum.Enum):
    OFFICIAL_SYLLABUS = "OFFICIAL_SYLLABUS"
    ADDITIONAL_LEARNING = "ADDITIONAL_LEARNING"
    USER_CREATED = "USER_CREATED"


class PracticalStatus(str, enum.Enum):
    NOT_STARTED = "NOT_STARTED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    NEEDS_REDO = "NEEDS_REDO"


class Subject(Base):
    __tablename__ = "subjects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    course_code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    credits: Mapped[int] = mapped_column(Integer, nullable=False, default=3)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    units = relationship("Unit", back_populates="subject", order_by="Unit.sort_order", lazy="noload")
    course_outcomes = relationship("CourseOutcome", back_populates="subject", lazy="noload")
    practicals = relationship("Practical", back_populates="subject", lazy="noload")


class Unit(Base):
    __tablename__ = "units"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    subject_id: Mapped[int] = mapped_column(Integer, ForeignKey("subjects.id"), nullable=False)
    unit_number: Mapped[int] = mapped_column(Integer, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    subject = relationship("Subject", back_populates="units", lazy="noload")
    topics = relationship("Topic", back_populates="unit", order_by="Topic.sort_order", lazy="noload")


class Topic(Base):
    __tablename__ = "topics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    unit_id: Mapped[int] = mapped_column(Integer, ForeignKey("units.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    source_type: Mapped[SourceType] = mapped_column(
        Enum(SourceType, native_enum=False), default=SourceType.OFFICIAL_SYLLABUS, nullable=False
    )
    has_coding: Mapped[bool] = mapped_column(Boolean, default=False)
    has_practical: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    unit = relationship("Unit", back_populates="topics", lazy="noload")
    subtopics = relationship("Subtopic", back_populates="topic", order_by="Subtopic.sort_order", lazy="noload")
    topic_progress = relationship("TopicProgress", back_populates="topic", lazy="noload")
    notes = relationship("Note", back_populates="topic", lazy="noload")
    bookmarks = relationship("Bookmark", back_populates="topic", lazy="noload")
    questions = relationship("Question", back_populates="topic", lazy="noload")
    coding_problems = relationship("CodingProblem", back_populates="topic", lazy="noload")
    revision_items = relationship("RevisionItem", back_populates="topic", lazy="noload")
    mistakes = relationship("Mistake", back_populates="topic", lazy="noload")


class Subtopic(Base):
    __tablename__ = "subtopics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    topic_id: Mapped[int] = mapped_column(Integer, ForeignKey("topics.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    source_type: Mapped[SourceType] = mapped_column(
        Enum(SourceType, native_enum=False), default=SourceType.OFFICIAL_SYLLABUS, nullable=False
    )

    topic = relationship("Topic", back_populates="subtopics", lazy="noload")


class CourseOutcome(Base):
    __tablename__ = "course_outcomes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    subject_id: Mapped[int] = mapped_column(Integer, ForeignKey("subjects.id"), nullable=False)
    outcome_code: Mapped[str] = mapped_column(String(10), nullable=False)  # CO1, CO2, etc.
    description: Mapped[str] = mapped_column(Text, nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    subject = relationship("Subject", back_populates="course_outcomes", lazy="noload")


class Practical(Base):
    __tablename__ = "practicals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    subject_id: Mapped[int] = mapped_column(Integer, ForeignKey("subjects.id"), nullable=False)
    practical_number: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    objective: Mapped[str] = mapped_column(Text, nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    code_template: Mapped[str] = mapped_column(Text, nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    subject = relationship("Subject", back_populates="practicals", lazy="noload")
    practical_progress = relationship("PracticalProgress", back_populates="practical", lazy="noload")
