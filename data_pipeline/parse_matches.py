"""
CricketIQ Data Pipeline - Match Parser.

Reads raw Cricsheet JSON files and extracts match metadata and ball-by-ball 
delivery records into structured pandas DataFrames.
"""
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Tuple

import pandas as pd
from tqdm import tqdm

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

PROJECT_ROOT = Path(__file__).parent.parent.resolve()
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"

def determine_phase(over: int, match_type: str = "T20") -> str:
    """Determine the phase of the game based on the over (0-indexed)."""
    if match_type in ["T20", "T20I", "IT20"]:
        if over < 6:
            return "powerplay"
        elif over < 15:
            return "middle"
        else:
            return "death"
    # Simple default fallback
    return "middle"

def parse_match(file_path: Path) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    """
    Parse a single match JSON file.
    Returns:
        match_info (dict): Metadata about the match.
        deliveries (list of dicts): Ball-by-ball data for the entire match.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    info = data.get("info", {})
    cricsheet_id = file_path.stem
    match_type = info.get("match_type", "T20")
    
    # Safe extraction of match metadata
    match_info = {
        "cricsheet_id": cricsheet_id,
        "season": info.get("season"),
        "match_date": info.get("dates", [None])[0],
        "venue": info.get("venue"),
        "city": info.get("city"),
        "team1": info.get("teams", [None, None])[0],
        "team2": info.get("teams", [None, None])[1] if len(info.get("teams", [])) > 1 else None,
        "toss_winner": info.get("toss", {}).get("winner"),
        "toss_decision": info.get("toss", {}).get("decision"),
        "winner": info.get("outcome", {}).get("winner"),
        "win_by_runs": info.get("outcome", {}).get("by", {}).get("runs"),
        "win_by_wickets": info.get("outcome", {}).get("by", {}).get("wickets"),
        "player_of_match": info.get("player_of_match", [None])[0] if info.get("player_of_match") else None,
        "match_type": match_type,
        "gender": info.get("gender"),
        "json_source": file_path.name
    }
    
    # Extract ball-by-ball deliveries
    deliveries_list = []
    
    innings_data = data.get("innings", [])
    for idx, inning_obj in enumerate(innings_data):
        innings_num = idx + 1
        
        # Depending on Cricsheet JSON format (sometimes it's nested dicts or lists)
        overs = inning_obj.get("overs", [])
        for over_data in overs:
            over = over_data.get("over", 0)
            phase = determine_phase(over, match_type)
            
            for ball_idx, ball_data in enumerate(over_data.get("deliveries", [])):
                ball = ball_idx + 1
                
                runs_info = ball_data.get("runs", {})
                extras_info = ball_data.get("extras", {})
                wickets_info = ball_data.get("wickets", [])
                
                is_wicket = len(wickets_info) > 0
                dismissal_type = wickets_info[0].get("kind") if is_wicket else None
                player_out = wickets_info[0].get("player_out") if is_wicket else None
                
                # Fielder extraction (might be an array of fielders)
                fielder = None
                if is_wicket and "fielders" in wickets_info[0] and len(wickets_info[0]["fielders"]) > 0:
                    fielder = wickets_info[0]["fielders"][0].get("name")
                
                runs_batter = runs_info.get("batter", 0)
                is_boundary_4 = runs_batter == 4
                is_boundary_6 = runs_batter == 6
                is_dot_ball = runs_batter == 0 and sum(extras_info.values()) == 0 and not is_wicket

                delivery_record = {
                    "cricsheet_id": cricsheet_id,  # to link back to match
                    "innings": innings_num,
                    "over": over,
                    "ball": ball,
                    "phase": phase,
                    "batter": ball_data.get("batter"),
                    "non_striker": ball_data.get("non_striker"),
                    "bowler": ball_data.get("bowler"),
                    "runs_batter": runs_batter,
                    "runs_extras": runs_info.get("extras", 0),
                    "runs_total": runs_info.get("total", 0),
                    "extras_wides": extras_info.get("wides", 0),
                    "extras_noballs": extras_info.get("noballs", 0),
                    "extras_byes": extras_info.get("byes", 0),
                    "extras_legbyes": extras_info.get("legbyes", 0),
                    "extras_penalty": extras_info.get("penalty", 0),
                    "is_wicket": is_wicket,
                    "dismissal_type": dismissal_type,
                    "player_out": player_out,
                    "fielder": fielder,
                    "is_boundary_4": is_boundary_4,
                    "is_boundary_6": is_boundary_6,
                    "is_dot_ball": is_dot_ball
                }
                deliveries_list.append(delivery_record)
                
    return match_info, deliveries_list

def main():
    """Main execution block."""
    if not RAW_DATA_DIR.exists():
        logging.error(f"Raw data directory missing: {RAW_DATA_DIR}. Run download_data.py first.")
        return

    json_files = list(RAW_DATA_DIR.glob("*.json"))
    if not json_files:
        logging.error(f"No JSON files found in {RAW_DATA_DIR}.")
        return
        
    logging.info(f"Found {len(json_files)} match files. Parsing...")
    
    all_matches = []
    all_deliveries = []
    
    # Process files
    for file_path in tqdm(json_files, desc="Parsing matches"):
        try:
            match_info, deliveries = parse_match(file_path)
            all_matches.append(match_info)
            all_deliveries.extend(deliveries)
        except Exception as e:
            logging.warning(f"Failed to parse {file_path.name}: {e}")
            
    # Convert to DataFrames
    matches_df = pd.DataFrame(all_matches)
    deliveries_df = pd.DataFrame(all_deliveries)
    
    # Clean matches formatting/types
    matches_df['match_date'] = pd.to_datetime(matches_df['match_date'], errors='coerce')
    
    logging.info(f"Parsed {len(matches_df)} matches and {len(deliveries_df)} deliveries.")
    
    # Save to processed directory (parquet is faster and maintains data types)
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    matches_df.to_parquet(PROCESSED_DATA_DIR / "matches.parquet", index=False)
    deliveries_df.to_parquet(PROCESSED_DATA_DIR / "deliveries.parquet", index=False)
    
    logging.info(f"Saved DataFrames to {PROCESSED_DATA_DIR}")

if __name__ == "__main__":
    main()
