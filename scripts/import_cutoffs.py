"""
Import cleaned JoSAA cutoff CSVs into Supabase (normalized schema).

Usage:
  1. Run  python3 scripts/clean_csvs.py  first to generate data/clean/
  2. Set SUPABASE_URL and SUPABASE_SERVICE_KEY env vars.
  3. Run:  python3 scripts/import_cutoffs.py

Requires:  pip install supabase
"""

import csv
import os
import re
import sys
from pathlib import Path

from supabase import create_client, Client

# ── Config ───────────────────────────────────────────────────
SUPABASE_URL = os.environ.get("SUPABASE_URL", "")  # Set in .env: https://your-project-ref.supabase.co
# ⚠️  Use the SERVICE ROLE key (not the anon key) — needed for INSERT with RLS
SUPABASE_SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_KEY", "")

DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "clean"
FILENAME_PATTERN = re.compile(r"(\d{4})_Round_(\d+)\.csv", re.IGNORECASE)
BATCH_SIZE = 500  # rows per upsert call


def import_lookup(supabase: Client, table: str, filepath: Path):
    """Import a lookup CSV into Supabase."""
    rows = []
    with open(filepath, "r", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            parsed = {}
            for k, v in row.items():
                try:
                    parsed[k] = int(v)
                except ValueError:
                    parsed[k] = v
            rows.append(parsed)
    for i in range(0, len(rows), BATCH_SIZE):
        supabase.table(table).insert(rows[i:i+BATCH_SIZE]).execute()
    print(f"  {table}: {len(rows)} rows")
    return len(rows)


def process_file(supabase: Client, filepath: Path, year: int, round_num: int):
    """Read one normalized CSV and insert rows into Supabase."""
    rows = []
    with open(filepath, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append({
                "year": year,
                "round": round_num,
                "iid": int(row["iid"]),
                "pid": int(row["pid"]),
                "quota": row["quota"],
                "seat": row["seat"],
                "gender": row["g"],
                "open": int(row["or"]),
                "close": int(row["cr"]),
                "prep": int(row["p"]),
            })

    total = len(rows)
    for i in range(0, total, BATCH_SIZE):
        supabase.table("cutoffs").insert(rows[i:i+BATCH_SIZE]).execute()
        print(f"  Inserted {min(i + BATCH_SIZE, total)}/{total} rows")
    return total


def main():
    if not SUPABASE_SERVICE_KEY:
        print("ERROR: Set SUPABASE_SERVICE_KEY env var (Dashboard → Settings → API → service_role key)")
        print("       export SUPABASE_SERVICE_KEY='eyJ...'")
        sys.exit(1)

    if not DATA_DIR.exists():
        print(f"ERROR: Data directory not found: {DATA_DIR}")
        print("       Run  python3 scripts/clean_csvs.py  first.")
        sys.exit(1)

    supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

    # Import lookup tables first
    print("Importing lookup tables...")
    inst_file = DATA_DIR / "_institutes.csv"
    prog_file = DATA_DIR / "_programs.csv"
    if inst_file.exists():
        import_lookup(supabase, "institutes", inst_file)
    if prog_file.exists():
        import_lookup(supabase, "programs", prog_file)

    # Import cutoff files
    csv_files = sorted(DATA_DIR.glob("*.csv"))
    grand_total = 0
    for filepath in csv_files:
        match = FILENAME_PATTERN.match(filepath.name)
        if not match:
            continue  # skip lookup files

        year = int(match.group(1))
        round_num = int(match.group(2))
        print(f"\n📄 {filepath.name} → year={year}, round={round_num}")

        count = process_file(supabase, filepath, year, round_num)
        grand_total += count

    print(f"\n✅ Done! Imported {grand_total} total rows.")


if __name__ == "__main__":
    main()

