-- ============================================================
-- college_info table — CollegePravesh scraped data
-- Run this in Supabase SQL Editor (Dashboard → SQL Editor)
-- ============================================================

create table college_info (
  institute text primary key,
  institute_type text,
  also_known_as text,
  established_year integer,
  city text,
  state text,
  address text,
  nearest_airport text,
  nearest_airport_km float,
  nearest_railway_station text,
  nearest_railway_km float,
  nirf_overall_rank integer,
  nirf_engineering_rank integer,
  nirf_research_rank integer,
  nirf_innovation_rank text,
  qs_world_rank text,
  qs_asia_rank text,
  the_world_rank text,
  the_asia_rank text,
  outlook_rank integer,
  the_week_rank integer,
  courses_offered text[],
  tuition_fee_per_sem integer,
  hostel_fee_per_sem integer,
  mess_advance_per_sem integer,
  one_time_fees integer,
  caution_money integer,
  annual_fees integer,
  total_institute_fee integer,
  total_hostel_fee integer,
  fee_waivers text[],
  overall_placement_pct float,
  avg_package_lpa float,
  median_package_lpa float,
  highest_package_lpa float,
  branch_wise_placement_pct jsonb,
  branch_wise_median_ctc jsonb,
  branch_wise_highest_ctc jsonb,
  branch_wise_avg_ctc jsonb,
  top_recruiters text[],
  placement_year integer,
  data_sources text[],
  data_confidence_score integer,
  needs_review boolean default false,
  collegepravesh_url text,
  last_scraped_at timestamptz default now()
);

create index idx_ci_institute_type on college_info(institute_type);
create index idx_ci_nirf on college_info(nirf_overall_rank);
create index idx_ci_placement on college_info(avg_package_lpa);
create index idx_ci_confidence on college_info(data_confidence_score);

-- Row Level Security
alter table college_info enable row level security;

create policy "Public read college_info" on college_info
  for select using (true);

create policy "Service write college_info" on college_info
  for all using (auth.role() = 'service_role');

