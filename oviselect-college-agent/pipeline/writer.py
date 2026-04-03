"""Write validated college data to Supabase."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from loguru import logger

from config import FAILURES_DIR
from models.college_schema import CollegeInfo
from pipeline.loader import get_supabase_client


def upsert_college(college: CollegeInfo) -> bool:
    """Upsert a validated CollegeInfo record into Supabase college_info table.

    Returns True on success, False on failure.
    """
    sb = get_supabase_client()

    # Convert to dict, handling datetime serialization
    data = college.model_dump(mode="json")
    data["last_updated"] = datetime.now(timezone.utc).isoformat()

    try:
        sb.table("college_info").upsert(
            data, on_conflict="institute"
        ).execute()
        logger.info(f"✓ Upserted {college.institute}")
        return True
    except Exception as e:
        logger.error(f"✗ Supabase upsert failed for {college.institute}: {e}")
        _save_failure(college.institute, data, str(e))
        return False


def upsert_reddit_mentions(institute: str, posts: list[dict[str, Any]]) -> int:
    """Upsert Reddit mentions into college_reddit_mentions table.

    Returns count of successfully upserted rows.
    """
    sb = get_supabase_client()
    count = 0
    for post in posts:
        row = {
            "institute": institute,
            "post_id": post.get("id", ""),
            "title": post.get("title", ""),
            "selftext": (post.get("selftext", "") or "")[:5000],
            "subreddit": post.get("subreddit", ""),
            "url": post.get("url", ""),
            "score": post.get("score", 0),
            "num_comments": post.get("num_comments", 0),
            "created_utc": post.get("created_utc", 0),
            "top_comments": post.get("top_comments", []),
        }
        try:
            sb.table("college_reddit_mentions").upsert(
                row, on_conflict="institute,post_id"
            ).execute()
            count += 1
        except Exception as e:
            logger.debug(f"Reddit mention upsert failed for {institute}/{row['post_id']}: {e}")
    if count:
        logger.info(f"✓ Upserted {count} Reddit mentions for {institute}")
    return count


def _save_failure(institute: str, data: dict[str, Any], error: str) -> None:
    """Save failed records locally for manual review."""
    import re
    slug = re.sub(r"[^a-z0-9]+", "_", institute.lower().strip())[:80]
    fp = FAILURES_DIR / f"{slug}.json"
    fp.parent.mkdir(parents=True, exist_ok=True)
    failure = {
        "institute": institute,
        "error": error,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "data": data,
    }
    with open(fp, "w", encoding="utf-8") as f:
        json.dump(failure, f, indent=2, ensure_ascii=False, default=str)
    logger.debug(f"Failure record saved to {fp}")


def write_summary_report(
    results: list[dict[str, Any]],
    output_path: Path | None = None,
) -> str:
    """Generate a summary report of the pipeline run.

    Returns the report as a string.
    """
    total = len(results)
    success = sum(1 for r in results if r.get("success"))
    failed = total - success
    needs_review = sum(1 for r in results if r.get("needs_review"))
    avg_confidence = (
        sum(r.get("confidence", 0) for r in results) / total if total else 0
    )

    lines = [
        "=" * 60,
        "  OviSelect College Agent — Pipeline Summary",
        "=" * 60,
        f"  Total institutes:    {total}",
        f"  Successfully stored: {success}",
        f"  Failed:              {failed}",
        f"  Needs review:        {needs_review}",
        f"  Avg confidence:      {avg_confidence:.1f}%",
        "=" * 60,
    ]

    if failed > 0:
        lines.append("\n  Failed institutes:")
        for r in results:
            if not r.get("success"):
                lines.append(f"    ✗ {r.get('institute', '?')}: {r.get('error', 'unknown')}")

    if needs_review > 0:
        lines.append("\n  Needs review (confidence < 60%):")
        for r in results:
            if r.get("needs_review"):
                lines.append(f"    ⚠ {r.get('institute', '?')} ({r.get('confidence', 0):.0f}%)")

    report = "\n".join(lines)

    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            f.write(report)
        logger.info(f"Summary report saved to {output_path}")

    return report

