-- ============================================================
-- college_info table — stores structured research data
-- Run this in Supabase SQL Editor (Dashboard → SQL Editor)
-- ============================================================

CREATE TABLE IF NOT EXISTS college_info (
  -- Identity & rankings
  institute                    TEXT PRIMARY KEY,
  institute_type               TEXT,
  nirf_rank                    INT,
  nirf_engineering_rank        INT,
  qs_india_rank                INT,
  the_india_rank               INT,
  naac_grade                   TEXT,
  naac_cgpa                    NUMERIC(3,2),
  nba_accredited_programs      TEXT[] DEFAULT '{}',
  establishment_year           INT,
  campus_area_acres            NUMERIC(8,2),
  total_departments            INT,
  pg_programs                  INT,
  phd_programs                 INT,

  -- Seats & fees
  total_ug_seats               INT,
  branch_wise_seats            JSONB,
  hs_os_split                  JSONB,
  tuition_fee_per_sem          INT,
  hostel_fee_single_per_sem    INT,
  hostel_fee_shared_per_sem    INT,
  mess_fee_per_month           INT,
  total_4yr_cost_estimate      INT,
  fee_waivers                  JSONB,
  scholarships_available       TEXT[] DEFAULT '{}',

  -- Faculty
  total_faculty                INT,
  professors                   INT,
  assoc_professors             INT,
  asst_professors              INT,
  faculty_with_phd_pct         NUMERIC(5,2),
  faculty_from_iit_nit_pct     NUMERIC(5,2),
  student_faculty_ratio        NUMERIC(5,2),
  hod_by_department            JSONB,
  faculty_with_grants          INT,
  patents_filed_5yr            INT,
  patents_granted_5yr          INT,
  sci_scopus_publications_per_yr INT,
  notable_faculty              TEXT[] DEFAULT '{}',

  -- Labs & infrastructure
  major_labs                   JSONB,
  hpc_access                   BOOLEAN,
  fab_lab                      BOOLEAN,
  three_d_printing             BOOLEAN,
  vlsi_lab                     BOOLEAN,
  eda_tools                    TEXT[] DEFAULT '{}',
  licensed_software            TEXT[] DEFAULT '{}',
  library_books                INT,
  digital_library_access       TEXT[] DEFAULT '{}',
  open_lab_24hr                BOOLEAN,
  incubation_center            BOOLEAN,

  -- Placements
  avg_package_lpa              NUMERIC(6,2),
  median_package_lpa           NUMERIC(6,2),
  highest_package_lpa          NUMERIC(6,2),
  lowest_package_lpa           NUMERIC(6,2),
  placement_percentage         NUMERIC(5,2),
  companies_visited            INT,
  ppo_count                    INT,
  top_recruiters               TEXT[] DEFAULT '{}',
  dream_companies              TEXT[] DEFAULT '{}',
  core_vs_software_pct         JSONB,
  gate_qualifiers_per_yr       INT,
  placement_trend_5yr          JSONB,
  ms_abroad_per_yr             INT,
  avg_internship_stipend_per_month INT,

  -- Coding & tech culture
  gsoc_selections_total        INT,
  icpc_regionals_3yr           INT,
  coding_club                  BOOLEAN,
  hackathon_wins_national      INT,
  gdsc_present                 BOOLEAN,
  mlsa_present                 BOOLEAN,
  startup_count                INT,

  -- Research
  total_research_grants_cr     NUMERIC(8,2),
  active_funded_projects       INT,
  funding_agencies             TEXT[] DEFAULT '{}',
  institution_h_index          INT,
  phd_scholars_enrolled        INT,
  phds_awarded_5yr             INT,
  centres_of_excellence        TEXT[] DEFAULT '{}',
  national_lab_collaborations  TEXT[] DEFAULT '{}',
  international_mous           INT,

  -- Alumni
  total_alumni                 INT,
  notable_alumni               TEXT[] DEFAULT '{}',
  alumni_founders              INT,
  alumni_in_academia           INT,
  linkedin_alumni_count        INT,

  -- Location
  city                         TEXT,
  state                        TEXT,
  nearest_major_city           TEXT,
  nearest_major_city_km        NUMERIC(6,1),
  nearest_airport              TEXT,
  nearest_airport_km           NUMERIC(6,1),
  nearest_railway_station      TEXT,
  nearest_railway_km           NUMERIC(6,1),
  city_tier                    TEXT,

  -- Campus life
  hostel_capacity_boys         INT,
  hostel_capacity_girls        INT,
  ac_hostel_available          BOOLEAN,
  gym_on_campus                BOOLEAN,
  swimming_pool                BOOLEAN,
  medical_facility             TEXT,
  mess_options                 INT,
  sports_achievements          TEXT[] DEFAULT '{}',
  student_clubs_count          INT,
  tech_fest_name               TEXT,
  cultural_fest_name           TEXT,
  international_exchange_programs INT,
  counselling_available        BOOLEAN,

  -- Reddit sentiment
  reddit_mentions_count        INT,
  reddit_positive_pct          NUMERIC(5,2),
  reddit_negative_pct          NUMERIC(5,2),
  reddit_neutral_pct           NUMERIC(5,2),
  reddit_top_positive_themes   TEXT[] DEFAULT '{}',
  reddit_top_negative_themes   TEXT[] DEFAULT '{}',
  reddit_summary               TEXT,

  -- Scores (1-10)
  placement_score              NUMERIC(4,2),
  academic_score               NUMERIC(4,2),
  campus_life_score            NUMERIC(4,2),
  research_score               NUMERIC(4,2),
  value_for_money_score        NUMERIC(4,2),
  overall_score                NUMERIC(4,2),

  -- Meta
  data_confidence_pct          NUMERIC(5,2),
  needs_review                 BOOLEAN DEFAULT true,
  sources                      TEXT[] DEFAULT '{}',
  last_updated                 TIMESTAMPTZ DEFAULT now()
);

