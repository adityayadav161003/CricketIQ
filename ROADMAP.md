# CricketIQ — Development Roadmap

> Build status: **Phase 1 — Architecture ✅**

---

## Overview

CricketIQ is built in 8 structured phases. Each phase produces clear, verifiable deliverables before moving to the next.

---

## Phase 1 — Project Architecture ✅
**Goal**: Establish project scaffold and development plan.

Deliverables:
- [x] Complete folder structure (`data/`, `data_pipeline/`, `analytics_engine/`, `ml_models/`, `backend/`, `frontend/`, `notebooks/`)
- [x] Python package stubs (`__init__.py` in every module)
- [x] `README.md` with quickstart guide
- [x] `requirements.txt` with all dependencies
- [x] `.env.example` template

---

## Phase 2 — Database Design ⬜
**Goal**: Design and initialize PostgreSQL schema.

Tables:
- `competitions` — IPL, T20I metadata
- `teams` — all franchise/national teams
- `players` — player profiles keyed by Cricsheet ID
- `matches` — match-level metadata
- `deliveries` — ball-by-ball records (core table)
- `player_stats` — aggregated per-match stats

Deliverables:
- [ ] `backend/models/schemas.py` — Pydantic models
- [ ] `database/init.sql` — DDL script
- [ ] `database/seed.py` — seed helper

---

## Phase 3 — Data Pipeline ⬜
**Goal**: Automate dataset download and storage.

Deliverables:
- [ ] `data_pipeline/download_data.py` — download + extract `all_json.zip` from Cricsheet
- [ ] Organize JSON files into `data/raw/ipl/` and `data/raw/t20i/`
- [ ] Validate counts and directory structure

---

## Phase 4 — Match Parser ⬜
**Goal**: Convert raw JSON files into structured ball-by-ball DataFrames.

Deliverables:
- [ ] `data_pipeline/parse_matches.py` — scalable JSON→DataFrame parser
- [ ] Output columns: `match_id`, `over`, `ball`, `batsman`, `bowler`, `runs`, `extras`, `dismissal`, `innings`, `phase`
- [ ] `notebooks/01_explore_match.ipynb` — EDA companion notebook
- [ ] Save processed Parquet files to `data/processed/`

---

## Phase 5 — Analytics Engine ⬜
**Goal**: Compute core cricket statistics from parsed data.

Deliverables:
- [ ] `analytics_engine/batting_metrics.py`
  - total runs, strike rate, boundary %, dot %, phase splits
- [ ] `analytics_engine/bowling_metrics.py`
  - economy rate, wickets, dot %, phase splits, length distribution
- [ ] Unit tests for core metrics

---

## Phase 6 — Machine Learning Models ⬜
**Goal**: Build predictive models for match outcomes and player performance.

Models:
| Model | Algorithm | Target |
|---|---|---|
| Match Win Probability | XGBoost Classifier | P(win) at any point |
| Player Performance | XGBoost Regressor | Expected runs/wickets |
| Fantasy Points | Gradient Boosted Trees | DreamTeam fantasy score |

Deliverables:
- [ ] `ml_models/match_prediction.py`
- [ ] `ml_models/player_performance.py`
- [ ] `ml_models/fantasy_points.py`
- [ ] Model training notebooks in `notebooks/`

---

## Phase 7 — Backend API ⬜
**Goal**: Expose analytics and predictions via FastAPI.

Key Endpoints:
```
GET  /players              → list all players
GET  /player/{id}          → player profile
GET  /player-analytics     → batting/bowling stats
GET  /match/{id}           → match metadata
GET  /match-analysis/{id}  → run rate, turning points, impact scores
GET  /predictions          → AI win probability
GET  /fantasy              → fantasy team recommendations
```

Deliverables:
- [ ] `backend/main.py` — FastAPI app
- [ ] `backend/api/players.py`
- [ ] `backend/api/matches.py`
- [ ] `backend/api/predictions.py`
- [ ] PostgreSQL integration with SQLAlchemy

---

## Phase 8 — Frontend Dashboard ⬜
**Goal**: Ship a dark futuristic Next.js dashboard.

Pages:
| Page | Route | Key Feature |
|---|---|---|
| Homepage | `/` | Hero + live stats ticker |
| Player Analytics | `/player/[id]` | Stat cards, Recharts graphs |
| Match Insights | `/match/[id]` | Run rate chart, turning points |
| AI Predictions | `/predictions` | Win probability gauge |
| Fantasy Assistant | `/fantasy` | Optimal team picker |

Deliverables:
- [ ] Next.js 14 app (App Router)
- [ ] Dark theme design system in Tailwind
- [ ] Recharts integration for all data visualizations
- [ ] Deployed to Vercel

---

## Deployment Targets

| Component | Platform | Status |
|---|---|---|
| Frontend | Vercel | ⬜ |
| Backend API | Render | ⬜ |
| Database | Supabase (PostgreSQL) | ⬜ |

---

## Timeline Estimate

| Phase | Estimated Effort |
|---|---|
| 1 — Architecture | 0.5 day ✅ |
| 2 — Database Design | 0.5 day |
| 3 — Data Pipeline | 1 day |
| 4 — Match Parser | 1 day |
| 5 — Analytics Engine | 2 days |
| 6 — ML Models | 3 days |
| 7 — Backend API | 2 days |
| 8 — Frontend | 3 days |
| **Total** | **~13 days** |
