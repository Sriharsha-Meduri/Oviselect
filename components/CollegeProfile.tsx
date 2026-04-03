import React from 'react';
import { ArrowLeft, MapPin, GraduationCap, TrendingDown, BookOpen, ExternalLink, Users, Building2, Star, DollarSign, Award, Briefcase, Code, FlaskConical, Home, Loader2, Trophy, Globe } from 'lucide-react';

/* Branch detection patterns (must match Hero.tsx) */
const BRANCH_PATTERNS: [RegExp, string][] = [
  [/computer science|cse|\bcs\b|artificial intelligence|data science|cyber|software/i, 'CSE'],
  [/information technology\b|^it\b/i, 'IT'],
  [/math.*comput|mnc|\bmnc\b|computational math/i, 'MnC'],
  [/electronics.*communic|ece|\bec\b|vlsi|telecom/i, 'ECE'],
  [/electrical.*electro|^electrical|eee|\beee\b|power.*auto|power.*electron/i, 'EEE'],
  [/instru|eni\b|biomedical.*eng/i, 'ENI'],
  [/mechani|aerospace|aeronaut/i, 'Mechanical'],
  [/chemical|biochem/i, 'Chemical'],
  [/produc|industr.*prod|manufact/i, 'Production'],
  [/civil|infra.*eng|environment.*eng|structural/i, 'Civil'],
  [/metallur|material/i, 'Metallurgy'],
  [/mining/i, 'Mining'],
];

const getBranchKey = (programName: string): string | null => {
  const lo = programName.toLowerCase();
  for (const [pat, key] of BRANCH_PATTERNS) {
    if (pat.test(lo)) return key;
  }
  return null;
};

interface CollegeProfileProps {
  college: any;
  homeState: string;
  priorityBranches: string[];
  onBack: () => void;
}

