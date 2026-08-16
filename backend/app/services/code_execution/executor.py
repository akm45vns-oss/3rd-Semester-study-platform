"""High-level code executor for Free Compiler and Practice Problem evaluations."""
import re
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from app.services.code_execution.sandbox import CodeSandbox, ExecutionOutput


class PublicTestCaseResult(BaseModel):
    test_index: int
    input_text: str
    expected_output: str
    actual_output: str
    passed: bool
    status: str


class PracticeEvaluationResult(BaseModel):
    status: str  # ACCEPTED | WRONG_ANSWER | COMPILATION_ERROR | RUNTIME_ERROR | TIME_LIMIT_EXCEEDED | SYSTEM_ERROR
    passed: bool
    tests_passed: int
    tests_total: int
    public_test_results: List[PublicTestCaseResult] = []
    hidden_passed: int = 0
    hidden_total: int = 0
    execution_time_ms: int = 0
    output_message: str = ""
    compile_error: Optional[str] = None
    runtime_error: Optional[str] = None


def normalize_output(text: str) -> str:
    """Normalize string for reliable output comparison (strip whitespace and unify newlines)."""
    if not text:
        return ""
    # Normalize Windows CRLF to LF
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    # Strip trailing whitespace on each line and at ends
    lines = [line.rstrip() for line in text.strip().split("\n")]
    return "\n".join(lines).strip()


class CodeExecutor:
    """Orchestrates free compiler runs and multi-test practice grading."""

    @staticmethod
    def execute_free_code(
        language: str,
        source_code: str,
        stdin_input: str = "",
    ) -> ExecutionOutput:
        """Run student code in Free Compiler mode."""
        return CodeSandbox.execute(
            language=language,
            source_code=source_code,
            stdin_input=stdin_input,
        )

    @staticmethod
    def evaluate_practice_submission(
        problem: Any,
        source_code: str,
        language: str,
    ) -> PracticeEvaluationResult:
        """
        Evaluate student submission against public and hidden test cases.
        Guarantees that hidden test inputs and expected outputs are never returned to client.
        """
        # 1. First compilation / sanity run check
        initial_run = CodeSandbox.execute(
            language=language,
            source_code=source_code,
            stdin_input="",
        )

        if initial_run.status == "COMPILATION_ERROR":
            return PracticeEvaluationResult(
                status="COMPILATION_ERROR",
                passed=False,
                tests_passed=0,
                tests_total=1,
                compile_error=initial_run.compile_error or initial_run.stderr,
                output_message="Compilation Failed. Fix syntax errors and try again.",
                execution_time_ms=initial_run.execution_time_ms,
            )

        # 2. Extract Test Cases from Problem
        test_cases = CodeExecutor._extract_test_cases(problem)
        if not test_cases:
            # Fallback to single expected output comparison
            expected = normalize_output(problem.expected_output or "")
            actual = normalize_output(initial_run.stdout)
            passed = (expected in actual) or (expected == actual) if expected else (initial_run.status == "ACCEPTED")
            
            status = "ACCEPTED" if passed else "WRONG_ANSWER"
            return PracticeEvaluationResult(
                status=status,
                passed=passed,
                tests_passed=1 if passed else 0,
                tests_total=1,
                public_test_results=[
                    PublicTestCaseResult(
                        test_index=1,
                        input_text="Default",
                        expected_output=problem.expected_output or "(Program Execution)",
                        actual_output=initial_run.stdout,
                        passed=passed,
                        status=status,
                    )
                ],
                hidden_passed=0,
                hidden_total=0,
                execution_time_ms=initial_run.execution_time_ms,
                output_message="All tests passed successfully." if passed else "Output did not match expected result.",
            )

        public_results: List[PublicTestCaseResult] = []
        tests_passed = 0
        total_tests = len(test_cases)
        hidden_passed = 0
        hidden_total = 0
        total_time_ms = 0

        overall_status = "ACCEPTED"

        for idx, tc in enumerate(test_cases, 1):
            is_hidden = tc.get("hidden", False)
            tc_input = tc.get("input", "")
            tc_expected = normalize_output(tc.get("expected", ""))

            # Execute with test input
            run_result = CodeSandbox.execute(
                language=language,
                source_code=source_code,
                stdin_input=tc_input,
            )
            total_time_ms += run_result.execution_time_ms

            if run_result.status in ("COMPILATION_ERROR", "SYSTEM_ERROR"):
                overall_status = run_result.status
                return PracticeEvaluationResult(
                    status=run_result.status,
                    passed=False,
                    tests_passed=tests_passed,
                    tests_total=total_tests,
                    compile_error=run_result.compile_error or run_result.stderr,
                    output_message=f"Execution halted with {run_result.status}.",
                    execution_time_ms=total_time_ms,
                )

            actual_norm = normalize_output(run_result.stdout)
            tc_passed = (tc_expected in actual_norm) or (actual_norm == tc_expected)

            if tc_passed:
                tests_passed += 1
                if is_hidden:
                    hidden_passed += 1
            else:
                if overall_status == "ACCEPTED":
                    overall_status = run_result.status if run_result.status != "ACCEPTED" else "WRONG_ANSWER"

            if is_hidden:
                hidden_total += 1
            else:
                public_results.append(
                    PublicTestCaseResult(
                        test_index=idx,
                        input_text=tc_input or "(None)",
                        expected_output=tc.get("expected", ""),
                        actual_output=run_result.stdout,
                        passed=tc_passed,
                        status="ACCEPTED" if tc_passed else run_result.status,
                    )
                )

        all_passed = (tests_passed == total_tests)
        
        msg = f"✓ All {total_tests} test cases passed ({len(public_results)} public, {hidden_total} hidden)." if all_passed \
            else f"✗ {tests_passed} / {total_tests} test cases passed."

        return PracticeEvaluationResult(
            status="ACCEPTED" if all_passed else overall_status,
            passed=all_passed,
            tests_passed=tests_passed,
            tests_total=total_tests,
            public_test_results=public_results,
            hidden_passed=hidden_passed,
            hidden_total=hidden_total,
            execution_time_ms=total_time_ms,
            output_message=msg,
        )

    @staticmethod
    def _extract_test_cases(problem: Any) -> List[Dict[str, Any]]:
        """Parse or generate test cases for a problem."""
        cases = []
        # Check if expected_output is present
        if problem.expected_output:
            cases.append({
                "input": "",
                "expected": problem.expected_output.strip(),
                "hidden": False,
            })

        # Check examples for additional test cases
        if problem.examples:
            # Pattern: Input: ... -> Output: ... or similar
            examples_text = problem.examples
            lines = examples_text.split("\n")
            for line in lines:
                if "->" in line:
                    parts = line.split("->")
                    inp = parts[0].replace("Input:", "").replace("input:", "").strip()
                    out = parts[1].replace("Output:", "").replace("output:", "").strip()
                    if out and out != (problem.expected_output or "").strip():
                        cases.append({
                            "input": inp,
                            "expected": out,
                            "hidden": False,
                        })

        # Add 1-2 synthetic hidden validation cases where appropriate
        if len(cases) == 1:
            cases.append({
                "input": "",
                "expected": problem.expected_output.strip() if problem.expected_output else "",
                "hidden": True,
            })

        return cases
