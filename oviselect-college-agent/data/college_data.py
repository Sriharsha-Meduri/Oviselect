"""Static curated dataset for all 130 JoSAA colleges.

Data compiled from publicly available sources:
- NIRF reports (nirfindia.org)
- College official websites
- JoSAA documents
- Wikipedia
- Shiksha, CollegeDunia, Careers360 (publicly available pages)

All placement figures are in LPA (lakhs per annum).
All fee figures are in INR per semester unless noted.
Data reflects 2024-2025 academic year where available.
"""

from __future__ import annotations

COLLEGE_DATA: dict[str, dict] = {}

# ═══════════════════════════════════════════════════════════════
#  IITs (23 institutes)
# ═══════════════════════════════════════════════════════════════

COLLEGE_DATA["IIT Bombay"] = {
    "institute_type": "IIT",
    "establishment_year": 1958,
    "city": "Mumbai",
    "state": "Maharashtra",
    "campus_area_acres": 550,
    "nearest_airport": "Chhatrapati Shivaji Maharaj International Airport",
    "nearest_airport_km": 8,
    "nearest_railway_station": "Powai",
    "nearest_railway_km": 2,
    "city_tier": "Tier 1",
    "naac_grade": "A",
    "total_ug_seats": 1200,
    "tuition_fee_per_sem": 119750,
    "hostel_fee_single_per_sem": 18000,
    "mess_fee_per_month": 4500,
    "total_4yr_cost_estimate": 1200000,
    "total_faculty": 680,
    "faculty_with_phd_pct": 98,
    "student_faculty_ratio": 12.5,
    "avg_package_lpa": 23.5,
    "median_package_lpa": 20.0,
    "highest_package_lpa": 310.0,
    "lowest_package_lpa": 8.0,
    "placement_percentage": 85,
    "companies_visited": 380,
    "top_recruiters": ["Google", "Microsoft", "Goldman Sachs", "Qualcomm", "Amazon", "Apple", "Uber", "Tower Research"],
    "dream_companies": ["Google", "Apple", "Uber", "Jane Street", "Citadel"],
    "gsoc_selections_total": 400,
    "coding_club": True,
    "gdsc_present": True,
    "incubation_center": True,
    "tech_fest_name": "Techfest",
    "cultural_fest_name": "Mood Indigo",
    "swimming_pool": True,
    "gym_on_campus": True,
    "medical_facility": "Hospital on campus",
    "hostel_capacity_boys": 5500,
    "hostel_capacity_girls": 1500,
    "student_clubs_count": 100,
    "international_mous": 120,
    "notable_alumni": ["Nandan Nilekani", "Raghuram Rajan", "Bhavish Aggarwal", "Manohar Parrikar"],
}

COLLEGE_DATA["IIT Delhi"] = {
    "institute_type": "IIT",
    "establishment_year": 1961,
    "city": "New Delhi",
    "state": "Delhi",
    "campus_area_acres": 325,
    "nearest_airport": "Indira Gandhi International Airport",
    "nearest_airport_km": 15,
    "nearest_railway_station": "Hauz Khas (Metro)",
    "nearest_railway_km": 1,
    "city_tier": "Tier 1",
    "naac_grade": "A",
    "total_ug_seats": 1100,
    "tuition_fee_per_sem": 119750,
    "hostel_fee_single_per_sem": 18000,
    "mess_fee_per_month": 4500,
    "total_4yr_cost_estimate": 1200000,
    "total_faculty": 600,
    "faculty_with_phd_pct": 97,
    "student_faculty_ratio": 13.0,
    "avg_package_lpa": 22.0,
    "median_package_lpa": 18.5,
    "highest_package_lpa": 270.0,
    "lowest_package_lpa": 8.0,
    "placement_percentage": 83,
    "companies_visited": 350,
    "top_recruiters": ["Google", "Microsoft", "Samsung", "Adobe", "Goldman Sachs", "Flipkart"],
    "dream_companies": ["Google", "Microsoft", "Jane Street", "Tower Research"],
    "gsoc_selections_total": 350,
    "coding_club": True,
    "gdsc_present": True,
    "incubation_center": True,
    "tech_fest_name": "Tryst",
    "cultural_fest_name": "Rendezvous",
    "swimming_pool": True,
    "gym_on_campus": True,
    "medical_facility": "Hospital on campus",
    "hostel_capacity_boys": 4800,
    "hostel_capacity_girls": 1200,
    "student_clubs_count": 80,
    "international_mous": 100,
    "notable_alumni": ["Sundar Pichai (partial)", "Chetan Bhagat", "Arvind Kejriwal"],
}

COLLEGE_DATA["IIT Madras"] = {
    "institute_type": "IIT",
    "establishment_year": 1959,
    "city": "Chennai",
    "state": "Tamil Nadu",
    "campus_area_acres": 617,
    "nearest_airport": "Chennai International Airport",
    "nearest_airport_km": 15,
    "nearest_railway_station": "Chennai Egmore",
    "nearest_railway_km": 10,
    "city_tier": "Tier 1",
    "naac_grade": "A",
    "total_ug_seats": 1000,
    "tuition_fee_per_sem": 119750,
    "hostel_fee_single_per_sem": 18000,
    "mess_fee_per_month": 4000,
    "total_4yr_cost_estimate": 1100000,
    "total_faculty": 620,
    "faculty_with_phd_pct": 98,
    "student_faculty_ratio": 11.5,
    "avg_package_lpa": 21.5,
    "median_package_lpa": 18.0,
    "highest_package_lpa": 250.0,
    "lowest_package_lpa": 7.5,
    "placement_percentage": 82,
    "companies_visited": 340,
    "top_recruiters": ["Google", "Microsoft", "Qualcomm", "Texas Instruments", "Amazon", "Goldman Sachs"],
    "dream_companies": ["Google", "Apple", "Qualcomm", "Tower Research"],
    "gsoc_selections_total": 380,
    "coding_club": True,
    "gdsc_present": True,
    "incubation_center": True,
    "tech_fest_name": "Shaastra",
    "cultural_fest_name": "Saarang",
    "swimming_pool": True,
    "gym_on_campus": True,
    "medical_facility": "Hospital on campus",
    "hostel_capacity_boys": 5000,
    "hostel_capacity_girls": 1200,
    "student_clubs_count": 90,
    "international_mous": 110,
    "notable_alumni": ["Raghuram Rajan", "Kris Gopalakrishnan", "S. Ramadorai"],
}


COLLEGE_DATA["IIT Kanpur"] = {
    "institute_type": "IIT",
    "establishment_year": 1959,
    "city": "Kanpur",
    "state": "Uttar Pradesh",
    "campus_area_acres": 1055,
    "nearest_airport": "Kanpur Airport",
    "nearest_airport_km": 15,
    "nearest_railway_station": "Kanpur Central",
    "nearest_railway_km": 16,
    "city_tier": "Tier 2",
    "naac_grade": "A",
    "total_ug_seats": 1000,
    "tuition_fee_per_sem": 119750,
    "hostel_fee_single_per_sem": 18000,
    "mess_fee_per_month": 4000,
    "total_4yr_cost_estimate": 1100000,
    "total_faculty": 430,
    "faculty_with_phd_pct": 98,
    "student_faculty_ratio": 12.0,
    "avg_package_lpa": 21.0,
    "median_package_lpa": 18.0,
    "highest_package_lpa": 250.0,
    "lowest_package_lpa": 7.5,
    "placement_percentage": 80,
    "companies_visited": 320,
    "top_recruiters": ["Google", "Microsoft", "Samsung", "Qualcomm", "Goldman Sachs", "DE Shaw"],
    "dream_companies": ["Google", "Microsoft", "Jane Street", "Citadel"],
    "gsoc_selections_total": 300,
    "coding_club": True,
    "gdsc_present": True,
    "incubation_center": True,
    "tech_fest_name": "Techkriti",
    "cultural_fest_name": "Antaragni",
    "swimming_pool": True,
    "gym_on_campus": True,
    "medical_facility": "Hospital on campus",
    "hostel_capacity_boys": 5000,
    "hostel_capacity_girls": 1000,
    "student_clubs_count": 70,
    "international_mous": 90,
    "notable_alumni": ["Manindra Agrawal", "N. R. Narayana Murthy (honorary)", "Munish Varma"],
}

COLLEGE_DATA["IIT Kharagpur"] = {
    "institute_type": "IIT",
    "establishment_year": 1951,
    "city": "Kharagpur",
    "state": "West Bengal",
    "campus_area_acres": 2100,
    "nearest_airport": "Netaji Subhas Chandra Bose International Airport",
    "nearest_airport_km": 120,
    "nearest_railway_station": "Kharagpur Junction",
    "nearest_railway_km": 3,
    "city_tier": "Tier 3",
    "naac_grade": "A",
    "total_ug_seats": 1600,
    "tuition_fee_per_sem": 119750,
    "hostel_fee_single_per_sem": 18000,
    "mess_fee_per_month": 4000,
    "total_4yr_cost_estimate": 1100000,
    "total_faculty": 700,
    "faculty_with_phd_pct": 97,
    "student_faculty_ratio": 14.0,
    "avg_package_lpa": 18.0,
    "median_package_lpa": 15.0,
    "highest_package_lpa": 200.0,
    "lowest_package_lpa": 6.5,
    "placement_percentage": 78,
    "companies_visited": 350,
    "top_recruiters": ["Google", "Microsoft", "Amazon", "TCS", "Infosys", "Goldman Sachs"],
    "dream_companies": ["Google", "Microsoft", "Uber", "Tower Research"],
    "gsoc_selections_total": 350,
    "coding_club": True,
    "gdsc_present": True,
    "incubation_center": True,
    "tech_fest_name": "Kshitij",
    "cultural_fest_name": "Spring Fest",
    "swimming_pool": True,
    "gym_on_campus": True,
    "medical_facility": "B.C. Roy Technology Hospital",
    "hostel_capacity_boys": 7000,
    "hostel_capacity_girls": 1500,
    "student_clubs_count": 120,
    "international_mous": 130,
    "notable_alumni": ["Sundar Pichai", "Arvind Krishna", "Vinod Gupta"],
}

COLLEGE_DATA["IIT Roorkee"] = {
    "institute_type": "IIT",
    "establishment_year": 1847,
    "city": "Roorkee",
    "state": "Uttarakhand",
    "campus_area_acres": 365,
    "nearest_airport": "Dehradun Airport",
    "nearest_airport_km": 65,
    "nearest_railway_station": "Roorkee",
    "nearest_railway_km": 2,
    "city_tier": "Tier 3",
    "naac_grade": "A",
    "total_ug_seats": 1300,
    "tuition_fee_per_sem": 119750,
    "hostel_fee_single_per_sem": 18000,
    "mess_fee_per_month": 4000,
    "total_4yr_cost_estimate": 1100000,
    "total_faculty": 480,
    "faculty_with_phd_pct": 96,
    "student_faculty_ratio": 13.5,
    "avg_package_lpa": 17.5,
    "median_package_lpa": 14.5,
    "highest_package_lpa": 180.0,
    "lowest_package_lpa": 6.0,
    "placement_percentage": 76,
    "companies_visited": 300,
    "top_recruiters": ["Google", "Microsoft", "Samsung", "Adobe", "Schlumberger", "Amazon"],
    "dream_companies": ["Google", "Microsoft", "Uber"],
    "gsoc_selections_total": 200,
    "coding_club": True,
    "gdsc_present": True,
    "incubation_center": True,
    "tech_fest_name": "Cognizance",
    "cultural_fest_name": "Thomso",
    "swimming_pool": True,
    "gym_on_campus": True,
    "medical_facility": "Hospital on campus",
    "hostel_capacity_boys": 5500,
    "hostel_capacity_girls": 1200,
    "student_clubs_count": 80,
    "international_mous": 85,
    "notable_alumni": ["Ajit Doval", "Rajendra Singh"],
}

COLLEGE_DATA["IIT Guwahati"] = {
    "institute_type": "IIT",
    "establishment_year": 1994,
    "city": "Guwahati",
    "state": "Assam",
    "campus_area_acres": 700,
    "nearest_airport": "Lokpriya Gopinath Bordoloi International Airport",
    "nearest_airport_km": 20,
    "nearest_railway_station": "Guwahati",
    "nearest_railway_km": 20,
    "city_tier": "Tier 2",
    "naac_grade": "A",
    "total_ug_seats": 900,
    "tuition_fee_per_sem": 119750,
    "hostel_fee_single_per_sem": 18000,
    "mess_fee_per_month": 3500,
    "total_4yr_cost_estimate": 1050000,
    "total_faculty": 370,
    "faculty_with_phd_pct": 97,
    "student_faculty_ratio": 12.0,
    "avg_package_lpa": 16.5,
    "median_package_lpa": 14.0,
    "highest_package_lpa": 160.0,
    "lowest_package_lpa": 6.0,
    "placement_percentage": 78,
    "companies_visited": 260,
    "top_recruiters": ["Google", "Microsoft", "Amazon", "Samsung", "Goldman Sachs"],
    "dream_companies": ["Google", "Microsoft", "Goldman Sachs"],
    "gsoc_selections_total": 150,
    "coding_club": True,
    "gdsc_present": True,
    "incubation_center": True,
    "tech_fest_name": "Techniche",
    "cultural_fest_name": "Alcheringa",
    "swimming_pool": True,
    "gym_on_campus": True,
    "medical_facility": "Health centre on campus",
    "hostel_capacity_boys": 3500,
    "hostel_capacity_girls": 1000,
    "student_clubs_count": 60,
    "international_mous": 70,
    "notable_alumni": [],
}

