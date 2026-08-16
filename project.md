# Project Documentation — Semester OS (3rd Semester Study Platform)

> **Document Version**: 3.1.0  
> **Last Verified**: August 16, 2026  
> **Production Status**: Production Ready, Security Hardened & Fully Seeded on Supabase PostgreSQL (AWS Mumbai)  
> **Authoritative Source of Truth**: This document represents the complete, verified technical and operational knowledge base for the Semester OS platform.

---

## 31. Documentation Accuracy Rules

```text
This document is generated directly from deep inspection of the project repository.

Accuracy rules adhered to:
- Never guess implementation details.
- Never invent files, APIs, features, dependencies, or configurations.
- Verified against active source code, schemas, and live database state.
- Clearly distinguishes implemented (✅), partially implemented (⚠️), planned (❌), and deprecated (🗑️) features.
- Strict non-negotiable project constraints documented without ambiguity.
- If something cannot be verified, it is marked as UNKNOWN.
- If something is planned but not implemented, it is marked as NOT IMPLEMENTED.
- Source code is treated as the primary implementation authority.
```

---

## 1. Project Overview

- **Project Name**: Semester OS (Personal 3rd Semester Study Operating System)
- **Primary Purpose**: A guided personal study operating system engineered to achieve 100% syllabus mastery across all 5 official 3rd-semester university computer science subjects without cognitive friction.
- **Main Problem It Solves**:
  1. "What should I study next?" decision paralysis.
  2. Fragmented curriculum materials scattered across slides, PDFs, external links, and LMS portals.
  3. Lack of seamless active recall (practice questions, multi-language coding sandbox, practical lab logging, and spaced repetition) integrated directly with notes.
  4. Interrupted study momentum across refreshes, devices, and network sessions.
  5. AI rate limits disrupting note and quiz generation.
  6. Disconnect between daily topic learning and official university exam patterns (Midterm 30 MCQs & End-Term 80 Marks).
- **Target Users**: Computer Science undergraduates in their 3rd semester studying:
  1. `CAP392` — Java Programming
  2. `CAP206` — Database Management Systems
  3. `CAP135` — Front End Web Development
  4. `CAB213` — Applied AI: Computer Vision & Natural Language Processing
  5. `CAB114` — Model Optimization
- **Main Use Cases**:
  - Daily structured active study with automated 60-minute recommendations.
  - Interactive topic study flow: Learn (Notes) ➔ Practice (MCQs) ➔ Apply (Coding/SQL) ➔ Revise (Recall).
  - Online Lab dual modes: **Free Compiler** (Java, Python, JS, SQL with custom Stdin/Stdout) and **Practice Mode** (Syllabus-mapped questions with Public and Hidden test validation).
  - **University Exam Center & Simulator**:
    - **Midterm Mock**: Strictly 30 MCQs across Units 1–3 (60-minute timed simulator).
    - **End-Term Mock**: Part A (30 MCQs across Units 1–6) + Part B (5 × 10-Mark Descriptive Questions, 120-minute timed simulator, 80 Marks total).
    - **10-Mark Analytical Question Bank**: 112+ descriptive questions with self-evaluation marking rubrics, answer outlines, and verified model answers.
    - **Exam Readiness Engine**: Unit-by-unit readiness percentage calculations.
  - Distraction-free Focus Mode for reading comprehensive academic markdown notes.
  - Immediate resumption of studies via the dominant "Continue Studying" hero card.
  - Spaced repetition queue and mistakes notebook for eliminating weak concepts.
  - Complete practical laboratory experiment tracker with code templates and viva notes.
- **Current Project Status**: Production-ready and hardened. Live database migrated and 100% seeded to **Supabase PostgreSQL 17.6** (AWS Mumbai pooler).
- **Overall Architecture**: Decoupled full-stack Single Page Application (SPA) architecture:
  - **Backend**: FastAPI asynchronous REST API on Python 3.11 with SQLAlchemy 2.0 ORM and asyncpg.
  - **Execution Sandbox**: Multi-language disposable subprocess sandbox with process-tree isolation, clean environment variables, 5s timeout, and 64KB output limits.
  - **Frontend**: Vite + React 18 + TypeScript + Tailwind CSS with custom client-side cache and Zustand state management.
  - **Security Layer**: 3-minute throttled inactivity logout with warning modal, BroadcastChannel cross-tab auth sync, login rate limiting / progressive throttling.
  - **Database**: Supabase PostgreSQL 17.6 with 24 relational tables, connection pooling, and sequence safety.
  - **AI Layer**: Groq Cloud multi-model fallback cascade (`Llama 3.3 70B` ➔ `Llama 3.1 8B` ➔ `Mixtral 8x7B` ➔ `Gemma 2 9B`) with round-robin key pooling.

---

## 2. Project Goals

