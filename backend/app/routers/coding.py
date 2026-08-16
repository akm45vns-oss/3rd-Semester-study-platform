"""Coding Lab and Multi-Language Online Compiler Router."""
import sqlite3
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from sqlalchemy.orm import selectinload
from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.curriculum import Topic, Unit, Subject
from app.models.progress import TopicProgress, Mistake
from app.models.practice import CodingProblem, CodingSubmission, Difficulty
from app.schemas.coding import (
    CodingProblemOut, CodingSubmissionCreate, CodingSubmissionOut,
    SqlExecuteRequest, SqlExecuteResult, LanguageInfoOut,
    CodeExecuteRequest, CodeExecuteResult, PracticeSubmitResultOut, PublicTestCaseOut
)
from app.services.code_execution.registry import list_available_languages, get_language_config
from app.services.code_execution.executor import CodeExecutor

router = APIRouter(prefix="/coding", tags=["coding"])


DEFAULT_SQL_SCHEMA = """
CREATE TABLE Departments (
    id INTEGER PRIMARY KEY,
    dept_name TEXT NOT NULL
);

CREATE TABLE Students (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    course TEXT NOT NULL,
    dept_id INTEGER,
    score INTEGER,
    FOREIGN KEY (dept_id) REFERENCES Departments(id)
);

INSERT INTO Departments (id, dept_name) VALUES 
(101, 'Computer Science'),
(102, 'Electronics'),
(103, 'Artificial Intelligence');

INSERT INTO Students (id, name, course, dept_id, score) VALUES 
(1, 'Alice', 'CS', 101, 92),
(2, 'Bob', 'AI', 101, 85),
(3, 'Charlie', 'ECE', 102, 78),
(4, 'Diana', 'Data Science', 103, 95);
"""


@router.get("/languages", response_model=List[LanguageInfoOut])
async def get_supported_languages():
    """Retrieve all supported online lab compiler runtimes."""
    langs = list_available_languages()
    return [
        LanguageInfoOut(
            id=l.id,
            display_name=l.display_name,
            category=l.category,
            file_name=l.file_name,
            entry_point=l.entry_point,
            starter_code=l.starter_code,
            supports_stdin=l.supports_stdin,
            timeout_seconds=l.timeout_seconds,
            course_code=l.course_code,
            description=l.description,
        )
        for l in langs
    ]


@router.post("/execute", response_model=CodeExecuteResult)
async def execute_free_code(
    req: CodeExecuteRequest,
    _: User = Depends(get_current_user),
):
    """Execute code in Free Compiler mode with custom stdin and isolated sandbox."""
    res = CodeExecutor.execute_free_code(
        language=req.language,
        source_code=req.source_code,
        stdin_input=req.stdin or "",
    )
    return CodeExecuteResult(
        status=res.status,
        stdout=res.stdout,
        stderr=res.stderr,
        compile_error=res.compile_error,
        runtime_error=res.runtime_error,
        execution_time_ms=res.execution_time_ms,
        memory_usage_mb=res.memory_usage_mb,
        exit_code=res.exit_code,
    )


