"""Quick test of NIT Calicut faculty scraper fix."""
import sys
sys.path.insert(0, ".")
import warnings
warnings.filterwarnings("ignore")

from scraper.nit_deep_scraper import scrape_nit_calicut, _scrape_nitc_dept

print("Testing NIT Calicut faculty scraper (2 departments only)...")

# Test 2 departments to verify fix
depts = {
    "Civil Engineering": "civil-engineering",
    "Computer Science & Engineering": "computer-science-amp-engineering",
}

total_faculty = 0
for dept_name, slug in depts.items():
    dept = _scrape_nitc_dept(dept_name, slug)
    fac = dept.get("faculty", [])
    total_faculty += len(fac)
    print(f"\n  {dept_name}: {len(fac)} faculty")
    for m in fac[:5]:
        print(f"    - {m.get('name')} [{m.get('designation')}]")

print(f"\nTotal faculty found in 2 test departments: {total_faculty}")
if total_faculty > 0:
    print("✅ NIT Calicut fix WORKS")
else:
    print("❌ NIT Calicut still returning 0 faculty (JS-rendered)")