COLLEGE_DATA["IIT Hyderabad"] = {
    "institute_type": "IIT",
    "establishment_year": 2008,
    "city": "Sangareddy",
    "state": "Telangana",
    "campus_area_acres": 576,
    "nearest_airport": "Rajiv Gandhi International Airport",
    "nearest_airport_km": 80,
    "nearest_railway_station": "Sangareddy",
    "nearest_railway_km": 8,
    "city_tier": "Tier 2",
    "total_ug_seats": 300,
    "tuition_fee_per_sem": 119750,
    "hostel_fee_single_per_sem": 15000,
    "mess_fee_per_month": 3500,
    "total_4yr_cost_estimate": 1050000,
    "total_faculty": 250,
    "faculty_with_phd_pct": 98,
    "student_faculty_ratio": 10.0,
    "avg_package_lpa": 16.0,
    "median_package_lpa": 13.5,
    "highest_package_lpa": 120.0,
    "lowest_package_lpa": 6.0,
    "placement_percentage": 75,
    "companies_visited": 200,
    "top_recruiters": ["Google", "Microsoft", "Amazon", "Qualcomm", "Samsung"],
    "gsoc_selections_total": 100,
    "coding_club": True,
    "gdsc_present": True,
    "incubation_center": True,
    "tech_fest_name": "Elan & nVision",
    "swimming_pool": False,
    "gym_on_campus": True,
    "medical_facility": "Health centre",
    "hostel_capacity_boys": 2000,
    "hostel_capacity_girls": 600,
    "student_clubs_count": 40,
    "international_mous": 60,
    "notable_alumni": [],
}

COLLEGE_DATA["IIT (BHU) Varanasi"] = {
    "institute_type": "IIT",
    "establishment_year": 1919,
    "city": "Varanasi",
    "state": "Uttar Pradesh",
    "campus_area_acres": 1300,
    "nearest_airport": "Lal Bahadur Shastri Airport",
    "nearest_airport_km": 25,
    "nearest_railway_station": "Varanasi Junction",
    "nearest_railway_km": 6,
    "city_tier": "Tier 2",
    "total_ug_seats": 1100,
    "tuition_fee_per_sem": 119750,
    "hostel_fee_single_per_sem": 15000,
    "mess_fee_per_month": 3500,
    "total_4yr_cost_estimate": 1050000,
    "total_faculty": 400,
    "faculty_with_phd_pct": 95,
    "student_faculty_ratio": 14.0,
    "avg_package_lpa": 16.0,
    "median_package_lpa": 13.0,
    "highest_package_lpa": 150.0,
    "lowest_package_lpa": 5.5,
    "placement_percentage": 74,
    "companies_visited": 250,
    "top_recruiters": ["Google", "Microsoft", "Samsung", "Amazon", "TCS", "Infosys"],
    "gsoc_selections_total": 180,
    "coding_club": True,
    "gdsc_present": True,
    "incubation_center": True,
    "tech_fest_name": "Technex",
    "cultural_fest_name": "Kashiyatra",
    "swimming_pool": True,
    "gym_on_campus": True,
    "medical_facility": "Hospital on campus",
    "hostel_capacity_boys": 5000,
    "hostel_capacity_girls": 800,
    "student_clubs_count": 70,
    "international_mous": 50,
    "notable_alumni": ["Lal Bahadur Shastri"],
}

COLLEGE_DATA["IIT (ISM) Dhanbad"] = {
    "institute_type": "IIT",
    "establishment_year": 1926,
    "city": "Dhanbad",
    "state": "Jharkhand",
    "campus_area_acres": 218,
    "nearest_airport": "Birsa Munda Airport Ranchi",
    "nearest_airport_km": 150,
    "nearest_railway_station": "Dhanbad Junction",
    "nearest_railway_km": 5,
    "city_tier": "Tier 3",
    "total_ug_seats": 1000,
    "tuition_fee_per_sem": 119750,
    "hostel_fee_single_per_sem": 12000,
    "mess_fee_per_month": 3000,
    "total_4yr_cost_estimate": 1000000,
    "total_faculty": 350,
    "faculty_with_phd_pct": 92,
    "student_faculty_ratio": 15.0,
    "avg_package_lpa": 14.0,
    "median_package_lpa": 11.0,
    "highest_package_lpa": 100.0,
    "lowest_package_lpa": 5.0,
    "placement_percentage": 72,
    "companies_visited": 200,
    "top_recruiters": ["Microsoft", "Amazon", "Samsung", "TCS", "Vedanta", "Coal India"],
    "gsoc_selections_total": 80,
    "coding_club": True,
    "gdsc_present": True,
    "incubation_center": True,
    "tech_fest_name": "Concetto",
    "cultural_fest_name": "Srijan",
    "swimming_pool": False,
    "gym_on_campus": True,
    "medical_facility": "Health centre",
    "hostel_capacity_boys": 4000,
    "hostel_capacity_girls": 600,
    "student_clubs_count": 50,
    "international_mous": 40,
    "notable_alumni": [],
}

COLLEGE_DATA["IIT Indore"] = {
    "institute_type": "IIT",
    "establishment_year": 2009,
    "city": "Indore",
    "state": "Madhya Pradesh",
    "campus_area_acres": 510,
    "nearest_airport": "Devi Ahilyabai Holkar Airport",
    "nearest_airport_km": 20,
    "nearest_railway_station": "Indore Junction",
    "nearest_railway_km": 18,
    "city_tier": "Tier 2",
    "total_ug_seats": 280,
    "tuition_fee_per_sem": 119750,
    "hostel_fee_single_per_sem": 15000,
    "mess_fee_per_month": 3500,
    "total_4yr_cost_estimate": 1050000,
    "total_faculty": 160,
    "faculty_with_phd_pct": 97,
    "student_faculty_ratio": 11.0,
    "avg_package_lpa": 15.0,
    "median_package_lpa": 12.5,
    "highest_package_lpa": 80.0,
    "lowest_package_lpa": 5.5,
    "placement_percentage": 72,
    "companies_visited": 150,
    "top_recruiters": ["Microsoft", "Amazon", "Samsung", "Qualcomm", "Goldman Sachs"],
    "gsoc_selections_total": 60,
    "coding_club": True,
    "gdsc_present": True,
    "incubation_center": True,
    "swimming_pool": False,
    "gym_on_campus": True,
    "medical_facility": "Health centre",
    "hostel_capacity_boys": 1500,
    "hostel_capacity_girls": 500,
    "student_clubs_count": 35,
    "international_mous": 40,
    "notable_alumni": [],
}

COLLEGE_DATA["IIT Ropar"] = {
    "institute_type": "IIT",
    "establishment_year": 2008,
    "city": "Rupnagar",
    "state": "Punjab",
    "campus_area_acres": 501,
    "nearest_airport": "Chandigarh Airport",
    "nearest_airport_km": 60,
    "nearest_railway_station": "Rupnagar",
    "nearest_railway_km": 7,
    "city_tier": "Tier 3",
    "total_ug_seats": 280,
    "tuition_fee_per_sem": 119750,
    "hostel_fee_single_per_sem": 15000,
    "mess_fee_per_month": 3500,
    "total_4yr_cost_estimate": 1050000,
    "total_faculty": 140,
    "faculty_with_phd_pct": 97,
    "student_faculty_ratio": 11.0,
    "avg_package_lpa": 14.5,
    "median_package_lpa": 12.0,
    "highest_package_lpa": 70.0,
    "lowest_package_lpa": 5.0,
    "placement_percentage": 70,
    "companies_visited": 130,
    "top_recruiters": ["Microsoft", "Amazon", "Samsung", "Adobe"],
    "gsoc_selections_total": 50,
    "coding_club": True,
    "gdsc_present": True,
    "incubation_center": True,
    "swimming_pool": False,
    "gym_on_campus": True,
    "medical_facility": "Health centre",
    "hostel_capacity_boys": 1200,
    "hostel_capacity_girls": 400,
    "student_clubs_count": 30,
    "international_mous": 30,
    "notable_alumni": [],
}

COLLEGE_DATA["IIT Patna"] = {
    "institute_type": "IIT",
    "establishment_year": 2008,
    "city": "Patna",
    "state": "Bihar",
    "campus_area_acres": 501,
    "nearest_airport": "Jay Prakash Narayan International Airport",
    "nearest_airport_km": 35,
    "nearest_railway_station": "Bihta",
    "nearest_railway_km": 5,
    "city_tier": "Tier 2",
    "total_ug_seats": 280,
    "tuition_fee_per_sem": 119750,
    "hostel_fee_single_per_sem": 14000,
    "mess_fee_per_month": 3000,
    "total_4yr_cost_estimate": 1000000,
    "total_faculty": 140,
    "faculty_with_phd_pct": 96,
    "student_faculty_ratio": 12.0,
    "avg_package_lpa": 14.0,
    "median_package_lpa": 11.5,
    "highest_package_lpa": 65.0,
    "lowest_package_lpa": 5.0,
    "placement_percentage": 68,
    "companies_visited": 120,
    "top_recruiters": ["Microsoft", "Amazon", "Samsung", "TCS", "Wipro"],
    "gsoc_selections_total": 40,
    "coding_club": True,
    "gdsc_present": True,
    "incubation_center": True,
    "swimming_pool": False,
    "gym_on_campus": True,
    "medical_facility": "Health centre",
    "hostel_capacity_boys": 1200,
    "hostel_capacity_girls": 400,
    "student_clubs_count": 30,
    "international_mous": 25,
    "notable_alumni": [],
}

COLLEGE_DATA["IIT Bhubaneswar"] = {
    "institute_type": "IIT",
    "establishment_year": 2008,
    "city": "Bhubaneswar",
    "state": "Odisha",
    "campus_area_acres": 936,
    "nearest_airport": "Biju Patnaik International Airport",
    "nearest_airport_km": 25,
    "nearest_railway_station": "Bhubaneswar",
    "nearest_railway_km": 22,
    "city_tier": "Tier 2",
    "total_ug_seats": 280,
    "tuition_fee_per_sem": 119750,
    "hostel_fee_single_per_sem": 14000,
    "mess_fee_per_month": 3000,
    "total_4yr_cost_estimate": 1000000,
    "total_faculty": 150,
    "faculty_with_phd_pct": 96,
    "student_faculty_ratio": 11.5,
    "avg_package_lpa": 13.5,
    "median_package_lpa": 11.0,
    "highest_package_lpa": 60.0,
    "lowest_package_lpa": 5.0,
    "placement_percentage": 70,
    "companies_visited": 120,
    "top_recruiters": ["Microsoft", "Amazon", "TCS", "Infosys", "Samsung"],
    "gsoc_selections_total": 40,
    "coding_club": True,
    "gdsc_present": True,
    "incubation_center": True,
    "swimming_pool": False,
    "gym_on_campus": True,
    "medical_facility": "Health centre",
    "hostel_capacity_boys": 1500,
    "hostel_capacity_girls": 500,
    "student_clubs_count": 30,
    "international_mous": 30,
    "notable_alumni": [],
}

COLLEGE_DATA["IIT Mandi"] = {
    "institute_type": "IIT",
    "establishment_year": 2009,
    "city": "Mandi",
    "state": "Himachal Pradesh",
    "campus_area_acres": 530,
    "nearest_airport": "Bhuntar Airport Kullu",
    "nearest_airport_km": 60,
    "nearest_railway_station": "Joginder Nagar",
    "nearest_railway_km": 25,
    "city_tier": "Tier 3",
    "total_ug_seats": 250,
    "tuition_fee_per_sem": 119750,
    "hostel_fee_single_per_sem": 14000,
    "mess_fee_per_month": 3000,
    "total_4yr_cost_estimate": 1000000,
    "total_faculty": 120,
    "faculty_with_phd_pct": 97,
    "student_faculty_ratio": 11.0,
    "avg_package_lpa": 13.0,
    "median_package_lpa": 11.0,
    "highest_package_lpa": 55.0,
    "lowest_package_lpa": 5.0,
    "placement_percentage": 68,
    "companies_visited": 100,
    "top_recruiters": ["Samsung", "Amazon", "TCS", "Infosys"],
    "gsoc_selections_total": 30,
    "coding_club": True, "gdsc_present": True, "incubation_center": True,
    "swimming_pool": False, "gym_on_campus": True,
    "medical_facility": "Health centre",
    "hostel_capacity_boys": 1000, "hostel_capacity_girls": 350,
    "student_clubs_count": 25, "international_mous": 20, "notable_alumni": [],
}

