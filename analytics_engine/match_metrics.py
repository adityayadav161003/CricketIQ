"""
CricketIQ Analytics Engine — Match Metrics.

Computes match-level analytics including phase scoring, run rate progression
per over, and partnership data from the ball-by-ball deliveries dataset.

Inputs:
    data/processed/deliveries.parquet
    data/processed/matches.parquet

Outputs:
    data/processed/match_stats.parquet        — per-match phase summary
    data/processed/over_progression.parquet   — over-by-over run rate (all matches)

Usage:
    python -m analytics_engine.match_metrics
"""
import logging
from pathlib import Path
from typing import Optional

import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [match] %(levelname)s — %(message)s",
)

PROJECT_ROOT = Path(__file__).parent.parent.resolve()
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
DELIVERIES_PATH = PROCESSED_DIR / "deliveries.csv"
MATCHES_PATH = PROCESSED_DIR / "matches.csv"


# ── I/O ───────────────────────────────────────────────────────────────────────

def load_data(
    deliveries_path: Path = DELIVERIES_PATH,
    matches_path: Path = MATCHES_PATH,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Load deliveries and matches parquets."""
    for p in (deliveries_path, matches_path):
        if not p.exists():
            raise FileNotFoundError(
                f"Required parquet not found: {p}. "
                "Run data_pipeline/parse_matches.py first."
            )

    logging.info("Loading deliveries and matches...")
    deliveries = pd.read_csv(deliveries_path)
    matches = pd.read_csv(matches_path)
    logging.info(
        f"  Deliveries: {len(deliveries):,} rows | Matches: {len(matches):,} rows"
    )
    return deliveries, matches


def save_parquet(df: pd.DataFrame, filename: str) -> None:
    """Save a DataFrame to the processed directory as parquet."""
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    out_path = PROCESSED_DIR / filename
    df.to_csv(out_path, index=False)
    logging.info(f"  Saved {len(df):,} rows → {out_path.name}")


# ── Phase Summary Per Match ───────────────────────────────────────────────────

def compute_match_phase_stats(deliveries: pd.DataFrame) -> pd.DataFrame:
    """
    Compute per-match, per-innings, per-phase scoring summary.

    For each combination of (match, innings, phase) returns:
        runs  — total runs scored
        balls — legal balls faced
        wickets — wickets fallen
        run_rate — (runs / balls) * 6
        boundary_count — fours + sixes

    Returns:
        DataFrame with cols: cricsheet_id, innings, phase, runs, balls,
        wickets, run_rate, boundary_count.
    """
    logging.info("Computing match phase stats...")

    legal = deliveries[deliveries["extras_wides"] == 0].copy()

    agg = (
        legal
        .groupby(["cricsheet_id", "innings", "phase"])
        .agg(
            runs=("runs_total", "sum"),
            balls=("runs_total", "count"),
            wickets=("is_wicket", "sum"),
            fours=("is_boundary_4", "sum"),
            sixes=("is_boundary_6", "sum"),
        )
        .reset_index()
    )

    agg["run_rate"] = ((agg["runs"] / agg["balls"]) * 6).round(2)
    agg["boundary_count"] = agg["fours"] + agg["sixes"]
    agg = agg.drop(columns=["fours", "sixes"])

    logging.info(f"  Phase stats: {len(agg):,} match×innings×phase rows.")
    return agg


# ── Over-by-Over Run Rate Progression ────────────────────────────────────────

def compute_over_progression(deliveries: pd.DataFrame) -> pd.DataFrame:
    """
    Compute over-by-over scoring and cumulative run totals per match per innings.

    Returns:
        DataFrame with cols: cricsheet_id, innings, over, runs_in_over,
        wickets_in_over, balls_in_over, run_rate_over, cumulative_runs.
    """
    logging.info("Computing over-by-over run rate progression...")

    over_agg = (
        deliveries
        .groupby(["cricsheet_id", "innings", "over"])
        .agg(
            runs_in_over=("runs_total", "sum"),
            wickets_in_over=("is_wicket", "sum"),
            balls_in_over=("runs_total", "count"),
        )
        .reset_index()
    )

    # Cumulative runs within each innings of each match
    over_agg = over_agg.sort_values(["cricsheet_id", "innings", "over"])
    over_agg["cumulative_runs"] = (
        over_agg
        .groupby(["cricsheet_id", "innings"])["runs_in_over"]
        .cumsum()
    )

    over_agg["run_rate_over"] = (
        (over_agg["runs_in_over"] / over_agg["balls_in_over"].replace(0, pd.NA)) * 6
    ).round(2)

    # Display over as 1-indexed for readability
    over_agg["over_display"] = over_agg["over"] + 1

    logging.info(f"  Over progression: {len(over_agg):,} match×innings×over rows.")
    return over_agg


# ── Powerplay / Middle / Death Splits ─────────────────────────────────────────

def compute_global_phase_averages(deliveries: pd.DataFrame) -> pd.DataFrame:
    """
    Compute league-wide average scoring rates per phase across all matches.

    Useful for benchmarking a player or team's phase performance against
    the competition average.

    Returns:
        DataFrame with cols: phase, avg_runs_per_over, avg_wickets_per_match.
    """
    logging.info("Computing global phase averages...")

    legal = deliveries[deliveries["extras_wides"] == 0].copy()

    phase_agg = (
        legal
        .groupby(["cricsheet_id", "innings", "phase"])
        .agg(
            runs=("runs_total", "sum"),
            balls=("runs_total", "count"),
            wickets=("is_wicket", "sum"),
        )
        .reset_index()
    )

    global_avg = (
        phase_agg
        .groupby("phase")
        .agg(
            avg_runs_per_over=("runs", lambda x: ((x / phase_agg.loc[x.index, "balls"]) * 6).mean()),
            avg_wickets=("wickets", "mean"),
            sample_size=("runs", "count"),
        )
        .round(2)
        .reset_index()
    )

    logging.info("  Global phase averages computed.")
    return global_avg


# ── Match Summary Stats ───────────────────────────────────────────────────────

def compute_match_summary(
    deliveries: pd.DataFrame,
    matches: pd.DataFrame,
) -> pd.DataFrame:
    """
    Build a rich per-match summary table joining match metadata with
    aggregate totals from deliveries.

    Returns:
        DataFrame with match metadata + total_runs, total_wickets per innings.
    """
    logging.info("Computing overall match summaries...")

    innings_totals = (
        deliveries
        .groupby(["cricsheet_id", "innings"])
        .agg(
            total_runs=("runs_total", "sum"),
            total_wickets=("is_wicket", "sum"),
            total_deliveries=("runs_total", "count"),
        )
        .reset_index()
    )

    # Pivot to get innings 1 and innings 2 as separate columns
    pivot = innings_totals.pivot_table(
        index="cricsheet_id",
        columns="innings",
        values=["total_runs", "total_wickets"],
    )
    pivot.columns = [f"inn{col[1]}_{col[0]}" for col in pivot.columns]
    pivot = pivot.reset_index()

    # Join with match metadata
    meta_cols = [
        "cricsheet_id", "season", "match_date", "venue", "city",
        "team1", "team2", "winner", "player_of_match", "match_type",
    ]
    existing_meta_cols = [c for c in meta_cols if c in matches.columns]
    summary = matches[existing_meta_cols].merge(pivot, on="cricsheet_id", how="left")

    logging.info(f"  Match summaries: {len(summary):,} matches.")
    return summary


# ── Entry Point ───────────────────────────────────────────────────────────────

def run(
    deliveries_path: Path = DELIVERIES_PATH,
    matches_path: Path = MATCHES_PATH,
) -> None:
    """Full pipeline: load → compute → save."""
    deliveries, matches = load_data(deliveries_path, matches_path)

    # 1 — Per-match phase scoring summary
    phase_stats = compute_match_phase_stats(deliveries)
    save_parquet(phase_stats, "match_stats.csv")

    # 2 — Over-by-over run rate progression
    over_prog = compute_over_progression(deliveries)
    save_parquet(over_prog, "over_progression.csv")

    # 3 — Match-level summary (for API list views)
    match_summary = compute_match_summary(deliveries, matches)
    save_parquet(match_summary, "match_summary.csv")

    logging.info("Match analytics complete.")


if __name__ == "__main__":
    run()
