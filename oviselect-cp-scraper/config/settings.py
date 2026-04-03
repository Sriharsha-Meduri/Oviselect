"""Constants and configuration for the CollegePravesh scraper."""

from pathlib import Path

# ── Paths ────────────────────────────────────────────────────
ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"
CACHE_DIR = DATA_DIR / "cache"
OFFICIAL_CACHE_DIR = DATA_DIR / "official_cache"   # cache for official site pages
PARSED_DIR = DATA_DIR / "parsed"
FAILURES_DIR = DATA_DIR / "failures"
LOGS_DIR = ROOT_DIR / "logs"

# Create directories
for d in [CACHE_DIR, OFFICIAL_CACHE_DIR, PARSED_DIR, FAILURES_DIR, LOGS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# ── CollegePravesh ───────────────────────────────────────────
CP_BASE_URL = "https://www.collegepravesh.com/engineering-colleges"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "identity",
    "Referer": "https://www.collegepravesh.com/",
    "Connection": "keep-alive",
}

# ── Ollama ───────────────────────────────────────────────────
import os
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3.1")
OLLAMA_URL = "http://localhost:11434"

# ── Confidence scoring ───────────────────────────────────────
CRITICAL_FIELDS = [
    "established_year", "city", "state",
    "nearest_airport_km", "nearest_railway_km",
    "nirf_overall_rank", "nirf_engineering_rank",
    "tuition_fee_per_sem", "hostel_fee_per_sem",
    "total_institute_fee", "total_hostel_fee",
    "overall_placement_pct", "avg_package_lpa",
    "median_package_lpa", "highest_package_lpa",
    "top_recruiters", "branch_wise_placement_pct",
    "branch_wise_median_ctc", "courses_offered",
    "fee_waivers",
    # New official-site fields
    "departments", "ug_programmes", "research", "infrastructure",
]
CONFIDENCE_THRESHOLD = 60  # Below this → needs_review = True

