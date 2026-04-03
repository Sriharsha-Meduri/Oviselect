"""AI structuring layer — extracts structured JSON from raw scraped text.

Supports two backends:
  1. Ollama (free, local) — default, uses llama3.1 or mistral
  2. Anthropic Claude — if ANTHROPIC_API_KEY is set in env

The Ollama API is OpenAI-compatible at http://localhost:11434/v1
"""

from __future__ import annotations

import json
import os
import re
from typing import Any

import requests
from loguru import logger

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3.1")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

EXTRACTION_PROMPT = """You are a data extraction assistant. Given raw text about an Indian engineering college, extract structured data into JSON.

Extract ONLY these fields (use null if not found):
- avg_package_lpa (float): Average placement package in LPA
- median_package_lpa (float): Median placement package in LPA
- highest_package_lpa (float): Highest placement package in LPA
- lowest_package_lpa (float): Lowest placement package in LPA
- placement_percentage (float): Placement rate as percentage
- companies_visited (int): Number of recruiting companies
- top_recruiters (list[str]): Names of top recruiting companies
- total_faculty (int): Total number of faculty
- student_faculty_ratio (float): Student to faculty ratio
- campus_area_acres (float): Campus area in acres
- establishment_year (int): Year established
- total_ug_seats (int): Total undergraduate seats
- tuition_fee_per_sem (int): Tuition fee per semester in INR
- hostel_fee_per_sem (int): Hostel fee per semester in INR
- naac_grade (str): NAAC grade like A++, A+, A, B++
- reddit_sentiment (str): Overall sentiment from Reddit (positive/mixed/negative)
- reddit_common_praises (list[str]): Common positive themes from student reviews
- reddit_common_complaints (list[str]): Common negative themes from student reviews

College: {college_name}

Raw text from multiple sources:
{raw_text}

Return ONLY valid JSON, no explanation. Use null for unknown fields."""


def _call_ollama(prompt: str) -> str | None:
    """Call Ollama local LLM."""
    try:
        resp = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False},
            timeout=120,
        )
        if resp.status_code != 200:
            logger.warning(f"Ollama returned {resp.status_code}")
            return None
        return resp.json().get("response", "")
    except requests.ConnectionError:
        logger.warning("Ollama not running at {OLLAMA_URL}. Install from ollama.ai and run: ollama pull llama3.1")
        return None
    except Exception as e:
        logger.warning(f"Ollama call failed: {e}")
        return None


def _call_claude(prompt: str) -> str | None:
    """Call Anthropic Claude API."""
    try:
        resp = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": ANTHROPIC_API_KEY,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": "claude-sonnet-4-20250514",
                "max_tokens": 2000,
                "messages": [{"role": "user", "content": prompt}],
            },
            timeout=60,
        )
        if resp.status_code != 200:
            return None
        data = resp.json()
        return data["content"][0]["text"]
    except Exception as e:
        logger.warning(f"Claude call failed: {e}")
        return None


def _extract_json(text: str) -> dict | None:
    """Extract JSON from LLM response (may have markdown fences)."""
    # Try direct parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    # Try extracting from code fence
    m = re.search(r'```(?:json)?\s*\n?(.*?)\n?```', text, re.DOTALL)
    if m:
        try:
            return json.loads(m.group(1))
        except json.JSONDecodeError:
            pass
    # Try finding first { ... }
    m = re.search(r'\{.*\}', text, re.DOTALL)
    if m:
        try:
            return json.loads(m.group(0))
        except json.JSONDecodeError:
            pass
    return None


def structure_scraped_data(
    college_name: str,
    raw_texts: dict[str, str],
) -> dict[str, Any]:
    """Pass raw scraped text to LLM for structured extraction.

    Args:
        college_name: Name of the college
        raw_texts: Dict of source_name → raw text content

    Returns:
        Extracted structured data dict
    """
    # Combine all raw texts
    combined = ""
    for source, text in raw_texts.items():
        if text:
            combined += f"\n=== {source.upper()} ===\n{text[:3000]}\n"

    if not combined.strip():
        logger.info(f"Structurer: {college_name} → no raw text to process")
        return {}

    prompt = EXTRACTION_PROMPT.format(college_name=college_name, raw_text=combined[:8000])

    # Try Anthropic first if key is set, then Ollama
    response = None
    if ANTHROPIC_API_KEY:
        response = _call_claude(prompt)
        if response:
            logger.debug(f"Structurer: used Claude for {college_name}")
    
    if not response:
        response = _call_ollama(prompt)
        if response:
            logger.debug(f"Structurer: used Ollama for {college_name}")

    if not response:
        logger.warning(f"Structurer: no LLM available for {college_name}")
        return {}

    extracted = _extract_json(response)
    if not extracted:
        logger.warning(f"Structurer: failed to parse JSON for {college_name}")
        return {}

    logger.info(f"Structurer: {college_name} → {len(extracted)} fields extracted")
    return extracted

