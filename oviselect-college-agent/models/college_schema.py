"""Pydantic v2 model for structured college data — maps 1:1 to Supabase college_info."""

from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field, field_validator, model_validator


class CollegeInfo(BaseModel):
    """Complete college information schema.  Every field is Optional because
    data may be unavailable for some colleges."""

    # ── Identity & rankings ────────────────────────────────────────────────
    institute: str = Field(..., min_length=1)
    institute_type: Optional[str] = None
    nirf_rank: Optional[int] = None
    nirf_engineering_rank: Optional[int] = None
    qs_india_rank: Optional[int] = None
    the_india_rank: Optional[int] = None
    naac_grade: Optional[str] = None
    naac_cgpa: Optional[float] = None
    nba_accredited_programs: list[str] = Field(default_factory=list)
    establishment_year: Optional[int] = None
    campus_area_acres: Optional[float] = None
    total_departments: Optional[int] = None
    pg_programs: Optional[int] = None
    phd_programs: Optional[int] = None

    # ── Seats & fees ───────────────────────────────────────────────────────
    total_ug_seats: Optional[int] = None
    branch_wise_seats: Optional[dict[str, Any]] = None
    hs_os_split: Optional[dict[str, Any]] = None
    tuition_fee_per_sem: Optional[int] = None
    hostel_fee_single_per_sem: Optional[int] = None
    hostel_fee_shared_per_sem: Optional[int] = None
    mess_fee_per_month: Optional[int] = None
    total_4yr_cost_estimate: Optional[int] = None
    fee_waivers: Optional[dict[str, Any]] = None
    scholarships_available: list[str] = Field(default_factory=list)

    # ── Faculty ────────────────────────────────────────────────────────────
    total_faculty: Optional[int] = None
    professors: Optional[int] = None
    assoc_professors: Optional[int] = None
    asst_professors: Optional[int] = None
    faculty_with_phd_pct: Optional[float] = None
    faculty_from_iit_nit_pct: Optional[float] = None
    student_faculty_ratio: Optional[float] = None
    hod_by_department: Optional[dict[str, Any]] = None
    faculty_with_grants: Optional[int] = None
    patents_filed_5yr: Optional[int] = None
    patents_granted_5yr: Optional[int] = None
    sci_scopus_publications_per_yr: Optional[int] = None
    notable_faculty: list[str] = Field(default_factory=list)

    # ── Labs & infrastructure ──────────────────────────────────────────────
    major_labs: Optional[dict[str, Any]] = None
    hpc_access: Optional[bool] = None
    fab_lab: Optional[bool] = None
    three_d_printing: Optional[bool] = None
    vlsi_lab: Optional[bool] = None
    eda_tools: list[str] = Field(default_factory=list)
    licensed_software: list[str] = Field(default_factory=list)
    library_books: Optional[int] = None
    digital_library_access: list[str] = Field(default_factory=list)
    open_lab_24hr: Optional[bool] = None
    incubation_center: Optional[bool] = None

    # ── Placements ─────────────────────────────────────────────────────────
    avg_package_lpa: Optional[float] = None
    median_package_lpa: Optional[float] = None
    highest_package_lpa: Optional[float] = None
    lowest_package_lpa: Optional[float] = None
    placement_percentage: Optional[float] = None
    companies_visited: Optional[int] = None
    ppo_count: Optional[int] = None
    top_recruiters: list[str] = Field(default_factory=list)
    dream_companies: list[str] = Field(default_factory=list)
    core_vs_software_pct: Optional[dict[str, Any]] = None
    gate_qualifiers_per_yr: Optional[int] = None
    placement_trend_5yr: Optional[dict[str, Any]] = None
    ms_abroad_per_yr: Optional[int] = None
    avg_internship_stipend_per_month: Optional[int] = None

    # ── Coding & tech culture ──────────────────────────────────────────────
    gsoc_selections_total: Optional[int] = None
    icpc_regionals_3yr: Optional[int] = None
    coding_club: Optional[bool] = None
    hackathon_wins_national: Optional[int] = None
    gdsc_present: Optional[bool] = None
    mlsa_present: Optional[bool] = None
    startup_count: Optional[int] = None

    # ── Research ───────────────────────────────────────────────────────────
    total_research_grants_cr: Optional[float] = None
    active_funded_projects: Optional[int] = None
    funding_agencies: list[str] = Field(default_factory=list)
    institution_h_index: Optional[int] = None
    phd_scholars_enrolled: Optional[int] = None
    phds_awarded_5yr: Optional[int] = None
    centres_of_excellence: list[str] = Field(default_factory=list)
    national_lab_collaborations: list[str] = Field(default_factory=list)
    international_mous: Optional[int] = None

    # ── Alumni ─────────────────────────────────────────────────────────────
    total_alumni: Optional[int] = None
    notable_alumni: list[str] = Field(default_factory=list)
    alumni_founders: Optional[int] = None
    alumni_in_academia: Optional[int] = None
    linkedin_alumni_count: Optional[int] = None

    # ── Location ───────────────────────────────────────────────────────────
    city: Optional[str] = None
    state: Optional[str] = None
    nearest_major_city: Optional[str] = None
    nearest_major_city_km: Optional[float] = None
    nearest_airport: Optional[str] = None
    nearest_airport_km: Optional[float] = None
    nearest_railway_station: Optional[str] = None
    nearest_railway_km: Optional[float] = None
    city_tier: Optional[str] = None

    # ── Campus life ────────────────────────────────────────────────────────
    hostel_capacity_boys: Optional[int] = None
    hostel_capacity_girls: Optional[int] = None
    ac_hostel_available: Optional[bool] = None
    gym_on_campus: Optional[bool] = None
    swimming_pool: Optional[bool] = None
    medical_facility: Optional[str] = None
    mess_options: Optional[int] = None
    sports_achievements: list[str] = Field(default_factory=list)
    student_clubs_count: Optional[int] = None
    tech_fest_name: Optional[str] = None
    cultural_fest_name: Optional[str] = None
    international_exchange_programs: Optional[int] = None
    counselling_available: Optional[bool] = None

    # ── Reddit sentiment ────────────────────────────────────────────────
    reddit_mentions_count: Optional[int] = None
    reddit_positive_pct: Optional[float] = None
    reddit_negative_pct: Optional[float] = None
    reddit_neutral_pct: Optional[float] = None
    reddit_top_positive_themes: list[str] = Field(default_factory=list)
    reddit_top_negative_themes: list[str] = Field(default_factory=list)
    reddit_summary: Optional[str] = None

    # ── Scores (1-10, agent-computed) ───────────────────────────────────
    placement_score: Optional[float] = None
    academic_score: Optional[float] = None
    campus_life_score: Optional[float] = None
    research_score: Optional[float] = None
    value_for_money_score: Optional[float] = None
    overall_score: Optional[float] = None

    # ── Meta ─────────────────────────────────────────────────────────────
    data_confidence_pct: Optional[float] = None
    needs_review: bool = False
    sources: list[str] = Field(default_factory=list)
    last_updated: Optional[str] = None

    # ── Validators ───────────────────────────────────────────────────────
    @field_validator(
        "placement_score", "academic_score", "campus_life_score",
        "research_score", "value_for_money_score", "overall_score",
        mode="before",
    )
    @classmethod
    def clamp_score(cls, v: Any) -> Any:
        if v is None:
            return v
        v = float(v)
        return max(0.0, min(10.0, v))

    @field_validator(
        "reddit_positive_pct", "reddit_negative_pct", "reddit_neutral_pct",
        "placement_percentage", "faculty_with_phd_pct", "faculty_from_iit_nit_pct",
        "data_confidence_pct",
        mode="before",
    )
    @classmethod
    def clamp_pct(cls, v: Any) -> Any:
        if v is None:
            return v
        v = float(v)
        return max(0.0, min(100.0, v))

    @field_validator("institute_type", mode="before")
    @classmethod
    def normalize_type(cls, v: Any) -> Any:
        if v is None:
            return v
        v = str(v).upper().strip()
        mapping = {"IIT": "IIT", "NIT": "NIT", "IIIT": "IIIT", "GFTI": "GFTI"}
        return mapping.get(v, "GFTI")

    model_config = {"str_strip_whitespace": True}