const CollegeProfile: React.FC<CollegeProfileProps> = ({ college, homeState, priorityBranches, onBack }) => {
  // Filter out HS quota programs if the college is NOT in the user's home state
  const collegeState = college.state || null;
  const isHomeState = collegeState && homeState && collegeState.toLowerCase() === homeState.toLowerCase();
  const filteredPrograms = college.programs.filter((p: any) => {
    if (p.quota === 'HS' && !isHomeState) return false;
    return true;
  });

  // Split into priority vs other programs (only when there are priority branches)
  const hasPriority = priorityBranches.length > 0;
  const priorityPrograms = hasPriority ? filteredPrograms.filter((p: any) => {
    const key = getBranchKey(p.name);
    return key !== null && priorityBranches.includes(key);
  }) : [];
  const otherPrograms = hasPriority ? filteredPrograms.filter((p: any) => {
    const key = getBranchKey(p.name);
    return key === null || !priorityBranches.includes(key);
  }) : filteredPrograms;

  const typeBadge: Record<string, { bg: string; text: string; dot: string }> = {
    IIT:  { bg: 'bg-amber-100', text: 'text-amber-800', dot: 'bg-amber-500' },
    NIT:  { bg: 'bg-blue-100',  text: 'text-blue-800',  dot: 'bg-blue-500' },
    IIIT: { bg: 'bg-emerald-100', text: 'text-emerald-800', dot: 'bg-emerald-500' },
    GFTI: { bg: 'bg-violet-100', text: 'text-violet-800', dot: 'bg-violet-500' },
  };
  const badge = typeBadge[college.type] || typeBadge.GFTI;

  return (
    <div className="max-w-5xl mx-auto mt-4 mb-16 px-2">
      {/* Back button */}
      <button
        onClick={onBack}
        className="flex items-center gap-2 text-sm text-[#D4CFC8] hover:text-white transition-colors mb-6 group"
      >
        <ArrowLeft size={16} className="group-hover:-translate-x-0.5 transition-transform" />
        Back to results
      </button>

      {/* Hero card */}
      <div className="bg-[#FAF7F2] rounded-3xl overflow-hidden border border-[#E8E2D9] shadow-xl shadow-black/10">
        {/* Header */}
        <div className="bg-gradient-to-br from-[#F5F0E8] to-[#EDE8DF] px-8 py-10 border-b border-[#E8E2D9]">
          <div className="flex items-start justify-between mb-4">
            <span className={`inline-flex items-center gap-1.5 text-[11px] font-bold uppercase tracking-widest px-3 py-1.5 rounded-full ${badge.bg} ${badge.text}`}>
              <span className={`w-2 h-2 rounded-full ${badge.dot}`} />
              {college.type}
            </span>
          </div>
          <h1 className="text-3xl sm:text-4xl font-bold text-[#2C2824] leading-tight mb-3 font-display">
            {college.inst}
          </h1>
          <div className="flex flex-wrap items-center gap-4 text-sm text-[#8B8578]">
            <span className="flex items-center gap-1.5">
              <BookOpen size={15} className="text-[#A69F93]" />
              {filteredPrograms.length} program{filteredPrograms.length !== 1 ? 's' : ''} available
            </span>
            <span className="flex items-center gap-1.5">
              <TrendingDown size={15} className="text-[#A69F93]" />
              Best cutoff: <span className="font-bold text-[#2C2824]">{filteredPrograms[0]?.close.toLocaleString()}</span>
            </span>
          </div>
        </div>

        {/* College Info Section */}
        {college.loadingInfo && (
          <div className="px-8 py-8 border-b border-[#E8E2D9]">
            <div className="flex items-center justify-center gap-2 text-sm text-[#A69F93]">
              <Loader2 size={16} className="animate-spin" /> Loading college details...
            </div>
          </div>
        )}

        {!college.loadingInfo && college.collegeInfo && (
          <CollegeInfoSection info={college.collegeInfo} />
        )}

        {!college.loadingInfo && !college.collegeInfo && (
          <div className="px-8 py-8 border-b border-[#E8E2D9]">
            <div className="bg-[#F3EFE8] rounded-2xl p-6 text-center">
              <p className="text-sm text-[#A69F93] italic">Detailed college information not yet available.</p>
            </div>
          </div>
        )}

        {/* Priority programs */}
        {priorityPrograms.length > 0 && (
        <div className="px-8 py-8 border-b border-[#E8E2D9]">
          <h2 className="text-lg font-bold text-[#2C2824] mb-5 flex items-center gap-2">
            <Star size={18} className="text-amber-500" />
            Your Priority Branches
          </h2>

          <div className="space-y-2.5">
            {priorityPrograms.map((p: any, j: number) => (
              <div
                key={j}
                className="flex items-center justify-between bg-gradient-to-r from-amber-50/80 to-[#F3EFE8] hover:from-amber-50 hover:to-[#EDE8DF] rounded-xl px-5 py-4 transition-colors border border-amber-200/40"
              >
                <div className="flex items-center gap-4 flex-1 min-w-0 mr-4">
                  <span className="text-xs font-bold text-amber-500 w-6 text-center flex-shrink-0">
                    {j + 1}
                  </span>
                  <div className="min-w-0">
                    <p className="text-[14px] font-semibold text-[#2C2824] truncate">{p.name}</p>
                    <p className="text-[12px] text-[#A69F93] mt-0.5">{p.deg} · {p.yrs} years · {p.quota}</p>
                  </div>
                </div>
                <div className="text-right flex-shrink-0">
                  <div className="flex items-baseline gap-3">
                    <div>
                      <p className="text-xs text-[#A69F93] uppercase tracking-wider font-medium mb-0.5">Opening</p>
                      <p className="text-sm font-bold text-[#5C5650] tabular-nums">{p.open?.toLocaleString() || '—'}</p>
                    </div>
                    <div className="w-px h-8 bg-[#E8E2D9]" />
                    <div>
                      <p className="text-xs text-[#A69F93] uppercase tracking-wider font-medium mb-0.5">Closing</p>
                      <p className="text-base font-bold text-[#2C2824] tabular-nums">{p.close.toLocaleString()}</p>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
        )}

        {/* Other programs */}
        {otherPrograms.length > 0 && (
        <div className="px-8 py-8">
          <h2 className="text-lg font-bold text-[#2C2824] mb-5 flex items-center gap-2">
            <GraduationCap size={18} className="text-[#A69F93]" />
            {hasPriority ? 'Other Available Branches' : 'All Programs & Cutoffs'}
          </h2>

          <div className="space-y-2.5">
            {otherPrograms.map((p: any, j: number) => (
              <div
                key={j}
                className="flex items-center justify-between bg-[#F3EFE8] hover:bg-[#EDE8DF] rounded-xl px-5 py-4 transition-colors"
              >
                <div className="flex items-center gap-4 flex-1 min-w-0 mr-4">
                  <span className="text-xs font-bold text-[#A69F93] w-6 text-center flex-shrink-0">
                    {j + 1}
                  </span>
                  <div className="min-w-0">
                    <p className="text-[14px] font-semibold text-[#2C2824] truncate">{p.name}</p>
                    <p className="text-[12px] text-[#A69F93] mt-0.5">{p.deg} · {p.yrs} years · {p.quota}</p>
                  </div>
                </div>
                <div className="text-right flex-shrink-0">
                  <div className="flex items-baseline gap-3">
                    <div>
                      <p className="text-xs text-[#A69F93] uppercase tracking-wider font-medium mb-0.5">Opening</p>
                      <p className="text-sm font-bold text-[#5C5650] tabular-nums">{p.open?.toLocaleString() || '—'}</p>
                    </div>
                    <div className="w-px h-8 bg-[#E8E2D9]" />
                    <div>
                      <p className="text-xs text-[#A69F93] uppercase tracking-wider font-medium mb-0.5">Closing</p>
                      <p className="text-base font-bold text-[#2C2824] tabular-nums">{p.close.toLocaleString()}</p>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
        )}
      </div>
    </div>
  );
};

/* ── Helper: stat pill ─────────────────────────────────────────── */
const Stat: React.FC<{ label: string; value: string | number | null | undefined; icon?: React.ReactNode }> = ({ label, value, icon }) => {
  if (value === null || value === undefined) return null;
  return (
    <div className="bg-[#F3EFE8] rounded-xl px-4 py-3 flex flex-col gap-1">
      <span className="text-[10px] text-[#A69F93] uppercase tracking-wider font-medium flex items-center gap-1">{icon}{label}</span>
      <span className="text-sm font-bold text-[#2C2824]">{value}</span>
    </div>
  );
};

const TagList: React.FC<{ items: string[] | null | undefined; max?: number }> = ({ items, max = 8 }) => {
  if (!items || items.length === 0) return null;
  const shown = items.slice(0, max);
  return (
    <div className="flex flex-wrap gap-1.5 mt-2">
      {shown.map((t, i) => (
        <span key={i} className="text-[11px] bg-[#EDE8DF] text-[#5C5650] px-2.5 py-1 rounded-lg">{t}</span>
      ))}
      {items.length > max && <span className="text-[11px] text-[#A69F93] px-1 py-1">+{items.length - max} more</span>}
    </div>
  );
};

/* ── College Info Section ─────────────────────────────────────── */
const CollegeInfoSection: React.FC<{ info: any }> = ({ info }) => {
  const fmt = (v: number | null | undefined, suffix = '') => v != null ? `${v.toLocaleString()}${suffix}` : null;
  const fmtLPA = (v: number | null | undefined) => v != null ? `₹${v} LPA` : null;
  const fmtCr = (v: number | null | undefined) => v != null ? `₹${v} Cr` : null;

  return (
    <>
      {/* Rankings & Recognition */}
      <div className="px-8 py-6 border-b border-[#E8E2D9]">
        <h2 className="text-lg font-bold text-[#2C2824] mb-4 flex items-center gap-2">
          <Award size={18} className="text-[#A69F93]" />
          Rankings & Recognition
        </h2>
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
          <Stat label="NIRF Rank" value={fmt(info.nirf_rank)} icon={<Trophy size={10} />} />
          <Stat label="NIRF Engineering" value={fmt(info.nirf_engineering_rank)} />
          <Stat label="NAAC Grade" value={info.naac_grade} />
          <Stat label="NAAC CGPA" value={info.naac_cgpa} />
          <Stat label="Established" value={fmt(info.establishment_year)} />
          <Stat label="Campus Area" value={fmt(info.campus_area_acres, ' acres')} />
          <Stat label="Departments" value={fmt(info.total_departments)} />
        </div>
      </div>

      {/* Fees */}
      {(info.fees_general || info.hostel_fee_per_yr || info.total_4yr_cost_estimate) && (
      <div className="px-8 py-6 border-b border-[#E8E2D9]">
        <h2 className="text-lg font-bold text-[#2C2824] mb-4 flex items-center gap-2">
          <DollarSign size={18} className="text-[#A69F93]" />
          Fees & Costs
        </h2>
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
          <Stat label="Tuition / Year" value={info.fees_general != null ? `₹${info.fees_general.toLocaleString()}` : null} />
          <Stat label="Hostel / Year" value={info.hostel_fee_per_yr != null ? `₹${info.hostel_fee_per_yr.toLocaleString()}` : null} />
          <Stat label="Mess / Month" value={info.mess_fee_per_month != null ? `₹${info.mess_fee_per_month.toLocaleString()}` : null} />
          <Stat label="Total 4-Year Cost" value={info.total_4yr_cost_estimate != null ? `₹${info.total_4yr_cost_estimate.toLocaleString()}` : null} />
        </div>
      </div>
      )}

      {/* Placements */}
      {(info.avg_package_lpa || info.median_package_lpa || info.placement_percentage) && (
      <div className="px-8 py-6 border-b border-[#E8E2D9]">
        <h2 className="text-lg font-bold text-[#2C2824] mb-4 flex items-center gap-2">
          <Briefcase size={18} className="text-[#A69F93]" />
          Placements
        </h2>
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
          <Stat label="Average Package" value={fmtLPA(info.avg_package_lpa)} />
          <Stat label="Median Package" value={fmtLPA(info.median_package_lpa)} />
          <Stat label="Highest Package" value={fmtLPA(info.highest_package_lpa)} />
          <Stat label="Lowest Package" value={fmtLPA(info.lowest_package_lpa)} />
          <Stat label="Placement %" value={info.placement_percentage != null ? `${info.placement_percentage}%` : null} />
          <Stat label="Companies Visited" value={fmt(info.companies_visited)} />
          <Stat label="PPOs" value={fmt(info.ppo_count)} />
          <Stat label="MS Abroad / Year" value={fmt(info.ms_abroad_per_yr)} />
        </div>
        <TagList items={info.top_recruiters} max={10} />
      </div>
      )}

      {/* Coding & Tech Culture */}
      {(info.gsoc_selections_total || info.coding_club || info.startup_count) && (
      <div className="px-8 py-6 border-b border-[#E8E2D9]">
        <h2 className="text-lg font-bold text-[#2C2824] mb-4 flex items-center gap-2">
          <Code size={18} className="text-[#A69F93]" />
          Tech & Coding Culture
        </h2>
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
          <Stat label="GSoC Selections" value={fmt(info.gsoc_selections_total)} />
          <Stat label="ICPC Regionals (3yr)" value={fmt(info.icpc_regionals_3yr)} />
          <Stat label="Hackathon Wins" value={fmt(info.hackathon_wins_national)} />
          <Stat label="Startups" value={fmt(info.startup_count)} />
          {info.coding_club && <Stat label="Coding Club" value="Yes" />}
          {info.gdsc_present && <Stat label="GDSC" value="Yes" />}
        </div>
      </div>
      )}

      {/* Campus Life */}
      {(info.hostel_capacity_boys || info.student_clubs_count || info.tech_fest_name) && (
      <div className="px-8 py-6 border-b border-[#E8E2D9]">
        <h2 className="text-lg font-bold text-[#2C2824] mb-4 flex items-center gap-2">
          <Home size={18} className="text-[#A69F93]" />
          Campus Life
        </h2>
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
          <Stat label="Boys Hostel" value={fmt(info.hostel_capacity_boys, ' seats')} />
          <Stat label="Girls Hostel" value={fmt(info.hostel_capacity_girls, ' seats')} />
          <Stat label="Student Clubs" value={fmt(info.student_clubs_count)} />
          <Stat label="Tech Fest" value={info.tech_fest_name} />
          <Stat label="Cultural Fest" value={info.cultural_fest_name} />
          {info.swimming_pool && <Stat label="Swimming Pool" value="Yes" />}
          {info.gym_on_campus && <Stat label="Gym" value="Yes" />}
          <Stat label="Medical Facility" value={info.medical_facility} />
          <Stat label="Intl. Exchange" value={fmt(info.international_exchange_programs, ' programs')} />
          <Stat label="Intl. MOUs" value={fmt(info.international_mous)} />
        </div>
      </div>
      )}

      {/* Faculty & Research */}
      {(info.total_faculty || info.total_research_grants_cr) && (
      <div className="px-8 py-6 border-b border-[#E8E2D9]">
        <h2 className="text-lg font-bold text-[#2C2824] mb-4 flex items-center gap-2">
          <FlaskConical size={18} className="text-[#A69F93]" />
          Faculty & Research
        </h2>
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
          <Stat label="Total Faculty" value={fmt(info.total_faculty)} />
          <Stat label="PhD Faculty %" value={info.faculty_with_phd_pct != null ? `${info.faculty_with_phd_pct}%` : null} />
          <Stat label="Student:Faculty" value={info.student_faculty_ratio != null ? `${info.student_faculty_ratio}:1` : null} />
          <Stat label="Research Grants" value={fmtCr(info.total_research_grants_cr)} />
          <Stat label="Active Projects" value={fmt(info.active_funded_projects)} />
          <Stat label="Patents (5yr)" value={fmt(info.patents_filed_5yr)} />
          <Stat label="Publications/yr" value={fmt(info.sci_scopus_publications_per_yr)} />
        </div>
      </div>
      )}

      {/* Notable Alumni */}
      {info.notable_alumni && info.notable_alumni.length > 0 && (
      <div className="px-8 py-6 border-b border-[#E8E2D9]">
        <h2 className="text-lg font-bold text-[#2C2824] mb-4 flex items-center gap-2">
          <Users size={18} className="text-[#A69F93]" />
          Notable Alumni
        </h2>
        <TagList items={info.notable_alumni} max={12} />
      </div>
      )}

      {/* Location */}
      {(info.city || info.nearest_airport) && (
      <div className="px-8 py-6 border-b border-[#E8E2D9]">
        <h2 className="text-lg font-bold text-[#2C2824] mb-4 flex items-center gap-2">
          <Globe size={18} className="text-[#A69F93]" />
          Location & Connectivity
        </h2>
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
          <Stat label="City" value={info.city} icon={<MapPin size={10} />} />
          <Stat label="City Tier" value={info.city_tier} />
          <Stat label="Nearest Airport" value={info.nearest_airport ? `${info.nearest_airport}${info.nearest_airport_km ? ` (${info.nearest_airport_km} km)` : ''}` : null} />
          <Stat label="Nearest Railway" value={info.nearest_railway_station ? `${info.nearest_railway_station}${info.nearest_railway_km ? ` (${info.nearest_railway_km} km)` : ''}` : null} />
        </div>
      </div>
      )}
    </>
  );
};

export default CollegeProfile;
