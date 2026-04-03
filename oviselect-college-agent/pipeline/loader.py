"""Load the list of institutes from Supabase."""

from __future__ import annotations

import os

from dotenv import load_dotenv
from loguru import logger
from supabase import create_client, Client

load_dotenv()


def get_supabase_client() -> Client:
    """Create a Supabase client using service role key."""
    url = os.environ.get("SUPABASE_URL", "")
    key = os.environ.get("SUPABASE_SERVICE_KEY", "")
    if not url or not key:
        raise RuntimeError(
            "Missing SUPABASE_URL or SUPABASE_SERVICE_KEY env vars. "
            "Copy .env.example → .env and fill in the values."
        )
    return create_client(url, key)


def load_institutes() -> list[dict[str, any]]:
    """Fetch all distinct institute names from the Supabase `institutes` table.

    Returns a list of dicts: [{"id": 1, "name": "IIT Bombay"}, ...]
    """
    sb = get_supabase_client()
    resp = sb.table("institutes").select("id, name").order("id").execute()
    institutes = resp.data or []
    logger.info(f"Loaded {len(institutes)} institutes from Supabase")
    return institutes


def classify_institute(name: str) -> str:
    """Classify an institute name into IIT / NIT / IIIT / GFTI."""
    n = name.upper()
    if "IIT " in n or n.startswith("IIT") or "INDIAN INSTITUTE OF TECHNOLOGY" in n:
        return "IIT"
    if "NIT " in n or n.startswith("NIT") or "MNIT" in n or "MNNIT" in n or "MANIT" in n or "SVNIT" in n or "VNIT" in n:
        return "NIT"
    if "IIIT" in n or "INDIAN INSTITUTE OF INFORMATION" in n or "IIITDM" in n or "ABV-IIITM" in n:
        return "IIIT"
    return "GFTI"


if __name__ == "__main__":
    institutes = load_institutes()
    for inst in institutes:
        t = classify_institute(inst["name"])
        print(f"[{t:4s}] {inst['id']:3d}  {inst['name']}")

