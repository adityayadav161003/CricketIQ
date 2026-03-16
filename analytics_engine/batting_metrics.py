"""
CricketIQ Analytics Engine — Batting Metrics.

Computes career and phase-split batting statistics from the ball-by-ball
deliveries dataset. Reads from data/processed/deliveries.parquet and writes
output to data/processed/batting_stats.parquet and batting_phase_stats.parquet.

Usage:
    python -m analytics_engine.batting_metrics
"""
import logging
from pathlib import Path

import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [batting] %(levelname)s — %(message)s",
)

PROJECT_ROOT = Path(__file__).parent.parent.resolve()
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
DELIVERIES_PATH = PROCESSED_DIR / "deliveries.parquet"


# ── I/O ───────────────────────────────────────────────────────────────────────

def load_deliveries(path: Path = DELIVERIES_PATH) -> pd.DataFrame:
    """Load the ball-by-ball deliveries parquet into a DataFrame."""
    if not path.exists():
        raise FileNotFoundError(
            f"Deliveries parquet not found at {path}. "
            "Run data_pipeline/parse_matches.py first."
        )
    logging.info(f"Loading deliveries from {path}...")
    df = pd.read_parquet(path)
    logging.info(f"  Loaded {len(df):,} delivery records.")
    return df


def save_parquet(df: pd.DataFrame, filename: str) -> None:
    """Save a DataFrame to the processed directory as parquet."""
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    out_path = PROCESSED_DIR / filename
    df.to_parquet(out_path, index=False)
    logging.info(f"  Saved {len(df):,} rows → {out_path.name}")


# ── Core Metrics ──────────────────────────────────────────────────────────────

def compute_career_batting(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute aggregated career batting statistics per batter.

    Wides are excluded from balls faced (they are not legal deliveries
    that the batter faces).

    Returns:
        DataFrame with one row per batter and the following columns:
        matches, innings, total_runs, balls_faced, strike_rate, average,
        fours, sixes, boundary_pct, dot_pct, not_outs
    """
    logging.info("Computing career batting statistics...")

    # Legal deliveries only (no wides)
    legal = df[df["extras_wides"] == 0].copy()

    agg = (
        legal
        .groupby("batter")
        .agg(
            matches=("cricsheet_id", "nunique"),
            total_runs=("runs_batter", "sum"),
            balls_faced=("runs_batter", "count"),
            fours=("is_boundary_4", "sum"),
            sixes=("is_boundary_6", "sum"),
            dot_balls=("is_dot_ball", "sum"),
            dismissals=("is_wicket", "sum"),
        )
        .reset_index()
    )

    # Innings = matches where batter appeared
    innings = (
        legal
        .drop_duplicates(subset=["batter", "cricsheet_id"])
        .groupby("batter")
        .size()
        .rename("innings")
        .reset_index()
    )
    agg = agg.merge(innings, on="batter", how="left")

    # Derived metrics
    agg["not_outs"] = agg["innings"] - agg["dismissals"]
    agg["strike_rate"] = (
        (agg["total_runs"] / agg["balls_faced"]) * 100
    ).round(2)
    agg["average"] = (
        agg["total_runs"] / agg["dismissals"].replace(0, float("nan"))
    ).round(2)
    agg["boundary_pct"] = (
        (agg["fours"] + agg["sixes"]) / agg["balls_faced"] * 100
    ).round(2)
    agg["dot_pct"] = (
        agg["dot_balls"] / agg["balls_faced"] * 100
    ).round(2)

    # Clean column order
    cols = [
        "batter", "matches", "innings", "total_runs", "balls_faced",
        "strike_rate", "average", "fours", "sixes",
        "boundary_pct", "dot_pct", "dismissals", "not_outs",
    ]
    agg = agg[cols].sort_values("total_runs", ascending=False)

    logging.info(f"  Career batting stats for {len(agg):,} batters computed.")
    return agg


def compute_phase_batting(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute batting statistics split by game phase (powerplay / middle / death).

    Returns:
        DataFrame with columns: batter, phase, + same stat columns as career.
    """
    logging.info("Computing phase-split batting statistics...")

    legal = df[df["extras_wides"] == 0].copy()

    agg = (
        legal
        .groupby(["batter", "phase"])
        .agg(
            total_runs=("runs_batter", "sum"),
            balls_faced=("runs_batter", "count"),
            fours=("is_boundary_4", "sum"),
            sixes=("is_boundary_6", "sum"),
            dot_balls=("is_dot_ball", "sum"),
            dismissals=("is_wicket", "sum"),
        )
        .reset_index()
    )

    agg["strike_rate"] = (
        (agg["total_runs"] / agg["balls_faced"]) * 100
    ).round(2)
    agg["boundary_pct"] = (
        (agg["fours"] + agg["sixes"]) / agg["balls_faced"] * 100
    ).round(2)
    agg["dot_pct"] = (
        agg["dot_balls"] / agg["balls_faced"] * 100
    ).round(2)

    logging.info(f"  Phase batting stats: {len(agg):,} batter×phase rows computed.")
    return agg


# ── Entry Point ───────────────────────────────────────────────────────────────

def run(deliveries_path: Path = DELIVERIES_PATH) -> None:
    """Full pipeline: load → compute → save."""
    df = load_deliveries(deliveries_path)

    career = compute_career_batting(df)
    save_parquet(career, "batting_stats.parquet")

    phase = compute_phase_batting(df)
    save_parquet(phase, "batting_phase_stats.parquet")

    logging.info("Batting analytics complete.")


if __name__ == "__main__":
    run()
