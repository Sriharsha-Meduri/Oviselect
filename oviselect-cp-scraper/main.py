#!/usr/bin/env python3
"""OviSelect CollegePravesh Scraper — main orchestrator."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from loguru import logger

# Load .env before importing modules that need env vars
load_dotenv(Path(__file__).resolve().parent / ".env")

from config.settings import PARSED_DIR, LOGS_DIR, CP_BASE_URL
from models.college_schema import CollegeInfo
from pipeline.loader import get_colleges
from pipeline.validator import compute_confidence
from pipeline.writer import upsert_college
from scraper.fetcher import fetch_page
from scraper.parser import parse_college_page
from scraper.structurer import structure_with_llm
from scraper.official_scraper import scrape_official_site
from scraper.merger import merge


def setup_logging() -> None:
    """Configure loguru with console + timestamped file output."""
    logger.remove()  # Remove default handler
    logger.add(
        sys.stderr,
        level="INFO",
        format="<green>{time:HH:mm:ss}</green> | <level>{level:<7}</level> | {message}",
    )
    log_file = LOGS_DIR / f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    logger.add(
        str(log_file),
        level="DEBUG",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level:<7} | {message}",
        rotation="10 MB",
    )
    logger.info(f"Log file: {log_file}")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Scrape CollegePravesh for JoSAA college data")
    p.add_argument("--type", choices=["IIT", "NIT", "IIIT", "GFTI", "ALL"], default="ALL",
                    help="Filter by institute type (default: ALL)")
    p.add_argument("--college", type=str, default=None,
                    help="Process a single college by exact name")
    p.add_argument("--from-cache", action="store_true",
                    help="Only use cached HTML files, no HTTP requests")
    p.add_argument("--force-refresh", action="store_true",
                    help="Ignore cache and re-fetch all pages")
    p.add_argument("--dry-run", action="store_true",
                    help="Parse and structure without writing to Supabase")
    p.add_argument("--skip-llm", action="store_true",
                    help="Skip Ollama structuring, write raw parsed data")
    p.add_argument("--skip-official", action="store_true",
                    help="Skip official website scraping phase")
    p.add_argument("--official-from-cache", action="store_true",
                    help="Only use cached official site pages, no HTTP")
    p.add_argument("--no-profile-crawl", action="store_true",
                    help="Skip crawling individual faculty profile pages")
    p.add_argument("--concurrency", type=int, default=1,
                    help="Concurrency level (default: 1)")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    setup_logging()

    colleges = get_colleges(type_filter=args.type, single_college=args.college)
    if not colleges:
        logger.error("No colleges to process. Check --type or --college argument.")
        sys.exit(1)

    # Stats
    attempted = 0
    succeeded = 0
    failed: list[tuple[str, str]] = []
    review_count = 0
    confidence_scores: list[tuple[str, int]] = []

    for name, slug, inst_type in colleges:
        attempted += 1
        logger.info(f"[{slug}] Processing: {name} ({inst_type})")

        # 1. Fetch
        soup = fetch_page(slug, force_refresh=args.force_refresh, from_cache=args.from_cache)
        if soup is None:
            logger.error(f"[{slug}] ✗ Fetch failed — skipping")
            failed.append((name, "fetch_failed"))
            continue

        # 2. Parse CollegePravesh page
        raw_data = parse_college_page(soup, slug, name)
        raw_data["institute_type"] = inst_type
        raw_data["_slug"] = slug
        # Populate pipeline metadata so it flows into both JSON files and Supabase
        raw_data["collegepravesh_url"] = f"{CP_BASE_URL}/{slug}"
        raw_data["last_scraped_at"] = datetime.utcnow().isoformat()
        raw_data["data_sources"] = ["collegepravesh"]

        # 3. Official website scraping phase
        if not args.skip_official:
            logger.info(f"[{slug}] Phase 2 — scraping official website")
            official_data = scrape_official_site(
                name, slug,
                force_refresh=args.force_refresh,
                from_cache=args.official_from_cache,
                crawl_profiles=not args.no_profile_crawl,
            )
            if official_data:
                raw_data = merge(raw_data, official_data, slug=slug)
        raw_data["last_scraped_at"] = datetime.utcnow().isoformat()

        # Save raw parsed
        raw_path = PARSED_DIR / f"{slug}_raw.json"
        raw_path.write_text(json.dumps(raw_data, indent=2, default=str), encoding="utf-8")

        # 3. Structure with LLM
        if args.skip_llm:
            structured = raw_data
        else:
            structured = structure_with_llm(raw_data, slug)
            structured["institute_type"] = inst_type
            structured["_slug"] = slug

        # 4. Confidence score
        score, needs_review = compute_confidence(structured, slug)
        structured["data_confidence_score"] = score
        structured["needs_review"] = needs_review
        confidence_scores.append((name, score))
        if needs_review:
            review_count += 1

        # 5. Validate with Pydantic
        try:
            validated = CollegeInfo(**{k: v for k, v in structured.items() if not k.startswith("_")})
        except Exception as e:
            logger.error(f"[{slug}] Pydantic validation error: {e}")
            failed.append((name, f"validation: {e}"))
            # Still try to write raw data
            validated = None

        # 6. Write to Supabase
        if not args.dry_run:
            write_data = validated.model_dump() if validated else {k: v for k, v in structured.items() if not k.startswith("_")}
            write_data["_slug"] = slug
            if upsert_college(write_data):
                succeeded += 1
            else:
                failed.append((name, "upsert_failed"))
        else:
            succeeded += 1
            logger.info(f"[{slug}] Dry run — skipping Supabase write")

        # Save structured
        struct_path = PARSED_DIR / f"{slug}_structured.json"
        final_data = validated.model_dump() if validated else structured
        struct_path.write_text(json.dumps(final_data, indent=2, default=str), encoding="utf-8")

        status = "⚠ REVIEW" if needs_review else "✓"
        logger.info(f"[{slug}] {status} {name} — confidence: {score}%")

    # ── Final Summary ────────────────────────────────────────
    logger.info("=" * 60)
    logger.info("PIPELINE COMPLETE")
    logger.info(f"  Total attempted:     {attempted}")
    logger.info(f"  Successfully written: {succeeded}")
    logger.info(f"  Failed:              {len(failed)}")
    logger.info(f"  Needs review:        {review_count}")
    avg_conf = sum(s for _, s in confidence_scores) / len(confidence_scores) if confidence_scores else 0
    logger.info(f"  Avg confidence:      {avg_conf:.1f}%")

    if failed:
        logger.info("  Failures:")
        for name, reason in failed:
            logger.info(f"    ✗ {name}: {reason}")

    # Bottom 5 by confidence
    lowest = sorted(confidence_scores, key=lambda x: x[1])[:5]
    if lowest:
        logger.info("  Lowest confidence:")
        for name, score in lowest:
            logger.info(f"    {score}% — {name}")

    logger.info("=" * 60)


if __name__ == "__main__":
    main()

