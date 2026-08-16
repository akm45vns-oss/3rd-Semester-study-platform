# 🚀 Semester OS — Cloud Deployment Guide (Free-Tier Production)

This guide walks you through deploying **Semester OS** to production using free-tier cloud platforms:
- **Backend API**: [Render](https://render.com) or [Railway](https://railway.app) (Python 3.11 + FastAPI)
- **Frontend App**: [Vercel](https://vercel.com) or [Netlify](https://netlify.com) (React + Vite SPA)
- **Database**: [Supabase](https://supabase.com) (Managed PostgreSQL) or Render SQLite

---

## 📋 Prerequisites

1. A free [GitHub](https://github.com) account.
2. A free [Render](https://render.com) or [Railway](https://railway.app) account for backend hosting.
3. A free [Vercel](https://vercel.com) or [Netlify](https://netlify.com) account for frontend hosting.
4. (Optional) A free [Supabase](https://supabase.com) account for cloud PostgreSQL.
5. (Optional) A free [Groq Cloud](https://console.groq.com) API key for AI study assistant.

---

## Step 1: Push Code to GitHub

Open PowerShell in the project root (`c:\Users\akm45\OneDrive\Desktop\3rd semester`):

```powershell
# 1. Initialize git repository
git init

# 2. Add all project files (.gitignore will exclude node_modules, temp files, etc.)
git add .

# 3. Commit the production build
git commit -m "Semester OS - Production Release with Complete Modern UI/UX"

# 4. Link your remote GitHub repository and push
# (Create a new private or public repo on github.com first)
git remote add origin https://github.com/<your-username>/<your-repo-name>.git
git branch -M main
git push -u origin main
```

---

## Step 2: Set Up Database (Supabase PostgreSQL)

1. Log into [Supabase Dashboard](https://supabase.com/dashboard) and click **New Project**.
2. Set your Project Name (e.g. `semester-os`) and generate a strong Database Password.
3. Go to **Project Settings &rarr; Database**.
4. Under **Connection string**, select **URI** (Transaction Mode / Direct).
5. Copy the connection string:
   ```text
   postgresql://postgres:[YOUR-PASSWORD]@db.xxxx.supabase.co:5432/postgres
   ```
   *(Note: Semester OS automatically encodes special characters in passwords and formats the URI for asyncpg).*

---

## Step 3: Deploy Backend on Render

1. Log in to [Render Dashboard](https://dashboard.render.com).
2. Click **New + &rarr; Web Service**.
3. Connect your GitHub repository.
4. Fill in the following settings:
   - **Name**: `semester-os-backend`
   - **Root Directory**: `backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 2`
5. Under **Advanced &rarr; Environment Variables**, add:
   | Variable | Value / Description |
   | :--- | :--- |
   | `DATABASE_URL` | Your Supabase connection string from Step 2 (or leave default for SQLite) |
   | `SECRET_KEY` | Click **Generate** (or any 64-character random string) |
   | `ALLOWED_ORIGINS` | `https://*.vercel.app,https://*.netlify.app,http://localhost:5173` |
   | `GROQ_API_KEY` | *(Optional)* Your Groq API key (starts with `gsk_...`) |
   | `AI_MODEL` | `llama-3.3-70b-versatile` |
   | `DEBUG` | `false` |
6. Click **Create Web Service**.
7. Once deployed, copy your backend URL (e.g. `https://semester-os-backend.onrender.com`).
8. Verify health status by visiting `https://semester-os-backend.onrender.com/health` in your browser.

> **Tip (Database Seeding)**:
> In Render dashboard, open the **Shell** tab of your backend service and run:
> ```bash
> python -m app.seed.seeder
> ```
> This seeds all 6 curriculum subjects, units, notes, practice questions, and coding challenges.

---

## Step 4: Deploy Frontend on Vercel

1. Log in to [Vercel Dashboard](https://vercel.com).
2. Click **Add New... &rarr; Project**.
3. Import your GitHub repository.
4. In the configuration screen:
   - **Framework Preset**: `Vite`
   - **Root Directory**: Click *Edit* and select `frontend`.
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
5. Expand **Environment Variables** and add:
   | Variable | Value |
   | :--- | :--- |
   | `VITE_API_URL` | `https://semester-os-backend.onrender.com` *(your Render backend URL)* |
6. Click **Deploy**.
7. Vercel will build and assign your live production URL (e.g. `https://semester-os.vercel.app`).

---

## Step 5: Final CORS Whitelist Check

Once Vercel assigns your live domain (e.g. `https://semester-os.vercel.app`):
1. Return to your **Render Backend &rarr; Environment**.
2. Ensure `ALLOWED_ORIGINS` contains your exact Vercel domain:
   ```text
   https://semester-os.vercel.app,https://*.vercel.app,http://localhost:5173
   ```
3. Save changes (Render will automatically redeploy with the updated CORS rule in 30 seconds).

---

## 🎉 Verification Checklist

- [ ] Open your Vercel URL: `https://semester-os.vercel.app`
- [ ] Register a new student user account or log in
- [ ] Browse Subjects & Topic Digital Textbooks
- [ ] Practice MCQs & Timed Tests
- [ ] Run code in the Online Coding Lab
- [ ] Attempt a Midterm / End-term Mock Examination
- [ ] Review mistakes in the Mistakes Notebook
