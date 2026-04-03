"""Reddit search query templates and target subreddits."""

# Subreddits to search for college discussions
SUBREDDITS = [
    "Btechtards",
    "JEENEETards",
    "developersIndia",
    "india",
    "IITJEE",
    "indian_academia",
]

# Query suffixes to append to the college short name
QUERY_SUFFIXES = [
    "placements",
    "hostel",
    "campus",
    "coding culture",
    "faculty",
    "package",
    "review",
    "experience",
]

# Short name aliases for colleges (used in Reddit search queries)
# Maps official name → common Reddit abbreviations
SHORT_NAMES: dict[str, list[str]] = {
    "IIT Bombay": ["IITB", "IIT Bombay"],
    "IIT Delhi": ["IITD", "IIT Delhi"],
    "IIT Madras": ["IITM", "IIT Madras"],
    "IIT Kanpur": ["IITK", "IIT Kanpur"],
    "IIT Kharagpur": ["IITKGP", "IIT Kharagpur"],
    "IIT Roorkee": ["IITR", "IIT Roorkee"],
    "IIT Guwahati": ["IITG", "IIT Guwahati"],
    "IIT Hyderabad": ["IITH", "IIT Hyderabad"],
    "IIT (BHU) Varanasi": ["IIT BHU", "IIT Varanasi"],
    "IIT (ISM) Dhanbad": ["IIT ISM", "IIT Dhanbad", "ISM Dhanbad"],
    "IIT Indore": ["IIT Indore"],
    "IIT Bhubaneswar": ["IIT Bhubaneswar", "IIT BBS"],
    "IIT Gandhinagar": ["IITGN", "IIT Gandhinagar"],
    "IIT Jodhpur": ["IIT Jodhpur"],
    "IIT Patna": ["IIT Patna"],
    "IIT Ropar": ["IIT Ropar", "IIT Rupnagar"],
    "IIT Mandi": ["IIT Mandi"],
    "IIT Tirupati": ["IIT Tirupati"],
    "IIT Palakkad": ["IIT Palakkad", "IIT PKD"],
    "IIT Dharwad": ["IIT Dharwad"],
    "IIT Bhilai": ["IIT Bhilai"],
    "IIT Goa": ["IIT Goa"],
    "IIT Jammu": ["IIT Jammu"],
    "NIT Trichy": ["NIT Trichy", "NITT", "NIT Tiruchirappalli"],
    "NIT Warangal": ["NIT Warangal", "NITW"],
    "NIT Surathkal": ["NIT Surathkal", "NITK", "NIT Karnataka"],
    "NIT Calicut": ["NIT Calicut", "NITC"],
    "NIT Rourkela": ["NIT Rourkela", "NITR"],
    "NIT Allahabad": ["MNNIT", "NIT Allahabad", "MNNIT Allahabad"],
    "NIT Jaipur": ["MNIT Jaipur", "MNIT"],
    "NIT Bhopal": ["MANIT Bhopal", "MANIT"],
    "NIT Surat": ["SVNIT Surat", "SVNIT"],
    "NIT Nagpur": ["VNIT Nagpur", "VNIT"],
    "IIIT Hyderabad": ["IIIT Hyderabad", "IIITH"],
    "IIIT Delhi": ["IIIT Delhi", "IIITD"],
    "IIIT Bangalore": ["IIIT Bangalore", "IIITB"],
    "IIIT Allahabad": ["IIIT Allahabad", "IIITA"],
    "ABV-IIITM Gwalior": ["IIITM Gwalior", "ABV IIITM"],
    "IIITDM Kancheepuram": ["IIITDM Kancheepuram"],
    "IIITDM Jabalpur": ["IIITDM Jabalpur"],
    "BITS Pilani": ["BITS Pilani", "BITS"],
    "IIEST Shibpur": ["IIEST Shibpur", "IIEST"],
    "BIT Mesra": ["BIT Mesra"],
    "PEC Chandigarh": ["PEC Chandigarh"],
    "DA-IICT Gandhinagar": ["DAIICT", "DA-IICT"],
    "Thapar Institute": ["Thapar", "Thapar University"],
    "Jadavpur University": ["Jadavpur", "JU Kolkata"],
}


def get_search_queries(college_name: str) -> list[str]:
    """Generate Reddit search queries for a college."""
    names = SHORT_NAMES.get(college_name, [college_name])
    queries = []
    for name in names:
        for suffix in QUERY_SUFFIXES:
            queries.append(f"{name} {suffix}")
    return queries

