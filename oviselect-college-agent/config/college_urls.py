"""URL slug mappings for CollegeDunia, Shiksha, Wikipedia, and official sites.

Each college maps to a dict with keys:
  - collegedunia: slug for collegedunia.com/university/{slug}
  - shiksha: slug for shiksha.com/university/{slug}
  - wikipedia: Wikipedia article title
  - official_placement: direct URL to official placement page
"""

# fmt: off
COLLEGE_URLS: dict[str, dict[str, str]] = {
    # ── IITs ──────────────────────────────────────────────────────
    "IIT Bombay": {
        "collegedunia": "25587-indian-institute-of-technology-iit-mumbai",
        "shiksha": "indian-institute-of-technology-iit-bombay-mumbai",
        "wikipedia": "IIT_Bombay",
        "official_placement": "https://www.iitb.ac.in/en/about-iit-bombay/placement",
    },
    "IIT Delhi": {
        "collegedunia": "25595-indian-institute-of-technology-iit-new-delhi",
        "shiksha": "indian-institute-of-technology-iit-delhi-new-delhi",
        "wikipedia": "IIT_Delhi",
        "official_placement": "https://ocs.iitd.ac.in/",
    },
    "IIT Madras": {
        "collegedunia": "25589-indian-institute-of-technology-iit-chennai",
        "shiksha": "indian-institute-of-technology-iit-madras-chennai",
        "wikipedia": "IIT_Madras",
        "official_placement": "https://placement.iitm.ac.in/",
    },
    "IIT Kanpur": {
        "collegedunia": "25588-indian-institute-of-technology-iit-kanpur",
        "shiksha": "indian-institute-of-technology-iit-kanpur",
        "wikipedia": "IIT_Kanpur",
        "official_placement": "https://www.iitk.ac.in/spo/",
    },
    "IIT Kharagpur": {
        "collegedunia": "25586-indian-institute-of-technology-iit-kharagpur",
        "shiksha": "indian-institute-of-technology-iit-kharagpur",
        "wikipedia": "IIT_Kharagpur",
        "official_placement": "https://www.iitkgp.ac.in/placement",
    },
    "IIT Roorkee": {
        "collegedunia": "25596-indian-institute-of-technology-iit-roorkee",
        "shiksha": "indian-institute-of-technology-iit-roorkee",
        "wikipedia": "IIT_Roorkee",
        "official_placement": "https://channel.iitr.ac.in/",
    },
    "IIT Guwahati": {
        "collegedunia": "25594-indian-institute-of-technology-iit-guwahati",
        "shiksha": "indian-institute-of-technology-iit-guwahati",
        "wikipedia": "IIT_Guwahati",
        "official_placement": "https://www.iitg.ac.in/placement/",
    },
    "IIT Hyderabad": {
        "collegedunia": "25597-indian-institute-of-technology-iit-hyderabad",
        "shiksha": "indian-institute-of-technology-iit-hyderabad",
        "wikipedia": "IIT_Hyderabad",
        "official_placement": "https://placement.iith.ac.in/",
    },
    "NIT Trichy": {
        "collegedunia": "27291-national-institute-of-technology-nit-tiruchirappalli",
        "shiksha": "national-institute-of-technology-nit-tiruchirappalli",
        "wikipedia": "National_Institute_of_Technology,_Tiruchirappalli",
        "official_placement": "https://www.nitt.edu/home/students/placementstats/",
    },
    "NIT Warangal": {
        "collegedunia": "27302-national-institute-of-technology-nit-warangal",
        "shiksha": "national-institute-of-technology-nit-warangal",
        "wikipedia": "National_Institute_of_Technology,_Warangal",
        "official_placement": "https://www.nitw.ac.in/page/?url=/placement/PlacementStatistics",
    },
    "NIT Surathkal": {
        "collegedunia": "27305-national-institute-of-technology-karnataka-nitk-surathkal",
        "shiksha": "national-institute-of-technology-karnataka-nitk-surathkal",
        "wikipedia": "National_Institute_of_Technology_Karnataka",
        "official_placement": "https://www.nitk.ac.in/placement-statistics",
    },
    "IIIT Hyderabad": {
        "collegedunia": "28032-international-institute-of-information-technology-iiit-hyderabad",
        "shiksha": "international-institute-of-information-technology-iiit-hyderabad",
        "wikipedia": "International_Institute_of_Information_Technology,_Hyderabad",
        "official_placement": "https://www.iiit.ac.in/placement/",
    },
    "IIIT Delhi": {
        "collegedunia": "28085-indraprastha-institute-of-information-technology-iiitd-new-delhi",
        "shiksha": "indraprastha-institute-of-information-technology-iiitd-new-delhi",
        "wikipedia": "IIIT-Delhi",
        "official_placement": "https://iiitd.ac.in/placement",
    },
}
# fmt: on


def get_collegedunia_url(college: str, page: str = "placement") -> str | None:
    """Get CollegeDunia URL for a college. page can be 'placement', 'fees-and-eligibility', 'campus-life'."""
    urls = COLLEGE_URLS.get(college)
    if not urls or "collegedunia" not in urls:
        return None
    slug = urls["collegedunia"]
    return f"https://collegedunia.com/university/{slug}/{page}"


def get_shiksha_url(college: str) -> str | None:
    urls = COLLEGE_URLS.get(college)
    if not urls or "shiksha" not in urls:
        return None
    return f"https://www.shiksha.com/university/{urls['shiksha']}"


def get_wikipedia_title(college: str) -> str | None:
    urls = COLLEGE_URLS.get(college)
    if not urls or "wikipedia" not in urls:
        return None
    return urls["wikipedia"]


def get_official_placement_url(college: str) -> str | None:
    urls = COLLEGE_URLS.get(college)
    if not urls:
        return None
    return urls.get("official_placement")

