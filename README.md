# 🏏 CricketIQ — Decode Cricket Through Data

> **AI-powered SaaS cricket analytics platform** for IPL and International T20 matches.

[![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110-brightgreen?logo=fastapi)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-16-black?logo=next.js)](https://nextjs.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue?logo=postgresql)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker)](https://docs.docker.com/compose/)

---

## ✨ What is CricketIQ?

CricketIQ transforms raw ball-by-ball cricket data from [Cricsheet](https://cricsheet.org/) into production-quality analytics and dashboards.

| Feature | Description |
|---|---|
| 🏏 **Player Analytics** | Career stats, phase splits, strike rate, boundary %, dot % |
| 🎯 **Bowling Insights** | Economy, wickets, dot ball %, phase performance |
| 📈 **Match Analytics** | Over-by-over run rate, phase summaries, match results |
| 🤖 **AI Predictions** | Win probability, player performance forecasts *(Phase 8)* |
| 💡 **Fantasy Assistant** | Optimal team recommendations *(Phase 8)* |

---

## 🏗 System Architecture

```
Cricsheet.org
     │  JSON ball-by-ball data
     ▼
data_pipeline/
├── download_data.py    ← downloads & extracts ZIP
├── parse_matches.py    ← JSON → pandas DataFrame
└── load_to_db.py       ← DataFrame → PostgreSQL
     │
     ▼
data/processed/         ← Parquet files (fast I/O)
     │
     ├──► analytics_engine/
     │    ├── batting_metrics.py
     │    ├── bowling_metrics.py
     │    └── match_metrics.py
     │
     ▼
backend/api/            ← FastAPI (Python)
├── players.py          GET /api/v1/players
├── matches.py          GET /api/v1/matches
└── analytics.py        GET /api/v1/analytics/*
     │
     ▼
frontend/               ← Next.js 16 + Tailwind
├── app/page.tsx        ← Home dashboard
├── app/players/        ← Player cards
├── app/matches/        ← Match library
└── app/analytics/      ← Charts & leaderboards
```

---

## 🗂 Project Structure

```
CricketIQ/
├── data/
│   ├── raw/            ← Downloaded Cricsheet JSON files
│   └── processed/      ← Parquet analytics cache
├── data_pipeline/      ← Download, parse, load scripts
├── analytics_engine/   ← Batting, bowling, match metrics
├── ml_models/          ← ML model templates (Phase 8)
├── backend/
│   ├── api/            ← FastAPI routers + data loader
│   ├── models/         ← SQLAlchemy ORM models
│   └── services/       ← DB session config
├── database/
│   ├── init.sql        ← PostgreSQL DDL
│   └── init_db.py      ← Table creation script
├── frontend/           ← Next.js dashboard
├── docker-compose.yml
├── requirements.txt
└── ROADMAP.md
```

---

## ⚡ Quick Start (Local)

### Prerequisites
- Python 3.11+
- Node.js 20+
- PostgreSQL 16 (or use Docker)

### 1 — Clone & configure

```bash
git clone https://github.com/yourusername/CricketIQ.git
cd CricketIQ

# Python environment
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Environment variables
cp backend/.env.example backend/.env
# Edit backend/.env — fill in DATABASE_URL
```

### 2 — Download & process data

```bash
# Download Cricsheet datasets (~500 MB)
python data_pipeline/download_data.py

# Parse JSON → DataFrames & save as Parquet
python data_pipeline/parse_matches.py

# Compute analytics metrics
python analytics_engine/batting_metrics.py
python analytics_engine/bowling_metrics.py
python analytics_engine/match_metrics.py
```

### 3 — Start the backend

```bash
uvicorn backend.api.main:app --reload
# → http://localhost:8000
# → http://localhost:8000/docs  (Swagger UI)
```

### 4 — Start the frontend

```bash
cd frontend
cp .env.local.example .env.local
npm install
npm run dev
# → http://localhost:3000
```

---

## 🐳 Docker (Full Stack)

Run the complete stack with a single command:

```bash
docker compose up --build
```

| Service | URL |
|---|---|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| API Docs | http://localhost:8000/docs |
| PostgreSQL | localhost:5432 |

> **Note:** The database is initialized from `database/init.sql` automatically on first run.

---

## 🚀 Deployment

### Backend → Render / Railway / Fly.io

1. Set environment variables (see `backend/.env.example`)
2. Set build command: `pip install -r requirements.txt`
3. Set start command: `sh backend/start.sh`

### Frontend → Vercel

1. Import repo into Vercel
2. Set environment variable:
   ```
   NEXT_PUBLIC_API_BASE_URL=https://your-backend.onrender.com/api/v1
   ```
3. Deploy — Vercel auto-detects Next.js

### Database → Supabase

1. Create a Supabase project
2. Run `database/init.sql` in the Supabase SQL editor
3. Update `DATABASE_URL` and `DATABASE_URL_SYNC` in backend env vars

---

## 📡 API Reference

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/v1/players` | Paginated player list |
| GET | `/api/v1/players/{name}` | Player batting + bowling profile |
| GET | `/api/v1/players/{name}/phase` | Phase-split batting stats |
| GET | `/api/v1/matches` | Paginated match list (filter by season/team) |
| GET | `/api/v1/matches/{id}` | Match detail + phase summary |
| GET | `/api/v1/matches/{id}/overs` | Over-by-over run rate |
| GET | `/api/v1/analytics/batting-leaders` | Top run scorers |
| GET | `/api/v1/analytics/bowling-leaders` | Top wicket takers |
| GET | `/api/v1/analytics/phase-batting` | Phase batting leaderboard |
| GET | `/api/v1/analytics/phase-bowling` | Phase bowling leaderboard |
| GET | `/api/v1/analytics/run-rate-progression` | Avg run rate per over |
| GET | `/health` | API health + dataset row counts |

Full interactive docs available at `/docs` when the backend is running.

---

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| Data Processing | Python · Pandas · NumPy · PyArrow |
| Machine Learning | Scikit-learn · XGBoost *(Phase 8)* |
| Backend | FastAPI · SQLAlchemy 2.x · Pydantic v2 |
| Database | PostgreSQL 16 (Supabase) |
| Frontend | Next.js 16 · Tailwind CSS · Recharts · Framer Motion |
| Deployment | Vercel · Render · Docker Compose |

---

## 📅 Roadmap

| Phase | Status | Description |
|---|---|---|
| 1 — Architecture | ✅ | Folder structure, README, ROADMAP |
| 2 — Database | ✅ | PostgreSQL schema + SQLAlchemy ORM |
| 3 — Data Pipeline | ✅ | Download, parse, load to DB |
| 4 — Analytics Engine | ✅ | Batting, bowling, match metrics |
| 5 — Backend API | ✅ | FastAPI with 11 endpoints |
| 6 — Frontend | ✅ | Next.js dark dashboard |
| 7 — Deployment | ✅ | Docker, env config, deployment guides |
| 8 — ML Models | ⬜ | Win probability, fantasy predictions |

---

## 📊 Data Source

Ball-by-ball JSON from [Cricsheet.org](https://cricsheet.org/downloads/).

Competitions: **IPL** · **ICC Men's T20I** · expandable to BBL, PSL, SA20.

---

## 📄 License

MIT License — built as a portfolio and learning project.
