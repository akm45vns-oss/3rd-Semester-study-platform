# Setup & Installation Guide — Semester OS

## 1. Prerequisites

- **Python 3.11** (located at `C:\Users\akm45\AppData\Local\Programs\Python\Python311\python.exe` or standard python in PATH)
- **Node.js (v18+)** and **npm**

---

## 2. Quick One-Click Startup (Windows)

Simply run:
```powershell
.\start.ps1
```
or double-click `start.bat`.

This automatically launches the FastAPI Backend (Port 8000), Vite Frontend (Port 5173), and opens the app in your default browser.

---

## 3. Database Seeding

### Option A: Standard Curriculum Seeding (Instant, Offline)
Populates all 5 subjects, 30 units, all topics, baseline question bank, and coding challenges:
```powershell
cd backend
& "C:\Users\akm45\AppData\Local\Programs\Python\Python311\python.exe" -m app.seed.seeder
```

### Option B: AI-Powered Deep Curriculum Seeding (Using Groq API)
Generates comprehensive academic notes, high-rigor multi-choice & debugging questions, and practical coding exercises:

1. Obtain a free Groq API key from **[https://console.groq.com/keys](https://console.groq.com/keys)**
2. Seed the database using any of these commands:

```powershell
cd backend

# Seed ALL 5 subjects with comprehensive notes & questions
& "C:\Users\akm45\AppData\Local\Programs\Python\Python311\python.exe" -m app.seed.ai_seeder --api-key "YOUR_GROQ_KEY" --all

# Seed a specific subject (e.g. Java Programming)
& "C:\Users\akm45\AppData\Local\Programs\Python\Python311\python.exe" -m app.seed.ai_seeder --api-key "YOUR_GROQ_KEY" --subject CAP392

# Seed a specific unit (e.g. DBMS Unit 1)
& "C:\Users\akm45\AppData\Local\Programs\Python\Python311\python.exe" -m app.seed.ai_seeder --api-key "YOUR_GROQ_KEY" --subject CAP206 --unit 1
```

> **Tip**: You can also save `GROQ_API_KEY=gsk_...` in `backend/.env` or configure it directly in the web UI via the **"⚡ AI Study Config"** button in the sidebar.

---

## 4. Manual Step-by-Step Server Launch

### Step 1: Start Backend
```powershell
cd backend
& "C:\Users\akm45\AppData\Local\Programs\Python\Python311\python.exe" -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Step 2: Start Frontend
```powershell
cd frontend
npm run dev
```

---

## 5. Default URLs

| Service | URL |
|---------|-----|
| Web App | `http://localhost:5173` |
| REST API | `http://localhost:8000` |
| Swagger Docs | `http://localhost:8000/docs` |
| Curriculum Audit | `http://localhost:5173/audit` |
