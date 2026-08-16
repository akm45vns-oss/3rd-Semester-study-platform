"""Pydantic schemas for Coding problems, Multi-language Online Lab, and Submissions."""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List, Dict, Any
from app.models.practice import Difficulty


class LanguageInfoOut(BaseModel):
    id: str
    display_name: str
    category: str
    file_name: str
    entry_point: str
    starter_code: str
    supports_stdin: bool
    timeout_seconds: float
    course_code: str
    description: str


class CodeExecuteRequest(BaseModel):
    language: str
    source_code: str
    stdin: Optional[str] = ""


class CodeExecuteResult(BaseModel):
    status: str  # ACCEPTED | WRONG_ANSWER | COMPILATION_ERROR | RUNTIME_ERROR | TIME_LIMIT_EXCEEDED | SYSTEM_ERROR
    stdout: str = ""
    stderr: str = ""
    compile_error: Optional[str] = None
    runtime_error: Optional[str] = None
    execution_time_ms: int = 0
    memory_usage_mb: float = 0.0
    exit_code: int = 0


class PublicTestCaseOut(BaseModel):
    test_index: int
    input_text: str
    expected_output: str
    actual_output: Optional[str] = ""
    passed: Optional[bool] = None
    status: Optional[str] = None


class CodingProblemOut(BaseModel):
    id: int
    topic_id: int
    topic_name: Optional[str] = None
    course_code: Optional[str] = None
    unit_number: Optional[int] = None
    title: str
    description: str
    language: str
    difficulty: Difficulty
    starter_code: Optional[str] = None
    expected_output: Optional[str] = None
    hints: Optional[str] = None
    examples: Optional[str] = None
    source_type: str
    is_solved: Optional[bool] = False
    public_test_cases: Optional[List[PublicTestCaseOut]] = []

    model_config = {"from_attributes": True}


class CodingSubmissionCreate(BaseModel):
    problem_id: int
    code: str
    language: str


class PracticeSubmitResultOut(BaseModel):
    id: int
    problem_id: int
    status: str  # ACCEPTED | WRONG_ANSWER | COMPILATION_ERROR | RUNTIME_ERROR | TIME_LIMIT_EXCEEDED
    passed: bool
    tests_passed: int
    tests_total: int
    public_test_results: List[PublicTestCaseOut] = []
    hidden_passed: int = 0
    hidden_total: int = 0
    execution_time_ms: int = 0
    output_message: str = ""
    compile_error: Optional[str] = None
    runtime_error: Optional[str] = None
    submitted_at: datetime


class CodingSubmissionOut(BaseModel):
    id: int
    problem_id: int
    code: str
    language: str
    status: str
    output: Optional[str] = None
    passed: bool
    submitted_at: datetime


class SqlExecuteRequest(BaseModel):
    query: str
    schema_sql: Optional[str] = None


class SqlExecuteResult(BaseModel):
    success: bool
    columns: List[str] = []
    rows: List[List[str]] = []
    error: Optional[str] = None
    row_count: int = 0
