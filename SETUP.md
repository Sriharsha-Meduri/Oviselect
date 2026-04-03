# Oviselect — Setup Guide

## Prerequisites

| Tool | Version | Install |
|------|---------|---------|
| Node.js | ≥ 18 | https://nodejs.org |
| Python | ≥ 3.11 | https://python.org |
| Docker & Docker Compose | Latest | https://docs.docker.com/get-docker/ |
| Git | Any | https://git-scm.com |

---

## 1 · Frontend (Vite + React)

### Install dependencies
```bash
npm install
```

### Environment variables
Create a `.env` file in the project root:
```env
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-supabase-anon-key
VITE_GOOGLE_CLIENT_ID=your-google-oauth-client-id
```

> Get Supabase credentials from **Project Settings → API** in your Supabase dashboard.  
> Get the Google Client ID from **Google Cloud Console → APIs & Services → Credentials**.

### Run dev server
```bash
npm run dev
# App opens at http://localhost:5173
```

### Production build
```bash
npm run build      # outputs to dist/
npm run preview    # preview the production build locally
```

---

## 2 · Backend (FastAPI + PostgreSQL)

The backend is Dockerised. The easiest way to run it is with Docker Compose.

### Start everything (API + database)
```bash
docker-compose up --build
# API available at http://localhost:8000
# Docs at http://localhost:8000/docs
```

### Environment variables (backend)
Create `backend/.env` (or set these in your shell):
```env
DATABASE_URL=postgresql://oviguide:oviguide_secret@db:5432/oviguide
API_KEY=your-secret-api-key
ADMIN_PASSWORD=oviguide2026
```

> `DATABASE_URL` already defaults to the Docker Compose service name `db` — only change it if you're running Postgres externally.

### Run database migrations
```bash
cd backend
alembic upgrade head
```

### Run the API without Docker (local dev)
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

---

## 3 · College Data Scraper (`oviselect-cp-scraper`)

### Install Python dependencies
```bash
cd oviselect-cp-scraper
pip install -r requirements.txt
```

### Environment variables
Create `oviselect-cp-scraper/.env`:
```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your-supabase-service-role-key
```

> Use the **service role key** (not anon key) — the scraper needs write access.

### Run the full pipeline (dry run — writes JSON only, no DB)
```bash
cd oviselect-cp-scraper
python3 main.py --dry-run
```

### Write all 86 colleges to Supabase
```bash
python3 main.py
```

### Output
Structured JSON files are saved to `oviselect-cp-scraper/data/parsed/`.  
Coverage stats can be checked with:
```bash
python3 check_fields.py
```

---

## 4 · Troubleshooting

| Symptom | Likely cause | Fix |
|---------|-------------|-----|
| White / blank screen | Missing `.env` file | Create `.env` with the vars above |
| `VITE_SUPABASE_URL` undefined | `.env` not in project root | Move `.env` to the same folder as `package.json` |
| Google login not working | Wrong `VITE_GOOGLE_CLIENT_ID` | Add `http://localhost:5173` to Authorised JavaScript Origins in Google Cloud Console |
| Backend 500 errors | DB not running | Run `docker-compose up` first |
| Scraper SSL errors | Institute cert issues | Already handled — `verify=False` is set in fetch utils |
| `import.meta.env` TS error | Missing `vite/client` types | Already fixed in `tsconfig.json` |

