import React from 'react';
import { BarChart2, Zap, Search, Bot } from 'lucide-react';

interface PillarCardProps {
  title: string;
  badge: string;
  description: string;
  icon: React.ReactNode;
  gradient: string;
}

const PillarCard: React.FC<PillarCardProps> = ({ title, badge, description, icon, gradient }) => (
  <div className={`relative rounded-3xl p-8 overflow-hidden group hover:-translate-y-2 transition-all duration-400 ease-out cursor-default ${gradient}`}>
    <div className="absolute -top-10 -right-10 w-48 h-48 bg-white/10 rounded-full blur-3xl group-hover:scale-125 transition-transform duration-700" />

    <div className="relative z-10">
      <span className="inline-block px-3 py-1 bg-white/15 rounded-full text-[10px] font-semibold uppercase tracking-widest mb-6 text-white">
        {badge}
      </span>
      <div className="w-12 h-12 bg-white/20 rounded-2xl flex items-center justify-center mb-5 group-hover:scale-110 transition-transform duration-300">
        {icon}
      </div>
      <h3 className="font-display text-2xl font-semibold mb-3 text-white">{title}</h3>
      <p className="text-white/75 text-sm leading-relaxed">{description}</p>
    </div>
  </div>
);

const extras = [
  'ROI Calculator',
  'Multi-Counselling Hub',
  'Peer Benchmarking',
  'Scenario Simulator',
  'Seat Alert System',
  'Branch vs College Analyzer',
  'Category Probability Booster',
  'Decision Confidence Score',
];

const Features: React.FC = () => {
  const pillars: PillarCardProps[] = [
    {
      title: 'Prediction Engine',
      badge: 'Core AI',
      description: 'Admission probability across every college-branch combination using 5 years of historical JoSAA and state CET data.',
      icon: <BarChart2 size={22} className="text-white" />,
      gradient: 'bg-gradient-to-br from-cblue to-cblue/80',
    },
    {
      title: 'Optimization Engine',
      badge: 'Strategic',
      description: 'Generates a risk-balanced choice list that maximizes expected outcomes across every counselling round.',
      icon: <Zap size={22} className="text-white" />,
      gradient: 'bg-gradient-to-br from-camber to-camber/80',
    },
    {
      title: 'Truth Engine',
      badge: 'Real Insights',
      description: 'Aggregates Reddit, LinkedIn, and placement data into honest, unfiltered college intelligence. No marketing fluff.',
      icon: <Search size={22} className="text-white" />,
      gradient: 'bg-gradient-to-br from-cgreen to-cgreen/80',
    },
    {
      title: 'Counselling Copilot',
      badge: 'Always Live',
      description: 'Tracks seat allotments after every round and recommends Freeze, Float or Slide with clear risk reasoning.',
      icon: <Bot size={22} className="text-white" />,
      gradient: 'bg-gradient-to-br from-accent to-accent/80',
    },
  ];

  return (
    <section id="features" className="py-20 sm:py-28 md:py-36 bg-paper/70 backdrop-blur-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 md:px-12">

        {/* Header */}
        <div className="mb-12 md:mb-16 fade-up">
          <span className="text-xs font-semibold tracking-widest uppercase text-ink-4 mb-3 block">Product</span>
          <h2 className="font-display text-4xl sm:text-5xl md:text-6xl font-bold text-ink leading-[1.06] tracking-tight">
            Intelligence at<br />
            <span className="text-ink-4">every layer.</span>
          </h2>
        </div>

        {/* 4 Pillar Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 md:gap-5 mb-10">
          {pillars.map((p, i) => (
            <div key={i} className={`fade-up fade-up-d${i + 1}`}>
              <PillarCard {...p} />
            </div>
          ))}
        </div>

        {/* Additional features as chips */}
        <div className="fade-up">
          <p className="text-xs font-semibold tracking-widest uppercase text-ink-4 mb-4">And more</p>
          <div className="flex flex-wrap gap-2.5">
            {extras.map((e, i) => (
              <span key={i} className="px-4 py-2 bg-white/10 border border-white/10 rounded-full text-sm text-[#D4CFC8] font-medium hover:bg-white/15 hover:text-white transition-colors cursor-default">
                {e}
              </span>
            ))}
          </div>
        </div>

      </div>
    </section>
  );
};

export default Features;