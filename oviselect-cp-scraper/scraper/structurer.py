"""Use local Ollama LLM to clean and structure raw parsed college data."""

from __future__ import annotations

import json
from typing import Any

from loguru import logger

from config.settings import OLLAMA_MODEL, OLLAMA_URL


SYSTEM_PROMPT = """You are a data-structuring assistant. You receive raw scraped data about an Indian engineering college.
Your job: return a CLEAN JSON object with exactly the fields listed below, nothing else.
- Fix obvious OCR/scrape errors in numbers (e.g. "1,23,456" → 123456).
- Convert "₹1,23,456" to integer 123456.
- Convert "12.5 LPA" to float 12.5.
- Convert "85%" to float 85.0.
- If a field has no data, set it to null.
- Do NOT invent data. Only clean what is provided.
- Return ONLY valid JSON, no markdown, no explanation.

Fields:
institute, institute_type, also_known_as, established_year, city, state, address,
nearest_airport, nearest_airport_km, nearest_railway_station, nearest_railway_km,
nirf_overall_rank, nirf_engineering_rank, nirf_research_rank, nirf_innovation_rank,
qs_world_rank, qs_asia_rank, the_world_rank, the_asia_rank, outlook_rank, the_week_rank,
courses_offered (array of strings),
tuition_fee_per_sem (int), hostel_fee_per_sem (int), mess_advance_per_sem (int),
one_time_fees (int), caution_money (int), annual_fees (int),
total_institute_fee (int), total_hostel_fee (int), fee_waivers (array of strings),
overall_placement_pct (float), avg_package_lpa (float), median_package_lpa (float),
highest_package_lpa (float),
branch_wise_placement_pct (object), branch_wise_median_ctc (object),
branch_wise_highest_ctc (object), branch_wise_avg_ctc (object),
top_recruiters (array of strings), placement_year (int)"""


def _ollama_available() -> bool:
    """Check if Ollama is running."""
    try:
        import requests
        r = requests.get(f"{OLLAMA_URL}/api/tags", timeout=3)
        return r.status_code == 200
    except Exception:
        return False


def structure_with_llm(raw_data: dict[str, Any], slug: str) -> dict[str, Any]:
    """Send raw parsed data to Ollama for cleaning and structuring.

    Returns the cleaned dict, or the original raw_data if LLM is unavailable.
    """
    if not _ollama_available():
        logger.warning(f"[{slug}] Ollama not available — skipping LLM structuring")
        return raw_data

    try:
        import ollama as ollama_lib
    except ImportError:
        logger.warning(f"[{slug}] ollama package not installed — skipping")
        return raw_data

    prompt = f"Raw scraped data:\n```json\n{json.dumps(raw_data, indent=2, default=str)}\n```\n\nReturn ONLY the cleaned JSON."

    logger.info(f"[{slug}] Sending to Ollama ({OLLAMA_MODEL}) for structuring...")

    try:
        response = ollama_lib.chat(
            model=OLLAMA_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            options={"temperature": 0.1, "num_predict": 4096},
        )
        text = response["message"]["content"].strip()

        # Strip markdown code fences if present
        if text.startswith("```"):
            text = text.split("\n", 1)[1] if "\n" in text else text[3:]
        if text.endswith("```"):
            text = text[:-3].strip()
        if text.startswith("json"):
            text = text[4:].strip()

        structured = json.loads(text)
        # Preserve institute name from original
        structured["institute"] = raw_data["institute"]
        logger.info(f"[{slug}] LLM structuring complete — {len(structured)} fields")
        return structured

    except json.JSONDecodeError as e:
        logger.error(f"[{slug}] LLM returned invalid JSON: {e}")
        return raw_data
    except Exception as e:
        logger.error(f"[{slug}] LLM structuring failed: {e}")
        return raw_data

