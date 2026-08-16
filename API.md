# API Reference — Semester OS

Base URL: `http://localhost:8000` (or `/api` via Vite development proxy)  
Interactive Swagger Docs: `http://localhost:8000/docs`

---

## 1. Authentication (`/auth`)

- `POST /auth/register` — Register a new account (`username`, `email`, `password`, `full_name`)
- `POST /auth/login` — Login and receive JWT access token (`username`, `password`)
- `GET /auth/me` — Retrieve current authenticated user profile

---

## 2. Curriculum & Audit (`/subjects`, `/units`, `/topics`, `/curriculum`)

- `GET /subjects` — List all 5 official subjects with credit details
- `GET /subjects/{id}` — Subject detail with all 6 nested units and topics
- `GET /subjects/{id}/units` — List 6 units for a subject
- `GET /subjects/{id}/practicals` — List official laboratory experiments
- `GET /units/{id}` — Unit detail with topic list
- `GET /topics/{id}` — Topic metadata and syllabus scope
- `GET /curriculum/audit` — Automated syllabus audit verifying 5 subjects, 30 units, and strict exclusion of `CAP138` and `PES209`.

---

## 3. Progress & Dashboard (`/progress`, `/dashboard`)

- `GET /dashboard` — Overall semester progress %, learned/revision counts, and subject cards
- `GET /progress/subjects/{id}` — Subject completion statistics and average mastery
- `GET /progress/topics/{id}` — Retrieve 4-pillar mastery data for a specific topic
- `POST /progress/topics/{id}` — Update status, theory/practice/assessment flags (auto-recalculates mastery)
- `GET /progress/practicals/{id}` — User lab progress and code evidence
- `POST /progress/practicals/{id}` — Update practical status and save notes
- `GET /topics/{id}/notes` — Retrieve user notes for a topic
- `POST /topics/{id}/notes` — Save a new topic note

---

## 4. Practice & Assessments (`/practice`)

- `GET /practice/questions` — Filter questions by `subject_id`, `unit_id`, `topic_id`, `difficulty`
- `POST /practice/attempts` — Submit single question answer; auto-logs mistakes if wrong
- `POST /practice/tests/generate` — Generate scoped Unit Test, Subject Test, or Full Mock Exam
- `POST /practice/tests/submit` — Submit test answers for evaluation, score report, and weak topic identification
- `GET /practice/mistakes` — List mistakes notebook entries (`is_resolved=false/true`)
- `POST /practice/mistakes/{id}/resolve` — Mark a logged mistake as resolved

---

## 5. Coding Lab & SQL Sandbox (`/coding`)

- `GET /coding/problems` — List coding and SQL challenges
- `GET /coding/problems/{id}` — Challenge specification, starter code, and test cases
- `POST /coding/submit` — Submit code solution; updates topic coding mastery
- `POST /coding/execute-sql` — Run arbitrary SQL queries safely inside an isolated in-memory SQLite sandbox

---

## 6. Intelligence & Revision (`/revision`, `/recommendations`, `/analytics`, `/search`)

- `GET /revision/queue` — Spaced repetition priority queue (`HIGH`, `MEDIUM`, `LOW`)
- `POST /revision/{topic_id}/complete` — Mark a topic revised (+25% revision mastery boost)
- `GET /recommendations/what-to-study` — Smart 60-minute timeboxed session roadmap
- `GET /practicals` — Full practical tracker across all subjects
- `GET /analytics/detailed` — Recharts analytics payload (mastery distributions, accuracy, streak)
- `GET /search?q={query}` — Global search across subjects, units, topics, practicals, and coding
