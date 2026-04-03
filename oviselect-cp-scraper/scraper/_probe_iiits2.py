"""Deeper probe for IIIT faculty page structures."""
import warnings, requests, re
from bs4 import BeautifulSoup
warnings.filterwarnings("ignore")
HEADERS = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}

def get(url, timeout=10):
    try:
        return requests.get(url, headers=HEADERS, timeout=timeout, verify=False, allow_redirects=True)
    except Exception as e:
        return None

def names_in(html):
    return re.findall(r"(?:Dr\.|Prof\.|Mr\.|Ms\.)\s+[A-Z][a-zA-Z][a-zA-Z\s\.]+", html)

# IIIT Naya Raipur faculty
r = get("https://www.iiitnr.ac.in/faculty")
if r and r.status_code == 200:
    soup = BeautifulSoup(r.text, "html.parser")
    text = soup.get_text(" ", strip=True)
    ns = names_in(text)
    print(f"IIIT Naya Raipur ({len(ns)} names):")
    for n in ns[:10]: print(f"  {n.strip()[:70]}")

# IIITDM Kancheepuram - check alternate faculty pages
print("\n--- IIITDM Kancheepuram paths ---")
for path in ["/int/depts/cse/", "/academics/faculty/", "/cse/faculty", "/ece/faculty", "/people/"]:
    url = "https://www.iiitdm.ac.in" + path
    r2 = get(url, timeout=5)
    if r2:
        n = r2.text.count("Dr.") + r2.text.count("Prof.")
        print(f"  {path}: HTTP {r2.status_code} | names~{n} | len={len(r2.text)}")
    else:
        print(f"  {path}: timeout")

# IIIT Kota - look at li elements with Dr./Prof.
r3 = get("https://www.iiitkota.ac.in/faculty")
if r3 and r3.status_code == 200:
    soup3 = BeautifulSoup(r3.text, "html.parser")
    lis = soup3.find_all("li")
    print(f"\nIIIT Kota lis: {len(lis)}")
    for li in lis[:10]:
        t = li.get_text(" ", strip=True)[:100]
        if "Dr." in t or "Prof." in t:
            print(f"  {t}")

# IIIT Lucknow - check faculty structure
r4 = get("https://www.iiitl.ac.in/index.php/faculty/")
if r4 and r4.status_code == 200:
    soup4 = BeautifulSoup(r4.text, "html.parser")
    rows = soup4.find_all("tr")
    print(f"\nIIIT Lucknow rows: {len(rows)}")
    for row in rows[:5]:
        cells = [c.get_text(" ", strip=True)[:80] for c in row.find_all(["td","th"])]
        if cells and any("Dr." in c or "Prof." in c for c in cells):
            print(f"  {cells[:3]}")
    # Also try sections
    text4 = soup4.get_text(" ", strip=True)
    ns4 = names_in(text4)
    print(f"  Names from text: {ns4[:8]}")

# IIIT Kalyani - look at section structure
r5 = get("https://www.iiitkalyani.ac.in/faculty")
if r5 and r5.status_code == 200:
    soup5 = BeautifulSoup(r5.text, "html.parser")
    sections = soup5.find_all("section")
    print(f"\nIIIT Kalyani sections: {len(sections)}")
    for sec in sections[:3]:
        t = sec.get_text(" ", strip=True)[:300]
        if "Dr." in t or "Prof." in t:
            print(f"  {t[:250]}")