class RedditMention(BaseModel):
    """A single Reddit post/comment about a college."""
    institute: str = Field(..., min_length=1)
    post_id: str
    title: str = ""
    selftext: str = ""
    subreddit: str = ""
    url: str = ""
    score: int = 0
    num_comments: int = 0
    created_utc: float = 0
    top_comments: list[dict[str, Any]] = Field(default_factory=list)


# ── Research query templates (for Perplexity) ───────────────────────────────
RESEARCH_QUERIES: dict[str, str] = {
    "rankings_accreditation": (
        "What is the NIRF ranking (overall and engineering), QS India ranking, "
        "THE India ranking, NAAC grade and CGPA, and NBA accreditation status of {college}? "
        "When was it established? How large is the campus in acres?"
    ),
    "seats_fees": (
        "What are the total UG BTech seats at {college}? What is the branch-wise seat "
        "distribution? What is the HS/OS quota split? What are the semester-wise tuition fees, "
        "hostel fees, mess charges? Are there fee waivers for SC/ST/EWS students? "
        "What scholarships are available?"
    ),
    "faculty": (
        "How many faculty members does {college} have? Break down by Professor, Associate "
        "Professor, Assistant Professor. What percentage have PhDs? What is the student-faculty "
        "ratio? How many patents have been filed and granted in the last 5 years? "
        "How many Scopus/SCI publications per year? Name any notable faculty."
    ),
    "labs_infra": (
        "What major laboratories and research facilities does {college} have? Does it have "
        "HPC access, fabrication lab, 3D printing, VLSI lab? What EDA tools and licensed "
        "software are available? How many books in the library? Is there 24-hour lab access? "
        "Is there an incubation center or startup ecosystem?"
    ),
    "placements": (
        "What are the placement statistics of {college} for the latest year? Include average, "
        "median, highest, and lowest package in LPA. What is the placement percentage? "
        "How many companies visited? How many PPOs? List top recruiters and dream companies. "
        "What is the core vs software placement split? What is the GATE qualification rate? "
        "How many students go for MS abroad each year?"
    ),
    "coding_culture": (
        "What is the coding and tech culture at {college}? How many GSoC selections total? "
        "ICPC regional qualifications in last 3 years? Are there active coding clubs? "
        "National hackathon wins? Is there a GDSC or MLSA chapter? How many startups "
        "have come out of {college}?"
    ),
    "research": (
        "What is the research output of {college}? Total research grants in crores? "
        "Active funded projects? Which funding agencies (DST, SERB, DRDO etc)? "
        "What is the institution's h-index? How many PhD scholars are enrolled? "
        "PhDs awarded in last 5 years? Any centres of excellence or national lab collaborations? "
        "How many international MOUs?"
    ),
    "alumni": (
        "Who are notable alumni of {college}? How many total alumni? "
        "How many alumni have founded startups? How many are in academia? "
        "Approximate LinkedIn alumni network size?"
    ),
    "location": (
        "Where is {college} located? City, state, nearest major city and distance, "
        "nearest airport and distance, nearest railway station and distance. "
        "Is it in a Tier 1, Tier 2, or Tier 3 city?"
    ),
    "campus_life": (
        "What is campus life like at {college}? Hostel capacity for boys and girls? "
        "AC hostels? Gym, swimming pool, medical facility? How many mess options? "
        "Sports achievements? Number of student clubs? Names of tech fest and cultural fest? "
        "International exchange programs? Mental health counselling available?"
    ),
    "student_reviews": (
        "What do current students and recent alumni say about {college} on Reddit "
        "(r/Btechtards, r/JEENEETards, r/indian_academia), Quora, and College Dunia? "
        "Summarize the general sentiment about placements, academics, campus life, "
        "and food/hostel quality. What are the most common complaints and praises?"
    ),
}

