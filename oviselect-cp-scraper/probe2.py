import requests
from bs4 import BeautifulSoup

HEADERS = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'}

PAGES = [
    ('https://www.svnit.ac.in/web/department/chemical/faculty-achievements.php', 'Chemical'),
    ('https://www.svnit.ac.in/web/department/chemistry/faculty-achievements.php', 'Chemistry'),
    ('https://www.svnit.ac.in/web/department/civil/faculty-achievements.php', 'Civil'),
    ('https://www.svnit.ac.in/web/department/Electrical/faculty-achievements.php', 'Electrical'),
    ('https://www.svnit.ac.in/web/department/Mechanical/faculty-achievements.php', 'Mechanical'),
    ('https://www.svnit.ac.in/web/department/physics/achievement-faculty.php', 'Physics'),
    ('https://www.svnit.ac.in/web/department/maths/faculty_achievements.php', 'Maths'),
    ('https://www.svnit.ac.in/web/department/Electronics/faculty.php', 'Electronics'),
]

for url, label in PAGES:
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(r.text, 'html.parser')
        main = soup.find('main')
        if not main:
            print(f"{label} -> NO <main> tag (status {r.status_code})")
            continue
        teachers = main.find_all('div', class_='teachers')
        names_h4 = main.find_all('h4', class_='author-name')
        tables = main.find_all('table')
        rows_divs = main.find_all('div', class_='row')
        print(f"{label} -> teachers={len(teachers)}, author-name h4={len(names_h4)}, tables={len(tables)}, .row divs={len(rows_divs)}")
        if names_h4:
            print(f"  First name: {names_h4[0].get_text(strip=True)}")
        elif tables:
            row = tables[0].find('tr')
            if row:
                print(f"  First table row: {row.get_text(strip=True)[:100]}")
        # Show first 500 chars of main content for debugging
        print(f"  Main snippet: {main.get_text(separator=' ', strip=True)[:200]}")
        print()
    except Exception as e:
        print(f"{label} -> ERROR: {e}")

