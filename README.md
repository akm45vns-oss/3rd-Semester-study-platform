# Semester OS

> **Your complete 3rd semester in one place.**

A personal study, practice, assessment, and progress-tracking platform built for 5 subjects:

| Code    | Subject                                      |
|---------|----------------------------------------------|
| CAP392  | Java Programming (4 credits)                 |
| CAP206  | Database Management Systems (3 credits)      |
| CAP135  | Front End Web Development (3 credits)        |
| CAB213  | Applied AI: CV and NLP (3 credits)          |
| CAB114  | Model Optimization (3 credits)               |

## Quick Start

```bash
# Option 1: Double-click
start.bat

# Option 2: Manual
# Terminal 1 — Backend
cd backend
C:\Users\akm45\AppData\Local\Programs\Python\Python311\python.exe -m uvicorn app.main:app --port 8000 --reload

# Terminal 2 — Frontend
cd frontend
npm run dev
```

Then open **http://localhost:5173**

## First Time Setup

```bash
# Install backend deps
cd backend
C:\Users\akm45\AppData\Local\Programs\Python\Python311\python.exe -m pip install -r requirements.txt

# Seed the database with curriculum
C:\Users\akm45\AppData\Local\Programs\Python\Python311\python.exe -m app.seed.seeder

# Install frontend deps
cd ../frontend
npm install
```

## Features (Phase 1)

- 🔐 Authentication (register / login)
- 📚 Complete syllabus browser (5 subjects → 30 units → all topics)
- 📊 Semester & subject progress dashboard
- ✅ Topic status tracking (Not Started / Learning / Learned / Needs Revision)
- 📈 Mastery scoring (theory 25% + practice 25% + assessment 25% + revision 25%)
- 📝 Notes per topic
- 🔍 Curriculum audit page (validates all 5 subjects, 30 units, no CAP138/PES209)

## URL Summary

| URL                          | Description          |
|------------------------------|----------------------|
| http://localhost:5173        | Frontend             |
| http://localhost:8000        | Backend              |
| http://localhost:8000/docs   | Interactive API docs |
| /dashboard                   | Semester overview    |
| /subjects                    | All subjects         |
| /subjects/:id                | Subject detail       |
| /topics/:id                  | Topic detail         |
| /audit                       | Curriculum audit     |

## Documentation

- [BRAIN.md](BRAIN.md) — Project state (read this first)
- [ARCHITECTURE.md](ARCHITECTURE.md) — System design
- [DATABASE.md](DATABASE.md) — Schema documentation
- [SETUP.md](SETUP.md) — Full setup guide
