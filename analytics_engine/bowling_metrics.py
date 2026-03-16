"""
CricketIQ Analytics Engine — Bowling Metrics.

Computes career and phase-split bowling statistics from the ball-by-ball
deliveries dataset. Reads from data/processed/deliveries.parquet and writes
output to data/processed/bowling_stats.parquet and bowling_phase_stats.parquet.

Usage:
    python -m analytics_engine.bowling_metrics
"""
import logging
from pathlib import Path

import numpy as np
import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [bowling] %(levelname)s — %(message)s",
)

PROJECT_ROOT = Path(__file__).parent.parent.resolve()
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
DELIVERIES_PATH = PROCESSED_DIR / "deliveries.csv"


# ── I/O ───────────────────────────────────────────────────────────────────────

def load_deliveries(path: Path = DELIVERIES_PATH) -> pd.DataFrame:
    """Load the ball-by-ball deliveries parquet into a DataFrame."""
    if not path.exists():
        raise FileNotFoundError(
            f"Deliveries parquet not found at {path}. "
            "Run data_pipeline/parse_matches.py first."
        )
    logging.info(f"Loading deliveries from {path}...")
    df = pd.read_csv(path)
    logging.info(f"  Loaded {len(df):,} delivery records.")
    return df


def save_parquet(df: pd.DataFrame, filename: str) -> None:
    """Save a DataFrame to the processed directory as parquet."""
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    out_path = PROCESSED_DIR / filename
    df.to_csv(out_path, index=False)
    logging.info(f"  Saved {len(df):,} rows → {out_path.name}")


# ── Core Metrics ──────────────────────────────────────────────────────────────

def compute_career_bowling(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute aggregated career bowling statistics per bowler.

    Notes:
    - Wides and no-balls are INCLUDED in runs conceded.
    - Only legal balls (no wides, no no-balls) count toward balls_bowled
      for economy and dot ball calculations — consistent with Duckworth–Lewis.
    - Economy = (runs_conceded / balls_bowled) * 6.

    Returns:
        DataFrame with one row per bowler and columns:
        matches, balls_bowled, overs, runs_conceded, wickets,
        economy, average, dot_pct, boundary_pct.
    """
    logging.info("Computing career bowling statistics...")

    # All deliveries contribute to runs conceded
    all_del = df.copy()

    runs_agg = (
        all_del
        .groupby("bowler")
        .agg(
            matches=("cricsheet_id", "nunique"),
            runs_conceded=("runs_total", "sum"),
            wickets=("is_wicket", "sum"),
        )
        .reset_index()
    )

    # Legal balls for economy / dot / boundary calculations
    legal = df[(df["extras_wides"] == 0) & (df["extras_noballs"] == 0)].copy()

    legal_agg = (
        legal
        .groupby("bowler")
        .agg(
            balls_bowled=("runs_batter", "count"),
            dot_balls=("is_dot_ball", "sum"),
            fours_conceded=("is_boundary_4", "sum"),
            sixes_conceded=("is_boundary_6", "sum"),
        )
        .reset_index()
    )

    agg = runs_agg.merge(legal_agg, on="bowler", how="left")

    # Derived metrics
    agg["overs"] = (agg["balls_bowled"] / 6).round(1)
    agg["economy"] = (
        (agg["runs_conceded"] / agg["balls_bowled"]) * 6
    ).round(2)
    agg["average"] = (
        agg["runs_conceded"] / agg["wickets"].replace(0, np.nan)
    ).round(2)
    agg["strike_rate"] = (
        agg["balls_bowled"] / agg["wickets"].replace(0, np.nan)
    ).round(2)
    agg["dot_pct"] = (
        agg["dot_balls"] / agg["balls_bowled"] * 100
    ).round(2)
    agg["boundary_pct"] = (
        (agg["fours_conceded"] + agg["sixes_conceded"]) / agg["balls_bowled"] * 100
    ).round(2)

    cols = [
        "bowler", "matches", "balls_bowled", "overs", "runs_conceded",
        "wickets", "economy", "average", "strike_rate",
        "dot_pct", "boundary_pct",
    ]
    agg = agg[cols].sort_values("wickets", ascending=False)

    logging.info(f"  Career bowling stats for {len(agg):,} bowlers computed.")
    return agg


def compute_phase_bowling(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute bowling statistics split by game phase (powerplay / middle / death).

    Returns:
        DataFrame with columns: bowler, phase, + same stat columns as career.
    """
    logging.info("Computing phase-split bowling statistics...")

    legal = df[(df["extras_wides"] == 0) & (df["extras_noballs"] == 0)].copy()

    agg = (
        legal
        .groupby(["bowler", "phase"])
        .agg(
            balls_bowled=("runs_batter", "count"),
            runs_conceded=("runs_total", "sum"),
            wickets=("is_wicket", "sum"),
            dot_balls=("is_dot_ball", "sum"),
            fours_conceded=("is_boundary_4", "sum"),
            sixes_conceded=("is_boundary_6", "sum"),
        )
        .reset_index()
    )

    agg["overs"] = (agg["balls_bowled"] / 6).round(1)
    agg["economy"] = (
        (agg["runs_conceded"] / agg["balls_bowled"]) * 6
    ).round(2)
    agg["dot_pct"] = (
        agg["dot_balls"] / agg["balls_bowled"] * 100
    ).round(2)
    agg["boundary_pct"] = (
        (agg["fours_conceded"] + agg["sixes_conceded"]) / agg["balls_bowled"] * 100
    ).round(2)

    logging.info(f"  Phase bowling stats: {len(agg):,} bowler×phase rows computed.")
    return agg


# ── Entry Point ───────────────────────────────────────────────────────────────

def run(deliveries_path: Path = DELIVERIES_PATH) -> None:
    """Full pipeline: load → compute → save."""
    df = load_deliveries(deliveries_path)

    career = compute_career_bowling(df)
    save_parquet(career, "bowling_stats.csv")

    phase = compute_phase_bowling(df)
    save_parquet(phase, "bowling_phase_stats.csv")

    logging.info("Bowling analytics complete.")


if __name__ == "__main__":
    run()
