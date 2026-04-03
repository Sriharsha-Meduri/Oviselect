"""Validate and compute confidence scores for structured college data."""

from __future__ import annotations

from typing import Any

from loguru import logger
from pydantic import ValidationError

from config import CONFIDENCE_REVIEW_THRESHOLD
from models.college_schema import CollegeInfo


# Fields grouped by importance for confidence scoring
_CRITICAL_FIELDS = [
    "institute_type", "establishment_year", "city", "state",
    "nirf_rank", "total_ug_seats", "tuition_fee_per_sem",
]

_IMPORTANT_FIELDS = [
    "avg_package_lpa", "highest_package_lpa", "placement_percentage",
    "companies_visited", "total_faculty", "student_faculty_ratio",
    "campus_area_acres", "hostel_capacity_boys", "hostel_capacity_girls",
]

_NICE_TO_HAVE_FIELDS = [
    "median_package_lpa", "naac_grade", "coding_club", "tech_fest_name",
    "cultural_fest_name", "reddit_mentions_count", "gsoc_selections_total",
    "international_mous", "incubation_center",
]


def compute_confidence(data: dict[str, Any]) -> float:
    """Compute a 0-100 confidence score based on field coverage.

    Weights: critical=3, important=2, nice-to-have=1.
    """
    total_weight = 0
    filled_weight = 0

    for f in _CRITICAL_FIELDS:
        total_weight += 3
        v = data.get(f)
        if v is not None and v != "" and v != []:
            filled_weight += 3

    for f in _IMPORTANT_FIELDS:
        total_weight += 2
        v = data.get(f)
        if v is not None and v != "" and v != []:
            filled_weight += 2

    for f in _NICE_TO_HAVE_FIELDS:
        total_weight += 1
        v = data.get(f)
        if v is not None and v != "" and v != []:
            filled_weight += 1

    if total_weight == 0:
        return 0.0
    return round((filled_weight / total_weight) * 100, 1)


def validate_college(data: dict[str, Any]) -> tuple[CollegeInfo | None, list[str]]:
    """Validate raw dict against CollegeInfo schema.

    Returns (validated_model, errors).
    If validation succeeds, errors is empty.
    Also computes and sets confidence + needs_review.
    """
    errors: list[str] = []

    # Compute confidence before validation
    confidence = compute_confidence(data)
    data["data_confidence_pct"] = confidence
    data["needs_review"] = confidence < CONFIDENCE_REVIEW_THRESHOLD

    try:
        model = CollegeInfo.model_validate(data)
        logger.info(
            f"✓ {model.institute} validated — confidence {confidence}%"
            f"{' ⚠️  NEEDS REVIEW' if model.needs_review else ''}"
        )
        return model, errors
    except ValidationError as e:
        for err in e.errors():
            field = ".".join(str(x) for x in err["loc"])
            errors.append(f"{field}: {err['msg']}")
        logger.warning(f"✗ Validation failed for {data.get('institute', '?')}: {errors}")
        return None, errors

