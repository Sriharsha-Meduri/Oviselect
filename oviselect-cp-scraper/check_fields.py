import json, glob, os

files = sorted(glob.glob('data/parsed/*_structured.json'))

fee_fields = [
    'tuition_fee_per_sem', 'hostel_fee_per_sem', 'mess_advance_per_sem',
    'one_time_fees', 'total_institute_fee', 'total_hostel_fee', 'fee_waivers'
]
placement_fields = [
    'avg_package_lpa', 'median_package_lpa', 'highest_package_lpa',
    'overall_placement_pct', 'top_recruiters', 'branch_wise_placement_pct'
]
research_fields = [
    'active_projects', 'total_funding_crores', 'patents_filed',
    'patents_granted', 'publications_per_year', 'phd_students_enrolled'
]
infra_fields = [
    'infrastructure', 'student_activities', 'international_relations'
]
basic_fields = [
    'nirf_overall_rank', 'qs_world_rank', 'established_year',
    'nearest_airport', 'nearest_railway_station', 'official_website'
]

def count_filled(field_list, all_data):
    counts = {}
    for f in field_list:
        filled = 0
        for d in all_data:
            val = d.get(f)
            if val is None:
                # check nested research
                if f in research_fields:
                    val = (d.get('research') or {}).get(f)
            if val is not None and val != [] and val != {}:
                filled += 1
        counts[f] = filled
    return counts

all_data = []
for f in files:
    try:
        all_data.append(json.load(open(f)))
    except:
        pass

n = len(all_data)
print("=" * 55)
print(f"FIELD COVERAGE ACROSS {n} COLLEGES")
print("=" * 55)

print("\n--- FEES ---")
for field, count in count_filled(fee_fields, all_data).items():
    bar = "#" * int(count / n * 20)
    print(f"  {field:<30} {count:>2}/{n}  [{bar:<20}]")

print("\n--- PLACEMENTS ---")
for field, count in count_filled(placement_fields, all_data).items():
    bar = "#" * int(count / n * 20)
    print(f"  {field:<30} {count:>2}/{n}  [{bar:<20}]")

print("\n--- RESEARCH ---")
for field, count in count_filled(research_fields, all_data).items():
    bar = "#" * int(count / n * 20)
    print(f"  {field:<30} {count:>2}/{n}  [{bar:<20}]")

print("\n--- INFRASTRUCTURE / ACTIVITIES ---")
for field, count in count_filled(infra_fields, all_data).items():
    bar = "#" * int(count / n * 20)
    print(f"  {field:<30} {count:>2}/{n}  [{bar:<20}]")

print("\n--- BASIC INFO ---")
for field, count in count_filled(basic_fields, all_data).items():
    bar = "#" * int(count / n * 20)
    print(f"  {field:<30} {count:>2}/{n}  [{bar:<20}]")

print()
# Show IIT BHU as example
bhu = next((d for d in all_data if 'bhu' in (d.get('collegepravesh_url') or '')), None)
if bhu:
    print("--- IIT BHU VARANASI (sample) ---")
    for f in fee_fields:
        print(f"  {f}: {bhu.get(f)}")

