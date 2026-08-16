"""SQLAlchemy User model."""
from datetime import datetime, timezone
from sqlalchemy import Integer, String, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    topic_progress = relationship("TopicProgress", back_populates="user", lazy="noload")
    study_sessions = relationship("StudySession", back_populates="user", lazy="noload")
    notes = relationship("Note", back_populates="user", lazy="noload")
    bookmarks = relationship("Bookmark", back_populates="user", lazy="noload")
    mistakes = relationship("Mistake", back_populates="user", lazy="noload")
    practice_attempts = relationship("PracticeAttempt", back_populates="user", lazy="noload")
    coding_submissions = relationship("CodingSubmission", back_populates="user", lazy="noload")
    daily_goals = relationship("DailyGoal", back_populates="user", lazy="noload")
    achievements = relationship("Achievement", back_populates="user", lazy="noload")
    revision_items = relationship("RevisionItem", back_populates="user", lazy="noload")
