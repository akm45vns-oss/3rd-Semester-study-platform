"""
Models package — import all models here so SQLAlchemy
registers them and all relationships resolve before any query runs.
"""
from app.models.user import User
from app.models.curriculum import Subject, Unit, Topic, Subtopic, CourseOutcome, Practical
from app.models.progress import (
    TopicProgress, PracticalProgress, StudySession,
    RevisionItem, Mistake, Note, Bookmark, DailyGoal, Achievement
)
from app.models.practice import (
    Question, QuestionOption, PracticeAttempt,
    CodingProblem, CodingSubmission, SqlProblem,
    DescriptiveQuestion, DescriptiveSubmission
)

__all__ = [
    "User",
    "Subject", "Unit", "Topic", "Subtopic", "CourseOutcome", "Practical",
    "TopicProgress", "PracticalProgress", "StudySession",
    "RevisionItem", "Mistake", "Note", "Bookmark", "DailyGoal", "Achievement",
    "Question", "QuestionOption", "PracticeAttempt",
    "CodingProblem", "CodingSubmission", "SqlProblem",
    "DescriptiveQuestion", "DescriptiveSubmission",
]
