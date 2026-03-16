"""
CricketIQ Data Pipeline — Match Parser (IPL + T20I filtered, CSV output).

Reads raw Cricsheet JSON files, keeps only T20 matches, and writes:
  - matches.csv     : match metadata
  - deliveries.csv  : ball-by-ball records

Processes in batches of 1000 for memory safety.
"""
import json
import logging
from pathlib import Path

import pandas as pd
from tqdm import tqdm

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

PROJECT_ROOT = Path(__file__).parent.parent.resolve()
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"

# Allowed match types (T20 covers IPL; T20I / IT20 covers internationals)
ALLOWED_MATCH_TYPES = {"T20", "T20I", "IT20"}


def _phase(over: int) -> str:
    if over < 6:
        return "powerplay"
    if over < 15:
        return "middle"
    return "death"


def _s(v) -> str:
    return str(v) if v is not None else ""


def _i(v) -> int:
    try:
        return int(v)
    except (TypeError, ValueError):
        return 0


def parse_match(file_path: Path):
    """
    Parse one Cricsheet JSON and return (match_row, deliveries).
    Returns (None, None) if the match should be skipped.
    """
    with open(file_path, "r", encoding="utf-8") as fh:
        data = json.load(fh)

    info = data.get("info", {})
    match_type = _s(info.get("match_type", ""))

    # ── Filter: only T20 formats ──────────────────────────────────────────
    if match_type not in ALLOWED_MATCH_TYPES:
        return None, None

    cid = file_path.stem
    teams = info.get("teams", [])
    outcome = info.get("outcome", {})
    toss = info.get("toss", {})
    potm = info.get("player_of_match") or []
    event = info.get("event", {})

    match_row = {
        "cricsheet_id":    cid,
        "competition":     _s(event.get("name")),
        "season":          _s(info.get("season")),
        "match_date":      _s((info.get("dates") or [""])[0]),
        "venue":           _s(info.get("venue")),
        "city":            _s(info.get("city")),
        "team1":           _s(teams[0]) if len(teams) > 0 else "",
        "team2":           _s(teams[1]) if len(teams) > 1 else "",
        "toss_winner":     _s(toss.get("winner")),
        "toss_decision":   _s(toss.get("decision")),
        "winner":          _s(outcome.get("winner")),
        "win_by_runs":     _i(outcome.get("by", {}).get("runs", 0)),
        "win_by_wickets":  _i(outcome.get("by", {}).get("wickets", 0)),
        "player_of_match": _s(potm[0]) if potm else "",
        "match_type":      match_type,
        "gender":          _s(info.get("gender")),
    }

    deliveries = []
    for inn_idx, inning in enumerate(data.get("innings", [])):
        inn_num = inn_idx + 1
        for od in inning.get("overs", []):
            ov = _i(od.get("over", 0))
            ph = _phase(ov)
            for ball_idx, ball in enumerate(od.get("deliveries", [])):
                runs   = ball.get("runs", {})
                extras = ball.get("extras", {})
                wkts   = ball.get("wickets", [])

                rb  = _i(runs.get("batter", 0))
                ext = _i(runs.get("extras", 0))
                rt  = _i(runs.get("total",  0))

                is_wkt = 1 if wkts else 0
                dt = _s(wkts[0].get("kind"))           if wkts else ""
                po = _s(wkts[0].get("player_out"))     if wkts else ""
                fi_list = wkts[0].get("fielders", [])  if wkts else []
                fi = _s(fi_list[0].get("name")) if fi_list else ""

                deliveries.append({
                    "cricsheet_id":   cid,
                    "innings":        inn_num,
                    "over":           ov,
                    "ball":           ball_idx + 1,
                    "phase":          ph,
                    "batter":         _s(ball.get("batter")),
                    "non_striker":    _s(ball.get("non_striker")),
                    "bowler":         _s(ball.get("bowler")),
                    "runs_batter":    rb,
                    "runs_extras":    ext,
                    "runs_total":     rt,
                    "extras_wides":   _i(extras.get("wides",   0)),
                    "extras_noballs": _i(extras.get("noballs", 0)),
                    "extras_byes":    _i(extras.get("byes",    0)),
                    "extras_legbyes": _i(extras.get("legbyes", 0)),
                    "extras_penalty": _i(extras.get("penalty", 0)),
                    "is_wicket":      is_wkt,
                    "dismissal_type": dt,
                    "player_out":     po,
                    "fielder":        fi,
                    "is_boundary_4":  1 if rb == 4 else 0,
                    "is_boundary_6":  1 if rb == 6 else 0,
                    "is_dot_ball":    1 if (rb == 0 and ext == 0 and not is_wkt) else 0,
                })

    return match_row, deliveries


def main():
    if not RAW_DATA_DIR.exists():
        logging.error(f"Raw data dir missing: {RAW_DATA_DIR}. Run download_data.py first.")
        return

    json_files = list(RAW_DATA_DIR.glob("*.json"))
    logging.info(f"Found {len(json_files)} JSON files. Parsing (T20 only)...")

    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    matches_csv = PROCESSED_DATA_DIR / "matches.csv"
    deliveries_csv = PROCESSED_DATA_DIR / "deliveries.csv"

    if matches_csv.exists():
        matches_csv.unlink()
    if deliveries_csv.exists():
        deliveries_csv.unlink()

    batch_size = 1000
    total_m, total_d, skipped = 0, 0, 0

    for i in tqdm(range(0, len(json_files), batch_size), desc="Batch parsing"):
        batch = json_files[i:i + batch_size]
        batch_matches, batch_deliveries = [], []

        for fp in batch:
            try:
                m, d = parse_match(fp)
                if m is None:
                    skipped += 1
                    continue
                batch_matches.append(m)
                batch_deliveries.extend(d)
            except Exception as exc:
                logging.warning(f"Skipping {fp.name}: {exc}")

        if not batch_matches:
            continue

        mdf = pd.DataFrame(batch_matches)
        ddf = pd.DataFrame(batch_deliveries)
        total_m += len(mdf)
        total_d += len(ddf)

        mode = "a" if i > 0 else "w"
        header = (i == 0)
        mdf.to_csv(matches_csv, mode=mode, header=header, index=False)
        ddf.to_csv(deliveries_csv, mode=mode, header=header, index=False)

    logging.info(f"Saved {total_m} matches ({total_d} deliveries). Skipped {skipped} non-T20 files.")


if __name__ == "__main__":
    main()
