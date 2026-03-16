"""
CricketIQ — Players API router.

Endpoints:
  GET  /players                    — paginated list of all players (batting stats)
  GET  /players/{player_name}      — full batting + bowling profile for one player
  GET  /players/{player_name}/phase — phase-split batting stats for one player
"""
import logging
from typing import Any

from fastapi import APIRouter, HTTPException, Query

from backend.api.data_loader import (
    batting_stats, batting_phase_stats, bowling_stats, safe_json,
)

logger = logging.getLogger("cricketiq.players")
router = APIRouter(prefix="/players", tags=["Players"])


@router.get("", summary="List all players")
def list_players(
    limit: int = Query(50, ge=1, le=500, description="Max number of players to return"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    sort_by: str = Query("total_runs", description="Column to sort by"),
    order: str = Query("desc", regex="^(asc|desc)$", description="Sort order"),
) -> dict[str, Any]:
    """
    Return a paginated, sortable list of player batting statistics.
    """
    df = batting_stats()
    if df.empty:
        return {"total": 0, "players": []}

    if sort_by not in df.columns:
        sort_by = "total_runs"

    ascending = order == "asc"
    sorted_df = df.sort_values(sort_by, ascending=ascending)
    page = sorted_df.iloc[offset : offset + limit]

    return {
        "total": len(df),
        "limit": limit,
        "offset": offset,
        "players": safe_json(page),
    }


@router.get("/{player_name}", summary="Player profile")
def get_player(player_name: str) -> dict[str, Any]:
    """
    Return full batting and bowling statistics for a single player.
    Player name matching is case-insensitive.
    """
    bat_df = batting_stats()
    bowl_df = bowling_stats()

    name_lower = player_name.strip().lower()

    batting_row = bat_df[bat_df["batter"].str.lower() == name_lower]
    bowling_row = bowl_df[bowl_df["bowler"].str.lower() == name_lower]

    if batting_row.empty and bowling_row.empty:
        raise HTTPException(status_code=404, detail=f"Player '{player_name}' not found.")

    return {
        "player": player_name,
        "batting": safe_json(batting_row)[0] if not batting_row.empty else None,
        "bowling": safe_json(bowling_row)[0] if not bowling_row.empty else None,
    }


@router.get("/{player_name}/phase", summary="Player phase-split batting")
def get_player_phase(player_name: str) -> dict[str, Any]:
    """
    Return powerplay / middle / death batting statistics for a single player.
    """
    df = batting_phase_stats()
    name_lower = player_name.strip().lower()
    player_df = df[df["batter"].str.lower() == name_lower]

    if player_df.empty:
        raise HTTPException(
            status_code=404,
            detail=f"No phase data found for player '{player_name}'.",
        )

    return {
        "player": player_name,
        "phase_stats": safe_json(player_df),
    }
