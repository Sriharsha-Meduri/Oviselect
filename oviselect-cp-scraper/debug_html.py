from bs4 import BeautifulSoup
html = open("data/cache/iit-bombay.html","r").read()
soup = BeautifulSoup(html, "lxml")

pr = soup.find("p", class_="cp-clg-h", string=lambda t: t and "recruiter" in t.lower())
print("Found:", pr.get_text(strip=True) if pr else "NONE")
if pr:
    for sib in pr.next_siblings:
        if hasattr(sib, "get") and sib.get("class") and "cp-clg-h" in sib.get("class", []):
            break
        if hasattr(sib, "name") and sib.name:
            cls = sib.get("class", [])
            txt = sib.get_text(strip=True)[:80]
            print(f"  tag={sib.name} cls={cls} text={txt}")

# Also check "Also Known as" and "ADDRESS" content
print("\n--- ALSO KNOWN AS ---")
aka = soup.find("p", class_="cp-clg-h", string=lambda t: t and "also known" in t.lower())
if aka:
    for sib in aka.next_siblings:
        if hasattr(sib, "get") and sib.get("class") and "cp-clg-h" in sib.get("class", []):
            break
        if hasattr(sib, "name") and sib.name:
            cls = sib.get("class", [])
            txt = sib.get_text(strip=True)[:80]
            print(f"  tag={sib.name} cls={cls} text={txt}")

print("\n--- ADDRESS ---")
addr = soup.find("p", class_="cp-clg-h", string=lambda t: t and "address" in t.lower())
if addr:
    for sib in addr.next_siblings:
        if hasattr(sib, "get") and sib.get("class") and "cp-clg-h" in sib.get("class", []):
            break
        if hasattr(sib, "name") and sib.name:
            cls = sib.get("class", [])
            txt = sib.get_text(strip=True)[:80]
            print(f"  tag={sib.name} cls={cls} text={txt}")

print("\n--- CAMPUS FACILITIES ---")
cf = soup.find("p", class_="cp-clg-h", string=lambda t: t and "campus" in t.lower())
if cf:
    for sib in cf.next_siblings:
        if hasattr(sib, "get") and sib.get("class") and "cp-clg-h" in sib.get("class", []):
            break
        if hasattr(sib, "name") and sib.name:
            cls = sib.get("class", [])
            txt = sib.get_text(strip=True)[:80]
            print(f"  tag={sib.name} cls={cls} text={txt}")

