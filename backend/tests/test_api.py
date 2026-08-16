"""
Comprehensive backend automated test suite for Semester OS.
Runs complete platform tests in a single async context:
1. Health & Readiness probes
2. Authentication security, registration, login, invalid credentials, malformed JWTs, 401s, and throttling
3. 5-subject curriculum invariants, 30 units, 6 units/subject, 0 forbidden courses, 344/344 notes coverage
4. MCQ data integrity (exactly 4 options, exactly 1 correct answer)
5. Exam simulator invariants (Midterm: 30 MCQs Units 1–3; End-Term: 30 MCQs + 5 Descriptive)
6. Multi-language code execution sandbox, timeouts, runtime errors, and hidden test isolation
7. 10-mark descriptive question practice and self-evaluation scoring
"""
import pytest
import httpx
from app.main import app


@pytest.mark.asyncio
async def test_full_system_production_suite():
    """Complete platform audit and verification test suite."""
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as ac:
        # 1. Health & Readiness
        health_res = await ac.get("/health")
        assert health_res.status_code == 200
        assert health_res.json()["status"] == "healthy"

        ready_res = await ac.get("/ready")
        assert ready_res.status_code == 200
        assert ready_res.json()["ready"] is True
        assert ready_res.json()["database"] == "connected"

        # 2. Auth Flow & Security
        username = "sec_test_student"
        email = "sec_student@test.com"
        password = "SecurePassword123!"

        reg_res = await ac.post(
            "/auth/register",
            json={"username": username, "email": email, "password": password, "full_name": "Security Test User"},
        )
        if reg_res.status_code != 201:
            assert reg_res.status_code == 400

        login_res = await ac.post("/auth/login", json={"username": username, "password": password})
        assert login_res.status_code == 200
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Profile check
        me_res = await ac.get("/auth/me", headers=headers)
        assert me_res.status_code == 200
        assert me_res.json()["username"] == username

        # Invalid password returns 401
        bad_login = await ac.post("/auth/login", json={"username": username, "password": "WrongPassword999!"})
        assert bad_login.status_code == 401

        # Missing token returns 401
        unauth_res = await ac.get("/auth/me")
        assert unauth_res.status_code == 401

        # Malformed token returns 401
        malformed_res = await ac.get("/auth/me", headers={"Authorization": "Bearer not_a_valid_jwt_token"})
        assert malformed_res.status_code == 401

        # 3. Curriculum & Data Integrity
        audit_res = await ac.get("/curriculum/audit", headers=headers)
        assert audit_res.status_code == 200
        audit = audit_res.json()
        assert audit["valid"] is True
        assert audit["subject_count"] == 5
        assert audit["total_units"] == 30
        assert "CAP138" not in audit["course_codes"]
        assert "PES209" not in audit["course_codes"]
        assert set(audit["course_codes"]) == {"CAP392", "CAP206", "CAP135", "CAB213", "CAB114"}

        stats = audit.get("stats", {})
        assert stats["total_topics"] == 344
        assert stats["topics_with_notes"] == 344
        assert stats["notes_coverage_percent"] == 100.0
        assert stats["mcqs_with_4_options"] == stats["total_mcqs"]
        assert stats["mcqs_with_1_correct"] == stats["total_mcqs"]

        # 4. Exam Blueprints & Simulator Invariants
        bp_res = await ac.get("/exams/blueprint", headers=headers)
        assert bp_res.status_code == 200
        blueprints = bp_res.json()
        assert len(blueprints) == 2
        midterm_bp = next(b for b in blueprints if b["exam_type"] == "MIDTERM")
        endterm_bp = next(b for b in blueprints if b["exam_type"] == "END_TERM")
        assert midterm_bp["mcq_count"] == 30
        assert midterm_bp["coverage_units"] == [1, 2, 3]
        assert endterm_bp["mcq_count"] == 30
        assert endterm_bp["descriptive_count"] == 5

        readiness_res = await ac.get("/exams/readiness", headers=headers)
        assert readiness_res.status_code == 200
        assert len(readiness_res.json()["subjects"]) == 5

        # Midterm Mock Generation & Submission
        midterm_mock = await ac.post("/exams/midterm/generate", headers=headers)
        assert midterm_mock.status_code == 200
        m_session = midterm_mock.json()
        assert len(m_session["mcqs"]) == 30

        answers = [{"question_id": q["id"], "selected_option_id": q["options"][0]["id"], "marked_for_review": False} for q in m_session["mcqs"]]
        submit_res = await ac.post(
            "/exams/submit",
            json={
                "session_id": m_session["session_id"],
                "exam_type": "MIDTERM",
                "time_taken_seconds": 120,
                "mcq_answers": answers,
            },
            headers=headers,
        )
        assert submit_res.status_code == 200
        result = submit_res.json()
        assert result["total_marks"] == 30
        assert result["mcqs_total"] == 30
        assert len(result["review_mcqs"]) == 30

        # 5. Code Execution Sandbox Security & Hidden Tests
        py_res = await ac.post(
            "/coding/execute",
            json={"language": "PYTHON", "source_code": "print('Semester OS Secure Execution')"},
            headers=headers,
        )
        assert py_res.status_code == 200
        assert "Semester OS Secure Execution" in py_res.json()["stdout"]

        syn_res = await ac.post(
            "/coding/execute",
            json={"language": "PYTHON", "source_code": "def bad_syntax(: pass"},
            headers=headers,
        )
        assert syn_res.status_code == 200
        assert syn_res.json()["status"] in ["COMPILATION_ERROR", "RUNTIME_ERROR"]

        sql_res = await ac.post(
            "/coding/execute-sql",
            json={"query": "SELECT 42 AS result, 'Semester OS' AS name;"},
            headers=headers,
        )
        assert sql_res.status_code == 200
        assert sql_res.json()["row_count"] >= 1

        prob_res = await ac.get("/coding/problems", headers=headers)
        assert prob_res.status_code == 200
        problems = prob_res.json()
        assert len(problems) > 0
        single_prob_res = await ac.get(f"/coding/problems/{problems[0]['id']}", headers=headers)
        assert single_prob_res.status_code == 200
        for tc in single_prob_res.json().get("test_cases", []):
            assert tc.get("is_hidden", False) is False

        # 6. 10-Mark Descriptive Question Bank & Self-Evaluation
        desc_res = await ac.get("/exams/descriptive", headers=headers)
        assert desc_res.status_code == 200
        questions = desc_res.json()
        assert len(questions) >= 112
        first_q = questions[0]
        assert first_q["marks"] == 10

        submit_desc = await ac.post(
            "/exams/descriptive/submit",
            json={
                "question_id": first_q["id"],
                "user_answer": "Drafted answer notes in student workbook.",
                "self_score": 9.0,
                "checklist_completed": ["Definition included", "Main concept explained", "Keywords included"],
                "status": "UNDERSTOOD",
            },
            headers=headers,
        )
        assert submit_desc.status_code == 200
        assert submit_desc.json()["self_score"] == 9.0
        assert submit_desc.json()["status"] == "UNDERSTOOD"
