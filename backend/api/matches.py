"""
CricketIQ — Matches API router.

Endpoints:
  GET  /matches                        — paginated match list
  GET  /matches/{cricsheet_id}         — match metadata + phase summary
  GET  /matches/{cricsheet_id}/overs   — over-by-over run rate progression
"""
import logging
from typing import Any

from fastapi import APIRouter, HTTPException, Query

from backend.api.data_loader import (
    match_summary, match_stats, over_progression, safe_json,
)

logger = logging.getLogger("cricketiq.matches")
router = APIRouter(prefix="/matches", tags=["Matches"])


@router.get("", summary="List all matches")
def list_matches(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    season: str | None = Query(None, description="Filter by season, e.g. '2023'"),
    team: str | None = Query(None, description="Filter by team name (partial match)"),
) -> dict[str, Any]:
    """
    Return a paginated list of match summaries.
    Optionally filter by season or team.
    """
    df = match_summary()
    if df.empty:
        return {"total": 0, "matches": []}

    if season and "season" in df.columns:
        df = df[df["season"].astype(str) == season]

    if team and "team1" in df.columns:
        mask = (
            df["team1"].str.contains(team, case=False, na=False)
            | df["team2"].str.contains(team, case=False, na=False)
        )
        df = df[mask]

    page = df.iloc[offset : offset + limit]
    return {"total": len(df), "limit": limit, "offset": offset, "matches": safe_json(page)}


@router.get("/{cricsheet_id}", summary="Match detail")
def get_match(cricsheet_id: str) -> dict[str, Any]:
    """
    Return match metadata combined with per-phase scoring summary for both innings.
    """
    # Match metadata
    summary_df = match_summary()
    meta_row = summary_df[summary_df["cricsheet_id"] == cricsheet_id]
    if meta_row.empty:
        raise HTTPException(status_code=404, detail=f"Match '{cricsheet_id}' not found.")

    # Phase stats for this match
    phase_df = match_stats()
    this_phase = phase_df[phase_df["cricsheet_id"] == cricsheet_id] if not phase_df.empty else phase_df

    return {
        "match": safe_json(meta_row)[0],
        "phase_summary": safe_json(this_phase),
    }


@router.get("/{cricsheet_id}/overs", summary="Over-by-over progression")
def get_match_overs(cricsheet_id: str, innings: int = Query(1, ge=1, le=4)) -> dict[str, Any]:
    """
    Return over-by-over run rate and cumulative runs for a specific innings.
    Useful for charting run rate progression on the frontend.
    """
    df = over_progression()
    if df.empty:
        raise HTTPException(status_code=404, detail="No over progression data available.")

    filtered = df[
        (df["cricsheet_id"] == cricsheet_id) & (df["innings"] == innings)
    ]

    if filtered.empty:
        raise HTTPException(
            status_code=404,
            detail=f"No over data for match '{cricsheet_id}' innings {innings}.",
        )

    return {
        "match_id": cricsheet_id,
        "innings": innings,
        "overs": safe_json(filtered.sort_values("over")),
    }
