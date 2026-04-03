"""Pydantic v2 model for structured college data."""

from __future__ import annotations

from typing import Optional, Any

from pydantic import BaseModel, field_validator


# ── Nested models ─────────────────────────────────────────────────────────────

class Qualification(BaseModel):
    degree: Optional[str] = None
    institution: Optional[str] = None
    year: Optional[int] = None


class FacultyMember(BaseModel):
    name: Optional[str] = None
    designation: Optional[str] = None          # Professor / Associate Professor / Assistant Professor
    department: Optional[str] = None
    qualifications: Optional[list[Qualification]] = None
    specializations: Optional[list[str]] = None
    experience_years: Optional[int] = None
    awards: Optional[list[str]] = None
    profile_url: Optional[str] = None
    publications: Optional[list[str]] = None   # from individual profile pages
    patents: Optional[list[str]] = None
    funded_projects: Optional[list[str]] = None
    phd_students_supervised: Optional[list[str]] = None
    courses_taught: Optional[list[str]] = None


class Department(BaseModel):
    name: Optional[str] = None
    hod_name: Optional[str] = None
    hod_designation: Optional[str] = None
    faculty_count: Optional[int] = None
    faculty: Optional[list[FacultyMember]] = None


class Programme(BaseModel):
    name: Optional[str] = None
    level: Optional[str] = None                # UG / PG / PhD / Dual / Integrated
    duration_years: Optional[float] = None
    intake_seats: Optional[int] = None
    total_credits: Optional[int] = None
    eligibility: Optional[str] = None


class YearWisePlacement(BaseModel):
    year: Optional[int] = None
    overall_pct: Optional[float] = None
    avg_package_lpa: Optional[float] = None
    median_package_lpa: Optional[float] = None
    highest_package_lpa: Optional[float] = None
    total_offers: Optional[int] = None
    ppo_ppi_count: Optional[int] = None
    companies_visited: Optional[list[str]] = None


class PlacementContact(BaseModel):
    name: Optional[str] = None
    designation: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None


class ResearchInfo(BaseModel):
    active_projects: Optional[int] = None
    funding_agencies: Optional[list[str]] = None
    total_funding_crores: Optional[float] = None
    consultancy_projects: Optional[int] = None
    patents_filed: Optional[int] = None
    patents_granted: Optional[int] = None
    publications_per_year: Optional[int] = None
    phd_students_enrolled: Optional[int] = None
    phds_awarded: Optional[int] = None
    research_centres: Optional[list[str]] = None
    international_collaborations: Optional[list[str]] = None


class Library(BaseModel):
    volumes: Optional[int] = None
    journals_subscribed: Optional[int] = None
    digital_databases: Optional[list[str]] = None


class Hostel(BaseModel):
    name: Optional[str] = None
    gender: Optional[str] = None               # boys / girls / mixed
    capacity: Optional[int] = None
    room_types: Optional[list[str]] = None
    facilities: Optional[list[str]] = None


class MedicalCentre(BaseModel):
    beds: Optional[int] = None
    full_time_doctor: Optional[bool] = None
    hospital_tie_up: Optional[str] = None


class InfrastructureInfo(BaseModel):
    labs: Optional[list[str]] = None
    central_instruments: Optional[list[str]] = None   # SEM, XRD, FESEM, etc.
    library: Optional[Library] = None
    sports_facilities: Optional[list[str]] = None
    hostels: Optional[list[Hostel]] = None
    hostel_count_boys: Optional[int] = None
    hostel_count_girls: Optional[int] = None
    total_hostel_capacity: Optional[int] = None
    medical_centre: Optional[MedicalCentre] = None
    has_bank_atm: Optional[bool] = None
    has_post_office: Optional[bool] = None
    cafeteria_messes: Optional[int] = None
    guest_house: Optional[bool] = None
    transport_buses: Optional[int] = None


class StudentActivities(BaseModel):
    clubs: Optional[list[str]] = None
    technical_societies: Optional[list[str]] = None
    technical_fests: Optional[list[str]] = None
    cultural_fests: Optional[list[str]] = None
    has_nss: Optional[bool] = None
    has_ncc: Optional[bool] = None
    sports_teams: Optional[list[str]] = None
    student_publications: Optional[list[str]] = None
    student_council_positions: Optional[list[str]] = None


class MoU(BaseModel):
    university: Optional[str] = None
    country: Optional[str] = None
    focus_area: Optional[str] = None


class InternationalRelations(BaseModel):
    mous: Optional[list[MoU]] = None
    mou_count: Optional[int] = None
    exchange_students_outgoing: Optional[int] = None
    foreign_students_on_campus: Optional[int] = None
    faculty_exchange_programmes: Optional[list[str]] = None
    joint_phd_programmes: Optional[list[str]] = None


# ── Main model ────────────────────────────────────────────────────────────────

