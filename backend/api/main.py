"""
CricketIQ — FastAPI Application Entry Point.

Run with:
    uvicorn backend.api.main:app --reload

API root: http://localhost:8000
Docs:    http://localhost:8000/docs
"""
import logging
import os
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.players import router as players_router
from backend.api.matches import router as matches_router
from backend.api.analytics import router as analytics_router

# Pre-warm all parquet caches on startup
from backend.api import data_loader as _dl

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s — %(message)s",
)
logger = logging.getLogger("cricketiq.main")

# ── CORS origins ─────────────────────────────────────────────────────────────
_cors_raw = os.getenv("CORS_ORIGINS", "http://localhost:3000")
CORS_ORIGINS: list[str] = [o.strip() for o in _cors_raw.split(",")]


# ── Startup / Shutdown ────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Pre-load all parquet files into memory at startup."""
    logger.info("CricketIQ API starting — warming data cache...")
    try:
        _dl.batting_stats()
        _dl.batting_phase_stats()
        _dl.bowling_stats()
        _dl.bowling_phase_stats()
        _dl.match_summary()
        _dl.match_stats()
        _dl.over_progression()
        logger.info("Data cache warm — API ready.")
    except Exception as exc:
        logger.warning(f"Cache warm-up warning: {exc}")
    yield
    logger.info("CricketIQ API shutting down.")


# ── Application ───────────────────────────────────────────────────────────────

app = FastAPI(
    title="CricketIQ API",
    description=(
        "AI-powered cricket analytics platform. "
        "Serves ball-by-ball IPL and T20I insights, "
        "player profiles, bowling metrics, and match analytics."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ── CORS ──────────────────────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────

API_PREFIX = "/api/v1"

app.include_router(players_router,  prefix=API_PREFIX)
app.include_router(matches_router,  prefix=API_PREFIX)
app.include_router(analytics_router, prefix=API_PREFIX)


# ── Root & Health ─────────────────────────────────────────────────────────────

@app.get("/", tags=["Root"])
def root() -> dict[str, str]:
    """API root — returns version info."""
    return {
        "name": "CricketIQ API",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "running",
    }


@app.get("/health", tags=["Root"])
def health_check() -> dict[str, Any]:
    """
    Health check endpoint.
    Reports whether each parquet dataset has been loaded successfully.
    """
    bat = _dl.batting_stats()
    bowl = _dl.bowling_stats()
    match_sum = _dl.match_summary()

    return {
        "status": "healthy",
        "data": {
            "batting_stats_rows": len(bat),
            "bowling_stats_rows": len(bowl),
            "match_summary_rows": len(match_sum),
            "data_available": not bat.empty,
        },
    }