@router.get("/problems", response_model=List[CodingProblemOut])
async def list_coding_problems(
    language: Optional[str] = Query(None),
    difficulty: Optional[Difficulty] = Query(None),
    subject_id: Optional[int] = Query(None),
    unit_id: Optional[int] = Query(None),
    topic_id: Optional[int] = Query(None),
    solved: Optional[bool] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve coding and SQL problems with curriculum relationships and solved status."""
    stmt = (
        select(CodingProblem)
        .options(selectinload(CodingProblem.topic).selectinload(Topic.unit).selectinload(Unit.subject))
        .where(CodingProblem.is_active == True)
    )

    if language and language.upper() != "ALL":
        stmt = stmt.where(CodingProblem.language == language.upper())
    if difficulty:
        stmt = stmt.where(CodingProblem.difficulty == difficulty)
    if topic_id:
        stmt = stmt.where(CodingProblem.topic_id == topic_id)
    elif unit_id:
        stmt = stmt.join(Topic, CodingProblem.topic_id == Topic.id).where(Topic.unit_id == unit_id)
    elif subject_id:
        stmt = (
            stmt.join(Topic, CodingProblem.topic_id == Topic.id)
            .join(Unit, Topic.unit_id == Unit.id)
            .where(Unit.subject_id == subject_id)
        )

    res = await db.execute(stmt)
    problems = res.scalars().all()

    # Get user submissions to determine is_solved
    prob_ids = [p.id for p in problems]
    solved_set = set()
    if prob_ids:
        sub_res = await db.execute(
            select(CodingSubmission.problem_id)
            .where(
                CodingSubmission.user_id == current_user.id,
                CodingSubmission.problem_id.in_(prob_ids),
                CodingSubmission.status == "PASSED",
            )
        )
        solved_set = set(sub_res.scalars().all())

    out = []
    for p in problems:
        is_p_solved = p.id in solved_set
        if solved is not None and is_p_solved != solved:
            continue

        p_dict = CodingProblemOut.model_validate(p)
        p_dict.topic_name = p.topic.name if p.topic else None
        p_dict.course_code = p.topic.unit.subject.course_code if (p.topic and p.topic.unit and p.topic.unit.subject) else None
        p_dict.unit_number = p.topic.unit.unit_number if (p.topic and p.topic.unit) else None
        p_dict.is_solved = is_p_solved
        
        # Public test cases only
        cases = CodeExecutor._extract_test_cases(p)
        p_dict.public_test_cases = [
            PublicTestCaseOut(
                test_index=i + 1,
                input_text=tc.get("input", ""),
                expected_output=tc.get("expected", ""),
            )
            for i, tc in enumerate(cases) if not tc.get("hidden", False)
        ]
        out.append(p_dict)

    return out


@router.get("/problems/recommended", response_model=List[CodingProblemOut])
async def get_recommended_problems(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve 3-5 high-priority recommended coding problems based on student weakness and unsolved topics."""
    # Find user weak or in-progress topics
    prog_stmt = (
        select(TopicProgress.topic_id)
        .where(
            TopicProgress.user_id == current_user.id,
            TopicProgress.coding_completed == False,
        )
        .order_by(TopicProgress.mastery_percent.asc())
        .limit(5)
    )
    prog_res = await db.execute(prog_stmt)
    weak_topic_ids = prog_res.scalars().all()

    stmt = (
        select(CodingProblem)
        .options(selectinload(CodingProblem.topic).selectinload(Topic.unit).selectinload(Unit.subject))
        .where(CodingProblem.is_active == True)
    )
    if weak_topic_ids:
        stmt = stmt.where(CodingProblem.topic_id.in_(weak_topic_ids))

    stmt = stmt.limit(5)
    res = await db.execute(stmt)
    problems = res.scalars().all()

    if not problems:
        # Fallback to any 5 active problems
        fallback_stmt = (
            select(CodingProblem)
            .options(selectinload(CodingProblem.topic).selectinload(Topic.unit).selectinload(Unit.subject))
            .where(CodingProblem.is_active == True)
            .limit(5)
        )
        fb_res = await db.execute(fallback_stmt)
        problems = fb_res.scalars().all()

    out = []
    for p in problems:
        p_dict = CodingProblemOut.model_validate(p)
        p_dict.topic_name = p.topic.name if p.topic else None
        p_dict.course_code = p.topic.unit.subject.course_code if (p.topic and p.topic.unit and p.topic.unit.subject) else None
        p_dict.unit_number = p.topic.unit.unit_number if (p.topic and p.topic.unit) else None
        p_dict.is_solved = False
        cases = CodeExecutor._extract_test_cases(p)
        p_dict.public_test_cases = [
            PublicTestCaseOut(
                test_index=i + 1,
                input_text=tc.get("input", ""),
                expected_output=tc.get("expected", ""),
            )
            for i, tc in enumerate(cases) if not tc.get("hidden", False)
        ]
        out.append(p_dict)
    return out


@router.get("/problems/{problem_id}", response_model=CodingProblemOut)
async def get_coding_problem(
    problem_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve single coding problem detail with public test cases."""
    stmt = (
        select(CodingProblem)
        .options(selectinload(CodingProblem.topic).selectinload(Topic.unit).selectinload(Unit.subject))
        .where(CodingProblem.id == problem_id)
    )
    res = await db.execute(stmt)
    p = res.scalar_one_or_none()
    if not p:
        raise HTTPException(status_code=404, detail="Coding problem not found")

    sub_res = await db.execute(
        select(CodingSubmission.id)
        .where(
            CodingSubmission.user_id == current_user.id,
            CodingSubmission.problem_id == p.id,
            CodingSubmission.status == "PASSED",
        )
    )
    is_solved = sub_res.scalar_one_or_none() is not None

    p_dict = CodingProblemOut.model_validate(p)
    p_dict.topic_name = p.topic.name if p.topic else None
    p_dict.course_code = p.topic.unit.subject.course_code if (p.topic and p.topic.unit and p.topic.unit.subject) else None
    p_dict.unit_number = p.topic.unit.unit_number if (p.topic and p.topic.unit) else None
    p_dict.is_solved = is_solved
    
    cases = CodeExecutor._extract_test_cases(p)
    p_dict.public_test_cases = [
        PublicTestCaseOut(
            test_index=i + 1,
            input_text=tc.get("input", ""),
            expected_output=tc.get("expected", ""),
        )
        for i, tc in enumerate(cases) if not tc.get("hidden", False)
    ]
    return p_dict


@router.post("/submit", response_model=PracticeSubmitResultOut)
async def submit_coding_solution(
    data: CodingSubmissionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Submit code solution, evaluate against all test cases, update topic mastery and mistake notebook."""
    stmt = (
        select(CodingProblem)
        .options(selectinload(CodingProblem.topic).selectinload(Topic.unit).selectinload(Unit.subject))
        .where(CodingProblem.id == data.problem_id)
    )
    res = await db.execute(stmt)
    problem = res.scalar_one_or_none()
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")

    # Evaluate submission
    eval_result = CodeExecutor.evaluate_practice_submission(
        problem=problem,
        source_code=data.code,
        language=data.language,
    )

    status_str = "PASSED" if eval_result.passed else eval_result.status

    submission = CodingSubmission(
        user_id=current_user.id,
        problem_id=problem.id,
        code=data.code,
        language=data.language,
        status=status_str,
        output=eval_result.output_message,
    )
    db.add(submission)

    # If passed, update topic progress and mastery
    if eval_result.passed:
        prog_res = await db.execute(
            select(TopicProgress).where(
                TopicProgress.user_id == current_user.id,
                TopicProgress.topic_id == problem.topic_id,
            )
        )
        prog = prog_res.scalar_one_or_none()
        if not prog:
            prog = TopicProgress(user_id=current_user.id, topic_id=problem.topic_id)
            db.add(prog)

        prog.coding_completed = True
        prog.practice_completion = max(prog.practice_completion or 0.0, 1.0)
        prog.last_studied_at = datetime.now(timezone.utc)
        prog.calculate_mastery()
    else:
        # Check failed attempts count to optionally log into mistakes notebook
        fail_res = await db.execute(
            select(func.count(CodingSubmission.id))
            .where(
                CodingSubmission.user_id == current_user.id,
                CodingSubmission.problem_id == problem.id,
                CodingSubmission.status != "PASSED",
            )
        )
        failed_count = fail_res.scalar() or 0
        if failed_count >= 2:
            # Check if mistake already logged
            mistake_check = await db.execute(
                select(Mistake).where(
                    Mistake.user_id == current_user.id,
                    Mistake.topic_id == problem.topic_id,
                    Mistake.source_type == "CODING_CHALLENGE",
                    Mistake.is_resolved == False,
                )
            )
            if not mistake_check.scalar_one_or_none():
                topic_name = problem.topic.name if problem.topic else problem.title
                course_code = problem.topic.unit.subject.course_code if (problem.topic and problem.topic.unit and problem.topic.unit.subject) else "CURRICULUM"
                mistake_entry = Mistake(
                    user_id=current_user.id,
                    topic_id=problem.topic_id,
                    topic_name=topic_name,
                    course_code=course_code,
                    description=f"Struggled with coding problem: '{problem.title}' ({data.language}). Failed {failed_count + 1} test runs.",
                    correction=f"Review algorithm concepts for {topic_name}. Starter hint: {problem.hints or 'Check edge cases and constraints'}",
                    source_type="CODING_CHALLENGE",
                    is_resolved=False,
                )
                db.add(mistake_entry)

    await db.commit()
    await db.refresh(submission)

    return PracticeSubmitResultOut(
        id=submission.id,
        problem_id=submission.problem_id,
        status=status_str,
        passed=eval_result.passed,
        tests_passed=eval_result.tests_passed,
        tests_total=eval_result.tests_total,
        public_test_results=[
            PublicTestCaseOut(
                test_index=tr.test_index,
                input_text=tr.input_text,
                expected_output=tr.expected_output,
                actual_output=tr.actual_output,
                passed=tr.passed,
                status=tr.status,
            )
            for tr in eval_result.public_test_results
        ],
        hidden_passed=eval_result.hidden_passed,
        hidden_total=eval_result.hidden_total,
        execution_time_ms=eval_result.execution_time_ms,
        output_message=eval_result.output_message,
        compile_error=eval_result.compile_error,
        runtime_error=eval_result.runtime_error,
        submitted_at=submission.submitted_at,
    )


@router.post("/execute-sql", response_model=SqlExecuteResult)
async def execute_sql_sandbox(
    req: SqlExecuteRequest,
    _: User = Depends(get_current_user),
):
    """Execute arbitrary user SQL in a secure, isolated in-memory SQLite sandbox."""
    try:
        conn = sqlite3.connect(":memory:")
        cursor = conn.cursor()
        
        schema = req.schema_sql if req.schema_sql else DEFAULT_SQL_SCHEMA
        cursor.executescript(schema)
        cursor.execute(req.query)
        
        if cursor.description:
            columns = [col[0] for col in cursor.description]
            raw_rows = cursor.fetchall()
            rows = [[str(val) if val is not None else "NULL" for val in r] for r in raw_rows]
            row_count = len(rows)
        else:
            conn.commit()
            columns = ["Result"]
            rows = [["Statement executed successfully"]]
            row_count = cursor.rowcount

        conn.close()
        return SqlExecuteResult(
            success=True,
            columns=columns,
            rows=rows,
            row_count=row_count,
        )
    except Exception as err:
        return SqlExecuteResult(
            success=False,
            error=str(err),
            columns=[],
            rows=[],
            row_count=0,
        )
