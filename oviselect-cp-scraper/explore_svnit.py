"""Explore SVNIT department page structure."""
import requests
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}

DEPT_URLS = {
    "Artificial Intelligence": "https://www.svnit.ac.in/web/department/ai/",
    "Chemical Engineering": "https://www.svnit.ac.in/web/department/chemical/",
    "Chemistry": "https://www.svnit.ac.in/web/department/chemistry/",
    "Civil Engineering": "https://www.svnit.ac.in/web/department/civil/",
    "Computer Science and Engineering": "https://www.svnit.ac.in/web/department/computer/",
    "Electrical Engineering": "https://www.svnit.ac.in/web/department/Electrical/",
    "Electronics Engineering": "https://www.svnit.ac.in/web/department/Electronics/",
    "Humanities and Social Sciences": "https://www.svnit.ac.in/web/department/humanities/index.php",
    "Management Studies": "https://www.svnit.ac.in/web/department/management/",
    "Mathematics": "https://www.svnit.ac.in/web/department/maths/",
    "Mechanical Engineering": "https://www.svnit.ac.in/web/department/Mechanical/",
    "Physics": "https://www.svnit.ac.in/web/department/physics/",
}

def explore_dept(name, url):
    print(f"\n{'='*60}")
    print(f"DEPT: {name}")
    print(f"URL:  {url}")
    try:
        r = requests.get(url, timeout=15, headers=HEADERS)
        soup = BeautifulSoup(r.text, "html.parser")
        
        # Find all sub-links within this department
        base = url.rstrip("/")
        dept_path = "/web/department/"
        links = {}
        for a in soup.find_all("a", href=True):
            href = a["href"]
            text = a.get_text(strip=True)
            if not text or len(text) < 2:
                continue
            # Only show dept-relative links
            if dept_path in href or href.startswith("faculty") or href.startswith("research"):
                links[text[:60]] = href[:120]
        
        print("Sub-links:")
        for t, h in sorted(links.items()):
            print(f"  {t!r}: {h}")
        
        # Also print page headings
        headings = [tag.get_text(strip=True) for tag in soup.find_all(["h1","h2","h3"]) if tag.get_text(strip=True)]
        print(f"Headings: {headings[:10]}")
        
    except Exception as e:
        print(f"  ERROR: {e}")

def explore_faculty_page(dept_name, faculty_url):
    print(f"\n{'='*60}")
    print(f"FACULTY PAGE: {dept_name}")
    print(f"URL: {faculty_url}")
    try:
        r = requests.get(faculty_url, timeout=15, headers=HEADERS)
        soup = BeautifulSoup(r.text, "html.parser")
        text = soup.get_text(separator="\n", strip=True)
        # Print first 3000 chars to understand structure
        print("TEXT PREVIEW:")
        print(text[:3000])
        # Look for any table structure
        tables = soup.find_all("table")
        print(f"\nTables found: {len(tables)}")
        for i, tbl in enumerate(tables[:2]):
            rows = tbl.find_all("tr")
            print(f"  Table {i}: {len(rows)} rows")
            for row in rows[:5]:
                cells = [td.get_text(strip=True)[:40] for td in row.find_all(["td","th"])]
                print(f"    {cells}")
    except Exception as e:
        print(f"  ERROR: {e}")

def find_dept_subpages(dept_name, dept_url):
    """Find all sub-page links in a department."""
    print(f"\n{'='*50}")
    print(f"DEPT: {dept_name} ({dept_url})")
    try:
        r = requests.get(dept_url, timeout=15, headers=HEADERS)
        soup = BeautifulSoup(r.text, "html.parser")
        base = dept_url.rstrip("/")
        sub_links = {}
        for a in soup.find_all("a", href=True):
            href = a["href"]
            text = a.get_text(strip=True)
            # Only relative links that are dept-local
            if href and not href.startswith("http") and not href.startswith("//") and not href.startswith("#"):
                if "/" not in href or href.startswith("./"):
                    sub_links[text] = f"{base}/{href.lstrip('./')}"
        print("Sub-pages:")
        for t, h in sorted(sub_links.items()):
            print(f"  {t!r}: {h}")
    except Exception as e:
        print(f"  ERROR: {e}")

if __name__ == "__main__":
    for name, url in DEPT_URLS.items():
        find_dept_subpages(name, url)

