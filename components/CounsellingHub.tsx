import React from 'react';
import { ArrowRight, Lock } from 'lucide-react';

interface Portal {
  id: string;
  name: string;
  fullName: string;
  accent: string;
  live: boolean;
  description: string;
  scope: string;
}

const PORTALS: Portal[] = [
  { id: 'josaa',          name: 'JoSAA',          fullName: 'Joint Seat Allocation Authority',                      accent: '#4A9EFF', live: true,  description: 'IITs, NITs, IIITs & GFTIs',           scope: 'National' },
  { id: 'csab',           name: 'CSAB',            fullName: 'Central Seat Allocation Board',                        accent: '#34D399', live: false, description: 'NIT+ System special rounds',            scope: 'National' },
  { id: 'jac-delhi',      name: 'JAC Delhi',       fullName: 'Joint Admission Counselling — Delhi',                  accent: '#A78BFA', live: false, description: 'DTU, NSIT, IGDTUW, IIIT Delhi',         scope: 'Delhi' },
  { id: 'jac-chandigarh', name: 'JAC Chandigarh',  fullName: 'Joint Admission Counselling — Chandigarh',             accent: '#38BDF8', live: false, description: 'PEC, UIET & Chandigarh colleges',        scope: 'Chandigarh' },
  { id: 'comedk',         name: 'COMEDK',          fullName: 'Consortium of Medical & Dental Colleges of Karnataka', accent: '#F87171', live: false, description: 'Karnataka private engineering',          scope: 'Karnataka' },
  { id: 'kcet',           name: 'KCET',            fullName: 'Karnataka Common Entrance Test',                       accent: '#C084FC', live: false, description: 'Karnataka government colleges',          scope: 'Karnataka' },
  { id: 'mhtcet',         name: 'MHT-CET',         fullName: 'Maharashtra Common Entrance Test',                     accent: '#60A5FA', live: false, description: 'Maharashtra engineering colleges',        scope: 'Maharashtra' },
  { id: 'wbjee',          name: 'WBJEE',           fullName: 'West Bengal Joint Entrance Exam',                      accent: '#4ADE80', live: false, description: 'West Bengal state colleges',             scope: 'West Bengal' },
  { id: 'viteee',         name: 'VITEEE',          fullName: 'VIT Engineering Entrance Exam',                        accent: '#FBBF24', live: false, description: 'VIT Vellore, Chennai & others',           scope: 'Private' },
  { id: 'met',            name: 'MET',             fullName: 'Manipal Entrance Test',                                accent: '#F472B6', live: false, description: 'Manipal Academy of Higher Ed.',          scope: 'Private' },
  { id: 'tiet',           name: 'TIET',            fullName: 'Thapar Institute of Engg & Tech',                      accent: '#818CF8', live: false, description: 'Thapar University admissions',           scope: 'Private' },
];

interface CounsellingHubProps {
  userName: string;
  onSelect: (portalId: string) => void;
}

const CounsellingHub: React.FC<CounsellingHubProps> = ({ userName, onSelect }) => {
  const firstName = userName?.split(' ')[0] || 'there';

  return (
    <div className="min-h-screen bg-[#0A0A0A] px-4 sm:px-8 py-12">
      <div className="max-w-6xl mx-auto">

        {/* Header */}
        <div className="mb-14">
          <p className="text-sm font-medium text-white/30 tracking-widest uppercase mb-4">Welcome back, {firstName}</p>
          <h1 className="text-5xl sm:text-6xl font-bold text-white tracking-tight leading-none mb-4">
            Choose your<br />
            <span className="text-white/40">counselling portal.</span>
          </h1>
          <p className="text-lg text-white/50 max-w-lg leading-relaxed">
            Get cutoff predictions, college comparisons, and seat availability — all in one place.
          </p>
        </div>

        {/* Live portal — featured full-width */}
        {PORTALS.filter(p => p.live).map(portal => (
          <button
            key={portal.id}
            onClick={() => onSelect(portal.id)}
            className="group w-full mb-6 text-left rounded-2xl border border-white/10 bg-white/[0.03] hover:bg-white/[0.06] hover:border-white/20 transition-all duration-200 p-8 sm:p-10"
          >
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-6">
              <div className="flex items-center gap-5">
                <div
                  className="w-16 h-16 rounded-2xl flex items-center justify-center text-xl font-black flex-shrink-0"
                  style={{ background: `${portal.accent}18`, border: `1.5px solid ${portal.accent}40`, color: portal.accent }}
                >
                  {portal.name.slice(0, 2)}
                </div>
                <div>
                  <div className="flex items-center gap-3 mb-1">
                    <span className="text-2xl font-bold text-white tracking-tight">{portal.name}</span>
                    <span
                      className="flex items-center gap-1.5 text-xs font-semibold px-2.5 py-0.5 rounded-full"
                      style={{ background: `${portal.accent}20`, color: portal.accent, border: `1px solid ${portal.accent}35` }}
                    >
                      <span className="w-1.5 h-1.5 rounded-full animate-pulse" style={{ background: portal.accent }} />
                      Live
                    </span>
                  </div>
                  <p className="text-white/50 text-base">{portal.description}</p>
                  <p className="text-white/25 text-sm mt-1">{portal.fullName}</p>
                </div>
              </div>
              <div
                className="flex items-center gap-2 text-sm font-semibold whitespace-nowrap flex-shrink-0"
                style={{ color: portal.accent }}
              >
                Start Predicting
                <ArrowRight size={16} className="group-hover:translate-x-1 transition-transform" />
              </div>
            </div>
          </button>
        ))}

        {/* Section label */}
        <p className="text-xs font-semibold text-white/20 uppercase tracking-widest mb-4">Coming Soon</p>

        {/* Other portals grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3">
          {PORTALS.filter(p => !p.live).map(portal => (
            <PortalCard key={portal.id} portal={portal} onSelect={onSelect} />
          ))}
        </div>

        <p className="text-center text-xs text-white/15 mt-10 tracking-wide">
          Oviselect · Data updated for JoSAA 2025
        </p>
      </div>
    </div>
  );
};

const PortalCard: React.FC<{ portal: Portal; onSelect: (id: string) => void }> = ({ portal }) => {
  return (
    <div className="relative text-left rounded-xl border border-white/[0.06] bg-white/[0.02] p-6 opacity-50 cursor-not-allowed select-none">
      <div className="flex items-start justify-between mb-5">
        <div
          className="w-12 h-12 rounded-xl flex items-center justify-center text-sm font-black"
          style={{ background: `${portal.accent}12`, border: `1px solid ${portal.accent}25`, color: portal.accent }}
        >
          {portal.name.slice(0, 2)}
        </div>
        <span className="flex items-center gap-1 text-[10px] font-medium text-white/25 uppercase tracking-wider px-2 py-0.5 rounded-full bg-white/5 border border-white/8">
          <Lock size={8} /> Soon
        </span>
      </div>

      <h3 className="text-base font-bold text-white/80 tracking-tight mb-1">{portal.name}</h3>
      <p className="text-sm text-white/40 leading-snug mb-3">{portal.description}</p>
      <p className="text-xs text-white/20">{portal.scope}</p>
    </div>
  );
};

export default CounsellingHub;

 