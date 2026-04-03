"""Local JSON file cache — one file per college per stage.

Cache layout:
    data/cache/{slug}/{stage}.json

Where slug = sanitized college name, stage = research query key or 'structured' / 'reddit'.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Optional

from loguru import logger

from config import CACHE_DIR


def _slug(name: str) -> str:
    """Convert a college name to a filesystem-safe slug."""
    s = name.lower().strip()
    s = re.sub(r"[^a-z0-9]+", "_", s)
    return s.strip("_")[:80]


def cache_path(college: str, stage: str) -> Path:
    """Return the cache file path for a given college + stage."""
    return CACHE_DIR / _slug(college) / f"{stage}.json"


def has_cache(college: str, stage: str) -> bool:
    """Check if a cached result exists."""
    return cache_path(college, stage).exists()


def read_cache(college: str, stage: str) -> Optional[dict[str, Any]]:
    """Read cached JSON data. Returns None if not cached."""
    fp = cache_path(college, stage)
    if not fp.exists():
        return None
    try:
        with open(fp, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        logger.warning(f"Cache read error for {college}/{stage}: {e}")
        return None


def write_cache(college: str, stage: str, data: Any) -> None:
    """Write data to cache as JSON."""
    fp = cache_path(college, stage)
    fp.parent.mkdir(parents=True, exist_ok=True)
    with open(fp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False, default=str)
    logger.debug(f"Cached {college}/{stage}")


def clear_cache(college: str) -> int:
    """Delete all cache files for a college. Returns count of files removed."""
    d = CACHE_DIR / _slug(college)
    if not d.exists():
        return 0
    count = 0
    for f in d.iterdir():
        f.unlink()
        count += 1
    d.rmdir()
    return count

