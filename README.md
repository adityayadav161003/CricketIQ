# 🏏 CricketIQ — Decode Cricket Through Data

> **AI-powered SaaS cricket analytics platform** for IPL and International T20 matches.

[![Python](https://img.shields.io/badge/Python-3.11-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110-green)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-14-black)](https://nextjs.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue)](https://www.postgresql.org/)

---

## 📌 What Is CricketIQ?

CricketIQ transforms raw ball-by-ball cricket data from [Cricsheet](https://cricsheet.org/) into:

- **Player dashboards** — strike rate, phase performance, boundary %, scoring zones
- **Bowling insights** — economy trends, wicket zones, length distribution
- **Match analytics** — run rate progression, turning points, player impact score
- **AI predictions** — win probability, player form projections
- **Fantasy assistant** — optimal team recommendations

---

## 🗂 Project Structure

```
CricketIQ/
├── data/
│   ├── raw/          ← Downloaded Cricsheet JSON files
│   │   ├── ipl/
│   │   └── t20i/
│   └── processed/    ← Cleaned DataFrames ready for analytics
│       ├── ipl/
│       └── t20i/
├── data_pipeline/    ← Download + parse scripts
├── analytics_engine/ ← Batting / bowling metric modules
├── ml_models/        ← ML model templates
├── backend/          ← FastAPI application
│   ├── api/          ← Route handlers
│   ├── models/       ← Pydantic schemas
│   └── services/     ← Business logic
├── frontend/         ← Next.js dashboard (dark futuristic UI)
├── notebooks/        ← EDA and experimentation
└── assets/           ← Logos, images
```

---

## ⚡ Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 16

### Backend Setup

```bash
# Install Python dependencies
pip install -r requirements.txt

# Copy environment variables
cp .env.example .env
# → fill in DATABASE_URL, API keys, etc.

# Download datasets
python data_pipeline/download_data.py

# Parse matches into DataFrames
python data_pipeline/parse_matches.py

# Start API server
uvicorn backend.main:app --reload
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

---

## 🛠 Tech Stack

| Layer           | Technology                     |
|-----------------|--------------------------------|
| Backend         | Python + FastAPI               |
| Data Processing | Pandas + NumPy                 |
| Machine Learning| Scikit-learn + XGBoost         |
| Database        | PostgreSQL (Supabase)          |
| Frontend        | Next.js 14 + Tailwind CSS      |
| Charts          | Recharts                       |
| Deployment      | Vercel (frontend) + Render (API)|

---

## 📅 Development Phases

See [ROADMAP.md](./ROADMAP.md) for the full phased plan.

---

## 📊 Data Source

Ball-by-ball JSON data from [Cricsheet.org](https://cricsheet.org/downloads/).

Competitions covered:
- Indian Premier League (IPL)
- ICC Men's T20 International

---

## 📄 License

MIT License — built for portfolio and learning purposes.
