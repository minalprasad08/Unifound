# UniFound: Cloud Production Deployment Guide (Render & Vercel)

This guide provides step-by-step instructions for deploying UniFound live to free cloud hosting to obtain public URLs for both the backend API and frontend application.

---

## 🏗️ Architecture Overview

```text
[ Browser / Client ]
        │
        ▼ (HTTPS)
[ Vercel CDN ] ───► React + Vite SPA (dist/)
        │
        ▼ (HTTPS /api/v1/*)
[ Render Cloud ] ───► FastAPI ASGI Server (uvicorn/gunicorn)
        │
        ▼ (Internal TCP)
[ Render Managed PostgreSQL ] (SQLAlchemy 2.0 + Alembic DDL)
```

---

## 📦 Ready-Made Deployment Configurations in Codebase

1. **Backend Blueprint (`render.yaml`)**:
   - Automatically provisions a free PostgreSQL database (`unifound-db`).
   - Automatically builds the Python 3.11 environment, executes migrations (`alembic upgrade head`), and starts Uvicorn.
2. **Backend Procfile (`backend/Procfile`)**:
   - Fallback startup entry point for standard PaaS runtime.
3. **Frontend Routing (`frontend/vercel.json`)**:
   - SPA route rewrites configured to prevent 404s on browser reloads.
4. **CORS Middleware (`backend/app/main.py`)**:
   - Automatically permits all `https://*.vercel.app` production and preview domains.

---

## 🚀 Step 1: Push Project to GitHub

Both Render and Vercel automatically deploy from your GitHub repository.

### If Git is not yet installed on Windows:
Open PowerShell and run:
```powershell
winget install --id Git.Git -e --source winget
```
*(Restart terminal after installation).*

### Initialize Git & Push to GitHub:
```powershell
cd "c:\Users\MINAL PRASAD\OneDrive\Desktop\Unifound"

# Initialize git repository
git init

# Add all files (secrets & DBs are already protected in .gitignore)
git add .

# Initial commit
git commit -m "feat: complete production cloud deployment configuration"

# Rename branch to main
git branch -M main

# Link to your GitHub repo (create an empty repo on github.com first)
git remote add origin https://github.com/<YOUR_GITHUB_USERNAME>/unifound.git

# Push
git push -u origin main
```

---

## 🌐 Step 2: Deploy Backend & PostgreSQL on Render (Free)

1. Go to [https://dashboard.render.com/](https://dashboard.render.com/) and sign in with GitHub.
2. Click **New +** in the top navigation and select **Blueprint**.
3. Select your GitHub **`unifound`** repository.
4. Render will detect [`render.yaml`](render.yaml) automatically:
   - **Service 1:** `unifound-api` (Web Service on Python 3.11)
   - **Service 2:** `unifound-db` (Free PostgreSQL instance)
5. Click **Apply**.
6. Render will provision the database, run Alembic migrations, and launch your API.
7. Note down your backend URL (e.g., `https://unifound-api.onrender.com`).
   - Verify health: `https://unifound-api.onrender.com/health`
   - View Swagger API Docs: `https://unifound-api.onrender.com/docs`

---

## ⚡ Step 3: Deploy Frontend on Vercel (Free)

You have two fast ways to deploy the frontend:

### Method A: Via Vercel Web Dashboard (Recommended)
1. Go to [https://vercel.com/](https://vercel.com/) and sign in with GitHub.
2. Click **Add New...** $\to$ **Project**.
3. Select your **`unifound`** repository and click **Import**.
4. In the Project Configuration:
   - **Framework Preset:** `Vite`
   - **Root Directory:** Click Edit and select `frontend`
   - **Build Command:** `npm run build`
   - **Output Directory:** `dist`
5. Expand **Environment Variables** and add:
   - **Name:** `VITE_API_BASE_URL`
   - **Value:** `https://<YOUR_RENDER_BACKEND_URL>/api/v1` *(e.g., `https://unifound-api.onrender.com/api/v1`)*
6. Click **Deploy**.
7. In ~30 seconds, Vercel will give you a live production URL (e.g., `https://unifound.vercel.app`)!

---

### Method B: Direct CLI Deployment (Without Web Dashboard)
In your terminal, run:
```powershell
cd "c:\Users\MINAL PRASAD\OneDrive\Desktop\Unifound\frontend"
npx vercel
```
- Follow the interactive prompts (log in with email or GitHub).
- When prompted for settings:
  - Link to existing project: **No**
  - Project name: **unifound**
  - Directory located: **./**
- To set the production backend URL:
  ```powershell
  npx vercel env add VITE_API_BASE_URL production
  ```
  *(Enter your Render backend URL: `https://<YOUR_RENDER_BACKEND_URL>/api/v1`)*
- Deploy to production:
  ```powershell
  npx vercel --prod
  ```

---

## ✅ Step 4: Live Verification Checklist

Once both services are deployed:
- [ ] Open your Vercel URL in the browser (`https://unifound.vercel.app`).
- [ ] Verify that the footer shows **API: Healthy & Connected**.
- [ ] Register a new test campus user.
- [ ] Test reporting a lost or found item.
- [ ] Verify search & claims workflow.
