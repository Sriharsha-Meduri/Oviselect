"""OviSelect College Agent — Zero-API-key pipeline.

Stage 1: Load curated static data from data/college_data.py
Stage 2: Scrape public sources (NIRF, Reddit, Wikipedia, CollegeDunia, Shiksha,
         official sites, Google Scholar) — all free, no auth required
Stage 3: Pass raw scraped text to Ollama (local LLM) or Claude for structuring
Stage 4: Validate with Pydantic
Stage 5: Upsert into Supabase college_info + college_reddit_mentions

Usage:
    python main.py                          # Process all institutes
    python main.py --only "IIT Bombay"      # Process one institute
    python main.py --type IIT               # Process only IITs
    python main.py --skip-nirf              # Skip NIRF scraping
    python main.py --skip-scrape            # Skip all web scraping (static data only)
    python main.py --from-cache             # Use only cached data, no new HTTP requests
    python main.py --dry-run                # Validate only, don't write to Supabase
    python main.py --force-refresh          # Ignore cache, re-scrape everything
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone

from loguru import logger

from config import LOGS_DIR
from data.college_data import COLLEGE_DATA
from agents.nirf_scraper import scrape_nirf_rankings, find_nirf_rank
from pipeline.loader import classify_institute
from pipeline.cache import has_cache, clear_cache
from pipeline.validator import validate_college
from pipeline.writer import upsert_college, write_summary_report, upsert_reddit_mentions

# ── Logging setup ────────────────────────────────────────────────────────────
logger.remove()
logger.add(sys.stderr, level="INFO", format="<green>{time:HH:mm:ss}</green> | <level>{level:7s}</level> | {message}")
logger.add(
    LOGS_DIR / "agent_{time:YYYY-MM-DD}.log",
    level="DEBUG",
    rotation="10 MB",
    retention="30 days",
)


def _scrape_all_sources(name: str, from_cache: bool = False) -> dict:
    """Run all scrapers for a college. Returns merged scraped data + raw texts."""
    scraped: dict = {}
    raw_texts: dict[str, str] = {}
    sources_used: list[str] = ["static_data"]

    if from_cache and not has_cache(name, "reddit"):
        # Skip scraping if --from-cache and no cache exists
        pass
    else:
        try:
            from scrapers.reddit_scraper import scrape_reddit_for_college
            reddit = scrape_reddit_for_college(name)
            if reddit.get("total_posts", 0) > 0:
                sources_used.append("reddit")
                scraped["_reddit_posts"] = reddit.get("posts", [])
                scraped["reddit_mentions_count"] = reddit["total_posts"]
                # Combine Reddit text for structuring
                texts = []
                for p in reddit.get("posts", [])[:20]:
                    texts.append(f"Title: {p['title']}\n{p.get('selftext', '')}")
                    for c in p.get("top_comments", []):
                        texts.append(f"Comment: {c.get('body', '')}")
                raw_texts["reddit"] = "\n---\n".join(texts)[:5000]
        except Exception as e:
            logger.debug(f"Reddit scraper failed for {name}: {e}")

    if from_cache and not has_cache(name, "wikipedia"):
        pass
    else:
        try:
            from scrapers.wikipedia_scraper import scrape_wikipedia
            wiki = scrape_wikipedia(name)
            if wiki.get("found"):
                sources_used.append("wikipedia")
                for field in ["establishment_year", "campus_area_acres"]:
                    if field in wiki:
                        scraped.setdefault(field, wiki[field])
                raw_texts["wikipedia"] = wiki.get("extract", "")
        except Exception as e:
            logger.debug(f"Wikipedia scraper failed for {name}: {e}")

    if from_cache and not has_cache(name, "collegedunia"):
        pass
    else:
        try:
            from scrapers.collegedunia_scraper import scrape_collegedunia
            cd = scrape_collegedunia(name)
            if cd.get("found"):
                sources_used.append("collegedunia")
                for field in ["avg_package_lpa", "highest_package_lpa",
                              "placement_percentage", "companies_visited", "top_recruiters"]:
                    if field in cd:
                        scraped.setdefault(field, cd[field])
        except Exception as e:
            logger.debug(f"CollegeDunia scraper failed for {name}: {e}")

    if from_cache and not has_cache(name, "shiksha"):
        pass
    else:
        try:
            from scrapers.shiksha_scraper import scrape_shiksha
            sh = scrape_shiksha(name)
            if sh.get("found"):
                sources_used.append("shiksha")
                for field in ["total_faculty", "student_faculty_ratio", "naac_grade"]:
                    if field in sh:
                        scraped.setdefault(field, sh[field])
        except Exception as e:
            logger.debug(f"Shiksha scraper failed for {name}: {e}")

    if from_cache and not has_cache(name, "official_site"):
        pass
    else:
        try:
            from scrapers.official_site_scraper import scrape_official_site
            off = scrape_official_site(name)
            if off.get("found"):
                sources_used.append("official_site")
                raw_texts["official_site"] = off.get("raw_text", "")
        except Exception as e:
            logger.debug(f"Official site scraper failed for {name}: {e}")

    if from_cache and not has_cache(name, "scholar"):
        pass
    else:
        try:
            from scrapers.scholar_scraper import scrape_scholar
            sch = scrape_scholar(name)
            if sch.get("found"):
                sources_used.append("scholar")
        except Exception as e:
            logger.debug(f"Scholar scraper failed for {name}: {e}")

    # Pass raw texts through structuring layer if we have any
    if raw_texts:
        try:
            from scrapers.structurer import structure_scraped_data
            structured = structure_scraped_data(name, raw_texts)
            if structured:
                sources_used.append("llm_structured")
                for k, v in structured.items():
                    if v is not None:
                        scraped.setdefault(k, v)
        except Exception as e:
            logger.debug(f"Structurer failed for {name}: {e}")

    scraped["sources"] = sources_used
    return scraped


def process_one(
    name: str,
    static_data: dict,
    nirf_rankings: dict,
    skip_scrape: bool = False,
    from_cache: bool = False,
    dry_run: bool = False,
) -> dict:
    """Process a single institute through the full pipeline."""
    result = {"institute": name, "success": False, "confidence": 0, "needs_review": False}

    try:
        # 1. Start with static curated data
        data = {"institute": name, **static_data}

        # 2. Merge NIRF rankings
        nirf = find_nirf_rank(name, nirf_rankings)
        if nirf:
            if "engineering_rank" in nirf:
                data.setdefault("nirf_engineering_rank", nirf["engineering_rank"])
            if "overall_rank" in nirf:
                data.setdefault("nirf_rank", nirf["overall_rank"])

        # 3. Scrape public sources + structure with LLM
        if not skip_scrape:
            scraped = _scrape_all_sources(name, from_cache=from_cache)
            reddit_posts = scraped.pop("_reddit_posts", [])
            # Merge scraped data (static data takes priority via setdefault)
            for k, v in scraped.items():
                if v is not None and k != "sources":
                    data.setdefault(k, v)
            if "sources" in scraped:
                data["sources"] = scraped["sources"]
        else:
            reddit_posts = []
            data.setdefault("sources", ["static_data"])

        # 4. Validate with Pydantic
        model, errors = validate_college(data)
        if model is None:
            result["error"] = f"Validation failed: {errors}"
            return result

        result["confidence"] = model.data_confidence_pct or 0
        result["needs_review"] = model.needs_review

        # 5. Write to Supabase
        if not dry_run:
            ok = upsert_college(model)
            if not ok:
                result["error"] = "Supabase upsert failed"
                return result
            # Write Reddit mentions
            if reddit_posts:
                upsert_reddit_mentions(name, reddit_posts)
        else:
            logger.info(f"  [dry-run] Would upsert {name} (sources: {data.get('sources', [])})")

        result["success"] = True

    except Exception as e:
        logger.error(f"Pipeline failed for {name}: {e}")
        result["error"] = str(e)

    return result


def run_pipeline(args: argparse.Namespace) -> None:
    """Main pipeline: static data → scrape → structure → validate → store."""
    mode = "from-cache" if args.from_cache else ("static-only" if args.skip_scrape else "full")
    logger.info(f"🚀 OviSelect College Agent starting (mode: {mode})...")

    # Load static curated data
    colleges = dict(COLLEGE_DATA)
    logger.info(f"Loaded {len(colleges)} institutes from static data")

    # Filter by type
    if args.type:
        colleges = {k: v for k, v in colleges.items()
                    if classify_institute(k) == args.type.upper()}
        logger.info(f"Filtered to {len(colleges)} {args.type.upper()} institutes")

    # Filter by name
    if args.only:
        colleges = {k: v for k, v in colleges.items()
                    if args.only.lower() in k.lower()}
        logger.info(f"Filtered to {len(colleges)} matching '{args.only}'")

    if not colleges:
        logger.error("No institutes to process")
        return

    # Force refresh: clear cache
    if args.force_refresh:
        for name in colleges:
            cleared = clear_cache(name)
            if cleared:
                logger.debug(f"Cleared {cleared} cache files for {name}")

    # Scrape NIRF rankings (once, shared)
    nirf_rankings = {}
    if not args.skip_nirf:
        try:
            nirf_rankings = scrape_nirf_rankings()
            logger.info(f"NIRF rankings loaded: {len(nirf_rankings)} entries")
        except Exception as e:
            logger.warning(f"NIRF scraping failed (continuing without): {e}")

    # Process each institute
    results: list[dict] = []
    total = len(colleges)
    for i, (name, static_data) in enumerate(colleges.items(), 1):
        r = process_one(
            name, static_data, nirf_rankings,
            skip_scrape=args.skip_scrape,
            from_cache=args.from_cache,
            dry_run=args.dry_run,
        )
        results.append(r)
        status = "✓" if r["success"] else "✗"
        logger.info(f"[{i}/{total}] {status} {name}")

    # Summary report
    ts = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
    report_path = LOGS_DIR / f"report_{ts}.txt"
    report = write_summary_report(results, report_path)
    print(report)


def main() -> None:
    parser = argparse.ArgumentParser(description="OviSelect College Agent (Zero-API)")
    parser.add_argument("--only", type=str, help="Process only institutes matching this name")
    parser.add_argument("--type", type=str, choices=["IIT", "NIT", "IIIT", "GFTI"],
                        help="Filter by institute type")
    parser.add_argument("--skip-nirf", action="store_true", help="Skip NIRF scraping")
    parser.add_argument("--skip-scrape", action="store_true",
                        help="Skip all web scraping (static data + NIRF only)")
    parser.add_argument("--from-cache", action="store_true",
                        help="Use only cached scraped data, no new HTTP requests")
    parser.add_argument("--force-refresh", action="store_true",
                        help="Clear cache and re-scrape everything")
    parser.add_argument("--dry-run", action="store_true", help="Don't write to Supabase")
    args = parser.parse_args()

    run_pipeline(args)


if __name__ == "__main__":
    main()

