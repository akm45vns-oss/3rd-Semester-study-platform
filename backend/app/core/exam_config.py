"""Centralized University Examination Configurations for Semester OS."""
from dataclasses import dataclass
from typing import List, Dict, Any


@dataclass(frozen=True)
class ExamConfig:
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

    def to_dict(self) -> Dict[str, Any]:
        return {
            "exam_type": self.exam_type,
            "title": self.title,
            "description": self.description,
            "coverage_units": self.coverage_units,
            "mcq_count": self.mcq_count,
            "descriptive_count": self.descriptive_count,
            "descriptive_marks_per_q": self.descriptive_marks_per_q,
            "duration_minutes": self.duration_minutes,
            "total_marks": self.total_marks,
            "part_a_title": self.part_a_title,
            "part_b_title": self.part_b_title,
        }


MIDTERM_EXAM_CONFIG = ExamConfig(
    exam_type="MIDTERM",
    title="Official University Midterm Examination",
    description="30 MCQs covering the first 3 syllabus chapters/units. Single 60-minute timed simulator.",
    coverage_units=[1, 2, 3],
    mcq_count=30,
    descriptive_count=0,
    descriptive_marks_per_q=0,
    duration_minutes=60,
    total_marks=30,
    part_a_title="Section 1: Objective MCQs (30 Marks)",
    part_b_title="",
)

END_TERM_EXAM_CONFIG = ExamConfig(
    exam_type="END_TERM",
    title="Official University End-Term Examination",
    description="Full syllabus examination consisting of Part A (30 MCQs) and Part B (5 × 10-Mark Descriptive Questions).",
    coverage_units=[1, 2, 3, 4, 5, 6],
    mcq_count=30,
    descriptive_count=5,
    descriptive_marks_per_q=10,
    duration_minutes=120,
    total_marks=80,
    part_a_title="Part A: Objective MCQs (30 Questions · 30 Marks)",
    part_b_title="Part B: Descriptive / Analytical Questions (5 Questions · 50 Marks)",
)


def get_exam_config(exam_type: str) -> ExamConfig:
    norm = (exam_type or "").upper().replace("-", "_")
    if norm in ["MIDTERM", "MID_TERM", "MID"]:
        return MIDTERM_EXAM_CONFIG
    return END_TERM_EXAM_CONFIG
