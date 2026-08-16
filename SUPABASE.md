# Supabase Integration & Production Deployment Guide — Semester OS

This guide explains how to store all Semester OS data in **Supabase PostgreSQL** and deploy the project to production.

---

## 1. Quick Setup: Connect Supabase to Semester OS

### Step A: Create a Free Supabase Project
1. Go to **[https://supabase.com](https://supabase.com)** and sign in / create an account.
2. Click **"New Project"**.
3. Choose a project name (e.g. `semester-os`) and set a strong database password.
4. Select the region closest to you.

---

### Step B: Copy Your Connection String
1. In your Supabase Project Dashboard, navigate to:
   **Project Settings** (⚙️ bottom left) ➔ **Database**.
2. Scroll down to **Connection string** ➔ select **URI** (or **Nodejs/Python**).
3. Select **Mode: Transaction** (Port 6543) or **Session** (Port 5432).
4. Copy the connection string. It looks like:
   ```
   postgresql://postgres.[PROJECT-REF]:[YOUR-PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres
   ```
   *(Replace `[YOUR-PASSWORD]` with your actual database password).*

---

### Step C: Migrate All Local Data into Supabase
Run the automatic migration script. This script automatically creates all 22 tables in Supabase and migrates your entire dataset (curriculum, AI notes, questions, coding challenges, user progress):

```powershell
cd "c:\Users\akm45\OneDrive\Desktop\3rd semester\backend"

& "C:\Users\akm45\AppData\Local\Programs\Python\Python311\python.exe" -m app.seed.migrate_to_supabase --supabase-url "YOUR_SUPABASE_URI_HERE"
```

---

### Step D: Switch Backend to Use Supabase Permanently
Open `backend/.env` and update `DATABASE_URL`:

```env
DATABASE_URL=postgresql+asyncpg://postgres.[PROJECT-REF]:[YOUR-PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres
```

> **Note**: If you paste `postgresql://...` or `postgres://...`, Semester OS automatically normalizes it to `postgresql+asyncpg://` and enables connection pooling and SSL health checks automatically.

---

## 2. Production Deployment Options

### Option 1: Docker Compose (Unified Containerization)
To run the full-stack app in production with optimized Nginx and multi-worker FastAPI:

```bash
# 1. Start all containers
docker-compose up -d --build

# 2. Access the production application
# Frontend: http://localhost:80
# Backend API: http://localhost:8000
```

---

### Option 2: Cloud Deployment (Vercel / Render / Railway)

#### Backend on Render / Railway:
1. Connect your repository to **Render** or **Railway**.
2. Build Command: `pip install -r requirements.txt`
3. Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 2`
4. Set Environment Variables:
   - `DATABASE_URL`: Your Supabase connection string
   - `SECRET_KEY`: A secure random secret string
   - `GROQ_API_KEY`: Your Groq API key
   - `ALLOWED_ORIGINS`: `["https://your-frontend-domain.vercel.app"]`

#### Frontend on Vercel:
1. Import `frontend` directory into **Vercel**.
2. Framework Preset: **Vite**.
3. Build Command: `npm run build`
4. Output Directory: `dist`
5. Configure reverse proxy / environment variable for API endpoints.

---

## 3. Verifying Production Readiness

| Component | Status | Details |
|---|---|---|
| **Database** | ✅ **PostgreSQL / Supabase** | 22 relational tables with connection pooling & SSL |
| **Data Migration** | ✅ **One-Click Script** | `migrate_to_supabase.py` with sequence synchronization |
| **Authentication** | ✅ **JWT + Salted Bcrypt** | Secure user sessions with persistent storage |
| **AI Study Engine** | ✅ **Groq 5-Key Pool** | High-speed generation with auto load-balancing & failover |
| **Frontend** | ✅ **Production Optimized** | Zero TypeScript errors, Tailwind dark theme, responsive SPA |
| **Docker** | ✅ **Multi-Stage Builds** | Nginx Alpine web server + Python 3.11 slim backend |
