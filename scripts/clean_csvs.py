#!/usr/bin/env python3
"""Clean JoSAA cutoff CSVs to reduce file size.

Changes:
- Institute names: abbreviate common prefixes (IIT, NIT, IIIT, etc.)
- Program names: extract field name only, move degree type to short code column
- Gender: F / N
- Seat Type: compact (remove spaces around PwD)
- Ranks: integer columns + boolean P (preparatory) flag
- Remove double spaces
"""

import csv, re, sys, os, glob

# ── Institute abbreviations ──────────────────────────────────────────
INST_ABBREVS = [
    ("Indian Institute  of Technology", "IIT"),
    ("Indian Institute of Technology", "IIT"),
    ("National Institute of Technology", "NIT"),
    ("Indian Institute of Information Technology", "IIIT"),
    ("Indian Institute  of Information Technology", "IIIT"),
    ("Atal Bihari Vajpayee Indian Institute of Information Technology & Management", "ABV-IIITM"),
    ("International Institute of Information Technology", "IntIIIT"),
    ("Maulana Azad National Institute of Technology", "MANIT"),
    ("Visvesvaraya National Institute of Technology", "VNIT"),
    ("Sardar Vallabhbhai National Institute of Technology", "SVNIT"),
    ("Motilal Nehru National Institute of Technology", "MNNIT"),
    ("Malaviya National Institute of Technology", "MNIT"),
    ("Dr. B R Ambedkar National Institute of Technology", "Dr.BRAMNIT"),
    ("School of Planning and Architecture", "SPA"),
    ("Birla Institute of Technology", "BIT"),
    ("Indian School of Mines", "ISM"),
    ("Institute of Infrastructure Technology Research and Management", "IITRAM"),
    ("Jawaharlal Nehru University", "JNU"),
    ("University of Hyderabad", "UoH"),
    ("Punjab Engineering College", "PEC"),
    ("Harcourt Butler Technical University", "HBTU"),
    ("International Institute of Information Technology, Naya Raipur", "IntIIIT Naya Raipur"),
]

# ── Degree type short codes ──────────────────────────────────────────
DEGREE_MAP = {
    "Bachelor of Technology": "BTech",
    "B. Tech / B. Tech (Hons.)": "BTech",
    "Bachelor of Architecture": "BArch",
    "Bachelor of Design": "BDes",
    "Bachelor of Planning": "BPlan",
    "Bachelor of Science": "BS",
    "Integrated Master of Science": "IMS",
    "Integrated Master of Technology": "IMTech",
    "Integrated Masters in Technology": "IMTech",
    "Integrated B. Tech. and M. Tech.": "BM.Tech",
    "Integrated B. Tech. and MBA": "BT+MBA",
    "B.Tech. + M.Tech./MS (Dual Degree)": "BM.Tech",
    "Bachelor and Master of Technology (Dual Degree)": "BM.Tech",
    "Bachelor of Technology and MBA (Dual Degree)": "BT+MBA",
    "Bachelor of Science and Master of Science (Dual Degree)": "BS+MS",
    "Bachelor of Science and MBA (Dual Degree)": "BS+MBA",
}

GENDER_MAP = {
    "Gender-Neutral": "N",
    "Female-only (including Supernumerary)": "F",
}

def shorten_institute(name: str) -> str:
    name = re.sub(r'\s{2,}', ' ', name).strip()
    for long, short in INST_ABBREVS:
        if name.startswith(long):
            name = short + name[len(long):]
            break
    # Remove trailing commas/spaces
    return name.strip().rstrip(',').strip()

def parse_program(prog: str):
    """Return (field_name, duration_years, degree_code)."""
    m = re.match(r'^(.+?)\s*\((\d+)\s+Years?,\s*(.+)\)\s*$', prog)
    if m:
        field = m.group(1).strip()
        years = int(m.group(2))
        degree = DEGREE_MAP.get(m.group(3).strip(), m.group(3).strip())
        return field, years, degree
    return prog.strip(), 4, "BTech"

def parse_rank(rank_str: str):
    """Return (int_rank, is_preparatory)."""
    rank_str = rank_str.strip()
    if rank_str.endswith('P'):
        return int(float(rank_str[:-1])), 1
    return int(float(rank_str)), 0

def clean_seat(seat: str) -> str:
    return seat.strip().replace(' (PwD)', '-PwD')

def find_header_row(filepath):
    """Find the first non-empty row (the header) and return its line index."""
    with open(filepath, newline='', encoding='utf-8-sig') as f:
        for i, row in enumerate(csv.reader(f)):
            if any(c.strip() for c in row):
                return i
    return 0

def open_csv_skip_blanks(filepath):
    """Open a CSV, skip leading blank rows, yield (header, reader)."""
    f = open(filepath, newline='', encoding='utf-8-sig')
    reader = csv.reader(f)
    for row in reader:
        if any(c.strip() for c in row):
            header = row
            return f, header, reader
    return f, None, reader

