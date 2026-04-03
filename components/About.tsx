import React from 'react';
import { Target, Eye, Heart, Sparkles } from 'lucide-react';

interface ValueCardProps {
  icon: React.ReactNode;
  title: string;
  description: string;
  iconBg: string;
  iconColor: string;
}

const ValueCard: React.FC<ValueCardProps> = ({ icon, title, description, iconBg, iconColor }) => (
  <div className="group bg-black/30 border border-white/10 p-7 rounded-2xl hover:shadow-xl hover:-translate-y-1.5 transition-all duration-400 cursor-default backdrop-blur-sm">
    <div className={`w-11 h-11 ${iconBg} rounded-xl flex items-center justify-center mb-5 group-hover:scale-110 transition-transform duration-300`}>
      <div className={iconColor}>{icon}</div>
    </div>
    <h3 className="font-display text-lg font-semibold text-ink mb-2">{title}</h3>
    <p className="text-sm text-ink-3 leading-relaxed">{description}</p>
  </div>
);

const About: React.FC = () => {
  const values: ValueCardProps[] = [
    {
      icon: <Target size={20} />,
      title: 'Our Mission',
      description: 'Make personalised, AI-powered counselling accessible to every JEE aspirant regardless of coaching resources or background.',
      iconBg: 'bg-accent-light',
      iconColor: 'text-accent',
    },
    {
      icon: <Eye size={20} />,
      title: 'Our Vision',
      description: 'Become the default decision infrastructure for higher education in India, shifting counselling from guesswork to data-driven optimisation.',
      iconBg: 'bg-cblue-light',
      iconColor: 'text-cblue',
    },
    {
      icon: <Heart size={20} />,
      title: 'Our Values',
      description: 'Decision intelligence over raw data. Truth over marketing. Personalisation by default. Long-term student success over short-term metrics.',
      iconBg: 'bg-accent-light',
      iconColor: 'text-accent',
    },
  ];

  const stats = [
    { num: '16L+', label: 'JEE students per year' },
    { num: '50K+', label: 'College-branch combos' },
    { num: '5+',   label: 'Counselling systems' },
  ];

  return (
    <section id="about-us" className="py-20 sm:py-28 md:py-36 bg-paper-2/70 backdrop-blur-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 md:px-12">

        {/* Header */}
        <div className="text-center mb-16 md:mb-20 fade-up">
          <span className="text-xs font-semibold tracking-widest uppercase text-accent mb-4 block">About Us</span>
          <h2 className="font-display text-4xl sm:text-5xl md:text-6xl font-bold text-ink leading-[1.06] tracking-tight mb-4">
            Born from the problem<br />
            <span className="text-ink-4">we lived through.</span>
          </h2>
        </div>

        {/* Story + Stats */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 lg:gap-20 items-start mb-16 md:mb-20">

          {/* Left column — fade-left for text content on the left */}
          <div className="fade-left">
            <h3 className="font-display text-2xl font-semibold text-ink mb-5 flex items-center gap-2">
              Our Story <Sparkles size={18} className="text-accent" />
            </h3>
            <div className="space-y-4 text-ink-3 text-base leading-relaxed">
              <p>
                Every year, brilliant students make wrong college choices not because they lacked intelligence, but because they lacked the right tools. Coaching PDFs, classmates' opinions, and scattered Reddit threads are no substitute for a real guidance system.
              </p>
              <p>
                OviGuide is our answer: a complete AI counselling OS that combines prediction, optimisation, honest insights, and real-time round guidance so no student has to navigate this alone.
              </p>
            </div>
          </div>

          {/* Stats — fade-right for the right-column visual */}
          <div className="grid grid-cols-3 gap-4 pt-2 fade-right">
            {stats.map(({ num, label }, i) => (
              <div key={i} className="bg-black/30 border border-white/10 rounded-2xl p-5 text-center group cursor-default hover:-translate-y-1 transition-all duration-300 backdrop-blur-sm">
                <p className="font-display text-3xl sm:text-4xl font-bold text-ink mb-1.5 group-hover:text-accent transition-colors">{num}</p>
                <p className="text-xs text-ink-4 leading-snug">{label}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Values */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 md:gap-5">
          {values.map((v, i) => (
            <div key={i} className={`fade-up fade-up-d${i + 1}`}>
              <ValueCard {...v} />
            </div>
          ))}
        </div>

      </div>
    </section>
  );
};

export default About;