-- ── Indexes ─────────────────────────────────────────────────
CREATE INDEX idx_college_info_type ON college_info (institute_type);
CREATE INDEX idx_college_info_nirf ON college_info (nirf_rank);
CREATE INDEX idx_college_info_state ON college_info (state);
CREATE INDEX idx_college_info_overall ON college_info (overall_score DESC NULLS LAST);

-- ── Row Level Security ──────────────────────────────────────
ALTER TABLE college_info ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Public read college_info" ON college_info
  FOR SELECT USING (true);

CREATE POLICY "Service write college_info" ON college_info
  FOR ALL USING (auth.role() = 'service_role');


-- ============================================================
-- college_reddit_mentions — raw Reddit posts/comments per college
-- ============================================================

CREATE TABLE IF NOT EXISTS college_reddit_mentions (
  id              BIGSERIAL PRIMARY KEY,
  institute       TEXT NOT NULL REFERENCES college_info(institute) ON DELETE CASCADE,
  post_id         TEXT NOT NULL,
  title           TEXT,
  selftext        TEXT,
  subreddit       TEXT,
  url             TEXT,
  score           INT DEFAULT 0,
  num_comments    INT DEFAULT 0,
  created_utc     DOUBLE PRECISION,
  top_comments    JSONB DEFAULT '[]',
  collected_at    TIMESTAMPTZ DEFAULT now(),
  UNIQUE(institute, post_id)
);

CREATE INDEX idx_reddit_institute ON college_reddit_mentions (institute);
CREATE INDEX idx_reddit_subreddit ON college_reddit_mentions (subreddit);
CREATE INDEX idx_reddit_score ON college_reddit_mentions (score DESC);

ALTER TABLE college_reddit_mentions ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Public read reddit_mentions" ON college_reddit_mentions
  FOR SELECT USING (true);

CREATE POLICY "Service write reddit_mentions" ON college_reddit_mentions
  FOR ALL USING (auth.role() = 'service_role');

