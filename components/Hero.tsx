import React, { useState, useRef, useEffect } from 'react';
import { ArrowRight, ChevronDown, ChevronUp, Loader2, MapPin, GraduationCap, TrendingDown, ChevronRight, GripVertical, ExternalLink, BookOpen, ArrowLeft } from 'lucide-react';
import { useGoogleLogin } from '@react-oauth/google';
import CopilotDashboard from './CopilotDashboard';
import CollegeProfile from './CollegeProfile';
import CounsellingHub from './CounsellingHub';
import { supabase } from '../lib/supabase';

const colleges = [
  'NIT Trichy', 'BITS Pilani', 'IIT Bombay', 'IIIT Hyderabad',
  'NIT Warangal', 'DTU Delhi', 'NIT Surathkal', 'Thapar University',
  'NIT Calicut', 'VIT Vellore', 'NIT Rourkela', 'COEP Pune',
  'RVCE Bangalore', 'Jadavpur University', 'BIT Mesra', 'NSIT Delhi',
];

const CATEGORIES = ['General', 'OBC-NCL', 'SC', 'ST', 'EWS', 'PwD'];
const GENDERS = ['Gender-Neutral', 'Female-Only'];

/* ── Institute classification ─────────────────────────────────────── */
const classifyInstitute = (name: string): 'IIT' | 'NIT' | 'IIIT' | 'GFTI' => {
  const n = name.trim();
  const lo = n.toLowerCase();

  // ── GFTIs that look like IIITs (must check BEFORE IIIT rules) ──
  if (lo.includes('international institute of information technology')) return 'GFTI'; // IntIIIT Bhubaneswar, Naya Raipur

  // ── IITs ──
  if (/^iit[\s(]/i.test(n)) return 'IIT';

  // ── NITs (including special-name NITs & IIEST Shibpur) ──
  if (/^nit[\s,]/i.test(n)) return 'NIT';
  if (/^manit\s/i.test(n)) return 'NIT';   // Maulana Azad NIT Bhopal
  if (/^mnit\s/i.test(n)) return 'NIT';    // Malaviya NIT Jaipur
  if (/^mnnit\s/i.test(n)) return 'NIT';   // Motilal Nehru NIT Allahabad
  if (/^svnit/i.test(n)) return 'NIT';     // Sardar Vallabhbhai NIT Surat
  if (/^vnit/i.test(n)) return 'NIT';      // Visvesvaraya NIT Nagpur
  if (/bramnit/i.test(n)) return 'NIT';    // Dr. B R Ambedkar NIT Jalandhar
  if (lo.includes('indian institute of engineering science and technology')) return 'NIT'; // IIEST Shibpur

  // ── IIITs ──
  if (/^iiit[\s(,]/i.test(n)) return 'IIIT';
  if (/^abv-iiitm/i.test(n)) return 'IIIT'; // ABV-IIITM Gwalior
  if (lo.includes('indian institute of information technology')) return 'IIIT'; // full-name IIITs (Raichur, Senapati Manipur, IIITDM Jabalpur, etc.)

  // ── Everything else → GFTI ──
  return 'GFTI';
};

/* ── Institute priority tiers ─────────────────────────────────────── */
const TIER_1_1: Record<string, boolean> = {                 // Old IITs
  'IIT Bombay': true, 'IIT Delhi': true, 'IIT Kharagpur': true,
  'IIT Madras': true, 'IIT Kanpur': true, 'IIT Roorkee': true,
  'IIT Guwahati': true,
};
const TIER_1_2: Record<string, boolean> = {                 // Not-so-old IITs
  'IIT Indore': true, 'IIT Ropar': true,
  'IIT (BHU) Varanasi': true, 'IIT (ISM) Dhanbad': true, 'IIT Mandi': true,
};
const TIER_1_3_EXPLICIT: Record<string, boolean> = {        // Top Govt + named NITs + top IIITs
  'NIT, Tiruchirappalli': true, 'NIT, Warangal': true,
  'NIT Karnataka, Surathkal': true,
  'IIIT, Allahabad': true, 'IIIT Hyderabad': true, 'IIIT, Bangalore': true,
};
const TIER_2_1_EXPLICIT: Record<string, boolean> = {        // Strong NITs & named colleges
  'NIT Calicut': true, 'MNNIT Allahabad': true,
  'PEC, Chandigarh': true, 'MNIT Jaipur': true,
  'ABV-IIITM Gwalior': true, 'IIIT Lucknow': true,
  'VNIT, Nagpur': true, 'SVNIT, Surat': true,
  'Dr.BRAMNIT, Jalandhar': true, 'NIT, Jamshedpur': true,
  'NIT, Kurukshetra': true, 'NIT Patna': true, 'NIT Raipur': true,
  'MANIT Bhopal': true, 'NIT, Rourkela': true, 'NIT, Silchar': true,
  'NIT Sikkim': true, 'NIT Durgapur': true, 'BIT, Mesra, Ranchi': true,
  'Indian Institute of Engineering Science and Technology, Shibpur': true,
};
// Also includes Pt. Dwarka Prasad Mishra IIIT Jabalpur (matched by substring below)

const getInstituteTier = (name: string): number => {
  if (TIER_1_1[name]) return 0;                          // Old IITs
  if (TIER_1_2[name]) return 1;                          // Not-so-old IITs
  if (TIER_1_3_EXPLICIT[name]) return 2;                 // Top 3 NITs + IIIT Allahabad/Hyd/Blr
  // All remaining IITs (new IITs) → tier 3 (below 1.3)
  if (classifyInstitute(name) === 'IIT') return 3;
  if (TIER_2_1_EXPLICIT[name]) return 4;                 // Strong NITs (Calicut, Durgapur, etc.)
  if (name.toLowerCase().includes('jabalpur')) return 4;  // IIITDM Jabalpur
  // All other NITs/IIITs → tier 5
  const cls = classifyInstitute(name);
  if (cls === 'NIT') return 5;
  if (cls === 'IIIT') return 5;
  // Everything else (GFTIs) → tier 6
  return 6;
};

/* ── Institute → State mapping (for HS quota filtering) ─────────── */
const INSTITUTE_STATE: Record<string, string> = {
  'ABV-IIITM Gwalior': 'Madhya Pradesh', 'Assam University, Silchar': 'Assam',
  'BIT, Deoghar Off-Campus': 'Jharkhand', 'BIT, Mesra, Ranchi': 'Jharkhand', 'BIT, Patna Off-Campus': 'Bihar',
  'CU Jharkhand': 'Jharkhand', 'Central University of Haryana': 'Haryana', 'Central University of Jammu': 'Jammu and Kashmir',
  'Central University of Rajasthan, Rajasthan': 'Rajasthan', 'Central institute of Technology Kokrajar, Assam': 'Assam',
  'Chhattisgarh Swami Vivekanada Technical University, Bhilai (CSVTU Bhilai)': 'Chhattisgarh',
  'Dr.BRAMNIT, Jalandhar': 'Punjab', 'Gati Shakti Vishwavidyalaya, Vadodara': 'Gujarat',
  'Ghani Khan Choudhary Institute of Engineering and Technology, Malda, West Bengal': 'West Bengal',
  'Gurukula Kangri Vishwavidyalaya, Haridwar': 'Uttarakhand',
  'IIIT (IIIT) Nagpur': 'Maharashtra', 'IIIT (IIIT) Pune': 'Maharashtra', 'IIIT (IIIT) Ranchi': 'Jharkhand',
  'IIIT (IIIT), Sri City, Chittoor': 'Andhra Pradesh', 'IIIT (IIIT)Kota, Rajasthan': 'Rajasthan',
  'IIIT Bhagalpur': 'Bihar', 'IIIT Bhopal': 'Madhya Pradesh',
  'IIIT Design & Manufacturing Kurnool, Andhra Pradesh': 'Andhra Pradesh',
  'IIIT Guwahati': 'Assam', 'IIIT Lucknow': 'Uttar Pradesh', 'IIIT Manipur': 'Manipur',
  'IIIT Surat': 'Gujarat', 'IIIT Tiruchirappalli': 'Tamil Nadu',
  'IIIT(IIIT) Dharwad': 'Karnataka', 'IIIT(IIIT) Kalyani, West Bengal': 'West Bengal',
  'IIIT(IIIT) Kilohrad, Sonepat, Haryana': 'Haryana', 'IIIT(IIIT) Kottayam': 'Kerala',
  'IIIT(IIIT) Una, Himachal Pradesh': 'Himachal Pradesh', 'IIIT(IIIT), Vadodara, Gujrat': 'Gujarat',
  'IIIT, Agartala': 'Tripura', 'IIIT, Allahabad': 'Uttar Pradesh',
  'IIIT, Design & Manufacturing, Kancheepuram': 'Tamil Nadu',
  'IIIT, Vadodara International Campus Diu (IIITVICD)': 'Dadra and Nagar Haveli and Daman and Diu',
  'IIT (BHU) Varanasi': 'Uttar Pradesh', 'IIT (ISM) Dhanbad': 'Jharkhand',
  'IIT Bhilai': 'Chhattisgarh', 'IIT Bhubaneswar': 'Odisha', 'IIT Bombay': 'Maharashtra',
  'IIT Delhi': 'Delhi', 'IIT Dharwad': 'Karnataka', 'IIT Gandhinagar': 'Gujarat',
  'IIT Goa': 'Goa', 'IIT Guwahati': 'Assam', 'IIT Hyderabad': 'Telangana',
  'IIT Indore': 'Madhya Pradesh', 'IIT Jammu': 'Jammu and Kashmir', 'IIT Jodhpur': 'Rajasthan',
  'IIT Kanpur': 'Uttar Pradesh', 'IIT Kharagpur': 'West Bengal', 'IIT Madras': 'Tamil Nadu',
  'IIT Mandi': 'Himachal Pradesh', 'IIT Palakkad': 'Kerala', 'IIT Patna': 'Bihar',
  'IIT Roorkee': 'Uttarakhand', 'IIT Ropar': 'Punjab', 'IIT Tirupati': 'Andhra Pradesh',
  'INDIAN INSTITUTE OF INFORMATION TECHNOLOGY SENAPATI MANIPUR': 'Manipur',
  'Indian Institute of Carpet Technology, Bhadohi': 'Uttar Pradesh',
  'Indian Institute of Engineering Science and Technology, Shibpur': 'West Bengal',
  'Indian Institute of Handloom Technology(IIHT), Varanasi': 'Uttar Pradesh',
  'Indian Institute of Handloom Technology, Salem': 'Tamil Nadu',
  'Indian institute of information technology, Raichur, Karnataka': 'Karnataka',
  'Institute of Chemical Technology, Mumbai: Indian Oil Odisha Campus, Bhubaneswar': 'Odisha',
  'Institute of Engineering and Technology, Dr. H. S. Gour University. Sagar (A Central University)': 'Madhya Pradesh',
  'Institute of Infrastructure, Technology, Research and Management-Ahmedabad': 'Gujarat',
  'Institute of Technology, Guru Ghasidas Vishwavidyalaya (A Central University), Bilaspur, (C.G.)': 'Chhattisgarh',
  'IntIIIT, Bhubaneswar': 'Odisha', 'IntIIIT, Naya Raipur': 'Chhattisgarh',
  'Islamic University of Science and Technology Kashmir': 'Jammu and Kashmir',
  'J.K. Institute of Applied Physics & Technology, Department of Electronics & Communication, University of Allahabad- Allahabad': 'Uttar Pradesh',
  'JNU, Delhi': 'Delhi', 'MANIT Bhopal': 'Madhya Pradesh', 'MNIT Jaipur': 'Rajasthan',
  'MNNIT Allahabad': 'Uttar Pradesh', 'Mizoram University, Aizawl': 'Mizoram',
  'NIT Agartala': 'Tripura', 'NIT Arunachal Pradesh': 'Arunachal Pradesh', 'NIT Calicut': 'Kerala',
  'NIT Delhi': 'Delhi', 'NIT Durgapur': 'West Bengal', 'NIT Goa': 'Goa', 'NIT Hamirpur': 'Himachal Pradesh',
  'NIT Karnataka, Surathkal': 'Karnataka', 'NIT Meghalaya': 'Meghalaya', 'NIT Nagaland': 'Nagaland',
  'NIT Patna': 'Bihar', 'NIT Puducherry': 'Puducherry', 'NIT Raipur': 'Chhattisgarh', 'NIT Sikkim': 'Sikkim',
  'NIT, Andhra Pradesh': 'Andhra Pradesh', 'NIT, Jamshedpur': 'Jharkhand', 'NIT, Kurukshetra': 'Haryana',
  'NIT, Manipur': 'Manipur', 'NIT, Mizoram': 'Mizoram', 'NIT, Rourkela': 'Odisha', 'NIT, Silchar': 'Assam',
  'NIT, Srinagar': 'Jammu and Kashmir', 'NIT, Tiruchirappalli': 'Tamil Nadu',
  'NIT, Uttarakhand': 'Uttarakhand', 'NIT, Warangal': 'Telangana',
  'National Institute of Advanced Manufacturing Technology, Ranchi': 'Jharkhand',
  'National Institute of Electronics and Information Technology, Ajmer (Rajasthan)': 'Rajasthan',
  'National Institute of Electronics and Information Technology, Aurangabad (Maharashtra)': 'Maharashtra',
  'National Institute of Electronics and Information Technology, Gorakhpur (UP)': 'Uttar Pradesh',
  'National Institute of Electronics and Information Technology, Patna (Bihar)': 'Bihar',
  'National Institute of Electronics and Information Technology, Ropar (Punjab)': 'Punjab',
  'National Institute of Food Technology Entrepreneurship and Management, Kundli': 'Haryana',
  'National Institute of Food Technology Entrepreneurship and Management, Thanjavur': 'Tamil Nadu',
  'North Eastern Regional Institute of Science and Technology, Nirjuli-791109 (Itanagar),Arunachal Pradesh': 'Arunachal Pradesh',
  'North-Eastern Hill University, Shillong': 'Meghalaya', 'PEC, Chandigarh': 'Chandigarh',
  'Pt. Dwarka Prasad Mishra Indian Institute of Information Technology, Design & Manufacture Jabalpur': 'Madhya Pradesh',
  'Puducherry Technological University, Puducherry': 'Puducherry',
  'Rajiv Gandhi National Aviation University, Fursatganj, Amethi (UP)': 'Uttar Pradesh',
  'SVNIT, Surat': 'Gujarat', 'Sant Longowal Institute of Engineering and Technology': 'Punjab',
  'School of Engineering, Tezpur University, Napaam, Tezpur': 'Assam',
  'School of Planning & Architecture, Bhopal': 'Madhya Pradesh',
  'School of Planning & Architecture, New Delhi': 'Delhi', 'School of Planning & Architecture: Vijayawada': 'Andhra Pradesh',
  'School of Studies of Engineering and Technology, Guru Ghasidas Vishwavidyalaya, Bilaspur': 'Chhattisgarh',
  'Shri G. S. Institute of Technology and Science Indore': 'Madhya Pradesh',
  'Shri Mata Vaishno Devi University, Katra, Jammu & Kashmir': 'Jammu and Kashmir',
  'UoH': 'Telangana', 'VNIT, Nagpur': 'Maharashtra',
  'IIIT Hyderabad': 'Telangana', 'IIIT, Bangalore': 'Karnataka',
};

const getInstituteState = (name: string): string | null => INSTITUTE_STATE[name] || null;

/* ── Branch preference ────────────────────────────────────────────── */
const DEFAULT_BRANCH_ORDER = [
  'CSE', 'IT', 'MnC', 'ECE', 'EEE', 'ENI', 'Mechanical', 'Chemical', 'Production', 'Civil', 'Metallurgy', 'Mining',
];

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

const getBranchRank = (programName: string, orderedBranches: string[]): number => {
  const lo = programName.toLowerCase();
  let branchKey: string | null = null;
  for (const [pat, key] of BRANCH_PATTERNS) {
    if (pat.test(lo)) { branchKey = key; break; }
  }
  if (!branchKey) return 99; // truly unknown branch → bottom
  const idx = orderedBranches.indexOf(branchKey);
  if (idx !== -1) return idx; // in user's priority list → top
  // Known branch but not in user's priority → middle (ordered by default list)
  const defIdx = DEFAULT_BRANCH_ORDER.indexOf(branchKey);
  return 50 + (defIdx !== -1 ? defIdx : 40);
};

const STATES = [
  'Andhra Pradesh', 'Arunachal Pradesh', 'Assam', 'Bihar', 'Chhattisgarh',
  'Goa', 'Gujarat', 'Haryana', 'Himachal Pradesh', 'Jharkhand', 'Karnataka',
  'Kerala', 'Madhya Pradesh', 'Maharashtra', 'Manipur', 'Meghalaya', 'Mizoram',
  'Nagaland', 'Odisha', 'Punjab', 'Rajasthan', 'Sikkim', 'Tamil Nadu',
  'Telangana', 'Tripura', 'Uttar Pradesh', 'Uttarakhand', 'West Bengal',
  'Andaman and Nicobar Islands', 'Chandigarh', 'Dadra and Nagar Haveli and Daman and Diu',
  'Delhi', 'Jammu and Kashmir', 'Ladakh', 'Lakshadweep', 'Puducherry',
];

const CollegeTicker: React.FC = () => {
  const all = [...colleges, ...colleges];
  return (
    <div className="overflow-hidden border-y border-white/10 py-3.5 mt-12">
      <div className="marquee-track flex whitespace-nowrap">
        {all.map((c, i) => (
          <span key={i} className="flex-shrink-0 flex items-center">
            <span className="text-sm text-[#D4CFC8]/60 mx-5">{c}</span>
            <span className="text-white/20 text-xs">+</span>
          </span>
        ))}
      </div>
    </div>
  );
};

/* ── Styled select wrapper ───────────────────────────────────────────────── */
const Select: React.FC<{
  value: string;
  onChange: (v: string) => void;
  options: string[];
  placeholder: string;
}> = ({ value, onChange, options, placeholder }) => (
  <div className="relative">
    <select
      value={value}
      onChange={(e) => onChange(e.target.value)}
      className="w-full appearance-none bg-white/[0.07] border border-white/10 rounded-xl px-4 py-3 text-sm text-[#F5F0E8] placeholder-[#D4CFC8]/50 focus:outline-none focus:ring-2 focus:ring-white/20 focus:border-transparent transition-all"
    >
      <option value="" disabled className="bg-[#1a1a1a] text-[#D4CFC8]">{placeholder}</option>
      {options.map((o) => (
        <option key={o} value={o} className="bg-[#1a1a1a] text-[#F5F0E8]">{o}</option>
      ))}
    </select>
    <ChevronDown size={16} className="absolute right-3 top-1/2 -translate-y-1/2 text-[#D4CFC8]/50 pointer-events-none" />
  </div>
);

/* ── Searchable state combobox with keyboard navigation ─────────────────── */
const StateCombobox: React.FC<{ value: string; onChange: (v: string) => void }> = ({ value, onChange }) => {
  const [query, setQuery] = useState('');
  const [open, setOpen] = useState(false);
  const [highlightIdx, setHighlightIdx] = useState(-1);
  const wrapperRef = useRef<HTMLDivElement>(null);
  const listRef = useRef<HTMLUListElement>(null);

  const filtered = STATES.filter((s) => s.toLowerCase().includes(query.toLowerCase()));

  // Reset highlight when filtered list changes
  useEffect(() => { setHighlightIdx(-1); }, [query]);

  // Close dropdown on outside click
  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (wrapperRef.current && !wrapperRef.current.contains(e.target as Node)) setOpen(false);
    };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, []);

  // Scroll highlighted item into view
  useEffect(() => {
    if (highlightIdx >= 0 && listRef.current) {
      const items = listRef.current.querySelectorAll('li[data-state]');
      items[highlightIdx]?.scrollIntoView({ block: 'nearest' });
    }
  }, [highlightIdx]);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (!open) {
      if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
        setOpen(true);
        setQuery('');
        e.preventDefault();
      }
      return;
    }
    if (e.key === 'ArrowDown') {
      e.preventDefault();
      setHighlightIdx((prev) => (prev < filtered.length - 1 ? prev + 1 : prev));
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setHighlightIdx((prev) => (prev > 0 ? prev - 1 : 0));
    } else if (e.key === 'Enter') {
      e.preventDefault();
      if (highlightIdx >= 0 && highlightIdx < filtered.length) {
        onChange(filtered[highlightIdx]);
        setQuery('');
        setOpen(false);
      }
    } else if (e.key === 'Escape') {
      setOpen(false);
    }
  };

  return (
    <div ref={wrapperRef} className="relative">
      <label className="block text-xs font-medium text-[#D4CFC8] uppercase tracking-wider mb-1.5">Home State / Domicile</label>
      <div className="relative">
        <input
          type="text"
          value={open ? query : value}
          onChange={(e) => { setQuery(e.target.value); setOpen(true); }}
          onFocus={() => { setOpen(true); setQuery(''); }}
          onKeyDown={handleKeyDown}
          placeholder="Enter your home state/domicile"
          required
          className="w-full bg-white/[0.07] border border-white/10 rounded-xl px-4 py-3 text-sm text-[#F5F0E8] placeholder-[#D4CFC8]/50 focus:outline-none focus:ring-2 focus:ring-white/20 focus:border-transparent transition-all"
        />
        <ChevronDown size={16} className={`absolute right-3 top-1/2 -translate-y-1/2 text-[#D4CFC8]/50 pointer-events-none transition-transform ${open ? 'rotate-180' : ''}`} />
      </div>
      {open && (
        <ul ref={listRef} className="absolute z-50 mt-1 w-full max-h-48 overflow-y-auto rounded-xl bg-[#1a1a1a] border border-white/10 py-1 scrollbar-hide">
          {filtered.length > 0 ? filtered.map((s, i) => (
            <li
              key={s}
              data-state={s}
              onClick={() => { onChange(s); setQuery(''); setOpen(false); }}
              className={`px-4 py-2.5 text-sm cursor-pointer transition-colors ${
                i === highlightIdx ? 'text-white bg-white/15' :
                s === value ? 'text-white bg-white/10' :
                'text-[#D4CFC8] hover:bg-white/[0.07] hover:text-[#F5F0E8]'
              }`}
            >
              {s}
            </li>
          )) : (
            <li className="px-4 py-2.5 text-sm text-[#D4CFC8]/50">No states found</li>
          )}
        </ul>
      )}
    </div>
  );
};