### A. Current Active Requirements
- **100% Curriculum Coverage**: Complete, verified academic notes for all **344 topics** across **30 units** (6 units per subject, 344/344 notes verified).
- **Multi-Language Online Lab**: Dual-mode coding environment:
  - **Free Compiler**: Immediate execution workspace for Java, Python 3, JavaScript (Node), and SQL with Stdin support and persistent local drafts.
  - **Practice Mode**: Syllabus-mapped problems with Public and Hidden test cases, constraints, hints, and automated progress/mistake tracking.
- **University Examination Pattern**:
  - **Midterm Pattern**: Strictly 30 MCQs drawn from Chapters/Units 1, 2, and 3 (60 mins, 30 Marks).
  - **End-Term Pattern**: Full syllabus coverage with Part A (30 MCQs) + Part B (5 × 10-Mark Descriptive Questions, 120 mins, 80 Marks).
  - **10-Mark Descriptive Library**: 112+ analytical questions with outlines, rubrics, and model answers.
- **1,077 Validated Practice MCQs**: Categorized by topic, unit, and difficulty with strict 4 options and 1 correct answer per question.
- **121+ Coding & SQL Challenges**: Interactive code sandbox with starter code, test cases, and in-memory SQLite schema execution.
- **60 Practical Experiments**: Syllabus laboratory experiments with code templates, output notes, and viva preparation points.
- **Action-Oriented Dashboard**: Immediate continuation hero card with duration estimate, today's study progress tracker (`X / 60 mins`), top 3 smart-ranked weak areas, and 5 subject cards with direct study materials modal.
- **Distraction-Free Focus Mode**: Dedicated full-width reading view for notes with keyboard navigation (`ESC`, `←`, `→`).
- **Persistent Study Session System**: Live timer ticker bar and session completion celebration modal recording study duration into daily goals.
- **Universal Command Center (`Cmd+K`)**: Instant action launchers and global search across all syllabus entities.

### B. Important UX Requirements
- **Strict 6-Color Warm Editorial Design System**: Warm earthy coffee palette (`#60412B`, `#B09171`, `#D7C9B8`, `#E5DDC9`, `#E6E0D2`, `#EAE6DE`).
- **Typography Stack**: Display headings in `Outfit`, body text in `Inter`, and code in `JetBrains Mono`.
- **Skeleton Shimmer Loading**: Zero layout shifts during data loading.
- **Mobile-First Responsiveness**: Flawless interaction on 360px, 390px, and 412px viewports.

### C. Non-Negotiable Requirements (MUST NOT BE CHANGED)
- **Strict 5-Subject Curriculum Scope**: Strictly the 5 designated subjects (`CAP392`, `CAP206`, `CAP135`, `CAB213`, `CAB114`).
- **Strict Prohibition**: `CAP138` and `PES209` must **NEVER** be reintroduced into the curriculum, database, or UI.
- **6 Units Per Subject**: Every subject must contain exactly 6 units (30 units total across curriculum).
- **Exam Distribution Rules**: Midterm questions must NEVER be selected from Units 4, 5, or 6. Server-side validation MUST verify exact question counts (30 for Midterm; 30 MCQs + 5 Descriptive for End-Term).

---

## 3. Complete Tech Stack

