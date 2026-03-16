import axios from "axios";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000/api/v1";

const api = axios.create({
  baseURL: API_BASE,
  timeout: 10000,
  headers: { "Content-Type": "application/json" },
});

// ── Players ──────────────────────────────────────────────────────────────────

export interface Player {
  batter: string;
  matches: number;
  innings: number;
  total_runs: number;
  balls_faced: number;
  strike_rate: number;
  average: number;
  fours: number;
  sixes: number;
  boundary_pct: number;
  dot_pct: number;
  dismissals: number;
  not_outs: number;
}

export interface BowlerStat {
  bowler: string;
  matches: number;
  balls_bowled: number;
  overs: number;
  runs_conceded: number;
  wickets: number;
  economy: number;
  average: number | null;
  dot_pct: number;
  boundary_pct: number;
}

export async function fetchPlayers(limit = 50, offset = 0): Promise<{ total: number; players: Player[] }> {
  const { data } = await api.get("/players", { params: { limit, offset } });
  return data;
}

export async function fetchPlayer(name: string): Promise<{ player: string; batting: Player | null; bowling: BowlerStat | null }> {
  const { data } = await api.get(`/players/${encodeURIComponent(name)}`);
  return data;
}

// ── Matches ───────────────────────────────────────────────────────────────────

export interface Match {
  cricsheet_id: string;
  season: string;
  match_date: string;
  venue: string;
  city: string;
  team1: string;
  team2: string;
  winner: string | null;
  player_of_match: string | null;
  match_type: string;
}

export interface OverData {
  over: number;
  over_display: number;
  runs_in_over: number;
  wickets_in_over: number;
  cumulative_runs: number;
  run_rate_over: number;
}

export async function fetchMatches(limit = 50, offset = 0, season?: string): Promise<{ total: number; matches: Match[] }> {
  const { data } = await api.get("/matches", { params: { limit, offset, season } });
  return data;
}

export async function fetchMatchOvers(id: string, innings = 1): Promise<{ overs: OverData[] }> {
  const { data } = await api.get(`/matches/${id}/overs`, { params: { innings } });
  return data;
}

// ── Analytics ─────────────────────────────────────────────────────────────────

export async function fetchBattingLeaders(limit = 20, min_innings = 5): Promise<{ leaders: Player[] }> {
  const { data } = await api.get("/analytics/batting-leaders", { params: { limit, min_innings } });
  return data;
}

export async function fetchBowlingLeaders(limit = 20, min_overs = 10): Promise<{ leaders: BowlerStat[] }> {
  const { data } = await api.get("/analytics/bowling-leaders", { params: { limit, min_overs } });
  return data;
}

export interface RunRatePoint {
  over: number;
  over_display: number;
  avg_runs: number;
  avg_wickets: number;
  matches: number;
}

export async function fetchRunRateProgression(innings = 1): Promise<{ progression: RunRatePoint[] }> {
  const { data } = await api.get("/analytics/run-rate-progression", { params: { innings } });
  return data;
}

export interface PhaseLeader {
  batter: string;
  phase: string;
  total_runs: number;
  balls_faced: number;
  strike_rate: number;
  boundary_pct: number;
  dot_pct: number;
}

export async function fetchPhaseBatting(phase = "powerplay", limit = 15): Promise<{ leaders: PhaseLeader[] }> {
  const { data } = await api.get("/analytics/phase-batting", { params: { phase, limit } });
  return data;
}
