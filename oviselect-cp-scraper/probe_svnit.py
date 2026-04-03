"""Probe SVNIT department pages to understand HTML structure."""
import requests
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}


def probe(url, label):
    r = requests.get(url, headers=HEADERS, timeout=15)
    soup = BeautifulSoup(r.text, "html.parser")
    main = soup.find("main")
    print(f"\n=== {label} (HTTP {r.status_code}) ===")
    if not main:
        print("  NO MAIN TAG")
        return
    teachers = main.find_all("div", class_="teachers")
    author_names = main.find_all("h4", class_="author-name")
    tables = main.find_all("table")
    rows = main.find_all("div", class_="row")
    print(f"  .teachers divs: {len(teachers)}")
    print(f"  h4.author-name: {len(author_names)}")
    print(f"  tables: {len(tables)}")
    print(f"  .row divs: {len(rows)}")
    if author_names:
        print("  First 5 author-names:")
        for h4 in author_names[:5]:
            print(f"    {h4.get_text(strip=True)}")
    elif tables:
        # Show first table's text
        print("  First table sample:")
        for td in tables[0].find_all(["td", "th"])[:10]:
            txt = td.get_text(strip=True)
            if txt:
                print(f"    {txt[:80]}")
    else:
        # Show any h3/h4 headings
        print("  h3/h4 tags:")
        for t in main.find_all(["h3", "h4"])[:8]:
            print(f"    <{t.name}> {t.get_text(strip=True)[:60]}")


probe("https://www.svnit.ac.in/web/department/chemical/faculty-achievements.php", "Chemical Engg - faculty-achievements.php")
probe("https://www.svnit.ac.in/web/department/chemistry/faculty-achievements.php", "Chemistry - faculty-achievements.php")
probe("https://www.svnit.ac.in/web/department/civil/faculty-achievements.php", "Civil - faculty-achievements.php")
probe("https://www.svnit.ac.in/web/department/Electrical/faculty-achievements.php", "Electrical - faculty-achievements.php")
probe("https://www.svnit.ac.in/web/department/Mechanical/faculty-achievements.php", "Mechanical - faculty-achievements.php")
probe("https://www.svnit.ac.in/web/department/physics/achievement-faculty.php", "Physics - achievement-faculty.php")
probe("https://www.svnit.ac.in/web/department/maths/faculty_achievements.php", "Maths - faculty_achievements.php")
probe("https://www.svnit.ac.in/web/department/Electronics/faculty.php", "Electronics - faculty.php")

