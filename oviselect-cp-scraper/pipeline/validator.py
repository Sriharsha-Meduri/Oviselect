"""Compute confidence score and needs_review flag."""

from __future__ import annotations

from typing import Any

from loguru import logger

from config.settings import CRITICAL_FIELDS, CONFIDENCE_THRESHOLD


def compute_confidence(data: dict[str, Any], slug: str) -> tuple[int, bool]:
    """Compute a confidence score (0-100) based on which critical fields are present.

    Returns:
        (confidence_score, needs_review)
    """
    present = 0
    total = len(CRITICAL_FIELDS)

    for field in CRITICAL_FIELDS:
        val = data.get(field)
        if val is not None:
            # Also check for empty lists/dicts
            if isinstance(val, (list, dict)) and len(val) == 0:
                continue
            present += 1

    score = int(round(present / total * 100)) if total > 0 else 0
    needs_review = score < CONFIDENCE_THRESHOLD

    if needs_review:
        missing = [f for f in CRITICAL_FIELDS if not data.get(f)]
        logger.warning(
            f"[{slug}] Low confidence ({score}%) — missing: {', '.join(missing[:5])}"
            + (f" (+{len(missing)-5} more)" if len(missing) > 5 else "")
        )
    else:
        logger.info(f"[{slug}] Confidence: {score}%")

    return score, needs_review

