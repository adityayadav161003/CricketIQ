-- =============================================================
-- CricketIQ — PostgreSQL Schema
-- Scalable for IPL, T20I, BBL, PSL, SA20, and future leagues.
-- =============================================================

-- Enable UUID generation
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- =============================================================
-- 1. COMPETITIONS
-- Stores league / tournament metadata
-- =============================================================
CREATE TABLE IF NOT EXISTS competitions (
    id          SERIAL PRIMARY KEY,
    code        VARCHAR(20)  UNIQUE NOT NULL,  -- e.g. 'IPL', 'T20I', 'BBL'
    name        VARCHAR(100) NOT NULL,          -- e.g. 'Indian Premier League'
    gender      VARCHAR(10)  NOT NULL CHECK (gender IN ('male', 'female', 'mixed')),
    match_type  VARCHAR(20)  NOT NULL,          -- 'T20', 'ODI', 'Test'
    country     VARCHAR(50),                    -- NULL for multi-country competitions
    created_at  TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

-- =============================================================
-- 2. TEAMS
-- =============================================================
CREATE TABLE IF NOT EXISTS teams (
    id              SERIAL PRIMARY KEY,
    name            VARCHAR(100) UNIQUE NOT NULL,  -- full name
    short_name      VARCHAR(10),                    -- e.g. 'MI', 'CSK'
    country         VARCHAR(50),
    competition_id  INT REFERENCES competitions(id) ON DELETE SET NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- =============================================================
-- 3. PLAYERS
-- One row per unique player (Cricsheet key-based identity)
-- =============================================================
CREATE TABLE IF NOT EXISTS players (
    id              SERIAL PRIMARY KEY,
    cricsheet_key   VARCHAR(64) UNIQUE,   -- Cricsheet registry identifier
    name            VARCHAR(120) NOT NULL,
    full_name       VARCHAR(200),
    country         VARCHAR(50),
    batting_style   VARCHAR(30),          -- 'Right', 'Left'
    bowling_style   VARCHAR(60),          -- 'Right arm fast', 'Left arm orthodox', etc.
    role            VARCHAR(30),          -- 'Batter', 'Bowler', 'All-rounder', 'WK'
    date_of_birth   DATE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- =============================================================
-- 4. MATCHES
-- One row per match
-- =============================================================
CREATE TABLE IF NOT EXISTS matches (
    id              SERIAL PRIMARY KEY,
    cricsheet_id    VARCHAR(64) UNIQUE NOT NULL,  -- original file key
    competition_id  INT  REFERENCES competitions(id) ON DELETE CASCADE,
    season          VARCHAR(20),                  -- e.g. '2023', '2023/24'
    match_date      DATE,
    venue           VARCHAR(150),
    city            VARCHAR(100),
    team1_id        INT REFERENCES teams(id) ON DELETE SET NULL,
    team2_id        INT REFERENCES teams(id) ON DELETE SET NULL,
    toss_winner_id  INT REFERENCES teams(id) ON DELETE SET NULL,
    toss_decision   VARCHAR(10) CHECK (toss_decision IN ('bat', 'field')),
    winner_id       INT REFERENCES teams(id) ON DELETE SET NULL,
    win_by_runs     INT,
    win_by_wickets  INT,
    player_of_match VARCHAR(120),
    match_type      VARCHAR(20),                  -- 'T20', 'ODI', 'Test'
    gender          VARCHAR(10),
    json_source     TEXT,                         -- path to raw JSON file
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_matches_competition ON matches(competition_id);
CREATE INDEX IF NOT EXISTS idx_matches_season      ON matches(season);
CREATE INDEX IF NOT EXISTS idx_matches_date        ON matches(match_date);

-- =============================================================
-- 5. DELIVERIES
-- Ball-by-ball records — the CORE analytics table
-- Every delivery in every innings of every match
-- =============================================================
CREATE TABLE IF NOT EXISTS deliveries (
    id              BIGSERIAL PRIMARY KEY,
    match_id        INT         NOT NULL REFERENCES matches(id) ON DELETE CASCADE,
    innings         SMALLINT    NOT NULL,          -- 1 or 2 (or 3/4 for Tests)
    over            SMALLINT    NOT NULL,          -- 0-indexed
    ball            SMALLINT    NOT NULL,          -- 1-indexed within over
    phase           VARCHAR(10) NOT NULL           -- 'powerplay', 'middle', 'death'
                        CHECK (phase IN ('powerplay', 'middle', 'death')),
    batter          VARCHAR(120) NOT NULL,
    non_striker     VARCHAR(120),
    bowler          VARCHAR(120) NOT NULL,
    runs_batter     SMALLINT    NOT NULL DEFAULT 0,
    runs_extras     SMALLINT    NOT NULL DEFAULT 0,
    runs_total      SMALLINT    NOT NULL DEFAULT 0,
    -- Extras breakdown
    extras_wides    SMALLINT    DEFAULT 0,
    extras_noballs  SMALLINT    DEFAULT 0,
    extras_byes     SMALLINT    DEFAULT 0,
    extras_legbyes  SMALLINT    DEFAULT 0,
    extras_penalty  SMALLINT    DEFAULT 0,
    -- Dismissal
    is_wicket       BOOLEAN     NOT NULL DEFAULT FALSE,
    dismissal_type  VARCHAR(40),                  -- 'bowled', 'caught', 'lbw', etc.
    player_out      VARCHAR(120),
    fielder         VARCHAR(120),                 -- fielder involved in dismissal
    -- Batter flags
    is_boundary_4   BOOLEAN     NOT NULL DEFAULT FALSE,
    is_boundary_6   BOOLEAN     NOT NULL DEFAULT FALSE,
    is_dot_ball     BOOLEAN     NOT NULL DEFAULT FALSE,  -- no runs to batter
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Performance-critical indexes for analytics queries
CREATE INDEX IF NOT EXISTS idx_del_match       ON deliveries(match_id);
CREATE INDEX IF NOT EXISTS idx_del_batter      ON deliveries(batter);
CREATE INDEX IF NOT EXISTS idx_del_bowler      ON deliveries(bowler);
CREATE INDEX IF NOT EXISTS idx_del_innings     ON deliveries(innings);
CREATE INDEX IF NOT EXISTS idx_del_phase       ON deliveries(phase);
CREATE INDEX IF NOT EXISTS idx_del_wicket      ON deliveries(is_wicket) WHERE is_wicket = TRUE;
CREATE INDEX IF NOT EXISTS idx_del_match_inn   ON deliveries(match_id, innings);

-- =============================================================
-- 6. PLAYER STATS (per match aggregates)
-- Pre-computed for dashboard performance
-- =============================================================
CREATE TABLE IF NOT EXISTS player_stats (
    id                  SERIAL PRIMARY KEY,
    player_id           INT     NOT NULL REFERENCES players(id) ON DELETE CASCADE,
    match_id            INT     NOT NULL REFERENCES matches(id) ON DELETE CASCADE,
    competition_id      INT     REFERENCES competitions(id) ON DELETE SET NULL,
    team_id             INT     REFERENCES teams(id) ON DELETE SET NULL,
    -- Batting
    batting_runs        SMALLINT DEFAULT 0,
    balls_faced         SMALLINT DEFAULT 0,
    batting_fours       SMALLINT DEFAULT 0,
    batting_sixes       SMALLINT DEFAULT 0,
    batting_dots        SMALLINT DEFAULT 0,
    did_bat             BOOLEAN  DEFAULT FALSE,
    was_dismissed       BOOLEAN  DEFAULT FALSE,
    -- Bowling
    balls_bowled        SMALLINT DEFAULT 0,
    runs_conceded       SMALLINT DEFAULT 0,
    wickets             SMALLINT DEFAULT 0,
    bowling_dots        SMALLINT DEFAULT 0,
    bowling_fours       SMALLINT DEFAULT 0,
    bowling_sixes       SMALLINT DEFAULT 0,
    did_bowl            BOOLEAN  DEFAULT FALSE,
    -- Fantasy points (computed later by ML model)
    fantasy_points      NUMERIC(6,2),
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    UNIQUE (player_id, match_id)
);

CREATE INDEX IF NOT EXISTS idx_pstats_player ON player_stats(player_id);
CREATE INDEX IF NOT EXISTS idx_pstats_match  ON player_stats(match_id);
CREATE INDEX IF NOT EXISTS idx_pstats_comp   ON player_stats(competition_id);
