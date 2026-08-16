"""SQLAlchemy progress tracking models."""
from datetime import datetime, timezone
from sqlalchemy import Integer, String, Text, Boolean, DateTime, ForeignKey, Float, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.models.curriculum import PracticalStatus
import enum


class TopicStatus(str, enum.Enum):
    NOT_STARTED = "NOT_STARTED"
    LEARNING = "LEARNING"
    LEARNED = "LEARNED"
    NEEDS_REVISION = "NEEDS_REVISION"


class TopicProgress(Base):
    __tablename__ = "topic_progress"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    topic_id: Mapped[int] = mapped_column(Integer, ForeignKey("topics.id"), nullable=False)

    status: Mapped[TopicStatus] = mapped_column(
        Enum(TopicStatus, native_enum=False), default=TopicStatus.NOT_STARTED, nullable=False
    )

    # Mastery breakdown (0.0 - 1.0 each)
    theory_completion: Mapped[float] = mapped_column(Float, default=0.0)
    practice_completion: Mapped[float] = mapped_column(Float, default=0.0)
    assessment_completion: Mapped[float] = mapped_column(Float, default=0.0)
    revision_completion: Mapped[float] = mapped_column(Float, default=0.0)

    # Computed mastery percentage (0-100)
    mastery_percent: Mapped[float] = mapped_column(Float, default=0.0)

    # Tracking
    notes_read: Mapped[bool] = mapped_column(Boolean, default=False)
    practice_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    quiz_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    coding_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    practical_completed: Mapped[bool] = mapped_column(Boolean, default=False)

    confidence_level: Mapped[int] = mapped_column(Integer, default=0)  # 0-5
    revision_count: Mapped[int] = mapped_column(Integer, default=0)
    quiz_best_score: Mapped[float] = mapped_column(Float, nullable=True)
    quiz_attempt_count: Mapped[int] = mapped_column(Integer, default=0)

    last_studied_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    first_learned_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    last_revised_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    user = relationship("User", back_populates="topic_progress", lazy="noload")
    topic = relationship("Topic", back_populates="topic_progress", lazy="noload")

    def calculate_mastery(self) -> float:
        """
        Mastery = 25% theory + 25% practice + 25% assessment + 25% revision
        Each component is 0.0-1.0
        """
        mastery = (
            (self.theory_completion or 0.0) * 0.25
            + (self.practice_completion or 0.0) * 0.25
            + (self.assessment_completion or 0.0) * 0.25
            + (self.revision_completion or 0.0) * 0.25
        ) * 100
        self.mastery_percent = round(mastery, 1)
        return self.mastery_percent


class PracticalProgress(Base):
    __tablename__ = "practical_progress"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    practical_id: Mapped[int] = mapped_column(Integer, ForeignKey("practicals.id"), nullable=False)
    status: Mapped[PracticalStatus] = mapped_column(
        Enum(PracticalStatus, native_enum=False), default=PracticalStatus.NOT_STARTED, nullable=False
    )
    code_content: Mapped[str] = mapped_column(Text, nullable=True)
    output_notes: Mapped[str] = mapped_column(Text, nullable=True)
    notes: Mapped[str] = mapped_column(Text, nullable=True)
    completed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    practical = relationship("Practical", back_populates="practical_progress", lazy="noload")


class Note(Base):
    __tablename__ = "notes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    topic_id: Mapped[int] = mapped_column(Integer, ForeignKey("topics.id"), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    user = relationship("User", back_populates="notes", lazy="noload")
    topic = relationship("Topic", back_populates="notes", lazy="noload")


class Bookmark(Base):
    __tablename__ = "bookmarks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    topic_id: Mapped[int] = mapped_column(Integer, ForeignKey("topics.id"), nullable=False)
    note: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    user = relationship("User", back_populates="bookmarks", lazy="noload")
    topic = relationship("Topic", back_populates="bookmarks", lazy="noload")


class RevisionPriority(str, enum.Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class RevisionItem(Base):
    __tablename__ = "revision_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    topic_id: Mapped[int] = mapped_column(Integer, ForeignKey("topics.id"), nullable=False)
    priority: Mapped[RevisionPriority] = mapped_column(
        Enum(RevisionPriority, native_enum=False), default=RevisionPriority.MEDIUM
    )
    reason: Mapped[str] = mapped_column(String(255), nullable=True)
    scheduled_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    completed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    user = relationship("User", back_populates="revision_items", lazy="noload")
    topic = relationship("Topic", back_populates="revision_items", lazy="noload")


class Mistake(Base):
    __tablename__ = "mistakes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    topic_id: Mapped[int] = mapped_column(Integer, ForeignKey("topics.id"), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    correction: Mapped[str] = mapped_column(Text, nullable=True)
    source_type: Mapped[str] = mapped_column(String(50), default="PRACTICE")  # PRACTICE, TEST, CODING
    is_resolved: Mapped[bool] = mapped_column(Boolean, default=False)
    resolved_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    user = relationship("User", back_populates="mistakes", lazy="noload")
    topic = relationship("Topic", back_populates="mistakes", lazy="noload")


class StudySession(Base):
    __tablename__ = "study_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    topic_id: Mapped[int] = mapped_column(Integer, ForeignKey("topics.id"), nullable=True)
    session_type: Mapped[str] = mapped_column(String(50), default="THEORY")  # THEORY, PRACTICE, QUIZ, CODING, REVISION
    duration_minutes: Mapped[int] = mapped_column(Integer, default=0)
    notes: Mapped[str] = mapped_column(Text, nullable=True)
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    ended_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)

    user = relationship("User", back_populates="study_sessions", lazy="noload")


class DailyGoal(Base):
    __tablename__ = "daily_goals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    target_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    topics_goal: Mapped[int] = mapped_column(Integer, default=3)
    topics_completed: Mapped[int] = mapped_column(Integer, default=0)
    minutes_goal: Mapped[int] = mapped_column(Integer, default=60)
    minutes_completed: Mapped[int] = mapped_column(Integer, default=0)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    user = relationship("User", back_populates="daily_goals", lazy="noload")


class Achievement(Base):
    __tablename__ = "achievements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    badge_type: Mapped[str] = mapped_column(String(50), nullable=False)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    awarded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    user = relationship("User", back_populates="achievements", lazy="noload")