const STORAGE_KEY = 'oviguide_user';

const Hero: React.FC = () => {
  /* auth state */
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [userProfile, setUserProfile] = useState<{ email: string; name: string; picture: string } | null>(null);

  /* counselling hub state: null = show hub, 'josaa' = show prediction form */
  const [activeCounselling, setActiveCounselling] = useState<string | null>(null);

  /* form state */
  const [name, setName] = useState('');
  const [mainsRank, setMainsRank] = useState('');
  const [advancedRank, setAdvancedRank] = useState('');
  const [advancedNA, setAdvancedNA] = useState(false);
  const [category, setCategory] = useState('');
  const [categoryRank, setCategoryRank] = useState('');
  const [categoryRankNA, setCategoryRankNA] = useState(false);
  const [gender, setGender] = useState('');
  const [homeState, setHomeState] = useState('');
  const [branchOrder, setBranchOrder] = useState<string[]>([]);
  const [branchNA, setBranchNA] = useState(false);
  const [branchMode, setBranchMode] = useState<'custom' | 'default' | 'none'>('custom');

  /* prediction state */
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<any[] | null>(null);
  const [error, setError] = useState('');
  const [expandedCollege, setExpandedCollege] = useState<string | null>(null);
  const [selectedCollege, setSelectedCollege] = useState<any | null>(null);
  const [activeBranches, setActiveBranches] = useState<string[]>(DEFAULT_BRANCH_ORDER);

  /* ── Fetch college_info from Supabase and open profile ────── */
  const openCollegeProfile = async (college: any) => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
    // Show the profile immediately with whatever we have
    setSelectedCollege({ ...college, collegeInfo: null, loadingInfo: true });
    try {
      const { data, error: fetchErr } = await supabase
        .from('college_info')
        .select('*')
        .eq('institute', college.inst)
        .maybeSingle();
      if (fetchErr) console.warn('college_info fetch error:', fetchErr.message);
      setSelectedCollege((prev: any) => prev ? { ...prev, collegeInfo: data || null, loadingInfo: false } : prev);
    } catch (err) {
      console.warn('college_info fetch failed:', err);
      setSelectedCollege((prev: any) => prev ? { ...prev, loadingInfo: false } : prev);
    }
  };

  /* ── Restore session from localStorage on mount ────────── */
  useEffect(() => {
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      if (saved) {
        const profile = JSON.parse(saved);
        if (profile?.email) {
          setUserProfile(profile);
          setName(profile.name || '');
          setIsLoggedIn(true);
        }
      }
    } catch {
      localStorage.removeItem(STORAGE_KEY);
    }
  }, []);

  /* ── Listen for logout from Navbar ────────── */
  useEffect(() => {
    const handleLogout = () => {
      setIsLoggedIn(false);
      setUserProfile(null);
      setResults(null);
      setError('');
      setName('');
      setMainsRank('');
      setAdvancedRank('');
      setAdvancedNA(false);
      setCategory('');
      setCategoryRank('');
      setCategoryRankNA(false);
      setGender('');
      setHomeState('');
      setBranchOrder([]);
      setBranchNA(true);
      setBranchMode('custom');
      setSelectedCollege(null);
      setActiveCounselling(null);
    };
    window.addEventListener('oviguide-logout', handleLogout);
    return () => window.removeEventListener('oviguide-logout', handleLogout);
  }, []);

  /* ── Listen for college search selection from Navbar ────────── */
  useEffect(() => {
    const handleSearchSelect = async (e: Event) => {
      const { name: instName } = (e as CustomEvent).detail as { name: string };
      if (!instName) return;
      window.scrollTo({ top: 0, behavior: 'smooth' });
      // Build a minimal college object for CollegeProfile
      const college: any = {
        inst: instName,
        type: classifyInstitute(instName),
        state: getInstituteState(instName),
        programs: [],
        collegeInfo: null,
        loadingInfo: true,
      };
      setSelectedCollege(college);
      // Fetch college_info from Supabase
      try {
        const { data, error: fetchErr } = await supabase
          .from('college_info')
          .select('*')
          .eq('institute', instName)
          .maybeSingle();
        if (fetchErr) console.warn('college_info fetch error:', fetchErr.message);
        setSelectedCollege((prev: any) => prev ? { ...prev, collegeInfo: data || null, loadingInfo: false } : prev);
      } catch {
        setSelectedCollege((prev: any) => prev ? { ...prev, loadingInfo: false } : prev);
      }
    };
    window.addEventListener('oviguide-search-college', handleSearchSelect);
    return () => window.removeEventListener('oviguide-search-college', handleSearchSelect);
  }, []);

  /* ── Helper: save user to Supabase users table ─────────── */
  const upsertUserToSupabase = async (profile: { email: string; name: string; picture: string }) => {
    try {
      // Try upsert — if user exists, bump login_count
      const { error: upsertErr } = await supabase.from('users').upsert(
        {
          email: profile.email,
          name: profile.name,
          picture: profile.picture,
          last_login: new Date().toISOString(),
        },
        { onConflict: 'email' }
      );
      if (upsertErr) {
        // Table might not exist yet — silently ignore
        console.warn('Supabase user upsert:', upsertErr.message);
      }
    } catch (err) {
      console.warn('Supabase user upsert failed:', err);
    }
  };

  const login = useGoogleLogin({
    onSuccess: async (tokenResponse) => {
      const res = await fetch('https://www.googleapis.com/oauth2/v3/userinfo', {
        headers: { Authorization: `Bearer ${tokenResponse.access_token}` },
      });
      const profile = await res.json();
      console.log('User email:', profile.email);

      const userInfo = {
        email: profile.email,
        name: profile.name || '',
        picture: profile.picture || '',
      };

      // 1. Save to localStorage for session persistence
      localStorage.setItem(STORAGE_KEY, JSON.stringify(userInfo));
      setUserProfile(userInfo);
      setName(userInfo.name);

      // 2. Upsert to Supabase users table (fire-and-forget)
      upsertUserToSupabase(userInfo);

      // 3. Also notify FastAPI backend (fire-and-forget)
      try {
        const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
        fetch(`${API_URL}/api/save-email`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(userInfo),
        });
      } catch (err) {
        console.error('Failed to save email:', err);
      }

      setIsLoggedIn(true);
      window.dispatchEvent(new Event('oviguide-login'));
    },
    onError: () => console.error('Google login failed'),
  });

  const handlePredict = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setResults(null);
    setExpandedCollege(null);

    try {
      const mRank = mainsRank ? Number(mainsRank) : null;
      const aRank = advancedRank && !advancedNA ? Number(advancedRank) : null;

      const seatMap: Record<string, string> = {
        'General': 'OPEN', 'OBC-NCL': 'OBC-NCL', 'SC': 'SC',
        'ST': 'ST', 'EWS': 'EWS', 'PwD': 'OPEN-PwD',
      };
      const seat = seatMap[category] || 'OPEN';
      const genderCode = gender === 'Female-Only' ? 'F' : 'N';

      if (!mRank) {
        setError('Please enter your JEE Mains rank.');
        setLoading(false);
        return;
      }

      // ── Save form data to Supabase (fire-and-forget) ──
      if (userProfile?.email) {
        supabase.from('predictions').upsert(
          {
            email: userProfile.email,
            name,
            mains_rank: mRank,
            advanced_rank: aRank,
            category,
            category_rank: categoryRank && !categoryRankNA ? Number(categoryRank) : null,
            gender,
            home_state: homeState,
            branch_order: branchMode === 'custom' ? branchOrder : null,
            branch_na: branchMode !== 'custom',
            branch_mode: branchMode,
            updated_at: new Date().toISOString(),
          },
          { onConflict: 'email' }
        ).then(({ error: saveErr }) => {
          if (saveErr) console.warn('Supabase prediction save:', saveErr.message);
        });
      }

      const SEL = 'quota, seat, gender, open, close, year, round, iid, institutes(name), programs(name, deg, yrs)';
      const YEAR = 2025;
      const ROUND = 6;
      const PAGE = 1000; // Supabase max rows per request

      /* Fetch ALL matching rows via pagination */
      const fetchAll = async (rank: number) => {
        let all: any[] = [];
        let from = 0;
        while (true) {
          const { data, error: err } = await supabase
            .from('cutoffs').select(SEL)
            .eq('seat', seat).eq('gender', genderCode)
            .eq('year', YEAR).eq('round', ROUND)
            .gte('close', rank)
            .order('close', { ascending: true })
            .range(from, from + PAGE - 1);
          if (err) throw err;
          if (!data || data.length === 0) break;
          all = all.concat(data);
          if (data.length < PAGE) break;   // last page
          from += PAGE;
        }
        return all;
      };

      // Fetch non-IIT (Mains rank) and IIT (Advanced rank) in parallel
      const [nonIitRows, iitRows] = await Promise.all([
        fetchAll(mRank),
        aRank ? fetchAll(aRank) : Promise.resolve([]),
      ]);

      // Merge: non-IIT results (excluding IITs) + IIT results (only IITs)
      const allResults = [
        ...nonIitRows.filter((r: any) => classifyInstitute(r.institutes?.name || '') !== 'IIT'),
        ...iitRows.filter((r: any) => classifyInstitute(r.institutes?.name || '') === 'IIT'),
      ];

      // Group by institute
      const grouped: Record<string, any> = {};
      for (const r of allResults) {
        const inst = r.institutes?.name || 'Unknown';
        if (!grouped[inst]) {
          grouped[inst] = { inst, type: classifyInstitute(inst), state: getInstituteState(inst), programs: [] };
        }
        grouped[inst].programs.push({
          name: r.programs?.name || '', deg: r.programs?.deg || '',
          yrs: r.programs?.yrs || 4, quota: r.quota,
          open: r.open, close: r.close,
        });
      }

      const noBranchPriority = branchMode === 'none';
      const effectiveBranches = noBranchPriority
        ? DEFAULT_BRANCH_ORDER  // still used for internal branch sorting within a college
        : (branchMode === 'default' || branchOrder.length === 0) ? DEFAULT_BRANCH_ORDER : branchOrder;
      setActiveBranches(noBranchPriority ? [] : effectiveBranches);

      const colleges = Object.values(grouped).map((c: any) => {
        // Sort programs within each college: branch preference → closing rank
        c.programs.sort((a: any, b: any) => {
          const ba = getBranchRank(a.name, effectiveBranches);
          const bb = getBranchRank(b.name, effectiveBranches);
          return ba !== bb ? ba - bb : a.close - b.close;
        });
        c.tier = getInstituteTier(c.inst);
        return c;
      });

      if (noBranchPriority) {
        // No branch priority: sort purely by college tier → best closing rank
        colleges.sort((a: any, b: any) => {
          if (a.tier !== b.tier) return a.tier - b.tier;
          return (a.programs[0]?.close || 0) - (b.programs[0]?.close || 0);
        });
      } else {
        // Sort colleges: branch preference FIRST → institute tier within same branch → closing rank
        // e.g. if CSE is #1 preference, show all colleges with CSE first (sorted by tier),
        // then all colleges with ECE (#2), etc.
        colleges.sort((a: any, b: any) => {
          const bestA = getBranchRank(a.programs[0]?.name || '', effectiveBranches);
          const bestB = getBranchRank(b.programs[0]?.name || '', effectiveBranches);
          if (bestA !== bestB) return bestA - bestB;
          if (a.tier !== b.tier) return a.tier - b.tier;
          return (a.programs[0]?.close || 0) - (b.programs[0]?.close || 0);
        });
      }

      setResults(colleges);
    } catch (err) {
      console.error('Predict error:', err);
      setError('Failed to fetch predictions.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="relative pt-24 sm:pt-32 md:pt-40 pb-0 overflow-hidden">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 md:px-12">

        {!isLoggedIn ? (
          /* ── Pre-auth hero ──────────────────────────────────────────── */
          <div className="text-center max-w-3xl mx-auto mb-12 sm:mb-16">
            <h1 className="font-display text-5xl sm:text-6xl md:text-7xl font-bold leading-[1.04] tracking-tight mb-5">
              <span className="text-black">Stop Guessing.</span><br />
              <span className="text-white">Start Choosing.</span>
            </h1>

            <p className="text-base sm:text-lg text-[#D4CFC8] leading-relaxed mb-8 max-w-lg mx-auto">
              OviGuide is your AI counselling OS. Enter your rank, get personalized college predictions, an optimized choice list, and live guidance through every counselling round.
            </p>

            <div className="flex justify-center">
              <button
                onClick={() => login()}
                className="flex items-center justify-center gap-2 bg-white hover:bg-white/90 text-[#1a1a1a] px-8 py-3.5 rounded-full font-semibold text-sm transition-all duration-200 hover:-translate-y-px shadow-lg shadow-white/25 hover:shadow-white/40"
              >
                Find the Perfect College for Me <ArrowRight size={16} />
              </button>
            </div>
          </div>
        ) : (
          /* ── Post-auth section ──────────────────────────────── */
          <>
          {/* College profile opened from search — always takes priority */}
          {selectedCollege && (
            <CollegeProfile
              college={selectedCollege}
              homeState={homeState}
              priorityBranches={activeBranches}
              onBack={() => setSelectedCollege(null)}
            />
          )}

          {/* Counselling Hub — shown when no counselling selected and no college profile */}
          {!selectedCollege && activeCounselling === null && (
            <CounsellingHub
              userName={userProfile?.name || ''}
              onSelect={(portalId) => setActiveCounselling(portalId)}
            />
          )}

          {/* JOSAA prediction form */}
          {!selectedCollege && activeCounselling === 'josaa' && (
          <div className="max-w-lg mx-auto mb-8">
            {/* Back to hub */}
            <button
              onClick={() => { setActiveCounselling(null); setResults(null); setError(''); }}
              className="flex items-center gap-2 text-sm text-[#D4CFC8]/60 hover:text-white transition-colors mb-6 group"
            >
              <ArrowLeft size={15} className="group-hover:-translate-x-0.5 transition-transform" />
              Back to Counselling Hub
            </button>

            <div className="text-center mb-8">
              <h1 className="font-display text-4xl sm:text-5xl font-bold leading-[1.08] tracking-tight mb-3">
                <span className="text-[#F5F0E8]">Let's </span>
                <span className="text-white">Predict</span>
              </h1>
              <p className="text-sm text-[#D4CFC8]">Fill in your details and we'll predict your best colleges.</p>
            </div>

            <form
              onSubmit={handlePredict}
              className="bg-black/30 backdrop-blur-xl border border-white/10 rounded-2xl p-6 sm:p-8 space-y-5"
            >
              {/* Name */}
              <div>
                <label className="block text-xs font-medium text-[#D4CFC8] uppercase tracking-wider mb-1.5">Name</label>
                <input
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="Your full name"
                  required
                  className="w-full bg-white/[0.07] border border-white/10 rounded-xl px-4 py-3 text-sm text-[#F5F0E8] placeholder-[#D4CFC8]/50 focus:outline-none focus:ring-2 focus:ring-white/20 focus:border-transparent transition-all"
                />
              </div>

              {/* JEE Mains Rank */}
              <div>
                <label className="block text-xs font-medium text-[#D4CFC8] uppercase tracking-wider mb-1.5">JEE Mains Rank</label>
                <input
                  type="number"
                  value={mainsRank}
                  onChange={(e) => setMainsRank(e.target.value)}
                  placeholder="Enter your JEE Mains rank"
                  min="1"
                  required
                  className="w-full bg-white/[0.07] border border-white/10 rounded-xl px-4 py-3 text-sm text-[#F5F0E8] placeholder-[#D4CFC8]/50 focus:outline-none focus:ring-2 focus:ring-white/20 focus:border-transparent transition-all"
                />
              </div>

              {/* JEE Advanced Rank */}
              <div>
                <div className="flex items-center justify-between mb-1.5">
                  <label className="block text-xs font-medium text-[#D4CFC8] uppercase tracking-wider">JEE Advanced Rank</label>
                  <label className="flex items-center gap-2 cursor-pointer select-none">
                    <input
                      type="checkbox"
                      checked={advancedNA}
                      onChange={(e) => { setAdvancedNA(e.target.checked); if (e.target.checked) setAdvancedRank(''); }}
                      className="accent-white w-3.5 h-3.5 rounded"
                    />
                    <span className="text-xs text-[#D4CFC8]/70">N/A</span>
                  </label>
                </div>
                <input
                  type="number"
                  value={advancedRank}
                  onChange={(e) => setAdvancedRank(e.target.value)}
                  placeholder={advancedNA ? 'Not applicable' : 'Enter your JEE Advanced rank'}
                  min="1"
                  disabled={advancedNA}
                  className={`w-full bg-white/[0.07] border border-white/10 rounded-xl px-4 py-3 text-sm text-[#F5F0E8] placeholder-[#D4CFC8]/50 focus:outline-none focus:ring-2 focus:ring-white/20 focus:border-transparent transition-all ${advancedNA ? 'opacity-40 cursor-not-allowed' : ''}`}
                />
              </div>

              {/* Home State — searchable dropdown */}
              <StateCombobox value={homeState} onChange={setHomeState} />

              {/* Category + Gender row */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-medium text-[#D4CFC8] uppercase tracking-wider mb-1.5">Category</label>
                  <Select
                    value={category}
                    onChange={(v) => {
                      setCategory(v);
                      if (v === 'General') {
                        setCategoryRankNA(true);
                        setCategoryRank('');
                      } else {
                        setCategoryRankNA(false);
                      }
                    }}
                    options={CATEGORIES}
                    placeholder="Select"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-[#D4CFC8] uppercase tracking-wider mb-1.5">Gender</label>
                  <Select value={gender} onChange={setGender} options={GENDERS} placeholder="Select" />
                </div>
              </div>

              {/* Category Rank */}
              <div>
                <div className="flex items-center justify-between mb-1.5">
                  <label className="block text-xs font-medium text-[#D4CFC8] uppercase tracking-wider">Category Rank</label>
                  {category !== 'General' && (
                    <label className="flex items-center gap-2 cursor-pointer select-none">
                      <input
                        type="checkbox"
                        checked={categoryRankNA}
                        onChange={(e) => { setCategoryRankNA(e.target.checked); if (e.target.checked) setCategoryRank(''); }}
                        className="accent-white w-3.5 h-3.5 rounded"
                      />
                      <span className="text-xs text-[#D4CFC8]/70">N/A</span>
                    </label>
                  )}
                </div>
                <input
                  type="number"
                  value={categoryRank}
                  onChange={(e) => setCategoryRank(e.target.value)}
                  placeholder={categoryRankNA || category === 'General' ? 'Not applicable' : 'Enter your category rank'}
                  min="1"
                  disabled={categoryRankNA || category === 'General'}
                  className={`w-full bg-white/[0.07] border border-white/10 rounded-xl px-4 py-3 text-sm text-[#F5F0E8] placeholder-[#D4CFC8]/50 focus:outline-none focus:ring-2 focus:ring-white/20 focus:border-transparent transition-all ${categoryRankNA || category === 'General' ? 'opacity-40 cursor-not-allowed' : ''}`}
                />
              </div>

              {/* Branch Preference — 3-mode selector */}
              <div>
                <label className="block text-xs font-medium text-[#D4CFC8] uppercase tracking-wider mb-2">Branch Priority</label>
                <div className="flex gap-1.5 mb-3">
                  {([
                    ['custom', 'Custom Order'],
                    ['default', 'Default Order'],
                    ['none', 'No Preference'],
                  ] as const).map(([mode, label]) => (
                    <button
                      key={mode}
                      type="button"
                      onClick={() => { setBranchMode(mode); if (mode !== 'custom') setBranchOrder([]); }}
                      className={`flex-1 px-3 py-2 text-xs font-medium rounded-lg border transition-all ${
                        branchMode === mode
                          ? 'bg-white/15 border-white/30 text-white'
                          : 'bg-white/[0.04] border-white/10 text-[#D4CFC8]/60 hover:bg-white/[0.08] hover:text-[#D4CFC8]'
                      }`}
                    >
                      {label}
                    </button>
                  ))}
                </div>

                {branchMode === 'custom' && (
                  <>
                    {/* Available branches to pick from */}
                    <div className="flex flex-wrap gap-1.5 mb-2">
                      {DEFAULT_BRANCH_ORDER.filter(b => !branchOrder.includes(b)).map(branch => (
                        <button
                          key={branch}
                          type="button"
                          onClick={() => setBranchOrder(prev => [...prev, branch])}
                          className="px-2.5 py-1 text-xs rounded-lg bg-white/[0.06] border border-white/10 text-[#D4CFC8] hover:bg-white/[0.12] hover:text-white transition-colors"
                        >
                          + {branch}
                        </button>
                      ))}
                    </div>

                    {/* User's ordered priority list */}
                    {branchOrder.length > 0 && (
                      <div className="space-y-1 bg-white/[0.04] border border-white/10 rounded-xl p-2.5 max-h-48 overflow-y-auto scrollbar-hide">
                        {branchOrder.map((branch, i) => (
                          <div key={branch} className="flex items-center gap-2 bg-white/[0.06] rounded-lg px-2.5 py-1.5 group hover:bg-white/[0.1] transition-colors">
                            <span className="text-[11px] font-bold text-white/40 w-5 text-center">{i + 1}</span>
                            <GripVertical size={12} className="text-[#D4CFC8]/30 flex-shrink-0" />
                            <span className="text-sm text-[#F5F0E8] flex-1">{branch}</span>
                            <div className="flex items-center gap-0.5">
                              <button type="button" disabled={i === 0}
                                onClick={() => { const a = [...branchOrder]; [a[i-1],a[i]]=[a[i],a[i-1]]; setBranchOrder(a); }}
                                className="p-0.5 text-[#D4CFC8]/40 hover:text-white disabled:opacity-20 disabled:cursor-not-allowed transition-colors">
                                <ChevronUp size={12} />
                              </button>
                              <button type="button" disabled={i === branchOrder.length - 1}
                                onClick={() => { const a = [...branchOrder]; [a[i],a[i+1]]=[a[i+1],a[i]]; setBranchOrder(a); }}
                                className="p-0.5 text-[#D4CFC8]/40 hover:text-white disabled:opacity-20 disabled:cursor-not-allowed transition-colors">
                                <ChevronDown size={12} />
                              </button>
                              <button type="button"
                                onClick={() => setBranchOrder(prev => prev.filter((_, j) => j !== i))}
                                className="p-0.5 ml-1 text-red-400/50 hover:text-red-400 transition-colors text-xs font-bold">
                                ✕
                              </button>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}

                    {branchOrder.length === 0 && (
                      <p className="text-xs text-[#D4CFC8]/40 text-center py-2">Click branches above to set your priority order</p>
                    )}
                  </>
                )}

                {branchMode === 'default' && (
                  <p className="text-xs text-[#D4CFC8]/40 mt-1">Default: CSE → IT → MnC → ECE → EEE → ENI → Mech → Chem → Prod → Civil → Met → Mining</p>
                )}

                {branchMode === 'none' && (
                  <p className="text-xs text-[#D4CFC8]/40 mt-1">Results will be sorted by best colleges first, showing all branches you can get</p>
                )}
              </div>

              {/* Submit */}
              <button
                type="submit"
                disabled={loading}
                className="w-full flex items-center justify-center gap-2 bg-white hover:bg-white/90 text-[#1a1a1a] py-3.5 rounded-full font-semibold text-sm transition-all duration-200 hover:-translate-y-px shadow-lg shadow-white/25 hover:shadow-white/40 mt-2 disabled:opacity-60 disabled:cursor-not-allowed"
              >
                {loading ? <><Loader2 size={16} className="animate-spin" /> Predicting...</> : <>Predict <ArrowRight size={16} /></>}
              </button>
            </form>

            {/* Error message */}
            {error && (
              <div className="mt-4 p-4 bg-red-500/10 border border-red-500/20 rounded-xl text-sm text-red-300 text-center">
                {error}
              </div>
            )}
          </div>
          )}

          {/* ── Results — cream card grid (JOSAA only) ──────────────────────────── */}
          {results && results.length > 0 && !selectedCollege && activeCounselling === 'josaa' && (
            <div className="max-w-7xl mx-auto mt-10 mb-16 px-2">
              <div className="flex items-center justify-between mb-8">
                <div>
                  <h3 className="text-2xl font-bold text-[#F5F0E8] mb-1">
                    <span className="mr-2">🎯</span>Your College Matches
                  </h3>
                  <p className="text-sm text-[#D4CFC8]/60">
                    {results.reduce((s: number, c: any) => s + c.programs.length, 0)} programs across {results.length} college{results.length !== 1 ? 's' : ''} · 2025 Round 6
                  </p>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-7">
                {results.map((college: any, i: number) => {
                  const typeBadge: Record<string, { bg: string; text: string; dot: string; glow: string }> = {
                    IIT:  { bg: 'bg-amber-50', text: 'text-amber-700', dot: 'bg-amber-400', glow: 'shadow-amber-200/40' },
                    NIT:  { bg: 'bg-sky-50',   text: 'text-sky-700',   dot: 'bg-sky-400',   glow: 'shadow-sky-200/40' },
                    IIIT: { bg: 'bg-emerald-50', text: 'text-emerald-700', dot: 'bg-emerald-400', glow: 'shadow-emerald-200/40' },
                    GFTI: { bg: 'bg-violet-50', text: 'text-violet-700', dot: 'bg-violet-400', glow: 'shadow-violet-200/40' },
                  };
                  const badge = typeBadge[college.type] || typeBadge.GFTI;
                  const topGrad: Record<string, string> = {
                    IIT: 'from-amber-400/20 via-amber-300/5 to-transparent',
                    NIT: 'from-sky-400/20 via-sky-300/5 to-transparent',
                    IIIT: 'from-emerald-400/20 via-emerald-300/5 to-transparent',
                    GFTI: 'from-violet-400/20 via-violet-300/5 to-transparent',
                  };
                  return (
                    <div
                      key={i}
                      onClick={() => openCollegeProfile(college)}
                      className={`group relative bg-[#FEFDFB] border border-[#E8E2D9]/80 rounded-3xl overflow-hidden cursor-pointer hover:shadow-2xl ${badge.glow} hover:-translate-y-1.5 transition-all duration-300 ease-out`}
                    >
                      {/* Subtle gradient glow at top */}
                      <div className={`absolute inset-x-0 top-0 h-24 bg-gradient-to-b ${topGrad[college.type] || topGrad.GFTI} pointer-events-none`} />

                      <div className="relative p-7">
                        {/* Badge + rank */}
                        <div className="flex items-center justify-between mb-4">
                          <span className={`inline-flex items-center gap-1.5 text-[10px] font-bold uppercase tracking-[0.08em] px-3 py-1.5 rounded-full border border-current/10 ${badge.bg} ${badge.text}`}>
                            <span className={`w-1.5 h-1.5 rounded-full ${badge.dot} animate-pulse`} />
                            {college.type}
                          </span>
                          <span className="text-[11px] font-mono text-[#B0A99E] bg-[#F5F1EB] px-2.5 py-1 rounded-lg">
                            #{i + 1}
                          </span>
                        </div>

                        {/* College name */}
                        <h4 className="text-[19px] font-bold text-[#1E1B18] leading-snug mb-1 group-hover:text-[#0d0b09] transition-colors tracking-[-0.01em]">
                          {college.inst}
                        </h4>

                        {/* State line */}
                        {college.state && (
                          <p className="text-[11px] text-[#B0A99E] mb-4 flex items-center gap-1">
                            <MapPin size={10} /> {college.state}
                          </p>
                        )}

                        {/* Stats pills */}
                        <div className="flex items-center gap-2.5 mb-5">
                          <div className="flex items-center gap-1.5 text-[11px] text-[#7A746B] bg-[#F5F1EB] rounded-lg px-2.5 py-1.5">
                            <BookOpen size={12} className="text-[#A69F93]" />
                            <span className="font-semibold">{college.programs.length}</span> program{college.programs.length !== 1 ? 's' : ''}
                          </div>
                          <div className="flex items-center gap-1.5 text-[11px] text-[#7A746B] bg-[#F5F1EB] rounded-lg px-2.5 py-1.5">
                            <TrendingDown size={12} className="text-[#A69F93]" />
                            Best: <span className="font-bold text-[#1E1B18]">{college.programs[0]?.close.toLocaleString()}</span>
                          </div>
                        </div>

                        {/* Top 3 programs */}
                        <div className="space-y-2">
                          {college.programs.slice(0, 3).map((p: any, j: number) => (
                            <div key={j} className="flex items-center justify-between bg-gradient-to-r from-[#F7F3ED] to-[#F3EFE8] rounded-xl px-4 py-3.5 group-hover:from-[#F0ECE4] group-hover:to-[#EDE8DF] transition-all duration-200">
                              <div className="flex-1 min-w-0 mr-3">
                                <p className="text-[13px] font-semibold text-[#2C2824] truncate leading-tight">{p.name}</p>
                                <p className="text-[10px] text-[#B0A99E] mt-1 tracking-wide uppercase">{p.deg} · {p.yrs}yr · {p.quota}</p>
                              </div>
                              <div className="text-right flex-shrink-0 pl-2">
                                <p className="text-[15px] font-bold text-[#1E1B18] tabular-nums tracking-tight">{p.close.toLocaleString()}</p>
                                <p className="text-[8px] text-[#B0A99E] uppercase tracking-[0.1em] font-semibold">Closing</p>
                              </div>
                            </div>
                          ))}
                        </div>

                        {college.programs.length > 3 && (
                          <p className="text-[11px] text-center text-[#B0A99E] mt-3 font-medium">
                            +{college.programs.length - 3} more · Click to view all
                          </p>
                        )}

                        {/* View profile footer */}
                        <div className="flex items-center justify-center gap-2 mt-6 pt-4 border-t border-[#EDE8DF]">
                          <span className="text-xs font-semibold text-[#A69F93] group-hover:text-[#1E1B18] transition-colors duration-200">View College Profile</span>
                          <ChevronRight size={14} className="text-[#B0A99E] group-hover:text-[#1E1B18] group-hover:translate-x-0.5 transition-all duration-200" />
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {results && results.length === 0 && !selectedCollege && activeCounselling === 'josaa' && (
            <div className="max-w-lg mx-auto mt-6 mb-16 p-5 bg-[#FAF7F2] border border-[#E8E2D9] rounded-xl text-sm text-[#8B8578] text-center">
              No matching colleges found for your rank and category. Try a different combination.
            </div>
          )}
        </>
        )}

        {/* Dashboard — full width showcase */}
        {!isLoggedIn && (
          <div className="relative pb-16 sm:pb-20 md:pb-24 fade-scale">
            <div className="absolute -inset-8 bg-gradient-to-b from-accent/5 via-transparent to-transparent rounded-3xl blur-3xl -z-10" />
            <CopilotDashboard />
          </div>
        )}
      </div>

      {/* Ticker runs full width */}
      <CollegeTicker />

      {/* Background */}
      <div className="absolute top-0 right-0 w-[500px] h-[500px] bg-white/5 rounded-full -translate-y-1/2 translate-x-1/2 blur-3xl -z-10 pointer-events-none" />
    </section>
  );
};

export default Hero;