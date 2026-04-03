import json, glob, os

files = sorted(glob.glob('data/parsed/*_structured.json'))
print("Total JSON files:", len(files))
print()

total_fac = 0
total_depts = 0
has_research = 0
has_placement = 0
low_conf = []
all_conf = []

for f in files:
    name = os.path.basename(f).replace('_structured.json', '')
    try:
        d = json.load(open(f))
    except Exception as e:
        print("  ERROR reading", name, str(e))
        continue

    depts = d.get('departments') or []
    fac = d.get('total_faculty') or sum(len(dep.get('faculty') or []) for dep in depts)
    conf = d.get('data_confidence_score', 0)
    research = d.get('research') or {}
    has_r = any(research.get(k) for k in ['active_projects', 'total_funding_crores', 'patents_filed', 'publications_per_year'])
    has_p = bool(d.get('avg_package_lpa') or d.get('median_package_lpa'))

    total_fac += fac
    total_depts += len(depts)
    if has_r:
        has_research += 1
    if has_p:
        has_placement += 1
    all_conf.append(conf)
    if conf < 60:
        low_conf.append((name, conf))

avg_conf = sum(all_conf) / len(all_conf) if all_conf else 0
print("Total departments across all colleges:", total_depts)
print("Total faculty across all colleges:    ", total_fac)
print("Colleges with research data:          ", str(has_research) + "/" + str(len(files)))
print("Colleges with placement data:         ", str(has_placement) + "/" + str(len(files)))
print("Average confidence score:             ", round(avg_conf, 1))
print()
print("Low confidence colleges (<60%):")
for name, conf in sorted(low_conf, key=lambda x: x[1]):
    print("  " + str(conf) + "% -- " + name)

