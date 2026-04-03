"""Global constants and configuration for the OviSelect College Agent.

Zero-API-key approach: uses static curated data + NIRF web scraping.
Only Supabase service key is needed for writing to the database.
"""

from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent
CACHE_DIR = PROJECT_ROOT / "data" / "cache"
FAILURES_DIR = PROJECT_ROOT / "data" / "failures"
LOGS_DIR = PROJECT_ROOT / "logs"

for d in (CACHE_DIR, FAILURES_DIR, LOGS_DIR):
    d.mkdir(parents=True, exist_ok=True)

# ── NIRF scraping ─────────────────────────────────────────────────────────────
NIRF_ENGINEERING_URL = "https://www.nirfindia.org/Rankings/2025/EngineeringRanking.html"
NIRF_OVERALL_URL = "https://www.nirfindia.org/Rankings/2025/OverallRanking.html"

# ── Retry settings (tenacity) ─────────────────────────────────────────────────
RETRY_MAX_ATTEMPTS = 3
RETRY_WAIT_MIN_SEC = 2
RETRY_WAIT_MAX_SEC = 15

# ── Agent defaults ─────────────────────────────────────────────────────────────
CONFIDENCE_REVIEW_THRESHOLD = 60  # mark needs_review if below this %

# ── Institute type ordering ────────────────────────────────────────────────────
INSTITUTE_TYPE_ORDER = ["IIT", "NIT", "IIIT", "GFTI"]

# ── User-Agent for HTTP requests ───────────────────────────────────────────────
HTTP_USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
