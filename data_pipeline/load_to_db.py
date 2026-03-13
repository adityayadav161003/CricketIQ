"""
CricketIQ Data Pipeline - Database Loader.

Loads parsed match metadata and ball-by-ball deliveries into PostgreSQL
via SQLAlchemy sessions. Handles existing records safely avoiding duplication.
"""
import sys
import os
import logging
from pathlib import Path

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd
from tqdm import tqdm
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import select

from backend.services.db import get_sync_session, init_db
from backend.models import Match, Delivery, Competition, Team

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"

def load_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Load the processed parquets."""
    matches_path = PROCESSED_DATA_DIR / "matches.parquet"
    deliveries_path = PROCESSED_DATA_DIR / "deliveries.parquet"
    
    if not matches_path.exists() or not deliveries_path.exists():
        logging.error("Processed parquets not found. Run parse_matches.py first.")
        sys.exit(1)
        
    logging.info("Reading DataFrames from disk...")
    matches_df = pd.read_parquet(matches_path)
    deliveries_df = pd.read_parquet(deliveries_path)
    return matches_df, deliveries_df

def get_or_create_team(session, name: str) -> int:
    """Gets an existing team ID or creates a generic one (returns ID or None)."""
    if pd.isna(name) or not name:
        return None
        
    team = session.execute(select(Team).where(Team.name == name)).scalar_one_or_none()
    if team:
        return team.id
        
    # Create new generic team if not found 
    # (assuming real competitions/teams were seeded during Phase 2)
    new_team = Team(name=name)
    session.add(new_team)
    session.flush()
    return new_team.id

def load_to_db(matches_df: pd.DataFrame, deliveries_df: pd.DataFrame):
    """Iterate through the DFs and insert into Database safely."""
    
    # Pre-fetch existing matches to avoid duplicates
    with get_sync_session() as session:
        existing_cricsheet_ids = set(session.scalars(select(Match.cricsheet_id)).all())
    
    new_matches_df = matches_df[~matches_df['cricsheet_id'].isin(existing_cricsheet_ids)]
    if new_matches_df.empty:
        logging.info("No new matches to insert. Database is up to date.")
        return
        
    logging.info(f"Found {len(new_matches_df)} new matches to load.")
    
    with get_sync_session() as session:
        # Cache for simple team lookups
        team_id_cache = {}
        def _get_team(name):
            if name not in team_id_cache:
                team_id_cache[name] = get_or_create_team(session, name)
            return team_id_cache[name]
        
        for _, match_row in tqdm(new_matches_df.iterrows(), total=len(new_matches_df), desc="Loading Matches"):
            # Prepare match entity
            match_data = match_row.to_dict()
            cricsheet_id = match_data['cricsheet_id']
            
            # Map teams
            team1_id = _get_team(match_data.get('team1'))
            team2_id = _get_team(match_data.get('team2'))
            toss_winner_id = _get_team(match_data.get('toss_winner'))
            winner_id = _get_team(match_data.get('winner'))
            
            # Date handling
            match_date = match_data.get('match_date')
            if pd.isna(match_date):
                match_date = None
            else:
                match_date = match_date.date() # Convert timestamp to date
                
            new_match = Match(
                cricsheet_id=cricsheet_id,
                season=str(match_data.get("season")) if not pd.isna(match_data.get("season")) else None,
                match_date=match_date,
                venue=match_data.get("venue"),
                city=match_data.get("city"),
                team1_id=team1_id,
                team2_id=team2_id,
                toss_winner_id=toss_winner_id,
                toss_decision=match_data.get("toss_decision"),
                winner_id=winner_id,
                win_by_runs=int(match_data["win_by_runs"]) if pd.notna(match_data.get("win_by_runs")) else None,
                win_by_wickets=int(match_data["win_by_wickets"]) if pd.notna(match_data.get("win_by_wickets")) else None,
                player_of_match=match_data.get("player_of_match"),
                match_type=match_data.get("match_type"),
                gender=match_data.get("gender"),
                json_source=match_data.get("json_source")
            )
            
            session.add(new_match)
            session.flush() # flush to get match ID
            
            # Filter deliveries for this match
            match_deliveries_df = deliveries_df[deliveries_df['cricsheet_id'] == cricsheet_id]
            
            deliveries_to_insert = []
            for _, del_row in match_deliveries_df.iterrows():
                del_dict = del_row.to_dict()
                
                new_delivery = Delivery(
                    match_id=new_match.id,
                    innings=int(del_dict["innings"]),
                    over=int(del_dict["over"]),
                    ball=int(del_dict["ball"]),
                    phase=del_dict["phase"],
                    batter=del_dict["batter"],
                    non_striker=del_dict.get("non_striker"),
                    bowler=del_dict["bowler"],
                    runs_batter=int(del_dict["runs_batter"]),
                    runs_extras=int(del_dict["runs_extras"]),
                    runs_total=int(del_dict["runs_total"]),
                    extras_wides=int(del_dict.get("extras_wides", 0)),
                    extras_noballs=int(del_dict.get("extras_noballs", 0)),
                    extras_byes=int(del_dict.get("extras_byes", 0)),
                    extras_legbyes=int(del_dict.get("extras_legbyes", 0)),
                    extras_penalty=int(del_dict.get("extras_penalty", 0)),
                    is_wicket=bool(del_dict["is_wicket"]),
                    dismissal_type=del_dict.get("dismissal_type"),
                    player_out=del_dict.get("player_out"),
                    fielder=del_dict.get("fielder"),
                    is_boundary_4=bool(del_dict.get("is_boundary_4", False)),
                    is_boundary_6=bool(del_dict.get("is_boundary_6", False)),
                    is_dot_ball=bool(del_dict.get("is_dot_ball", False))
                )
                deliveries_to_insert.append(new_delivery)
                
            session.bulk_save_objects(deliveries_to_insert)
            
            # Commit batch by batch (or every match) to save memory effectively 
            # and maintain progress in event of failure
            try:
                session.commit()
            except IntegrityError as e:
                session.rollback()
                logging.error(f"Failed to insert match {cricsheet_id} due to constraints. {e}")
                
    logging.info("Database loaded successfully.")

def main():
    """Main execution block."""
    logging.info("Starting Data Loader Pipeline.")
    
    # Ensure tables exist 
    init_db()
    
    matches_df, deliveries_df = load_data()
    load_to_db(matches_df, deliveries_df)

if __name__ == "__main__":
    main()
