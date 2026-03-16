"""
CricketIQ — Shared data loader for the FastAPI layer.

Loads processed parquet files once at startup and caches them in memory.
All routers import from this module to avoid redundant I/O.
"""
import logging
from functools import lru_cache
from pathlib import Path

import pandas as pd

logger = logging.getLogger("cricketiq.data")

PROJECT_ROOT = Path(__file__).parent.parent.parent.resolve()
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"


def _load(filename: str) -> pd.DataFrame:
    """Load a single parquet file. Returns an empty DataFrame if missing."""
    path = PROCESSED_DIR / filename
    if not path.exists():
        logger.warning(f"Parquet not found: {path}. Returning empty DataFrame.")
        return pd.DataFrame()
    df = pd.read_parquet(path)
    logger.info(f"Loaded {filename}: {len(df):,} rows")
    return df


# ── Cached loaders (called once per process lifetime) ────────────────────────

@lru_cache(maxsize=1)
def batting_stats() -> pd.DataFrame:
    return _load("batting_stats.parquet")

@lru_cache(maxsize=1)
def batting_phase_stats() -> pd.DataFrame:
    return _load("batting_phase_stats.parquet")

@lru_cache(maxsize=1)
def bowling_stats() -> pd.DataFrame:
    return _load("bowling_stats.parquet")

@lru_cache(maxsize=1)
def bowling_phase_stats() -> pd.DataFrame:
    return _load("bowling_phase_stats.parquet")

@lru_cache(maxsize=1)
def match_summary() -> pd.DataFrame:
    return _load("match_summary.parquet")

@lru_cache(maxsize=1)
def match_stats() -> pd.DataFrame:
    return _load("match_stats.parquet")

@lru_cache(maxsize=1)
def over_progression() -> pd.DataFrame:
    return _load("over_progression.parquet")


def safe_json(df: pd.DataFrame) -> list[dict]:
    """
    Convert a DataFrame to a JSON-serialisable list of dicts.
    Replaces NaN / NaT / inf with None so FastAPI can serialise cleanly.
    """
    return (
        df
        .where(df.notna(), other=None)
        .replace([float("inf"), float("-inf")], None)
        .to_dict(orient="records")
    )
