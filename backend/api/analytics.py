"""
CricketIQ — Analytics API router.

Endpoints:
  GET  /analytics/batting-leaders          — top batters by total runs
  GET  /analytics/bowling-leaders          — top bowlers by wickets
  GET  /analytics/phase-batting            — phase-split batting leaderboard
  GET  /analytics/phase-bowling            — phase-split bowling leaderboard
  GET  /analytics/run-rate-progression     — aggregated over-by-over run rates (all matches)
"""
import logging
from typing import Any

from fastapi import APIRouter, Query

from backend.api.data_loader import (
    batting_stats, batting_phase_stats,
    bowling_stats, bowling_phase_stats,
    over_progression, safe_json,
)

logger = logging.getLogger("cricketiq.analytics")
router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/batting-leaders", summary="Top run scorers")
def batting_leaders(
    limit: int = Query(20, ge=1, le=200),
    min_innings: int = Query(5, ge=1, description="Minimum innings to qualify"),
) -> dict[str, Any]:
    """
    Return the top batters ranked by total runs, filtered by a minimum
    innings threshold to exclude small-sample outliers.
    """
    df = batting_stats()
    if df.empty:
        return {"leaders": []}

    qualified = df[df["innings"] >= min_innings]
    leaders = qualified.sort_values("total_runs", ascending=False).head(limit)

    return {"count": len(leaders), "min_innings": min_innings, "leaders": safe_json(leaders)}


@router.get("/bowling-leaders", summary="Top wicket takers")
def bowling_leaders(
    limit: int = Query(20, ge=1, le=200),
    min_overs: float = Query(10.0, ge=1, description="Minimum overs bowled to qualify"),
) -> dict[str, Any]:
    """
    Return the top bowlers ranked by wickets, filtered by a minimum overs threshold.
    """
    df = bowling_stats()
    if df.empty:
        return {"leaders": []}

    qualified = df[df["overs"] >= min_overs]
    leaders = qualified.sort_values("wickets", ascending=False).head(limit)

    return {"count": len(leaders), "min_overs": min_overs, "leaders": safe_json(leaders)}


@router.get("/phase-batting", summary="Phase-split batting leaderboard")
def phase_batting_leaders(
    phase: str = Query("powerplay", regex="^(powerplay|middle|death)$"),
    sort_by: str = Query("total_runs"),
    limit: int = Query(20, ge=1, le=200),
) -> dict[str, Any]:
    """
    Return top batters in a specific game phase sorted by a chosen metric.
    """
    df = batting_phase_stats()
    if df.empty:
        return {"phase": phase, "leaders": []}

    phase_df = df[df["phase"] == phase]
    if sort_by not in phase_df.columns:
        sort_by = "total_runs"

    leaders = phase_df.sort_values(sort_by, ascending=False).head(limit)
    return {"phase": phase, "sort_by": sort_by, "count": len(leaders), "leaders": safe_json(leaders)}


@router.get("/phase-bowling", summary="Phase-split bowling leaderboard")
def phase_bowling_leaders(
    phase: str = Query("death", regex="^(powerplay|middle|death)$"),
    sort_by: str = Query("economy"),
    limit: int = Query(20, ge=1, le=200),
) -> dict[str, Any]:
    """
    Return top bowlers in a specific game phase sorted by a chosen metric.
    Economy is ascending (lower is better); wickets is descending.
    """
    df = bowling_phase_stats()
    if df.empty:
        return {"phase": phase, "leaders": []}

    phase_df = df[df["phase"] == phase]
    if sort_by not in phase_df.columns:
        sort_by = "economy"

    ascending = sort_by in ("economy", "dot_pct")  # lower is better
    leaders = phase_df.sort_values(sort_by, ascending=ascending).head(limit)
    return {"phase": phase, "sort_by": sort_by, "count": len(leaders), "leaders": safe_json(leaders)}


@router.get("/run-rate-progression", summary="Average run rate per over (all matches)")
def avg_run_rate_progression(
    innings: int = Query(1, ge=1, le=2, description="Innings number"),
    phase: str | None = Query(None, regex="^(powerplay|middle|death)$"),
) -> dict[str, Any]:
    """
    Compute the average run rate per over number across all matches.
    Useful for rendering an 'average innings template' chart on the frontend.
    """
    df = over_progression()
    if df.empty:
        return {"innings": innings, "progression": []}

    filtered = df[df["innings"] == innings]

    # Optionally restrict to a phase's over range
    if phase == "powerplay":
        filtered = filtered[filtered["over"] < 6]
    elif phase == "middle":
        filtered = filtered[(filtered["over"] >= 6) & (filtered["over"] < 15)]
    elif phase == "death":
        filtered = filtered[filtered["over"] >= 15]

    avg = (
        filtered
        .groupby("over")
        .agg(
            avg_runs=("runs_in_over", "mean"),
            avg_wickets=("wickets_in_over", "mean"),
            matches=("cricsheet_id", "nunique"),
        )
        .round(2)
        .reset_index()
    )
    avg["over_display"] = avg["over"] + 1

    return {"innings": innings, "phase": phase, "progression": safe_json(avg)}