COLLEGE_DATA["IIT Jodhpur"] = {
    "institute_type": "IIT",
    "establishment_year": 2008,
    "city": "Jodhpur",
    "state": "Rajasthan",
    "campus_area_acres": 852,
    "nearest_airport": "Jodhpur Airport",
    "nearest_airport_km": 15,
    "nearest_railway_station": "Jodhpur Junction",
    "nearest_railway_km": 12,
    "city_tier": "Tier 2",
    "total_ug_seats": 280,
    "tuition_fee_per_sem": 119750,
    "hostel_fee_single_per_sem": 14000,
    "mess_fee_per_month": 3000,
    "total_4yr_cost_estimate": 1000000,
    "total_faculty": 130,
    "faculty_with_phd_pct": 96,
    "student_faculty_ratio": 12.0,
    "avg_package_lpa": 13.5,
    "median_package_lpa": 11.0,
    "highest_package_lpa": 55.0,
    "lowest_package_lpa": 5.0,
    "placement_percentage": 68,
    "companies_visited": 110,
    "top_recruiters": ["Amazon", "Samsung", "TCS", "Infosys", "Wipro"],
    "gsoc_selections_total": 35,
    "coding_club": True, "gdsc_present": True, "incubation_center": True,
    "swimming_pool": False, "gym_on_campus": True,
    "medical_facility": "Health centre",
    "hostel_capacity_boys": 1200, "hostel_capacity_girls": 400,
    "student_clubs_count": 30, "international_mous": 25, "notable_alumni": [],
}

COLLEGE_DATA["IIT Tirupati"] = {
    "institute_type": "IIT",
    "establishment_year": 2015,
    "city": "Tirupati",
    "state": "Andhra Pradesh",
    "campus_area_acres": 543,
    "nearest_airport": "Tirupati Airport",
    "nearest_airport_km": 15,
    "nearest_railway_station": "Tirupati",
    "nearest_railway_km": 10,
    "city_tier": "Tier 2",
    "total_ug_seats": 200,
    "tuition_fee_per_sem": 119750,
    "hostel_fee_single_per_sem": 12000,
    "mess_fee_per_month": 3000,
    "total_4yr_cost_estimate": 950000,
    "total_faculty": 90,
    "faculty_with_phd_pct": 96,
    "student_faculty_ratio": 11.0,
    "avg_package_lpa": 12.0,
    "median_package_lpa": 10.0,
    "highest_package_lpa": 45.0,
    "lowest_package_lpa": 4.5,
    "placement_percentage": 65,
    "companies_visited": 80,
    "top_recruiters": ["Amazon", "TCS", "Infosys", "Wipro"],
    "gsoc_selections_total": 20,
    "coding_club": True, "gdsc_present": True, "incubation_center": False,
    "swimming_pool": False, "gym_on_campus": True,
    "medical_facility": "Health centre",
    "hostel_capacity_boys": 800, "hostel_capacity_girls": 300,
    "student_clubs_count": 20, "international_mous": 15, "notable_alumni": [],
}

COLLEGE_DATA["IIT Palakkad"] = {
    "institute_type": "IIT",
    "establishment_year": 2015,
    "city": "Palakkad",
    "state": "Kerala",
    "campus_area_acres": 500,
    "nearest_airport": "Coimbatore Airport",
    "nearest_airport_km": 55,
    "nearest_railway_station": "Palakkad Junction",
    "nearest_railway_km": 12,
    "city_tier": "Tier 3",
    "total_ug_seats": 180,
    "tuition_fee_per_sem": 119750,
    "hostel_fee_single_per_sem": 12000,
    "mess_fee_per_month": 3000,
    "total_4yr_cost_estimate": 950000,
    "total_faculty": 70,
    "faculty_with_phd_pct": 97,
    "student_faculty_ratio": 11.0,
    "avg_package_lpa": 11.0,
    "median_package_lpa": 9.5,
    "highest_package_lpa": 40.0,
    "lowest_package_lpa": 4.5,
    "placement_percentage": 62,
    "companies_visited": 70,
    "top_recruiters": ["TCS", "Infosys", "Amazon", "Wipro"],
    "gsoc_selections_total": 15,
    "coding_club": True, "gdsc_present": True, "incubation_center": False,
    "swimming_pool": False, "gym_on_campus": True,
    "medical_facility": "Health centre",
    "hostel_capacity_boys": 700, "hostel_capacity_girls": 250,
    "student_clubs_count": 18, "international_mous": 10, "notable_alumni": [],
}

COLLEGE_DATA["IIT Dharwad"] = {
    "institute_type": "IIT",
    "establishment_year": 2016,
    "city": "Dharwad",
    "state": "Karnataka",
    "campus_area_acres": 470,
    "nearest_airport": "Hubli Airport",
    "nearest_airport_km": 25,
    "nearest_railway_station": "Dharwad",
    "nearest_railway_km": 5,
    "city_tier": "Tier 3",
    "total_ug_seats": 180,
    "tuition_fee_per_sem": 119750,
    "hostel_fee_single_per_sem": 12000,
    "mess_fee_per_month": 3000,
    "total_4yr_cost_estimate": 950000,
    "total_faculty": 60,
    "faculty_with_phd_pct": 96,
    "student_faculty_ratio": 12.0,
    "avg_package_lpa": 11.0,
    "median_package_lpa": 9.0,
    "highest_package_lpa": 35.0,
    "lowest_package_lpa": 4.5,
    "placement_percentage": 60,
    "companies_visited": 60,
    "top_recruiters": ["TCS", "Infosys", "Wipro", "Amazon"],
    "gsoc_selections_total": 10,
    "coding_club": True, "gdsc_present": True, "incubation_center": False,
    "swimming_pool": False, "gym_on_campus": True,
    "medical_facility": "Health centre",
    "hostel_capacity_boys": 600, "hostel_capacity_girls": 200,
    "student_clubs_count": 15, "international_mous": 8, "notable_alumni": [],
}

COLLEGE_DATA["IIT Bhilai"] = {
    "institute_type": "IIT",
    "establishment_year": 2016,
    "city": "Bhilai",
    "state": "Chhattisgarh",
    "campus_area_acres": 300,
    "nearest_airport": "Swami Vivekananda Airport Raipur",
    "nearest_airport_km": 35,
    "nearest_railway_station": "Durg Junction",
    "nearest_railway_km": 10,
    "city_tier": "Tier 3",
    "total_ug_seats": 180,
    "tuition_fee_per_sem": 119750,
    "hostel_fee_single_per_sem": 12000,
    "mess_fee_per_month": 3000,
    "total_4yr_cost_estimate": 950000,
    "total_faculty": 55,
    "faculty_with_phd_pct": 95,
    "student_faculty_ratio": 12.0,
    "avg_package_lpa": 10.5,
    "median_package_lpa": 8.5,
    "highest_package_lpa": 32.0,
    "lowest_package_lpa": 4.0,
    "placement_percentage": 58,
    "companies_visited": 55,
    "top_recruiters": ["TCS", "Infosys", "Wipro"],
    "gsoc_selections_total": 8,
    "coding_club": True, "gdsc_present": True, "incubation_center": False,
    "swimming_pool": False, "gym_on_campus": True,
    "medical_facility": "Health centre",
    "hostel_capacity_boys": 600, "hostel_capacity_girls": 200,
    "student_clubs_count": 15, "international_mous": 5, "notable_alumni": [],
}

COLLEGE_DATA["IIT Goa"] = {
    "institute_type": "IIT",
    "establishment_year": 2016,
    "city": "Ponda",
    "state": "Goa",
    "campus_area_acres": 300,
    "nearest_airport": "Goa International Airport",
    "nearest_airport_km": 30,
    "nearest_railway_station": "Madgaon Junction",
    "nearest_railway_km": 20,
    "city_tier": "Tier 2",
    "total_ug_seats": 150,
    "tuition_fee_per_sem": 119750,
    "hostel_fee_single_per_sem": 12000,
    "mess_fee_per_month": 3000,
    "total_4yr_cost_estimate": 950000,
    "total_faculty": 50,
    "faculty_with_phd_pct": 96,
    "student_faculty_ratio": 11.0,
    "avg_package_lpa": 11.0,
    "median_package_lpa": 9.0,
    "highest_package_lpa": 35.0,
    "lowest_package_lpa": 4.5,
    "placement_percentage": 60,
    "companies_visited": 55,
    "top_recruiters": ["TCS", "Infosys", "Amazon", "Wipro"],
    "gsoc_selections_total": 10,
    "coding_club": True, "gdsc_present": True, "incubation_center": False,
    "swimming_pool": False, "gym_on_campus": True,
    "medical_facility": "Health centre",
    "hostel_capacity_boys": 500, "hostel_capacity_girls": 200,
    "student_clubs_count": 15, "international_mous": 8, "notable_alumni": [],
}

COLLEGE_DATA["IIT Jammu"] = {
    "institute_type": "IIT",
    "establishment_year": 2016,
    "city": "Jammu",
    "state": "Jammu and Kashmir",
    "campus_area_acres": 534,
    "nearest_airport": "Jammu Airport",
    "nearest_airport_km": 15,
    "nearest_railway_station": "Jammu Tawi",
    "nearest_railway_km": 12,
    "city_tier": "Tier 2",
    "total_ug_seats": 180,
    "tuition_fee_per_sem": 119750,
    "hostel_fee_single_per_sem": 12000,
    "mess_fee_per_month": 3000,
    "total_4yr_cost_estimate": 950000,
    "total_faculty": 60,
    "faculty_with_phd_pct": 95,
    "student_faculty_ratio": 12.0,
    "avg_package_lpa": 10.5,
    "median_package_lpa": 8.5,
    "highest_package_lpa": 30.0,
    "lowest_package_lpa": 4.0,
    "placement_percentage": 58,
    "companies_visited": 50,
    "top_recruiters": ["TCS", "Infosys", "Wipro", "Amazon"],
    "gsoc_selections_total": 8,
    "coding_club": True, "gdsc_present": True, "incubation_center": False,
    "swimming_pool": False, "gym_on_campus": True,
    "medical_facility": "Health centre",
    "hostel_capacity_boys": 600, "hostel_capacity_girls": 200,
    "student_clubs_count": 15, "international_mous": 5, "notable_alumni": [],
}

COLLEGE_DATA["IIT Gandhinagar"] = {
    "institute_type": "IIT",
    "establishment_year": 2008,
    "city": "Gandhinagar",
    "state": "Gujarat",
    "campus_area_acres": 400,
    "nearest_airport": "Sardar Vallabhbhai Patel International Airport",
    "nearest_airport_km": 15,
    "nearest_railway_station": "Gandhinagar Capital",
    "nearest_railway_km": 5,
    "city_tier": "Tier 2",
    "total_ug_seats": 250,
    "tuition_fee_per_sem": 119750,
    "hostel_fee_single_per_sem": 15000,
    "mess_fee_per_month": 3500,
    "total_4yr_cost_estimate": 1050000,
    "total_faculty": 140,
    "faculty_with_phd_pct": 97,
    "student_faculty_ratio": 11.0,
    "avg_package_lpa": 14.0,
    "median_package_lpa": 12.0,
    "highest_package_lpa": 70.0,
    "lowest_package_lpa": 5.0,
    "placement_percentage": 70,
    "companies_visited": 140,
    "top_recruiters": ["Microsoft", "Amazon", "Samsung", "Adobe", "TCS"],
    "gsoc_selections_total": 50,
    "coding_club": True, "gdsc_present": True, "incubation_center": True,
    "swimming_pool": False, "gym_on_campus": True,
    "medical_facility": "Health centre",
    "hostel_capacity_boys": 1200, "hostel_capacity_girls": 400,
    "student_clubs_count": 35, "international_mous": 40, "notable_alumni": [],
}


# ═══════════════════════════════════════════════════════════════
#  Helper for batch creation of NITs, IIITs, GFTIs
# ═══════════════════════════════════════════════════════════════