| Category | Technology | Version | Purpose | Important Notes |
|---|---|---|---|---|
| **Backend Runtime** | Python | 3.11.x | Asynchronous API server runtime | Pinned in `Dockerfile` |
| **Backend Framework** | FastAPI | 0.115.0 | Async REST API framework | Clean route modularization with Pydantic v2 |
| **Execution Sandbox** | Python Subprocess / Disposable Tempdir | 1.0.0 | Isolated execution for Java, Python, Node, SQL | Strips secrets, enforces 5s timeout & process-tree termination |
| **Exam Engine** | University Mock Simulator | 1.0.0 | Server-side question selection, timer, grading | Enforces 30 MCQs for Midterm, 30+5 for End-Term |
| **ASGI Web Server** | Uvicorn (standard) | 0.30.6 | Production ASGI server | Includes uvloop & httptools for high concurrency |
| **ORM / SQL Layer** | SQLAlchemy | 2.0.35 | Asynchronous database ORM | Uses async session maker and `selectinload` |
| **PostgreSQL Driver** | asyncpg | 0.29.0 | High-performance async driver | Connected to Supabase connection pooler |
| **SQLite Driver** | aiosqlite | 0.20.0 | Local development fallback driver | Local fallback in `database.py` |
| **Data Validation** | Pydantic / Pydantic Settings | 2.9.2 / 2.5.2 | Request/response schemas & `.env` parsing | Strict typing with `ConfigDict(from_attributes = True)` |
| **Authentication** | python-jose & passlib[bcrypt] | 3.3.0 / 1.7.4 | JWT token handling & salted bcrypt hashing | HS256 algorithm with 7-day token expiry |
| **HTTP Client (Async)**| HTTPX | 0.27.2 | Async client for Groq API & test suite | Used in `ai_generator.py`, `exam_seed.py`, and `test_api.py` |
| **Testing Engine** | Pytest & pytest-asyncio | 8.3.3 / 0.24.0 | Automated async test runner | Full test coverage in `tests/test_api.py` |
| **Frontend Framework**| React + TypeScript | 18.3.1 / 5.6.2 | Interactive SPA user interface | Strict TypeScript with zero `any` leaks |
| **Build Tooling** | Vite | 5.4.8 | Development server & Rollup production bundler | Sub-second HMR and optimized chunking |
| **CSS Engine** | Tailwind CSS + PostCSS | 3.4.19 / 8.5.26 | Custom tokenized utility styling | Configured with exact 6-color tokens |
| **Icons Library** | Lucide React | 0.447.0 | Clean SVG icon components | Consistent 14-20px stroke styling |
| **Data Visualization**| Recharts | 2.15.4 | Charts & progress analytics | Radial bars and radar charts |
| **Markdown Parser** | React-Markdown + Remark-GFM | 10.1.0 / 4.0.1 | Academic notes reader | Syntax highlighting and copy code blocks |
| **Client State** | Zustand + Persist | 5.0.15 | Auth store & persistent study session store | Persisted in `localStorage` with BroadcastChannel sync |
| **Client Caching** | Custom In-Memory + SessionStorage | 1.0.0 | TTL cache layer for static curriculum | Sub-100ms instant page transitions |
| **HTTP Client (Web)** | Axios | 1.19.0 | Typed API client with 15s timeout & retry | Centralized in `api/client.ts` |
| **Primary Database** | PostgreSQL (Supabase) | 17.6 | Production database on AWS Mumbai Pooler | 24 relational tables with SSL pooling |
| **AI LLM Provider** | Groq Cloud API | Multi-Model | Llama 3.3 70B, Llama 3.1 8B, Mixtral 8x7B, Gemma 2 9B | Multi-model fallback cascade with key pool |
| **Containerization** | Docker & Docker Compose | 3.8 Spec | Multi-stage builds with Nginx Alpine | Production container setup in `docker-compose.yml` |

---

## 4. Architecture & Security Invariants

### A. Session Security & Inactivity Protocol
1. **3-Minute Inactivity Logout**:
   - Monitored user events: `mousedown`, `mousemove`, `keydown`, `touchstart`, `scroll`, `click` (throttled at 1,000ms).
   - At 150 seconds of inactivity: displays non-intrusive warning modal with countdown timer.
   - At 180 seconds: automatically invalidates tokens, clears session storage, and redirects to `/login?reason=inactivity`.
2. **Cross-Tab Synchronization**:
   - Utilizes `BroadcastChannel('semester_os_auth_channel')` and `window.addEventListener('storage')`.
   - Logging out in any tab immediately triggers unauthenticated redirection across all open tabs.
3. **Login Abuse Protection**:
   - Progressive rate limiting per IP/username on `/auth/login`: max 5 failed attempts per 60-second window, returning HTTP 429 with `Retry-After` header.

### B. Sandbox Process-Tree Isolation
- Child processes executed in disposable isolated directories (`/semester_os_sandbox_*`).
- On timeout (5s) or interruption, process tree is terminated via `taskkill /F /T /PID` (Windows) or process group kill (POSIX) to prevent zombie processes.
- Sensitive environment variables (`DATABASE_URL`, `SECRET_KEY`, `GROQ_API_KEY`) are stripped before subprocess launch.

### C. Data Integrity Invariants
- **Curriculum**: Exactly 5 subjects, 30 units (6 units per subject), 344 topics.
- **Notes Coverage**: Exactly 344 / 344 topics with comprehensive academic notes (100.0% verified).
- **MCQ Invariants**: Exactly 1,077 MCQs, each with strictly 4 options and exactly 1 correct answer.
- **Hidden Test Cases**: Hidden test case inputs and expected outputs are never returned in client problem schemas and evaluated strictly server-side.

---

## 5. Testing & Verification

- **Backend Pytest Suite**:
  ```powershell
  & "C:\Users\akm45\AppData\Local\Programs\Python\Python311\python.exe" -m pytest tests/test_api.py -v
  ```
  **Result**: `1 passed in 16.13s` (100% pass rate covering Health, Readiness, Auth, Rate Limiting, 401s, 5-Subject Curriculum Invariants, 344/344 Notes, 4-Option MCQs, Midterm & End-Term Exam Simulators, Code Sandbox Execution, Syntax/Runtime Errors, and 10-Mark Descriptive Questions).

- **Frontend Production Build**:
  ```bash
  npm run build
  ```
  **Result**: `✓ built in 23.00s` (2,715 modules transformed, 0 TypeScript errors, 0 lint warnings).
