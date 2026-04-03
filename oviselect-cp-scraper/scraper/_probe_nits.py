"""Probe script to find correct faculty URLs for NITs returning 0 faculty."""
import requests
from bs4 import BeautifulSoup
import warnings
warnings.filterwarnings('ignore')

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'}

def get(url, **kw):
    try:
        r = requests.get(url, headers=headers, timeout=10, **kw)
        return r
    except Exception as e:
        print(f"  ERROR: {type(e).__name__}: {str(e)[:80]}")
        return None

# ── NIT CALICUT ──────────────────────────────────────────────────────────────
print("\n=== NIT CALICUT ===")
r = get("https://nitc.ac.in/department/computer-science-amp-engineering")
if r:
    print(f"Dept page: {r.status_code}")
    soup = BeautifulSoup(r.text, 'html.parser')
    fac_links = [(a.get_text().strip()[:40], a['href']) for a in soup.find_all('a', href=True)
                 if 'faculty' in a.get('href','').lower() or 'people' in a.get('href','').lower()][:5]
    for t, h in fac_links:
        print(f"  link: {t!r} -> {h}")

r2 = get("https://nitc.ac.in/department/computer-science-amp-engineering/faculty")
if r2:
    print(f"Faculty page: {r2.status_code}, len: {len(r2.text)}")
    if r2.status_code == 200:
        s = BeautifulSoup(r2.text, 'html.parser')
        for tag in s.find_all(['h3','h4','strong'])[:8]:
            print(f"  {tag.name}: {tag.get_text().strip()[:60]}")

# ── NIT PATNA ────────────────────────────────────────────────────────────────
print("\n=== NIT PATNA ===")
test_urls = [
    "https://www.nitp.ac.in/Department/CS",
    "https://www.nitp.ac.in/dept/cs",
    "https://nitp.ac.in/dept/cs",
    "https://www.nitp.ac.in/content/department-computer-science",
]
for url in test_urls:
    r = get(url)
    if r:
        print(f"  {url}: {r.status_code}")

# Try main page for dept links
r = get("https://www.nitp.ac.in/")
if r and r.status_code == 200:
    soup = BeautifulSoup(r.text, 'html.parser')
    dept_links = [(a.get_text().strip()[:40], a.get('href','')) for a in soup.find_all('a', href=True)
                  if any(k in a.get('href','').lower() for k in ['dept', 'department', 'faculty'])][:10]
    for t, h in dept_links:
        print(f"  link: {t!r} -> {h}")

# ── NIT SRINAGAR ─────────────────────────────────────────────────────────────
print("\n=== NIT SRINAGAR ===")
test_urls_sri = [
    "https://nitsri.ac.in/Department/Pages/FacultyList.aspx?nDeptID=c",
    "https://nitsri.ac.in/Department/Pages/FacultyList.aspx?nDeptID=cs",
    "https://nitsri.ac.in/Department/Deptindex.aspx?page=a&ItemID=cs&nDeptID=cs",
    "https://nitsri.ac.in/faculty",
    "https://nitsri.ac.in/Department/",
]
for url in test_urls_sri:
    r = get(url)
    if r:
        print(f"  {url}: {r.status_code}, len={len(r.text)}")
        if r.status_code == 200 and len(r.text) > 5000:
            soup = BeautifulSoup(r.text, 'html.parser')
            for tag in soup.find_all(['h3','h4','td'])[:5]:
                print(f"    {tag.name}: {tag.get_text().strip()[:50]}")

# ── NIT ROURKELA ─────────────────────────────────────────────────────────────
print("\n=== NIT ROURKELA ===")
test_rk = [
    "https://nitrkl.ac.in/FacultyStaff/Faculty/",
    "http://nitrkl.ac.in/FacultyStaff/Faculty/",
    "https://www.nitrkl.ac.in/FacultyStaff/Faculty/",
    "https://nitrkl.ac.in/Academics/Departments",
]
for url in test_rk:
    r = get(url, verify=False)
    if r:
        print(f"  {url}: {r.status_code}, len={len(r.text)}")
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, 'html.parser')
            names = [tag.get_text().strip()[:40] for tag in soup.find_all(['h3','h4'])[:3]]
            print(f"    h3/h4: {names}")

print("\nDone.")