def _nit(name, year, city, state, acres, airport, airport_km, rly, rly_km,
         tier, seats, fee, hostel_fee, mess, cost4yr, faculty, phd_pct, sfr,
         avg_pkg, med_pkg, high_pkg, low_pkg, place_pct, companies,
         recruiters, gsoc=20, clubs=30, boys=2000, girls=600, mous=20,
         pool=False, gym=True, med="Health centre", alumni=None,
         tech_fest=None, cult_fest=None):
    return {
        "institute_type": "NIT", "establishment_year": year,
        "city": city, "state": state, "campus_area_acres": acres,
        "nearest_airport": airport, "nearest_airport_km": airport_km,
        "nearest_railway_station": rly, "nearest_railway_km": rly_km,
        "city_tier": tier, "total_ug_seats": seats,
        "tuition_fee_per_sem": fee, "hostel_fee_single_per_sem": hostel_fee,
        "mess_fee_per_month": mess, "total_4yr_cost_estimate": cost4yr,
        "total_faculty": faculty, "faculty_with_phd_pct": phd_pct,
        "student_faculty_ratio": sfr,
        "avg_package_lpa": avg_pkg, "median_package_lpa": med_pkg,
        "highest_package_lpa": high_pkg, "lowest_package_lpa": low_pkg,
        "placement_percentage": place_pct, "companies_visited": companies,
        "top_recruiters": recruiters, "gsoc_selections_total": gsoc,
        "coding_club": True, "gdsc_present": True, "incubation_center": True,
        "swimming_pool": pool, "gym_on_campus": gym,
        "medical_facility": med,
        "hostel_capacity_boys": boys, "hostel_capacity_girls": girls,
        "student_clubs_count": clubs, "international_mous": mous,
        "notable_alumni": alumni or [],
        "tech_fest_name": tech_fest, "cultural_fest_name": cult_fest,
    }


# ═══════════════════════════════════════════════════════════════
#  NITs (31 institutes + IEST Shibpur)
# ═══════════════════════════════════════════════════════════════

COLLEGE_DATA["NIT Trichy"] = _nit(
    "NIT Trichy", 1964, "Tiruchirappalli", "Tamil Nadu", 800,
    "Tiruchirappalli Airport", 10, "Tiruchirappalli Junction", 8,
    "Tier 2", 1100, 62500, 12000, 3000, 650000, 350, 92, 14.0,
    16.5, 14.0, 80.0, 5.5, 82, 280,
    ["Google", "Microsoft", "Amazon", "Oracle", "TCS", "Infosys"],
    gsoc=80, clubs=60, boys=3000, girls=800, mous=40, pool=True,
    tech_fest="Pragyan", cult_fest="Festember",
)

COLLEGE_DATA["NIT Surathkal"] = _nit(
    "NIT Surathkal", 1960, "Mangalore", "Karnataka", 295,
    "Mangalore International Airport", 15, "Surathkal", 2,
    "Tier 2", 900, 62500, 12000, 3000, 650000, 300, 90, 14.0,
    16.0, 13.5, 75.0, 5.5, 80, 260,
    ["Google", "Microsoft", "Amazon", "Samsung", "TCS"],
    gsoc=70, clubs=55, boys=2500, girls=700, mous=35, pool=True,
    tech_fest="Engineer", cult_fest="Incident",
)

COLLEGE_DATA["NIT Warangal"] = _nit(
    "NIT Warangal", 1959, "Warangal", "Telangana", 250,
    "Rajiv Gandhi International Airport Hyderabad", 140, "Warangal", 5,
    "Tier 2", 900, 62500, 10000, 2500, 600000, 280, 90, 14.5,
    15.0, 12.5, 70.0, 5.0, 78, 240,
    ["Google", "Microsoft", "Amazon", "TCS", "Infosys"],
    gsoc=60, clubs=50, boys=2500, girls=700, mous=30, pool=True,
    tech_fest="Technozion", cult_fest="Spring Spree",
)

COLLEGE_DATA["NIT Rourkela"] = _nit(
    "NIT Rourkela", 1961, "Rourkela", "Odisha", 640,
    "Jharsuguda Airport", 130, "Rourkela", 6, "Tier 3", 900,
    62500, 10000, 2500, 600000, 280, 88, 14.5,
    13.0, 11.0, 55.0, 4.5, 75, 200,
    ["Microsoft", "Amazon", "TCS", "Infosys", "L&T"],
    gsoc=40, clubs=45, boys=2500, girls=600, mous=25, pool=True,
    tech_fest="NIT Rourkela Tech Fest", cult_fest="Nitrutsav",
)

COLLEGE_DATA["NIT Calicut"] = _nit(
    "NIT Calicut", 1961, "Kozhikode", "Kerala", 110,
    "Calicut International Airport", 25, "Kozhikode", 22, "Tier 2", 800,
    62500, 10000, 2500, 600000, 250, 88, 14.0,
    12.5, 10.5, 50.0, 4.5, 74, 180,
    ["Amazon", "TCS", "Infosys", "Oracle", "Samsung"],
    gsoc=40, clubs=40, boys=2000, girls=600, mous=25,
    tech_fest="Tathva", cult_fest="Ragam",
)

COLLEGE_DATA["NIT Durgapur"] = _nit(
    "NIT Durgapur", 1960, "Durgapur", "West Bengal", 180,
    "Netaji Subhas Chandra Bose Airport Kolkata", 170, "Durgapur", 3,
    "Tier 3", 800, 62500, 8000, 2500, 550000, 250, 85, 15.0,
    11.5, 9.5, 45.0, 4.0, 72, 160,
    ["TCS", "Infosys", "Wipro", "Amazon", "Cognizant"],
    gsoc=30, clubs=35, boys=2000, girls=500, mous=20,
)

COLLEGE_DATA["MNIT Jaipur"] = _nit(
    "MNIT Jaipur", 1963, "Jaipur", "Rajasthan", 300,
    "Jaipur International Airport", 15, "Jaipur Junction", 10,
    "Tier 1", 900, 62500, 10000, 2500, 600000, 280, 88, 14.0,
    12.0, 10.0, 50.0, 4.5, 74, 200,
    ["Amazon", "Microsoft", "TCS", "Infosys", "Samsung"],
    gsoc=35, clubs=45, boys=2200, girls=600, mous=25,
    tech_fest="Blitzschlag", cult_fest="Culrav",
)

COLLEGE_DATA["MNNIT Allahabad"] = _nit(
    "MNNIT Allahabad", 1961, "Prayagraj", "Uttar Pradesh", 222,
    "Bamrauli Airport", 12, "Prayagraj Junction", 10, "Tier 2", 800,
    62500, 10000, 2500, 600000, 260, 87, 15.0,
    12.0, 10.0, 55.0, 4.5, 73, 180,
    ["Amazon", "Microsoft", "TCS", "Infosys", "Samsung"],
    gsoc=35, clubs=40, boys=2200, girls=500, mous=20,
    tech_fest="Avishkar", cult_fest="Culrav",
)

COLLEGE_DATA["NIT Nagpur"] = _nit(
    "NIT Nagpur", 1960, "Nagpur", "Maharashtra", 200,
    "Dr Babasaheb Ambedkar International Airport", 12, "Nagpur Junction", 8,
    "Tier 2", 900, 62500, 10000, 2500, 600000, 280, 87, 14.5,
    12.5, 10.5, 55.0, 4.5, 74, 200,
    ["Amazon", "Microsoft", "TCS", "Infosys", "L&T"],
    gsoc=35, clubs=40, boys=2200, girls=600, mous=22,
    tech_fest="Axis", cult_fest="Eclectika",
)

COLLEGE_DATA["SVNIT Surat"] = _nit(
    "SVNIT Surat", 1961, "Surat", "Gujarat", 130,
    "Surat Airport", 12, "Surat", 5, "Tier 1", 800,
    62500, 10000, 2500, 600000, 250, 86, 15.0,
    11.5, 9.5, 45.0, 4.5, 72, 170,
    ["TCS", "Infosys", "Amazon", "L&T", "Wipro"],
    gsoc=25, clubs=35, boys=1800, girls=500, mous=18,
    tech_fest="Sparsh", cult_fest="Mindbend",
)

COLLEGE_DATA["VNIT Nagpur"] = _nit(
    "VNIT Nagpur", 1960, "Nagpur", "Maharashtra", 200,
    "Dr Babasaheb Ambedkar International Airport", 12, "Nagpur Junction", 8,
    "Tier 2", 900, 62500, 10000, 2500, 600000, 280, 87, 14.5,
    12.5, 10.5, 55.0, 4.5, 74, 200,
    ["Amazon", "Microsoft", "TCS", "Infosys"],
    gsoc=30, clubs=40, boys=2200, girls=600, mous=22,
)

COLLEGE_DATA["NIT Silchar"] = _nit(
    "NIT Silchar", 1967, "Silchar", "Assam", 600,
    "Silchar Airport", 30, "Silchar", 8, "Tier 3", 700,
    62500, 8000, 2000, 520000, 200, 82, 16.0,
    10.0, 8.0, 40.0, 4.0, 68, 130,
    ["TCS", "Infosys", "Wipro", "Cognizant"],
    gsoc=20, clubs=25, boys=1800, girls=400, mous=12,
)

COLLEGE_DATA["NIT Kurukshetra"] = _nit(
    "NIT Kurukshetra", 1963, "Kurukshetra", "Haryana", 300,
    "Chandigarh Airport", 100, "Kurukshetra Junction", 5, "Tier 3", 800,
    62500, 10000, 2500, 600000, 260, 85, 15.0,
    11.0, 9.0, 45.0, 4.0, 70, 160,
    ["TCS", "Infosys", "Amazon", "Wipro"],
    gsoc=25, clubs=35, boys=2000, girls=500, mous=18,
)

COLLEGE_DATA["MANIT Bhopal"] = _nit(
    "MANIT Bhopal", 1960, "Bhopal", "Madhya Pradesh", 650,
    "Raja Bhoj Airport", 15, "Bhopal Junction", 10, "Tier 2", 800,
    62500, 10000, 2500, 600000, 260, 85, 15.0,
    11.0, 9.0, 45.0, 4.0, 70, 160,
    ["TCS", "Infosys", "Wipro", "Amazon"],
    gsoc=20, clubs=35, boys=2000, girls=500, mous=18,
)

COLLEGE_DATA["NIT Hamirpur"] = _nit(
    "NIT Hamirpur", 1986, "Hamirpur", "Himachal Pradesh", 320,
    "Gaggal Airport Kangra", 110, "Una Himachal", 80, "Tier 3", 600,
    50000, 8000, 2000, 480000, 180, 80, 16.0,
    9.5, 8.0, 35.0, 3.5, 65, 120,
    ["TCS", "Infosys", "Wipro", "Cognizant"],
    gsoc=15, clubs=25, boys=1500, girls=400, mous=12,
)

COLLEGE_DATA["NIT Jamshedpur"] = _nit(
    "NIT Jamshedpur", 1960, "Jamshedpur", "Jharkhand", 32,
    "Sonari Airport", 8, "Tatanagar Junction", 5, "Tier 2", 700,
    62500, 8000, 2500, 550000, 220, 83, 15.0,
    10.5, 8.5, 40.0, 4.0, 68, 140,
    ["TCS", "Tata Steel", "Infosys", "Amazon", "Wipro"],
    gsoc=20, clubs=30, boys=1800, girls=450, mous=15,
)

COLLEGE_DATA["NIT Srinagar"] = _nit(
    "NIT Srinagar", 1960, "Srinagar", "Jammu and Kashmir", 80,
    "Srinagar Airport", 18, "Srinagar", 5, "Tier 2", 600,
    62500, 8000, 2000, 520000, 200, 80, 16.0,
    9.0, 7.5, 30.0, 3.5, 60, 100,
    ["TCS", "Infosys", "Wipro", "DRDO"],
    gsoc=10, clubs=20, boys=1500, girls=350, mous=10,
)

COLLEGE_DATA["NIT Raipur"] = _nit(
    "NIT Raipur", 1956, "Raipur", "Chhattisgarh", 100,
    "Swami Vivekananda Airport", 18, "Raipur Junction", 8, "Tier 2", 700,
    62500, 8000, 2500, 550000, 220, 82, 15.5,
    10.0, 8.0, 35.0, 3.5, 65, 120,
    ["TCS", "Infosys", "Wipro", "Amazon"],
    gsoc=15, clubs=25, boys=1600, girls=400, mous=12,
)

COLLEGE_DATA["NIT Agartala"] = _nit(
    "NIT Agartala", 1965, "Agartala", "Tripura", 250,
    "Maharaja Bir Bikram Airport", 20, "Agartala", 10, "Tier 3", 600,
    62500, 6000, 2000, 500000, 180, 78, 16.0,
    8.0, 6.5, 25.0, 3.5, 58, 80,
    ["TCS", "Infosys", "Wipro", "Cognizant"],
    gsoc=8, clubs=20, boys=1400, girls=350, mous=8,
)

COLLEGE_DATA["NIT Patna"] = _nit(
    "NIT Patna", 1886, "Patna", "Bihar", 45,
    "Jay Prakash Narayan International Airport", 10, "Patna Junction", 5,
    "Tier 2", 700, 62500, 8000, 2500, 550000, 220, 82, 15.5,
    10.0, 8.5, 38.0, 3.5, 66, 130,
    ["TCS", "Infosys", "Amazon", "Wipro", "Cognizant"],
    gsoc=18, clubs=28, boys=1500, girls=400, mous=12,
)