class CollegeInfo(BaseModel):
    institute: str
    institute_type: Optional[str] = None
    also_known_as: Optional[str] = None
    established_year: Optional[int] = None
    city: Optional[str] = None
    state: Optional[str] = None
    address: Optional[str] = None
    nearest_airport: Optional[str] = None
    nearest_airport_km: Optional[float] = None
    nearest_railway_station: Optional[str] = None
    nearest_railway_km: Optional[float] = None
    nirf_overall_rank: Optional[int] = None
    nirf_engineering_rank: Optional[int] = None
    nirf_research_rank: Optional[int] = None
    nirf_innovation_rank: Optional[str] = None
    qs_world_rank: Optional[str] = None
    qs_asia_rank: Optional[str] = None
    the_world_rank: Optional[str] = None
    the_asia_rank: Optional[str] = None
    outlook_rank: Optional[int] = None
    the_week_rank: Optional[int] = None
    courses_offered: Optional[list[str]] = None
    tuition_fee_per_sem: Optional[int] = None
    hostel_fee_per_sem: Optional[int] = None
    mess_advance_per_sem: Optional[int] = None
    one_time_fees: Optional[int] = None
    caution_money: Optional[int] = None
    annual_fees: Optional[int] = None
    total_institute_fee: Optional[int] = None
    total_hostel_fee: Optional[int] = None
    fee_waivers: Optional[list[str]] = None
    overall_placement_pct: Optional[float] = None
    avg_package_lpa: Optional[float] = None
    median_package_lpa: Optional[float] = None
    highest_package_lpa: Optional[float] = None
    branch_wise_placement_pct: Optional[dict] = None
    branch_wise_median_ctc: Optional[dict] = None
    branch_wise_highest_ctc: Optional[dict] = None
    branch_wise_avg_ctc: Optional[dict] = None
    top_recruiters: Optional[list[str]] = None
    placement_year: Optional[int] = None
    # ── Extended placement fields (official site) ──────────────
    placement_officer: Optional[PlacementContact] = None
    year_wise_placements: Optional[list[YearWisePlacement]] = None
    internship_placement_pct: Optional[float] = None
    internship_avg_stipend: Optional[float] = None
    sector_wise_placement: Optional[dict[str, float]] = None
    # ── Faculty & departments (official site) ──────────────────
    total_faculty_count: Optional[int] = None
    faculty_with_phd_pct: Optional[float] = None
    faculty_student_ratio: Optional[str] = None
    departments: Optional[list[Department]] = None
    # ── Programmes (official site) ─────────────────────────────
    ug_programmes: Optional[list[Programme]] = None
    pg_programmes: Optional[list[Programme]] = None
    phd_available: Optional[bool] = None
    phd_seats: Optional[int] = None
    dual_degree_programmes: Optional[list[Programme]] = None
    # ── Admissions (official site) ─────────────────────────────
    jee_advanced_cutoff_year: Optional[int] = None
    gate_cutoff_year: Optional[int] = None
    admission_documents_required: Optional[list[str]] = None
    refund_policy: Optional[str] = None
    # ── Detailed fees (official site) ──────────────────────────
    registration_fee_per_sem: Optional[int] = None
    exam_fee_per_sem: Optional[int] = None
    library_fee_per_sem: Optional[int] = None
    sports_fee_per_sem: Optional[int] = None
    medical_fee_per_sem: Optional[int] = None
    internet_charges_per_sem: Optional[int] = None
    development_fund_per_sem: Optional[int] = None
    alumni_fund_one_time: Optional[int] = None
    # ── Research (official site) ───────────────────────────────
    research: Optional[ResearchInfo] = None
    # ── Infrastructure (official site) ─────────────────────────
    infrastructure: Optional[InfrastructureInfo] = None
    # ── Student activities (official site) ─────────────────────
    student_activities: Optional[StudentActivities] = None
    # ── International relations (official site) ─────────────────
    international_relations: Optional[InternationalRelations] = None
    # ── Rankings extended ──────────────────────────────────────
    nirf_overall_rank_history: Optional[dict[str, int]] = None   # {"2024": 3, "2023": 4}
    nirf_management_rank: Optional[int] = None
    nirf_law_rank: Optional[int] = None
    # ── Official site metadata ─────────────────────────────────
    official_website: Optional[str] = None
    # ── Pipeline metadata ──────────────────────────────────────
    data_sources: Optional[list[str]] = None
    data_confidence_score: Optional[int] = None
    needs_review: Optional[bool] = False
    collegepravesh_url: Optional[str] = None
    last_scraped_at: Optional[str] = None

    # ── Validators ───────────────────────────────────────────

    @field_validator(
        "nirf_overall_rank", "nirf_engineering_rank", "nirf_research_rank",
        "established_year", "outlook_rank", "the_week_rank",
        mode="before",
    )
    @classmethod
    def parse_int_safely(cls, v):
        if v is None:
            return None
        try:
            return int(str(v).replace(",", "").strip())
        except (ValueError, TypeError):
            return None

    @field_validator(
        "tuition_fee_per_sem", "hostel_fee_per_sem", "total_institute_fee",
        "total_hostel_fee", "caution_money", "one_time_fees", "annual_fees",
        "mess_advance_per_sem",
        mode="before",
    )
    @classmethod
    def parse_rupees(cls, v):
        if v is None:
            return None
        cleaned = (
            str(v)
            .replace("₹", "")
            .replace(",", "")
            .replace("per Semester", "")
            .replace("/-", "")
            .strip()
        )
        try:
            return int(float(cleaned))
        except (ValueError, TypeError):
            return None

    @field_validator(
        "overall_placement_pct", "avg_package_lpa",
        "median_package_lpa", "highest_package_lpa",
        "nearest_airport_km", "nearest_railway_km",
        mode="before",
    )
    @classmethod
    def parse_float_safely(cls, v):
        if v is None:
            return None
        cleaned = (
            str(v)
            .replace("%", "")
            .replace("LPA", "")
            .replace("Lakhs", "")
            .replace("km", "")
            .replace(",", "")
            .strip()
        )
        try:
            return float(cleaned)
        except (ValueError, TypeError):
            return None

    @field_validator("placement_year", mode="before")
    @classmethod
    def parse_year(cls, v):
        if v is None:
            return None
        try:
            return int(str(v).strip()[:4])
        except (ValueError, TypeError):
            return None

