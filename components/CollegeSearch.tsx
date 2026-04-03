import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Search, X, MapPin } from 'lucide-react';
import { supabase } from '../lib/supabase';

interface Institute {
  id: number;
  name: string;
  state?: string;
  type?: string;
}

const classifyInstitute = (name: string): string => {
  const lo = name.toLowerCase();
  if (lo.includes('international institute of information technology') && (lo.includes('bhubaneswar') || lo.includes('naya raipur'))) return 'GFTI';
  if (/^iit[\s(]/i.test(name)) return 'IIT';
  if (/^(nit[\s,]|manit\s|mnit\s|mnnit\s|svnit|vnit|bramnit)/i.test(name)) return 'NIT';
  if (lo.includes('indian institute of engineering science and technology')) return 'NIT';
  if (/^(iiit[\s(,]|abv-iiitm)/i.test(name)) return 'IIIT';
  if (lo.includes('indian institute of information technology')) return 'IIIT';
  return 'GFTI';
};

const TYPE_STYLES: Record<string, { dot: string; text: string }> = {
  IIT:  { dot: 'bg-amber-400',   text: 'text-amber-400' },
  NIT:  { dot: 'bg-sky-400',     text: 'text-sky-400' },
  IIIT: { dot: 'bg-emerald-400', text: 'text-emerald-400' },
  GFTI: { dot: 'bg-violet-400',  text: 'text-violet-400' },
};

interface CollegeSearchProps {
  isLoggedIn: boolean;
}

const CollegeSearch: React.FC<CollegeSearchProps> = ({ isLoggedIn }) => {
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<Institute[]>([]);
  const [loading, setLoading] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);
  const wrapperRef = useRef<HTMLDivElement>(null);

  // Close on outside click
  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (wrapperRef.current && !wrapperRef.current.contains(e.target as Node)) {
        setOpen(false);
        setQuery('');
        setResults([]);
      }
    };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, []);

  // Search institutes
  const doSearch = useCallback(async (q: string) => {
    if (!q || q.length < 2) { setResults([]); return; }
    setLoading(true);
    try {
      const { data, error } = await supabase
        .from('institutes')
        .select('id, name')
        .ilike('name', `%${q}%`)
        .limit(10);
      if (!error && data) setResults(data as Institute[]);
    } catch {
      setResults([]);
    } finally {
      setLoading(false);
    }
  }, []);

  // Debounce search
  useEffect(() => {
    const t = setTimeout(() => doSearch(query), 250);
    return () => clearTimeout(t);
  }, [query, doSearch]);

  const handleOpen = () => {
    setOpen(true);
    setTimeout(() => inputRef.current?.focus(), 50);
  };

  const handleSelect = (inst: Institute) => {
    setOpen(false);
    setQuery('');
    setResults([]);
    // Dispatch event — Hero.tsx listens and opens the profile
    window.dispatchEvent(new CustomEvent('oviguide-search-college', { detail: { name: inst.name } }));
  };

  if (!isLoggedIn) return null;

  return (
    <div ref={wrapperRef} className="relative">
      {!open ? (
        <button
          onClick={handleOpen}
          className="flex items-center gap-2 text-sm text-[#D4CFC8] hover:text-white bg-white/[0.07] hover:bg-white/[0.12] border border-white/10 hover:border-white/20 px-3.5 py-2 rounded-full transition-all duration-200"
        >
          <Search size={14} />
          <span className="hidden sm:inline">Search colleges</span>
        </button>
      ) : (
        <div className="flex items-center bg-white/[0.08] border border-white/20 rounded-full px-3.5 py-2 gap-2 w-[260px] sm:w-[320px]">
          <Search size={14} className="text-[#D4CFC8]/60 flex-shrink-0" />
          <input
            ref={inputRef}
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search IITs, NITs, IIITs..."
            className="flex-1 bg-transparent text-sm text-[#F5F0E8] placeholder-[#D4CFC8]/40 outline-none"
          />
          <button onClick={() => { setOpen(false); setQuery(''); setResults([]); }}>
            <X size={14} className="text-[#D4CFC8]/50 hover:text-white transition-colors" />
          </button>
        </div>
      )}

      {/* Dropdown */}
      {open && (query.length >= 2) && (
        <div className="absolute top-full right-0 mt-2 w-[320px] sm:w-[400px] bg-[#111]/95 backdrop-blur-xl border border-white/10 rounded-2xl overflow-hidden shadow-2xl shadow-black/50 z-50">
          {loading && (
            <div className="px-4 py-3 text-xs text-[#D4CFC8]/50 text-center">Searching...</div>
          )}
          {!loading && results.length === 0 && query.length >= 2 && (
            <div className="px-4 py-3 text-xs text-[#D4CFC8]/50 text-center">No colleges found for "{query}"</div>
          )}
          {!loading && results.map((inst) => {
            const type = classifyInstitute(inst.name);
            const style = TYPE_STYLES[type] || TYPE_STYLES.GFTI;
            return (
              <button
                key={inst.id}
                onClick={() => handleSelect(inst)}
                className="w-full flex items-center gap-3 px-4 py-3.5 hover:bg-white/[0.07] transition-colors text-left border-b border-white/5 last:border-0"
              >
                <span className={`w-2 h-2 rounded-full flex-shrink-0 ${style.dot}`} />
                <div className="flex-1 min-w-0">
                  <p className="text-sm text-[#F5F0E8] truncate font-medium">{inst.name}</p>
                </div>
                <span className={`text-[10px] font-bold uppercase tracking-wider flex-shrink-0 ${style.text}`}>{type}</span>
              </button>
            );
          })}
          {!loading && results.length > 0 && (
            <div className="px-4 py-2 text-[10px] text-[#D4CFC8]/30 text-center tracking-wide">
              Click a college to view full profile
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default CollegeSearch;

