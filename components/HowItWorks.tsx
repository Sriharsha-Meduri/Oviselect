import React from 'react';
import { ClipboardList, Brain, BookOpen, ListChecks, Bot } from 'lucide-react';

const steps = [
  {
    number: '01',
    title: 'Share Your Profile',
    description: 'Rank, category, preferred states, and career goals. Takes two minutes.',
    icon: <ClipboardList size={20} />,
    color: 'text-accent',
    bg: 'bg-accent-light',
  },
  {
    number: '02',
    title: 'AI Maps Your Universe',
    description: 'Admission probability calculated across 50,000+ college-branch combinations.',
    icon: <Brain size={20} />,
    color: 'text-cblue',
    bg: 'bg-cblue-light',
  },
  {
    number: '03',
    title: 'Discover Real Insights',
    description: 'Reddit threads, placement data, and campus reviews — aggregated honestly.',
    icon: <BookOpen size={20} />,
    color: 'text-cgreen',
    bg: 'bg-cgreen-light',
  },
  {
    number: '04',
    title: 'Generate Choice List',
    description: 'AI builds a risk-balanced, round-optimised list of choices — ready to submit.',
    icon: <ListChecks size={20} />,
    color: 'text-camber',
    bg: 'bg-camber-light',
  },
  {
    number: '05',
    title: 'Navigate Every Round',
    description: 'Copilot tells you Freeze, Float or Slide after each allotment. In real time.',
    icon: <Bot size={20} />,
    color: 'text-accent',
    bg: 'bg-accent-light',
  },
];

const HowItWorks: React.FC = () => {
  return (
    <section id="how-it-works" className="py-20 sm:py-28 md:py-36 bg-paper-2/70 backdrop-blur-md">
      <div className="max-w-5xl mx-auto px-4 sm:px-6 md:px-12">

        {/* Header */}
        <div className="mb-16 md:mb-20 fade-up">
          <span className="text-xs font-semibold tracking-widest uppercase text-accent mb-4 block">Step by Step</span>
          <h2 className="font-display text-4xl sm:text-5xl md:text-6xl font-bold text-ink leading-[1.06] tracking-tight">
            From rank to<br />
            <span className="text-ink-4">right college.</span>
          </h2>
        </div>

        {/* Steps */}
        <div className="relative">
          {/* Vertical connector line */}
          <div className="absolute left-[27px] md:left-[31px] top-8 bottom-8 w-px bg-white/10 hidden sm:block" />

          <div className="space-y-0">
            {steps.map((step, i) => (
              <div key={i} className={`relative flex gap-6 md:gap-10 pb-10 last:pb-0 fade-up fade-up-d${(i % 4) + 1}`}>
                {/* Step icon circle */}
                <div className={`flex-shrink-0 w-14 h-14 rounded-2xl ${step.bg} flex items-center justify-center relative z-10`}>
                  <div className={step.color}>{step.icon}</div>
                </div>

                {/* Content */}
                <div className="pt-3 sm:pt-4">
                  <div className="flex items-center gap-3 mb-2">
                    <span className={`text-[11px] font-bold ${step.color} opacity-60 tracking-wider`}>{step.number}</span>
                  </div>
                  <h3 className="font-display text-xl sm:text-2xl font-semibold text-ink mb-1.5">{step.title}</h3>
                  <p className="text-base text-ink-3 max-w-md leading-relaxed">{step.description}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

      </div>
    </section>
  );
};

export default HowItWorks;
