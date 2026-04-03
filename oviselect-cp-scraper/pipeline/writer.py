"""Write structured college data to Supabase."""

from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any

from loguru import logger

try:
    from supabase import create_client, Client
except ImportError:
    create_client = None  # type: ignore
    Client = None  # type: ignore


def _get_client() -> Any:
    """Create a Supabase client from environment variables."""
    if create_client is None:
        raise ImportError("supabase package not installed")

    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_KEY")
    if not url or not key:
        raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_KEY must be set in .env")
    return create_client(url, key)


_client: Any = None


def _ensure_client() -> Any:
    global _client
    if _client is None:
        _client = _get_client()
    return _client


def upsert_college(data: dict[str, Any]) -> bool:
    """Upsert a single college row into the college_info table.

    Adds data_sources, last_scraped_at, and collegepravesh_url before upserting.

    Returns:
        True on success, False on failure.
    """
    slug = data.get("_slug", "unknown")
    institute = data.get("institute", "unknown")

    try:
        client = _ensure_client()
    except Exception as e:
        logger.error(f"[{slug}] Supabase client error: {e}")
        return False

    # Add metadata fields
    row = {k: v for k, v in data.items() if not k.startswith("_")}
    row["data_sources"] = ["collegepravesh"]
    row["last_scraped_at"] = datetime.now(timezone.utc).isoformat()
    if slug != "unknown":
        row["collegepravesh_url"] = f"https://www.collegepravesh.com/engineering-colleges/{slug}/"

    try:
        result = (
            client.table("college_info")
            .upsert(row, on_conflict="institute")
            .execute()
        )
        logger.info(f"[{slug}] ✓ Upserted {institute}")
        return True
    except Exception as e:
        logger.error(f"[{slug}] ✗ Upsert failed for {institute}: {e}")
        return False

