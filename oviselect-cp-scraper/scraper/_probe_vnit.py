import requests
from bs4 import BeautifulSoup
import warnings
warnings.filterwarnings('ignore')

base = 'https://vnit.ac.in'
test_depts = [
    ('Civil Engineering', '/engineering/civil/'),
    ('Computer Science', '/engineering/cse/'),
    ('Electrical Engineering', '/engineering/electrical/'),
    ('Mechanical Engineering', '/engineering/mech/'),
    ('Physics', '/basic_science/phy/'),
    ('Chemistry', '/basic_science/chemistry/'),
    ('Mathematics', '/basic_science/maths/'),
    ('Applied Mechanics', '/engineering/apm/'),
    ('Metallurgical', '/engineering/met/'),
    ('Electronics', '/engineering/eced/'),
    ('IT', '/engineering/it/'),
    ('Chemical Engineering', '/engineering/chemical/'),
]
for name, path in test_depts:
    try:
        r = requests.get(base + path, headers={'User-Agent': 'Mozilla/5.0'}, timeout=8, verify=False)
        soup = BeautifulSoup(r.text, 'html.parser')
        fac_links = [a['href'] for a in soup.find_all('a', href=True)
                     if 'faculty' in a['href'].lower() or 'people' in a['href'].lower()][:3]
        print(f'{name}: {r.status_code}, faculty links: {fac_links}')
    except Exception as e:
        print(f'{name}: ERROR {type(e).__name__}: {e}')