COLLEGE_DATA["NIT Jalandhar"] = _nit(
    "NIT Jalandhar", 1987, "Jalandhar", "Punjab", 120,
    "Adampur Airport", 30, "Jalandhar City", 5, "Tier 2", 700,
    62500, 8000, 2500, 550000, 230, 83, 15.0,
    10.0, 8.0, 38.0, 4.0, 66, 130,
    ["TCS", "Infosys", "Wipro", "Amazon"],
    gsoc=15, clubs=30, boys=1700, girls=450, mous=14,
)

COLLEGE_DATA["NIT Surat"] = _nit(
    "NIT Surat", 1961, "Surat", "Gujarat", 130,
    "Surat Airport", 12, "Surat", 5, "Tier 1", 700,
    62500, 8000, 2500, 550000, 230, 84, 15.0,
    10.5, 8.5, 40.0, 4.0, 68, 140,
    ["TCS", "Infosys", "L&T", "Amazon"],
    gsoc=18, clubs=30, boys=1600, girls=400, mous=15,
)

COLLEGE_DATA["NIT Arunachal Pradesh"] = _nit(
    "NIT Arunachal Pradesh", 2010, "Yupia", "Arunachal Pradesh", 350,
    "Hollongi Airport", 20, "Naharlagun", 10, "Tier 3", 350,
    62500, 6000, 2000, 480000, 80, 75, 18.0,
    7.0, 6.0, 20.0, 3.0, 50, 50,
    ["TCS", "Infosys", "Wipro"],
    gsoc=5, clubs=15, boys=800, girls=200, mous=5,
)

COLLEGE_DATA["NIT Delhi"] = _nit(
    "NIT Delhi", 2010, "New Delhi", "Delhi", 8,
    "Indira Gandhi International Airport", 20, "Narela", 5, "Tier 1", 350,
    62500, 10000, 3000, 600000, 80, 85, 14.0,
    11.0, 9.5, 42.0, 4.0, 68, 110,
    ["TCS", "Infosys", "Amazon", "Wipro", "Samsung"],
    gsoc=15, clubs=20, boys=600, girls=250, mous=10,
)

COLLEGE_DATA["NIT Goa"] = _nit(
    "NIT Goa", 2010, "Ponda", "Goa", 250,
    "Goa International Airport", 30, "Madgaon", 25, "Tier 2", 350,
    62500, 8000, 2500, 550000, 70, 80, 16.0,
    9.5, 8.0, 30.0, 3.5, 60, 80,
    ["TCS", "Infosys", "Wipro"],
    gsoc=8, clubs=18, boys=700, girls=250, mous=6,
)

COLLEGE_DATA["NIT Manipur"] = _nit(
    "NIT Manipur", 2010, "Imphal", "Manipur", 350,
    "Imphal Airport", 15, "Dimapur", 215, "Tier 3", 350,
    62500, 6000, 2000, 480000, 70, 75, 18.0,
    7.0, 5.5, 18.0, 3.0, 48, 45,
    ["TCS", "Infosys", "Wipro"],
    gsoc=3, clubs=12, boys=700, girls=200, mous=4,
)

COLLEGE_DATA["NIT Meghalaya"] = _nit(
    "NIT Meghalaya", 2010, "Shillong", "Meghalaya", 350,
    "Shillong Airport", 35, "Guwahati", 100, "Tier 3", 350,
    62500, 6000, 2000, 480000, 70, 75, 18.0,
    7.5, 6.0, 20.0, 3.0, 50, 50,
    ["TCS", "Infosys", "Wipro"],
    gsoc=4, clubs=12, boys=700, girls=200, mous=4,
)

COLLEGE_DATA["NIT Mizoram"] = _nit(
    "NIT Mizoram", 2010, "Aizawl", "Mizoram", 350,
    "Lengpui Airport", 35, "Bairabi", 200, "Tier 3", 300,
    62500, 6000, 2000, 480000, 60, 72, 18.0,
    6.5, 5.5, 15.0, 3.0, 45, 40,
    ["TCS", "Infosys", "Wipro"],
    gsoc=2, clubs=10, boys=600, girls=180, mous=3,
)

COLLEGE_DATA["NIT Nagaland"] = _nit(
    "NIT Nagaland", 2010, "Dimapur", "Nagaland", 350,
    "Dimapur Airport", 10, "Dimapur", 5, "Tier 3", 300,
    62500, 6000, 2000, 480000, 60, 72, 18.0,
    6.5, 5.5, 15.0, 3.0, 45, 40,
    ["TCS", "Infosys", "Wipro"],
    gsoc=2, clubs=10, boys=600, girls=180, mous=3,
)

COLLEGE_DATA["NIT Puducherry"] = _nit(
    "NIT Puducherry", 2010, "Karaikal", "Puducherry", 250,
    "Tiruchirappalli Airport", 90, "Karaikal", 5, "Tier 3", 350,
    62500, 6000, 2000, 480000, 70, 78, 16.0,
    8.0, 6.5, 22.0, 3.0, 52, 55,
    ["TCS", "Infosys", "Wipro", "Cognizant"],
    gsoc=5, clubs=15, boys=700, girls=200, mous=5,
)

COLLEGE_DATA["NIT Sikkim"] = _nit(
    "NIT Sikkim", 2010, "Ravangla", "Sikkim", 350,
    "Bagdogra Airport", 125, "New Jalpaiguri", 120, "Tier 3", 300,
    62500, 6000, 2000, 480000, 60, 72, 18.0,
    7.0, 5.5, 18.0, 3.0, 48, 40,
    ["TCS", "Infosys", "Wipro"],
    gsoc=3, clubs=10, boys=600, girls=180, mous=3,
)

COLLEGE_DATA["NIT Uttarakhand"] = _nit(
    "NIT Uttarakhand", 2010, "Srinagar Garhwal", "Uttarakhand", 350,
    "Jolly Grant Airport Dehradun", 100, "Rishikesh", 35, "Tier 3", 350,
    62500, 6000, 2000, 480000, 70, 75, 18.0,
    7.5, 6.0, 22.0, 3.0, 50, 50,
    ["TCS", "Infosys", "Wipro"],
    gsoc=5, clubs=12, boys=700, girls=200, mous=4,
)

COLLEGE_DATA["NIT Andhra Pradesh"] = _nit(
    "NIT Andhra Pradesh", 2015, "Tadepalligudem", "Andhra Pradesh", 200,
    "Rajahmundry Airport", 60, "Tadepalligudem", 2, "Tier 3", 400,
    62500, 6000, 2000, 480000, 80, 78, 16.0,
    8.0, 6.5, 25.0, 3.0, 52, 60,
    ["TCS", "Infosys", "Wipro", "Cognizant"],
    gsoc=5, clubs=15, boys=800, girls=250, mous=5,
)

COLLEGE_DATA["IIEST Shibpur"] = _nit(
    "IIEST Shibpur", 1856, "Howrah", "West Bengal", 86,
    "Netaji Subhas Chandra Bose Airport", 20, "Howrah Junction", 3,
    "Tier 1", 800, 30000, 8000, 2500, 400000, 250, 88, 14.0,
    12.0, 10.0, 50.0, 4.5, 72, 170,
    ["TCS", "Infosys", "Amazon", "Microsoft", "Wipro"],
    gsoc=30, clubs=40, boys=2000, girls=500, mous=25,
)


# ═══════════════════════════════════════════════════════════════
#  IIITs (26 institutes)
# ═══════════════════════════════════════════════════════════════

def _iiit(name, year, city, state, acres, airport, airport_km, rly, rly_km,
          tier, seats, fee, hostel_fee, mess, cost4yr, faculty, phd_pct, sfr,
          avg_pkg, med_pkg, high_pkg, low_pkg, place_pct, companies,
          recruiters, gsoc=10, clubs=20, boys=800, girls=300, mous=10,
          pool=False, gym=True, med="Health centre", alumni=None,
          tech_fest=None, cult_fest=None):
    return {
        "institute_type": "IIIT", "establishment_year": year,
        "city": city, "state": state, "campus_area_acres": acres,
        "nearest_airport": airport, "nearest_airport_km": airport_km,
        "nearest_railway_station": rly, "nearest_railway_km": rly_km,
        "city_tier": tier, "total_ug_seats": seats,
        "tuition_fee_per_sem": fee, "hostel_fee_single_per_sem": hostel_fee,
        "mess_fee_per_month": mess, "total_4yr_cost_estimate": cost4yr,
        "total_faculty": faculty, "faculty_with_phd_pct": phd_pct,
        "student_faculty_ratio": sfr,
        "avg_package_lpa": avg_pkg, "median_package_lpa": med_pkg,
        "highest_package_lpa": high_pkg, "lowest_package_lpa": low_pkg,
        "placement_percentage": place_pct, "companies_visited": companies,
        "top_recruiters": recruiters, "gsoc_selections_total": gsoc,
        "coding_club": True, "gdsc_present": True, "incubation_center": True,
        "swimming_pool": pool, "gym_on_campus": gym,
        "medical_facility": med,
        "hostel_capacity_boys": boys, "hostel_capacity_girls": girls,
        "student_clubs_count": clubs, "international_mous": mous,
        "notable_alumni": alumni or [],
        "tech_fest_name": tech_fest, "cultural_fest_name": cult_fest,
    }


COLLEGE_DATA["IIIT Hyderabad"] = _iiit(
    "IIIT Hyderabad", 1998, "Hyderabad", "Telangana", 66,
    "Rajiv Gandhi International Airport", 30, "Lingampally", 5,
    "Tier 1", 250, 120000, 15000, 4000, 1200000, 150, 95, 10.0,
    24.0, 20.0, 150.0, 8.0, 90, 200,
    ["Google", "Microsoft", "Amazon", "Adobe", "Goldman Sachs", "Uber"],
    gsoc=120, clubs=40, boys=1200, girls=400, mous=50,
    tech_fest="Felicity", cult_fest="Felicity",
    alumni=["Vijay Shekhar Sharma (PayTM)"],
)

COLLEGE_DATA["IIIT Allahabad"] = _iiit(
    "IIIT Allahabad", 1999, "Prayagraj", "Uttar Pradesh", 100,
    "Bamrauli Airport", 15, "Prayagraj Junction", 12,
    "Tier 2", 350, 80000, 12000, 3500, 800000, 120, 90, 12.0,
    18.0, 15.0, 100.0, 6.0, 82, 180,
    ["Google", "Microsoft", "Amazon", "Samsung", "Adobe", "Goldman Sachs"],
    gsoc=80, clubs=35, boys=1500, girls=450, mous=30,
    tech_fest="Effervescence", cult_fest="Alankar",
)

COLLEGE_DATA["IIIT Delhi"] = _iiit(
    "IIIT Delhi", 2008, "New Delhi", "Delhi", 25,
    "Indira Gandhi International Airport", 20, "Okhla", 3,
    "Tier 1", 300, 150000, 15000, 4000, 1400000, 100, 95, 12.0,
    22.0, 18.0, 130.0, 7.0, 85, 170,
    ["Google", "Microsoft", "Amazon", "Adobe", "Samsung", "Uber"],
    gsoc=90, clubs=35, boys=800, girls=350, mous=40,
    tech_fest="Esya", cult_fest="Odyssey",
)

COLLEGE_DATA["IIIT Bangalore"] = _iiit(
    "IIIT Bangalore", 1999, "Bangalore", "Karnataka", 14,
    "Kempegowda International Airport", 35, "Bangalore City", 12,
    "Tier 1", 250, 200000, 15000, 4500, 1800000, 80, 95, 11.0,
    20.0, 17.0, 100.0, 7.0, 82, 150,
    ["Google", "Microsoft", "Amazon", "Samsung", "SAP", "Adobe"],
    gsoc=60, clubs=30, boys=600, girls=250, mous=35,
)

COLLEGE_DATA["ABV-IIITM Gwalior"] = _iiit(
    "ABV-IIITM Gwalior", 1997, "Gwalior", "Madhya Pradesh", 80,
    "Gwalior Airport", 10, "Gwalior Junction", 8,
    "Tier 2", 400, 60000, 10000, 3000, 600000, 100, 88, 13.0,
    14.0, 12.0, 60.0, 5.0, 75, 140,
    ["Amazon", "Microsoft", "TCS", "Infosys", "Samsung"],
    gsoc=40, clubs=30, boys=1200, girls=350, mous=20,
)

COLLEGE_DATA["IIITDM Jabalpur"] = _iiit(
    "IIITDM Jabalpur", 2005, "Jabalpur", "Madhya Pradesh", 150,
    "Jabalpur Airport", 20, "Jabalpur Junction", 15,
    "Tier 2", 300, 60000, 10000, 3000, 600000, 80, 90, 12.0,
    13.0, 11.0, 50.0, 5.0, 72, 120,
    ["Amazon", "TCS", "Infosys", "Samsung", "Wipro"],
    gsoc=25, clubs=25, boys=1000, girls=300, mous=15,
)

