import React from 'react';
import { CheckCircle2 } from 'lucide-react';

const benefits = [
  'AI rank-to-college prediction across 50K+ combos',
  'Risk-balanced, round-aware choice list',
  'Real student insights from Reddit and LinkedIn',
  'Freeze, Float or Slide guidance every round',
  'Personalised to your goals, not just your rank',
];

const Benefits: React.FC = () => {
  return (
    <section id="about" className="py-20 sm:py-28 md:py-36 bg-paper/70 backdrop-blur-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 md:px-12">

        {/* Large manifesto statement */}
        <div className="max-w-4xl mb-20 md:mb-28 fade-up">
          <span className="text-xs font-semibold tracking-widest uppercase text-accent mb-5 block">The Problem</span>
          <h2 className="font-display text-4xl sm:text-5xl md:text-6xl lg:text-7xl font-bold text-ink leading-[1.06] tracking-tight">
            16 lakh students.<br />
            <span className="text-ink-4">Zero personalised guidance.</span>
          </h2>
        </div>

        {/* Two column */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 lg:gap-20 items-center">

          {/* Left: short explanation — fade-left for left-column text content */}
          <div className="fade-left">
            <p className="text-lg sm:text-xl text-ink-3 leading-relaxed mb-10">
              Every year, JEE aspirants navigate one of life's most consequential decisions using coaching PDFs, peer pressure, and half-truths online. OviGuide is the missing layer.
            </p>
            <button className="text-sm font-semibold text-[#F5F0E8] border-b-2 border-[#F5F0E8] pb-0.5 hover:text-white hover:border-white transition-all duration-200">
              Learn how we're different
            </button>
          </div>

          {/* Right: checklist — fade-right with staggered items */}
          <div className="space-y-5">
            {benefits.map((b, i) => (
              <div key={i} className={`flex items-start gap-4 fade-right fade-up-d${i + 1}`}>
                <CheckCircle2 size={20} className="text-accent flex-shrink-0 mt-0.5" strokeWidth={2} />
                <p className="text-base sm:text-lg font-medium text-ink-2">{b}</p>
              </div>
            ))}
          </div>
        </div>

      </div>
    </section>
  );
};

export default Benefits;
