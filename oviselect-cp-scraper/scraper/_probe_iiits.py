"""Probe IIIT faculty and infrastructure URLs."""
import warnings, requests
from bs4 import BeautifulSoup
warnings.filterwarnings("ignore")

HEADERS = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}

IIITS = [
    ("iiit-allahabad",      "https://www.iiita.ac.in",        ["/faculty/", "/research/labs/"]),
    ("iiit-bhagalpur",      "https://www.iiitbh.ac.in",       ["/faculty", "/people"]),
    ("iiit-bhopal",         "https://www.iiitbhopal.ac.in",   ["/faculty", "/people"]),
    ("iiit-bhubaneswar",    "http://www.iiit-bh.ac.in",       ["/faculty", "/people"]),
    ("iiit-dharwad",        "https://www.iiitdwd.ac.in",      ["/faculty", "/people"]),
    ("iiit-guwahati",       "https://www.iiitg.ac.in",        ["/faculty", "/people"]),
    ("iiit-kalyani",        "https://www.iiitkalyani.ac.in",  ["/faculty", "/people"]),
    ("iiit-kota",           "https://www.iiitkota.ac.in",     ["/faculty", "/people"]),
    ("iiit-kottayam",       "https://www.iiitkottayam.ac.in", ["/faculty", "/people"]),
    ("iiit-lucknow",        "https://www.iiitl.ac.in",        ["/index.php/faculty/", "/faculty"]),
    ("iiit-manipur",        "https://www.iiitmanipur.ac.in",  ["/faculty", "/people"]),
    ("iiit-nagpur",         "http://www.iiitn.ac.in",         ["/index.php/faculty", "/faculty"]),
    ("iiit-naya-raipur",    "https://www.iiitnr.ac.in",       ["/faculty", "/people"]),
    ("iiit-pune",           "https://www.iiitp.ac.in",        ["/index.php/faculty/", "/faculty"]),
    ("iiit-ranchi",         "https://www.iiitranchi.ac.in",   ["/faculty", "/people"]),
    ("iiit-sri-city",       "https://www.iiits.ac.in",        ["/faculty/", "/people"]),
    ("iiit-surat",          "https://www.iiitsurat.ac.in",    ["/faculty", "/people"]),
    ("iiit-trichy",         "https://www.iiitt.ac.in",        ["/faculty", "/people"]),
    ("iiitdm-jabalpur",     "https://www.iiitdmj.ac.in",      ["/faculty/", "/people"]),
    ("iiitdm-kancheepuram", "https://www.iiitdm.ac.in",       ["/faculty/", "/people"]),
    ("iiitdm-kurnool",      "https://www.iiitk.ac.in",        ["/faculty", "/people"]),
    ("iiitm-gwalior",       "https://www.iiitm.ac.in",        ["/index.php/en/faculty", "/faculty"]),
]

print(f"{'Slug':<26} {'URL':<55} {'Faculty?'}")
print("=" * 95)
for slug, base, paths in IIITS:
    found = False
    for p in paths:
        url = base + p
        try:
            r = requests.get(url, headers=HEADERS, timeout=8, verify=False, allow_redirects=True)
            if r.status_code == 200:
                soup = BeautifulSoup(r.text, "html.parser")
                text = soup.get_text(" ", strip=True)
                has_faculty = "Dr." in text or "Prof." in text or "professor" in text.lower()
                names_count = text.count("Dr.") + text.count("Prof.")
                print(f"✅ {slug:<24} {url:<55} names~{names_count}")
                found = True
                break
        except Exception:
            pass
    if not found:
        print(f"❌ {slug:<24} no working faculty page")