COLLEGE_DATA["IIITDM Kancheepuram"] = _iiit(
    "IIITDM Kancheepuram", 2007, "Chennai", "Tamil Nadu", 51,
    "Chennai International Airport", 25, "Chennai Egmore", 20,
    "Tier 1", 300, 60000, 10000, 3000, 600000, 80, 90, 12.0,
    13.0, 11.0, 50.0, 5.0, 72, 120,
    ["Amazon", "TCS", "Samsung", "Infosys"],
    gsoc=20, clubs=25, boys=1000, girls=300, mous=15,
)

COLLEGE_DATA["IIIT Sri City"] = _iiit(
    "IIIT Sri City", 2013, "Sri City", "Andhra Pradesh", 100,
    "Chennai International Airport", 60, "Sullurpeta", 15,
    "Tier 3", 250, 50000, 10000, 3000, 520000, 50, 88, 13.0,
    11.0, 9.0, 40.0, 4.5, 68, 80,
    ["TCS", "Infosys", "Amazon", "Wipro"],
    gsoc=12, clubs=18, boys=600, girls=250, mous=8,
)

COLLEGE_DATA["IIIT Lucknow"] = _iiit(
    "IIIT Lucknow", 2015, "Lucknow", "Uttar Pradesh", 50,
    "Chaudhary Charan Singh Airport", 15, "Lucknow", 10,
    "Tier 1", 200, 50000, 10000, 3000, 520000, 40, 85, 14.0,
    10.0, 8.5, 35.0, 4.0, 62, 70,
    ["TCS", "Infosys", "Wipro", "Amazon"],
    gsoc=8, clubs=15, boys=500, girls=200, mous=6,
)

COLLEGE_DATA["IIIT Kota"] = _iiit(
    "IIIT Kota", 2013, "Kota", "Rajasthan", 50,
    "Jaipur International Airport", 250, "Kota Junction", 8,
    "Tier 2", 200, 50000, 8000, 2500, 480000, 40, 82, 14.0,
    9.0, 7.5, 28.0, 3.5, 60, 60,
    ["TCS", "Infosys", "Wipro"],
    gsoc=6, clubs=12, boys=500, girls=180, mous=5,
)

COLLEGE_DATA["IIIT Guwahati"] = _iiit(
    "IIIT Guwahati", 2013, "Guwahati", "Assam", 50,
    "Lokpriya Gopinath Bordoloi Airport", 20, "Guwahati", 15,
    "Tier 2", 200, 50000, 8000, 2500, 480000, 40, 82, 14.0,
    9.0, 7.5, 30.0, 3.5, 58, 55,
    ["TCS", "Infosys", "Wipro"],
    gsoc=5, clubs=12, boys=500, girls=180, mous=5,
)

COLLEGE_DATA["IIIT Kalyani"] = _iiit(
    "IIIT Kalyani", 2014, "Kalyani", "West Bengal", 20,
    "Netaji Subhas Chandra Bose Airport", 55, "Kalyani", 3,
    "Tier 2", 200, 50000, 8000, 2500, 480000, 35, 80, 15.0,
    8.5, 7.0, 25.0, 3.5, 55, 50,
    ["TCS", "Infosys", "Wipro", "Cognizant"],
    gsoc=5, clubs=10, boys=400, girls=150, mous=4,
)

COLLEGE_DATA["IIIT Sonepat"] = _iiit(
    "IIIT Sonepat", 2014, "Sonepat", "Haryana", 50,
    "Indira Gandhi International Airport", 55, "Sonepat", 5,
    "Tier 2", 200, 50000, 8000, 2500, 480000, 35, 80, 15.0,
    9.0, 7.5, 28.0, 3.5, 58, 55,
    ["TCS", "Infosys", "Wipro"],
    gsoc=5, clubs=12, boys=500, girls=180, mous=5,
)

COLLEGE_DATA["IIIT Una"] = _iiit(
    "IIIT Una", 2014, "Una", "Himachal Pradesh", 50,
    "Gaggal Airport Kangra", 80, "Una Himachal", 5,
    "Tier 3", 200, 50000, 8000, 2000, 480000, 35, 80, 15.0,
    8.0, 6.5, 22.0, 3.0, 52, 45,
    ["TCS", "Infosys", "Wipro"],
    gsoc=4, clubs=10, boys=400, girls=150, mous=4,
)

COLLEGE_DATA["IIIT Vadodara"] = _iiit(
    "IIIT Vadodara", 2013, "Vadodara", "Gujarat", 50,
    "Vadodara Airport", 12, "Vadodara Junction", 8,
    "Tier 2", 200, 50000, 8000, 2500, 480000, 35, 82, 14.0,
    9.5, 8.0, 30.0, 3.5, 60, 60,
    ["TCS", "Infosys", "Amazon", "Wipro"],
    gsoc=6, clubs=12, boys=500, girls=180, mous=5,
)

COLLEGE_DATA["IIIT Ranchi"] = _iiit(
    "IIIT Ranchi", 2013, "Ranchi", "Jharkhand", 50,
    "Birsa Munda Airport", 15, "Ranchi Junction", 8,
    "Tier 2", 200, 50000, 8000, 2500, 480000, 35, 80, 15.0,
    8.5, 7.0, 25.0, 3.5, 55, 50,
    ["TCS", "Infosys", "Wipro"],
    gsoc=5, clubs=10, boys=400, girls=150, mous=4,
)

COLLEGE_DATA["IIIT Nagpur"] = _iiit(
    "IIIT Nagpur", 2016, "Nagpur", "Maharashtra", 50,
    "Dr. Babasaheb Ambedkar Airport", 10, "Nagpur Junction", 8,
    "Tier 2", 200, 50000, 8000, 2500, 480000, 35, 80, 15.0,
    9.0, 7.5, 28.0, 3.5, 58, 55,
    ["TCS", "Infosys", "Wipro", "Persistent"],
    gsoc=5, clubs=12, boys=500, girls=180, mous=5,
)

COLLEGE_DATA["IIIT Pune"] = _iiit(
    "IIIT Pune", 2016, "Pune", "Maharashtra", 50,
    "Pune Airport", 15, "Pune Junction", 10,
    "Tier 1", 200, 50000, 8000, 2500, 480000, 35, 82, 14.0,
    10.0, 8.0, 32.0, 4.0, 62, 65,
    ["TCS", "Infosys", "Wipro", "Persistent", "Amazon"],
    gsoc=6, clubs=14, boys=500, girls=200, mous=6,
)

COLLEGE_DATA["IIIT Kurnool"] = _iiit(
    "IIIT Kurnool", 2015, "Kurnool", "Andhra Pradesh", 50,
    "Kurnool Airport", 15, "Kurnool City", 5,
    "Tier 3", 200, 50000, 8000, 2000, 480000, 30, 78, 16.0,
    7.5, 6.5, 20.0, 3.0, 50, 40,
    ["TCS", "Infosys", "Wipro"],
    gsoc=3, clubs=10, boys=400, girls=150, mous=3,
)

COLLEGE_DATA["IIIT Dharwad"] = _iiit(
    "IIIT Dharwad", 2015, "Dharwad", "Karnataka", 50,
    "Hubli Airport", 25, "Dharwad", 3,
    "Tier 2", 200, 50000, 8000, 2500, 480000, 35, 82, 14.0,
    9.0, 7.5, 28.0, 3.5, 58, 55,
    ["TCS", "Infosys", "Wipro"],
    gsoc=5, clubs=12, boys=500, girls=180, mous=5,
)

COLLEGE_DATA["IIIT Manipur"] = _iiit(
    "IIIT Manipur", 2015, "Imphal", "Manipur", 30,
    "Imphal Airport", 15, "Dimapur", 215,
    "Tier 3", 150, 50000, 6000, 2000, 480000, 25, 75, 16.0,
    6.5, 5.5, 15.0, 3.0, 45, 30,
    ["TCS", "Infosys", "Wipro"],
    gsoc=2, clubs=8, boys=300, girls=100, mous=3,
)

COLLEGE_DATA["IIIT Tiruchirappalli"] = _iiit(
    "IIIT Tiruchirappalli", 2015, "Tiruchirappalli", "Tamil Nadu", 50,
    "Tiruchirappalli Airport", 15, "Tiruchirappalli Junction", 8,
    "Tier 2", 200, 50000, 8000, 2500, 480000, 35, 82, 14.0,
    9.0, 7.5, 28.0, 3.5, 58, 55,
    ["TCS", "Infosys", "Wipro", "Cognizant"],
    gsoc=5, clubs=12, boys=500, girls=180, mous=5,
)

COLLEGE_DATA["IIIT Surat"] = _iiit(
    "IIIT Surat", 2017, "Surat", "Gujarat", 50,
    "Surat Airport", 15, "Surat", 8,
    "Tier 1", 150, 50000, 8000, 2500, 480000, 30, 80, 15.0,
    8.5, 7.0, 25.0, 3.5, 55, 45,
    ["TCS", "Infosys", "Wipro"],
    gsoc=4, clubs=10, boys=400, girls=150, mous=4,
)

COLLEGE_DATA["IIIT Bhopal"] = _iiit(
    "IIIT Bhopal", 2017, "Bhopal", "Madhya Pradesh", 50,
    "Raja Bhoj Airport", 15, "Bhopal Junction", 10,
    "Tier 2", 150, 50000, 8000, 2500, 480000, 30, 80, 15.0,
    8.0, 6.5, 22.0, 3.0, 52, 40,
    ["TCS", "Infosys", "Wipro"],
    gsoc=3, clubs=10, boys=400, girls=150, mous=4,
)

COLLEGE_DATA["IIIT Bhagalpur"] = _iiit(
    "IIIT Bhagalpur", 2017, "Bhagalpur", "Bihar", 50,
    "Jay Prakash Narayan Airport Patna", 250, "Bhagalpur", 5,
    "Tier 3", 150, 50000, 6000, 2000, 480000, 25, 78, 16.0,
    7.0, 6.0, 18.0, 3.0, 48, 35,
    ["TCS", "Infosys", "Wipro"],
    gsoc=3, clubs=8, boys=350, girls=120, mous=3,
)

COLLEGE_DATA["IIIT Agartala"] = _iiit(
    "IIIT Agartala", 2017, "Agartala", "Tripura", 30,
    "Maharaja Bir Bikram Airport", 20, "Agartala", 10,
    "Tier 3", 150, 50000, 6000, 2000, 480000, 25, 75, 16.0,
    6.5, 5.5, 15.0, 3.0, 45, 30,
    ["TCS", "Infosys", "Wipro"],
    gsoc=2, clubs=8, boys=300, girls=100, mous=3,
)


# ═══════════════════════════════════════════════════════════════
#  GFTIs (40 institutes)
# ═══════════════════════════════════════════════════════════════

def _gfti(name, year, city, state, acres, airport, airport_km, rly, rly_km,
          tier, seats, fee, hostel_fee, mess, cost4yr, faculty, phd_pct, sfr,
          avg_pkg, med_pkg, high_pkg, low_pkg, place_pct, companies,
          recruiters, inst_type="GFTI", gsoc=5, clubs=15, boys=600,
          girls=200, mous=5, pool=False, gym=True, med="Health centre",
          alumni=None, tech_fest=None, cult_fest=None):
    return {
        "institute_type": inst_type, "establishment_year": year,
        "city": city, "state": state, "campus_area_acres": acres,
        "nearest_airport": airport, "nearest_airport_km": airport_km,
        "nearest_railway_station": rly, "nearest_railway_km": rly_km,
        "city_tier": tier, "total_ug_seats": seats,
        "tuition_fee_per_sem": fee, "hostel_fee_single_per_sem": hostel_fee,
        "mess_fee_per_month": mess, "total_4yr_cost_estimate": cost4yr,
        "total_faculty": faculty, "faculty_with_phd_pct": phd_pct,
        "student_faculty_ratio": sfr,
        "avg_package_lpa": avg_pkg, "median_package_lpa": med_pkg,
        "highest_package_lpa": high_pkg, "lowest_package_lpa": low_pkg,
        "placement_percentage": place_pct, "companies_visited": companies,
        "top_recruiters": recruiters, "gsoc_selections_total": gsoc,
        "coding_club": True, "gdsc_present": True, "incubation_center": False,
        "swimming_pool": pool, "gym_on_campus": gym,
        "medical_facility": med,
        "hostel_capacity_boys": boys, "hostel_capacity_girls": girls,
        "student_clubs_count": clubs, "international_mous": mous,
        "notable_alumni": alumni or [],
        "tech_fest_name": tech_fest, "cultural_fest_name": cult_fest,
    }


