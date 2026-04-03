"""Runner: scrape SVNIT departments and update nit-surat_structured.json."""

import json
from pathlib import Path
from datetime import datetime, timezone

from loguru import logger
from scraper.svnit_scraper import scrape_svnit_departments

STRUCTURED_PATH = Path("data/parsed/nit-surat_structured.json")


def main():
    logger.info("Starting SVNIT deep-scrape for all departments...")

    # Load existing structured JSON
    if not STRUCTURED_PATH.exists():
        logger.error(f"Structured JSON not found: {STRUCTURED_PATH}")
        return

    with open(STRUCTURED_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Scrape all departments
    departments = scrape_svnit_departments()

    if not departments:
        logger.error("No department data was scraped — aborting update.")
        return

    # Count totals
    total_faculty = sum(d.get("faculty_count", 0) for d in departments)
    depts_with_hod = sum(1 for d in departments if d.get("hod_name"))
    depts_with_faculty = sum(1 for d in departments if d.get("faculty_count", 0) > 0)

    logger.info(
        f"Scraped {len(departments)} departments | "
        f"HODs found: {depts_with_hod} | "
        f"Total faculty: {total_faculty} | "
        f"Depts with faculty data: {depts_with_faculty}"
    )

    # Merge into structured JSON
    data["departments"] = departments
    data["total_faculty_count"] = total_faculty

    # Update metadata
    if "data_sources" not in data or data["data_sources"] is None:
        data["data_sources"] = []
    if "official_website" not in data["data_sources"]:
        data["data_sources"].append("official_website")
    if "svnit_deep_scrape" not in data["data_sources"]:
        data["data_sources"].append("svnit_deep_scrape")

    data["last_scraped_at"] = datetime.now(timezone.utc).isoformat()

    # Write updated JSON
    with open(STRUCTURED_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    logger.success(f"Updated {STRUCTURED_PATH} with {len(departments)} departments and {total_faculty} faculty members.")

    # Print summary
    print("\n" + "="*60)
    print("SVNIT Department Summary")
    print("="*60)
    for dept in departments:
        name = dept.get("name", "Unknown")
        hod = dept.get("hod_name", "—")
        hod_d = dept.get("hod_designation", "")
        fac_count = dept.get("faculty_count", 0)
        labs_count = len(dept.get("labs", []))
        print(f"\n  {name}")
        print(f"    HoD: {hod} ({hod_d})")
        print(f"    Faculty: {fac_count} | Labs: {labs_count}")
        if dept.get("research_projects"):
            print(f"    R&D Projects listed: {len(dept['research_projects'])}")

    print(f"\n{'='*60}")
    print(f"Total departments: {len(departments)}")
    print(f"Total faculty:     {total_faculty}")
    print(f"HoDs identified:   {depts_with_hod}")
    print(f"Output file:       {STRUCTURED_PATH}")
    print("="*60)


if __name__ == "__main__":
    main()

