-- ============================================================
-- JoSAA cutoff data — normalized schema
-- Run this in Supabase SQL Editor (Dashboard → SQL Editor)
-- ============================================================

-- ── Drop old tables (order matters for foreign keys) ────────
DROP TABLE IF EXISTS cutoffs CASCADE;
DROP TABLE IF EXISTS programs CASCADE;
DROP TABLE IF EXISTS institutes CASCADE;

-- ── Lookup: institutes ──────────────────────────────────────
CREATE TABLE institutes (
  id    SMALLINT PRIMARY KEY,
  name  TEXT NOT NULL
);

-- ── Lookup: programs ────────────────────────────────────────
CREATE TABLE programs (
  id    SMALLINT PRIMARY KEY,
  name  TEXT     NOT NULL,       -- field/branch name
  deg   TEXT     NOT NULL,       -- BTech, BArch, IMS, BM.Tech, etc.
  yrs   SMALLINT NOT NULL        -- duration in years
);

-- ── Main: cutoffs ───────────────────────────────────────────
CREATE TABLE cutoffs (
  id      BIGINT   GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  year    SMALLINT NOT NULL,
  round   SMALLINT NOT NULL,
  iid     SMALLINT NOT NULL REFERENCES institutes(id),
  pid     SMALLINT NOT NULL REFERENCES programs(id),
  quota   TEXT     NOT NULL,       -- AI, HS, OS, GO, JK, LA
  seat    TEXT     NOT NULL,       -- OPEN, EWS, OBC-NCL, SC, ST, OPEN-PwD, etc.
  gender  CHAR(1)  NOT NULL,       -- N = Gender-Neutral, F = Female-only
  open    INT      NOT NULL,       -- opening rank
  close   INT      NOT NULL,       -- closing rank
  prep    SMALLINT NOT NULL DEFAULT 0  -- 1 = preparatory
);

-- ── Indexes ─────────────────────────────────────────────────
CREATE INDEX idx_cutoffs_lookup ON cutoffs (seat, gender, close);
CREATE INDEX idx_cutoffs_year   ON cutoffs (year, round);

-- ── Row Level Security ──────────────────────────────────────
ALTER TABLE institutes ENABLE ROW LEVEL SECURITY;
ALTER TABLE programs   ENABLE ROW LEVEL SECURITY;
ALTER TABLE cutoffs    ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Public read" ON institutes FOR SELECT USING (true);
CREATE POLICY "Public read" ON programs   FOR SELECT USING (true);
CREATE POLICY "Public read" ON cutoffs    FOR SELECT USING (true);

CREATE POLICY "Service write" ON institutes FOR ALL USING (auth.role() = 'service_role');
CREATE POLICY "Service write" ON programs   FOR ALL USING (auth.role() = 'service_role');
CREATE POLICY "Service write" ON cutoffs    FOR ALL USING (auth.role() = 'service_role');

-- ── Users (Google login tracking) ──────────────────────────
CREATE TABLE IF NOT EXISTS users (
  id           BIGINT   GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  email        TEXT     NOT NULL UNIQUE,
  name         TEXT,
  picture      TEXT,
  login_count  INT      NOT NULL DEFAULT 1,
  first_login  TIMESTAMPTZ NOT NULL DEFAULT now(),
  last_login   TIMESTAMPTZ NOT NULL DEFAULT now()
);

ALTER TABLE users ENABLE ROW LEVEL SECURITY;

-- Anyone can insert/update their own row (upsert on login)
CREATE POLICY "Public upsert" ON users FOR INSERT WITH CHECK (true);
CREATE POLICY "Public update" ON users FOR UPDATE USING (true);
CREATE POLICY "Service read"  ON users FOR SELECT USING (auth.role() = 'service_role');
-- Allow anon to read their own row by email (for session restore)
CREATE POLICY "Anon read own"  ON users FOR SELECT USING (true);

-- ── Predictions (form submissions) ────────────────────────
CREATE TABLE IF NOT EXISTS predictions (
  id              BIGINT       GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  email           TEXT         NOT NULL UNIQUE,
  name            TEXT,
  mains_rank      INT,
  advanced_rank   INT,                     -- NULL if N/A
  category        TEXT         NOT NULL,    -- General, OBC-NCL, SC, ST, EWS, PwD
  category_rank   INT,                     -- NULL if General or N/A
  gender          TEXT         NOT NULL,    -- Gender-Neutral, Female-Only
  home_state      TEXT         NOT NULL,
  branch_order    TEXT[],                   -- ordered array of branch names; NULL if N/A
  branch_na       BOOLEAN      NOT NULL DEFAULT false,
  created_at      TIMESTAMPTZ  NOT NULL DEFAULT now(),
  updated_at      TIMESTAMPTZ  NOT NULL DEFAULT now()
);

CREATE INDEX idx_predictions_email ON predictions (email);

ALTER TABLE predictions ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Anyone can insert predictions" ON predictions FOR INSERT WITH CHECK (true);
CREATE POLICY "Anyone can update predictions" ON predictions FOR UPDATE USING (true);
CREATE POLICY "Anyone can read own predictions" ON predictions FOR SELECT USING (true);