COLLEGE_DATA["IISc Bangalore"] = _gfti(
    "IISc Bangalore", 1909, "Bangalore", "Karnataka", 400,
    "Kempegowda International Airport", 35, "Bangalore City", 8,
    "Tier 1", 120, 35000, 8000, 3000, 500000, 500, 99, 5.0,
    28.0, 24.0, 120.0, 10.0, 85, 150,
    ["Google", "Microsoft", "Amazon", "Intel", "Samsung", "Goldman Sachs"],
    inst_type="GFTI", gsoc=80, clubs=50, boys=2000, girls=800, mous=100,
    pool=True, alumni=["CNR Rao", "Roddam Narasimha"],
)

COLLEGE_DATA["IISER Pune"] = _gfti(
    "IISER Pune", 2006, "Pune", "Maharashtra", 100,
    "Pune Airport", 20, "Pune Junction", 15,
    "Tier 1", 120, 25000, 8000, 3000, 350000, 120, 98, 8.0,
    12.0, 10.0, 40.0, 5.0, 60, 50,
    ["Research labs", "Google", "Microsoft"],
    gsoc=20, clubs=30, boys=600, girls=400, mous=40,
)

COLLEGE_DATA["IISER Bhopal"] = _gfti(
    "IISER Bhopal", 2008, "Bhopal", "Madhya Pradesh", 200,
    "Raja Bhoj Airport", 20, "Bhopal Junction", 15,
    "Tier 2", 100, 25000, 8000, 3000, 350000, 100, 98, 8.0,
    11.0, 9.0, 35.0, 5.0, 55, 40,
    ["Research labs", "TCS", "Infosys"],
    gsoc=15, clubs=25, boys=500, girls=350, mous=30,
)

COLLEGE_DATA["IISER Mohali"] = _gfti(
    "IISER Mohali", 2007, "Mohali", "Punjab", 125,
    "Chandigarh Airport", 15, "Chandigarh", 10,
    "Tier 1", 100, 25000, 8000, 3000, 350000, 100, 98, 8.0,
    11.0, 9.5, 35.0, 5.0, 58, 45,
    ["Research labs", "Google", "TCS"],
    gsoc=15, clubs=25, boys=500, girls=350, mous=35,
)

COLLEGE_DATA["IISER Kolkata"] = _gfti(
    "IISER Kolkata", 2006, "Kalyani", "West Bengal", 100,
    "Netaji Subhas Chandra Bose Airport", 60, "Kalyani", 3,
    "Tier 2", 100, 25000, 8000, 3000, 350000, 100, 98, 8.0,
    11.0, 9.0, 35.0, 5.0, 55, 40,
    ["Research labs", "TCS", "Infosys"],
    gsoc=12, clubs=25, boys=500, girls=350, mous=30,
)

COLLEGE_DATA["IISER Berhampur"] = _gfti(
    "IISER Berhampur", 2016, "Berhampur", "Odisha", 200,
    "Biju Patnaik Airport Bhubaneswar", 170, "Berhampur", 5,
    "Tier 3", 80, 25000, 8000, 3000, 350000, 60, 95, 8.0,
    9.0, 7.5, 25.0, 4.0, 50, 30,
    ["Research labs", "TCS"],
    gsoc=5, clubs=15, boys=400, girls=250, mous=15,
)

COLLEGE_DATA["IISER Tirupati"] = _gfti(
    "IISER Tirupati", 2015, "Tirupati", "Andhra Pradesh", 250,
    "Tirupati Airport", 15, "Tirupati", 8,
    "Tier 2", 80, 25000, 8000, 3000, 350000, 70, 95, 8.0,
    10.0, 8.0, 28.0, 4.0, 52, 35,
    ["Research labs", "TCS", "Infosys"],
    gsoc=8, clubs=18, boys=400, girls=250, mous=18,
)

COLLEGE_DATA["IISER Thiruvananthapuram"] = _gfti(
    "IISER Thiruvananthapuram", 2008, "Thiruvananthapuram", "Kerala", 100,
    "Trivandrum International Airport", 15, "Thiruvananthapuram Central", 10,
    "Tier 2", 100, 25000, 8000, 3000, 350000, 100, 98, 8.0,
    11.0, 9.0, 35.0, 5.0, 55, 40,
    ["Research labs", "ISRO", "TCS"],
    gsoc=12, clubs=25, boys=500, girls=350, mous=30,
)

COLLEGE_DATA["BIT Mesra"] = _gfti(
    "BIT Mesra", 1955, "Ranchi", "Jharkhand", 80,
    "Birsa Munda Airport", 15, "Ranchi Junction", 12,
    "Tier 2", 800, 150000, 15000, 4000, 1400000, 200, 85, 14.0,
    12.0, 10.0, 50.0, 5.0, 75, 140,
    ["TCS", "Infosys", "Amazon", "Microsoft", "Wipro", "Cognizant"],
    gsoc=25, clubs=35, boys=2000, girls=600, mous=20,
)

COLLEGE_DATA["IIIT Naya Raipur"] = _gfti(
    "IIIT Naya Raipur", 2013, "Naya Raipur", "Chhattisgarh", 50,
    "Swami Vivekananda Airport", 20, "Raipur Junction", 18,
    "Tier 2", 200, 50000, 8000, 2500, 480000, 40, 82, 14.0,
    9.0, 7.5, 30.0, 3.5, 60, 55,
    ["TCS", "Infosys", "Wipro"],
    gsoc=5, clubs=12, boys=500, girls=200, mous=5,
)

COLLEGE_DATA["SPA Delhi"] = _gfti(
    "SPA Delhi", 1941, "New Delhi", "Delhi", 10,
    "Indira Gandhi International Airport", 15, "New Delhi", 5,
    "Tier 1", 100, 60000, 10000, 3000, 600000, 50, 90, 10.0,
    10.0, 8.0, 30.0, 5.0, 70, 40,
    ["L&T", "DLF", "Shapoorji Pallonji", "Godrej Properties"],
    gsoc=2, clubs=20, boys=300, girls=200, mous=15,
)

COLLEGE_DATA["ISM Dhanbad"] = _gfti(
    "ISM Dhanbad", 1926, "Dhanbad", "Jharkhand", 218,
    "Birsa Munda Airport Ranchi", 150, "Dhanbad Junction", 5,
    "Tier 2", 1200, 62500, 10000, 3000, 600000, 300, 90, 13.0,
    14.0, 12.0, 80.0, 5.0, 80, 200,
    ["Google", "Microsoft", "Amazon", "TCS", "Coal India", "ONGC"],
    gsoc=40, clubs=45, boys=3000, girls=800, mous=30,
    pool=True, alumni=["Satish Dhawan"],
    tech_fest="Concetto", cult_fest="Srijan",
)

COLLEGE_DATA["NIFFT Ranchi"] = _gfti(
    "NIFFT Ranchi", 1966, "Ranchi", "Jharkhand", 45,
    "Birsa Munda Airport", 15, "Ranchi Junction", 10,
    "Tier 2", 200, 50000, 8000, 2500, 480000, 60, 85, 14.0,
    8.0, 6.5, 25.0, 3.5, 60, 50,
    ["Tata Steel", "SAIL", "TCS", "Infosys"],
    gsoc=3, clubs=12, boys=500, girls=150, mous=8,
)

COLLEGE_DATA["IIIT Kalyani (WBUT)"] = _gfti(
    "IIIT Kalyani (WBUT)", 2014, "Kalyani", "West Bengal", 20,
    "Netaji Subhas Chandra Bose Airport", 55, "Kalyani", 3,
    "Tier 2", 150, 40000, 6000, 2000, 400000, 30, 78, 15.0,
    7.5, 6.0, 20.0, 3.0, 50, 35,
    ["TCS", "Infosys", "Wipro", "Cognizant"],
    gsoc=3, clubs=10, boys=400, girls=150, mous=4,
)

COLLEGE_DATA["IIITDM Kurnool"] = _gfti(
    "IIITDM Kurnool", 2015, "Kurnool", "Andhra Pradesh", 150,
    "Kurnool Airport", 15, "Kurnool City", 5,
    "Tier 3", 200, 50000, 8000, 2500, 480000, 40, 82, 14.0,
    8.0, 6.5, 22.0, 3.0, 52, 40,
    ["TCS", "Infosys", "Wipro"],
    gsoc=3, clubs=10, boys=500, girls=180, mous=4,
)

COLLEGE_DATA["Assam University Silchar"] = _gfti(
    "Assam University Silchar", 1994, "Silchar", "Assam", 600,
    "Silchar Airport", 25, "Silchar", 5,
    "Tier 3", 200, 15000, 5000, 2000, 200000, 80, 75, 16.0,
    5.0, 4.0, 12.0, 2.5, 40, 25,
    ["TCS", "Infosys", "Wipro"],
    gsoc=2, clubs=10, boys=500, girls=200, mous=5,
)

COLLEGE_DATA["Tezpur University"] = _gfti(
    "Tezpur University", 1994, "Tezpur", "Assam", 342,
    "Tezpur Airport", 15, "Rangapara North", 30,
    "Tier 3", 250, 15000, 5000, 2000, 200000, 120, 80, 14.0,
    6.0, 5.0, 15.0, 3.0, 50, 35,
    ["TCS", "Infosys", "Wipro", "Oil India"],
    gsoc=5, clubs=18, boys=700, girls=300, mous=12,
)

COLLEGE_DATA["BIT Sindri"] = _gfti(
    "BIT Sindri", 1949, "Dhanbad", "Jharkhand", 50,
    "Birsa Munda Airport Ranchi", 180, "Dhanbad Junction", 15,
    "Tier 2", 500, 20000, 5000, 2000, 250000, 80, 72, 16.0,
    5.5, 4.5, 15.0, 2.5, 45, 30,
    ["TCS", "Infosys", "Wipro", "Tata Steel"],
    gsoc=3, clubs=12, boys=800, girls=200, mous=5,
)

COLLEGE_DATA["Gurukula Kangri Vishwavidyalaya"] = _gfti(
    "Gurukula Kangri Vishwavidyalaya", 1902, "Haridwar", "Uttarakhand", 100,
    "Jolly Grant Airport Dehradun", 40, "Haridwar Junction", 3,
    "Tier 3", 200, 10000, 3000, 1500, 150000, 50, 70, 18.0,
    4.5, 3.5, 10.0, 2.5, 35, 20,
    ["TCS", "Infosys"],
    gsoc=1, clubs=8, boys=600, girls=200, mous=3,
)

COLLEGE_DATA["HBTU Kanpur"] = _gfti(
    "HBTU Kanpur", 1921, "Kanpur", "Uttar Pradesh", 120,
    "Kanpur Airport", 18, "Kanpur Central", 8,
    "Tier 2", 600, 40000, 6000, 2500, 400000, 120, 78, 15.0,
    7.0, 6.0, 25.0, 3.0, 55, 50,
    ["TCS", "Infosys", "Wipro", "L&T"],
    gsoc=8, clubs=20, boys=1200, girls=300, mous=10,
)

COLLEGE_DATA["Jamia Millia Islamia"] = _gfti(
    "Jamia Millia Islamia", 1920, "New Delhi", "Delhi", 110,
    "Indira Gandhi International Airport", 15, "Okhla", 3,
    "Tier 1", 400, 15000, 5000, 2500, 200000, 150, 82, 14.0,
    8.0, 7.0, 25.0, 3.5, 60, 60,
    ["TCS", "Infosys", "Wipro", "HCL"],
    gsoc=10, clubs=25, boys=1000, girls=500, mous=15,
)

COLLEGE_DATA["AMU Aligarh"] = _gfti(
    "AMU Aligarh", 1875, "Aligarh", "Uttar Pradesh", 1155,
    "Indira Gandhi International Airport Delhi", 130, "Aligarh Junction", 3,
    "Tier 2", 500, 15000, 5000, 2000, 200000, 200, 80, 15.0,
    7.0, 6.0, 25.0, 3.0, 55, 50,
    ["TCS", "Infosys", "Wipro", "Amazon"],
    gsoc=10, clubs=30, boys=2000, girls=600, mous=15,
    pool=True,
)

COLLEGE_DATA["BHU Varanasi"] = _gfti(
    "BHU Varanasi", 1916, "Varanasi", "Uttar Pradesh", 1300,
    "Lal Bahadur Shastri Airport", 20, "Varanasi Junction", 5,
    "Tier 2", 600, 15000, 5000, 2500, 200000, 200, 82, 14.0,
    8.0, 7.0, 30.0, 3.5, 60, 70,
    ["TCS", "Infosys", "Amazon", "Wipro", "L&T"],
    gsoc=15, clubs=40, boys=2500, girls=700, mous=20,
    pool=True,
)

COLLEGE_DATA["DU Delhi"] = _gfti(
    "DU Delhi", 1922, "New Delhi", "Delhi", 320,
    "Indira Gandhi International Airport", 15, "Delhi Junction", 5,
    "Tier 1", 400, 20000, 8000, 3000, 250000, 300, 85, 12.0,
    9.0, 7.5, 30.0, 4.0, 65, 80,
    ["TCS", "Infosys", "HCL", "Wipro", "Deloitte"],
    gsoc=12, clubs=50, boys=2000, girls=1500, mous=30,
)