def discover_files(data_dir='data'):
    """Find all raw CSV files and return list of (filepath, year, round)."""
    results = []
    # Standard pattern: 2024_Round_1.csv or 2023Round_1.csv
    for fp in glob.glob(os.path.join(data_dir, '20*ound*.csv')):
        m = re.match(r'(\d{4})[_ ]?Round[_ ]?(\d+)\.csv', os.path.basename(fp), re.I)
        if m:
            results.append((fp, int(m.group(1)), int(m.group(2))))
    # 2025 irregular patterns
    for fp in glob.glob(os.path.join(data_dir, '*.csv')):
        basename = os.path.basename(fp)
        if basename.startswith('_') or '/clean/' in fp:
            continue
        # Already matched above?
        if any(r[0] == fp for r in results):
            continue
        # Try patterns: "2025_round1.csv", "2025 r4.csv", "r2 2025.csv", "r5 2025.csv"
        m = re.match(r'(\d{4})[_ ]?r(?:ound)?(\d+)\.csv', basename, re.I)
        if not m:
            m = re.match(r'r(\d+)[_ ](\d{4})\.csv', basename, re.I)
            if m:
                results.append((fp, int(m.group(2)), int(m.group(1))))
                continue
        if m:
            results.append((fp, int(m.group(1)), int(m.group(2))))
    results.sort(key=lambda x: (x[1], x[2]))
    return results

def collect_all_lookups(files_info):
    """First pass: collect every unique inst/prog across ALL raw files,
       then assign IDs alphabetically for deterministic results."""
    inst_set = set()
    prog_set = set()

    for filepath, year, rnd in files_info:
        f, header, reader = open_csv_skip_blanks(filepath)
        if not header:
            f.close()
            continue
        for row in reader:
            if not any(c.strip() for c in row):
                continue
            if len(row) < 7 or not row[5].strip() or not row[6].strip():
                continue
            inst_set.add(shorten_institute(row[0]))
            field, years, deg = parse_program(row[1])
            prog_set.add((field, deg, years))
        f.close()

    # Sort alphabetically and assign IDs 1..N
    inst_list = sorted(inst_set)
    prog_list = sorted(prog_set)
    inst_map = {name: i + 1 for i, name in enumerate(inst_list)}
    prog_map = {key: i + 1 for i, key in enumerate(prog_list)}
    return inst_list, inst_map, prog_list, prog_map

def write_lookup_csvs(outdir, inst_list, inst_map, prog_list, prog_map):
    with open(os.path.join(outdir, '_institutes.csv'), 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['id', 'name'])
        for name in inst_list:
            w.writerow([inst_map[name], name])
    with open(os.path.join(outdir, '_programs.csv'), 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['id', 'name', 'deg', 'yrs'])
        for (field, deg, yrs) in prog_list:
            w.writerow([prog_map[(field, deg, yrs)], field, deg, yrs])

def process_file(inpath, outpath, inst_map, prog_map):
    f, header, reader = open_csv_skip_blanks(inpath)
    if not header:
        f.close()
        return
    with open(outpath, 'w', newline='') as fout:
        writer = csv.writer(fout)
        writer.writerow(['iid', 'pid', 'quota', 'seat', 'g', 'or', 'cr', 'p'])
        for row in reader:
            if not any(c.strip() for c in row):
                continue
            # Skip junk rows (e.g. "Terms and Conditions" footer)
            if len(row) < 7 or not row[5].strip() or not row[6].strip():
                continue
            try:
                inst = shorten_institute(row[0])
                field, years, deg = parse_program(row[1])
                quota = row[2].strip()
                seat = clean_seat(row[3])
                gender = GENDER_MAP.get(row[4].strip(), row[4].strip())
                o_rank, o_prep = parse_rank(row[5])
                c_rank, c_prep = parse_rank(row[6])
                prep = 1 if (o_prep or c_prep) else 0
                iid = inst_map[inst]
                pid = prog_map[(field, deg, years)]
                writer.writerow([iid, pid, quota, seat, gender, o_rank, c_rank, prep])
            except (ValueError, KeyError) as e:
                print(f"    SKIP row in {os.path.basename(inpath)}: {e}")
    f.close()

def main():
    os.makedirs('data/clean', exist_ok=True)
    files_info = discover_files('data')
    if not files_info:
        print("No CSV files found in data/"); sys.exit(1)

    print(f"Found {len(files_info)} files:")
    for fp, year, rnd in files_info:
        print(f"  {os.path.basename(fp)} → {year} Round {rnd}")

    print("\nPass 1: building lookup tables (alphabetically sorted IDs)...")
    inst_list, inst_map, prog_list, prog_map = collect_all_lookups(files_info)
    write_lookup_csvs('data/clean', inst_list, inst_map, prog_list, prog_map)
    print(f"  Total: {len(inst_list)} institutes, {len(prog_list)} programs")

    print("\nPass 2: writing normalized CSVs...")
    total_before = 0
    total_after = 0
    for filepath, year, rnd in files_info:
        # Standardize output filename
        out_name = f"{year}_Round_{rnd}.csv"
        out = os.path.join('data/clean', out_name)
        process_file(filepath, out, inst_map, prog_map)
        before = os.path.getsize(filepath)
        after = os.path.getsize(out)
        total_before += before
        total_after += after
        print(f"  {os.path.basename(filepath):25s} → {out_name:25s}  {before/1024:.0f}KB → {after/1024:.0f}KB  ({100*(1-after/before):.0f}% smaller)")

    lookup_size = os.path.getsize('data/clean/_institutes.csv') + os.path.getsize('data/clean/_programs.csv')
    total_after += lookup_size
    print(f"\n  Lookup tables: {lookup_size/1024:.0f}KB")
    print(f"  TOTAL: {total_before/1024:.0f}KB → {total_after/1024:.0f}KB  ({100*(1-total_after/total_before):.0f}% reduction)")

if __name__ == '__main__':
    main()