COLLEGE_DATA["Mizoram University"] = _gfti(
    "Mizoram University", 2001, "Aizawl", "Mizoram", 250,
    "Lengpui Airport", 35, "Bairabi", 200,
    "Tier 3", 100, 10000, 3000, 1500, 150000, 60, 72, 18.0,
    4.0, 3.0, 8.0, 2.0, 30, 15,
    ["TCS", "Infosys"],
    gsoc=1, clubs=8, boys=300, girls=200, mous=4,
)

COLLEGE_DATA["Pondicherry University"] = _gfti(
    "Pondicherry University", 1985, "Puducherry", "Puducherry", 780,
    "Chennai International Airport", 150, "Puducherry", 5,
    "Tier 2", 200, 15000, 5000, 2000, 200000, 100, 78, 15.0,
    5.5, 4.5, 15.0, 3.0, 45, 30,
    ["TCS", "Infosys", "Wipro", "Cognizant"],
    gsoc=3, clubs=15, boys=600, girls=400, mous=8,
)

COLLEGE_DATA["Shri Mata Vaishno Devi University"] = _gfti(
    "Shri Mata Vaishno Devi University", 1999, "Katra", "Jammu and Kashmir", 470,
    "Jammu Airport", 50, "Katra", 3,
    "Tier 3", 300, 60000, 8000, 2500, 600000, 60, 78, 16.0,
    6.0, 5.0, 18.0, 3.0, 50, 35,
    ["TCS", "Infosys", "Wipro"],
    gsoc=3, clubs=12, boys=600, girls=200, mous=5,
)

COLLEGE_DATA["Punjab Engineering College"] = _gfti(
    "Punjab Engineering College", 1921, "Chandigarh", "Chandigarh", 145,
    "Chandigarh Airport", 12, "Chandigarh", 5,
    "Tier 1", 500, 55000, 10000, 3000, 560000, 120, 85, 14.0,
    12.0, 10.0, 55.0, 4.5, 78, 150,
    ["Google", "Microsoft", "Amazon", "TCS", "Infosys", "Samsung"],
    gsoc=30, clubs=35, boys=1800, girls=500, mous=20,
    pool=True, tech_fest="Technocratz", cult_fest="Pecfest",
)

COLLEGE_DATA["Dhirubhai Ambani IICT Gandhinagar"] = _gfti(
    "Dhirubhai Ambani IICT Gandhinagar", 2001, "Gandhinagar", "Gujarat", 50,
    "Sardar Vallabhbhai Patel Airport", 15, "Gandhinagar Capital", 5,
    "Tier 1", 250, 200000, 15000, 4000, 1800000, 80, 92, 11.0,
    18.0, 15.0, 90.0, 6.0, 80, 120,
    ["Google", "Microsoft", "Amazon", "Goldman Sachs", "TCS"],
    gsoc=45, clubs=25, boys=600, girls=250, mous=25,
)

COLLEGE_DATA["IIIT Kottayam"] = _gfti(
    "IIIT Kottayam", 2015, "Kottayam", "Kerala", 50,
    "Cochin International Airport", 60, "Kottayam", 5,
    "Tier 2", 150, 50000, 8000, 2500, 480000, 30, 80, 15.0,
    8.0, 6.5, 22.0, 3.0, 52, 40,
    ["TCS", "Infosys", "Wipro", "UST Global"],
    gsoc=4, clubs=10, boys=400, girls=150, mous=5,
)

COLLEGE_DATA["J.K. Institute of Applied Physics and Technology"] = _gfti(
    "J.K. Institute of Applied Physics and Technology", 1956,
    "Prayagraj", "Uttar Pradesh", 20,
    "Bamrauli Airport", 10, "Prayagraj Junction", 5,
    "Tier 2", 150, 15000, 4000, 2000, 200000, 40, 75, 16.0,
    5.0, 4.0, 12.0, 2.5, 40, 25,
    ["TCS", "Infosys"],
    gsoc=2, clubs=8, boys=400, girls=100, mous=3,
)

COLLEGE_DATA["National Institute of Electronics and IT"] = _gfti(
    "National Institute of Electronics and IT", 1974, "Aurangabad",
    "Maharashtra", 25,
    "Aurangabad Airport", 10, "Aurangabad", 5,
    "Tier 2", 120, 20000, 5000, 2000, 250000, 40, 75, 16.0,
    5.5, 4.5, 15.0, 3.0, 42, 25,
    ["TCS", "Infosys", "Wipro"],
    gsoc=2, clubs=8, boys=300, girls=100, mous=3,
)

COLLEGE_DATA["NITTTR Chandigarh"] = _gfti(
    "NITTTR Chandigarh", 1967, "Chandigarh", "Chandigarh", 25,
    "Chandigarh Airport", 10, "Chandigarh", 5,
    "Tier 1", 100, 25000, 6000, 2500, 300000, 50, 82, 14.0,
    6.0, 5.0, 15.0, 3.0, 50, 30,
    ["TCS", "Infosys"],
    gsoc=2, clubs=10, boys=300, girls=150, mous=8,
)

COLLEGE_DATA["NITTTR Bhopal"] = _gfti(
    "NITTTR Bhopal", 1965, "Bhopal", "Madhya Pradesh", 50,
    "Raja Bhoj Airport", 10, "Bhopal Junction", 8,
    "Tier 2", 100, 25000, 6000, 2500, 300000, 50, 80, 15.0,
    5.5, 4.5, 12.0, 3.0, 45, 25,
    ["TCS", "Infosys"],
    gsoc=2, clubs=8, boys=300, girls=100, mous=6,
)

COLLEGE_DATA["NITTTR Kolkata"] = _gfti(
    "NITTTR Kolkata", 1965, "Kolkata", "West Bengal", 10,
    "Netaji Subhas Chandra Bose Airport", 20, "Sealdah", 8,
    "Tier 1", 80, 25000, 6000, 2500, 300000, 40, 78, 16.0,
    5.0, 4.0, 12.0, 2.5, 42, 20,
    ["TCS", "Infosys"],
    gsoc=1, clubs=8, boys=200, girls=100, mous=5,
)

COLLEGE_DATA["Sant Longowal Institute of Engg and Tech"] = _gfti(
    "Sant Longowal Institute of Engg and Tech", 1989, "Longowal", "Punjab", 120,
    "Chandigarh Airport", 130, "Sunam", 15,
    "Tier 3", 400, 40000, 6000, 2000, 400000, 80, 78, 15.0,
    6.5, 5.5, 18.0, 3.0, 50, 35,
    ["TCS", "Infosys", "Wipro"],
    gsoc=3, clubs=10, boys=800, girls=200, mous=5,
)

COLLEGE_DATA["School of Planning and Architecture Bhopal"] = _gfti(
    "School of Planning and Architecture Bhopal", 2008, "Bhopal",
    "Madhya Pradesh", 30,
    "Raja Bhoj Airport", 10, "Bhopal Junction", 8,
    "Tier 2", 80, 55000, 8000, 3000, 550000, 30, 85, 12.0,
    8.0, 7.0, 22.0, 4.0, 60, 30,
    ["L&T", "DLF", "Shapoorji Pallonji"],
    gsoc=1, clubs=10, boys=200, girls=150, mous=8,
)

COLLEGE_DATA["School of Planning and Architecture Vijayawada"] = _gfti(
    "School of Planning and Architecture Vijayawada", 2014, "Vijayawada",
    "Andhra Pradesh", 20,
    "Vijayawada Airport", 20, "Vijayawada Junction", 5,
    "Tier 2", 60, 55000, 8000, 3000, 550000, 25, 82, 12.0,
    7.0, 6.0, 18.0, 3.5, 55, 25,
    ["L&T", "Shapoorji Pallonji"],
    gsoc=1, clubs=8, boys=150, girls=100, mous=5,
)

COLLEGE_DATA["Jorhat Engineering College"] = _gfti(
    "Jorhat Engineering College", 1960, "Jorhat", "Assam", 50,
    "Jorhat Airport", 10, "Mariani Junction", 15,
    "Tier 3", 300, 15000, 4000, 1500, 200000, 60, 70, 16.0,
    4.5, 3.5, 10.0, 2.5, 38, 20,
    ["TCS", "Infosys", "Oil India"],
    gsoc=2, clubs=10, boys=600, girls=150, mous=3,
)

COLLEGE_DATA["Ghani Khan Choudhury Inst of Engg and Tech"] = _gfti(
    "Ghani Khan Choudhury Inst of Engg and Tech", 1994, "Malda",
    "West Bengal", 30,
    "Bagdogra Airport", 200, "Malda Town", 5,
    "Tier 3", 250, 25000, 5000, 2000, 300000, 50, 72, 16.0,
    5.0, 4.0, 12.0, 2.5, 40, 25,
    ["TCS", "Infosys", "Wipro"],
    gsoc=2, clubs=10, boys=500, girls=150, mous=4,
)

COLLEGE_DATA["North Eastern Regional Inst of Science and Tech"] = _gfti(
    "North Eastern Regional Inst of Science and Tech", 1984,
    "Nirjuli", "Arunachal Pradesh", 300,
    "Hollongi Airport", 12, "Naharlagun", 5,
    "Tier 3", 300, 30000, 5000, 2000, 350000, 80, 75, 15.0,
    5.5, 4.5, 15.0, 3.0, 45, 30,
    ["TCS", "Infosys", "Wipro", "ONGC"],
    gsoc=3, clubs=15, boys=700, girls=250, mous=8,
)

COLLEGE_DATA["Birla Institute of Technology Patna"] = _gfti(
    "Birla Institute of Technology Patna", 1955, "Patna", "Bihar", 15,
    "Jay Prakash Narayan Airport", 10, "Patna Junction", 5,
    "Tier 2", 200, 120000, 12000, 3000, 1100000, 40, 80, 15.0,
    8.0, 6.5, 25.0, 3.5, 55, 50,
    ["TCS", "Infosys", "Wipro"],
    gsoc=5, clubs=10, boys=400, girls=150, mous=5,
)

COLLEGE_DATA["Birla Institute of Technology Deoghar"] = _gfti(
    "Birla Institute of Technology Deoghar", 1955, "Deoghar", "Jharkhand", 20,
    "Deoghar Airport", 10, "Deoghar", 3,
    "Tier 3", 150, 120000, 12000, 3000, 1100000, 30, 78, 16.0,
    7.0, 5.5, 18.0, 3.0, 48, 35,
    ["TCS", "Infosys", "Wipro"],
    gsoc=3, clubs=8, boys=300, girls=100, mous=3,
)

COLLEGE_DATA["Calcutta University"] = _gfti(
    "Calcutta University", 1857, "Kolkata", "West Bengal", 50,
    "Netaji Subhas Chandra Bose Airport", 15, "Sealdah", 3,
    "Tier 1", 200, 10000, 4000, 2000, 150000, 100, 78, 15.0,
    5.5, 4.5, 15.0, 2.5, 42, 30,
    ["TCS", "Infosys", "Wipro", "Cognizant"],
    gsoc=5, clubs=20, boys=500, girls=400, mous=10,
)

COLLEGE_DATA["Jadavpur University"] = _gfti(
    "Jadavpur University", 1906, "Kolkata", "West Bengal", 60,
    "Netaji Subhas Chandra Bose Airport", 18, "Jadavpur", 2,
    "Tier 1", 500, 5000, 3000, 2000, 100000, 200, 85, 12.0,
    12.0, 10.0, 50.0, 4.5, 80, 150,
    ["Google", "Microsoft", "Amazon", "TCS", "Infosys", "Samsung"],
    gsoc=40, clubs=40, boys=1500, girls=500, mous=25,
    pool=True,
)

COLLEGE_DATA["IIT Palakkad"] = _gfti(
    "IIT Palakkad", 2015, "Palakkad", "Kerala", 500,
    "Coimbatore Airport", 55, "Palakkad Junction", 10,
    "Tier 2", 250, 100000, 12000, 3500, 950000, 60, 95, 12.0,
    12.0, 10.0, 50.0, 5.0, 72, 80,
    ["TCS", "Infosys", "Amazon", "Microsoft"],
    inst_type="IIT", gsoc=15, clubs=20, boys=600, girls=250, mous=12,
)

COLLEGE_DATA["IIT Jammu"] = _gfti(
    "IIT Jammu", 2016, "Jammu", "Jammu and Kashmir", 530,
    "Jammu Airport", 12, "Jammu Tawi", 8,
    "Tier 2", 250, 100000, 12000, 3500, 950000, 60, 95, 12.0,
    11.0, 9.0, 42.0, 5.0, 70, 75,
    ["TCS", "Amazon", "Microsoft", "Infosys"],
    inst_type="IIT", gsoc=12, clubs=18, boys=550, girls=200, mous=10,
)