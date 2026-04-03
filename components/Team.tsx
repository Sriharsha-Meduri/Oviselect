import React from 'react';
import { Linkedin } from 'lucide-react';

const TeamMember: React.FC<{ name: string; role: string; description: string; image: string; linkedin: string }> = ({ name, role, description, image, linkedin }) => (
  <div className="flex flex-col items-center text-center p-6 sm:p-8 bg-black/30 border border-white/10 rounded-3xl hover:shadow-2xl hover:-translate-y-2 transition-all duration-500 ease-out group backdrop-blur-sm">
    {/* Photo */}
    <div className="w-32 h-32 sm:w-40 sm:h-40 md:w-48 md:h-48 mb-5 relative">
      <div className="absolute inset-0 bg-gradient-to-br from-accent to-camber rounded-full blur-xl opacity-0 group-hover:opacity-25 transition-opacity duration-500" />
      <img
        src={image}
        alt={name}
        className="w-full h-full object-cover rounded-full shadow-xl relative z-10 ring-4 ring-white/10 group-hover:ring-white/30 transition-all duration-300"
      />
    </div>
    <h3 className="text-lg sm:text-xl font-black text-ink mb-1">{name}</h3>
    <span className="text-xs sm:text-sm font-bold text-accent uppercase tracking-widest mb-2">{role}</span>
    <p className="text-xs sm:text-sm text-ink-3 mb-4 leading-relaxed max-w-xs">{description}</p>
    <div className="opacity-40 group-hover:opacity-100 transition-opacity duration-300">
      <a href={linkedin} target="_blank" rel="noopener noreferrer" className="text-ink-3 hover:text-accent transition-colors duration-300">
        <Linkedin size={18} />
      </a>
    </div>
  </div>
);

const Team: React.FC = () => {
  const team = [
    {
      name: 'Mohit P. S. Rathore',
      role: 'Founder & CEO',
      description: 'Building OviGuide to fix the counselling mess he witnessed firsthand. Ex Co-founder HDYUAI & COO CollabClan.',
      image: '/Founder1.jpg',
      linkedin: 'https://www.linkedin.com/in/mohit-pratap-singh-rathore-428b0b27a/',
    },
    {
      name: 'Sriharsha Meduri',
      role: 'Founding Engineer',
      description: 'Building AI systems that turn rank data into confident decisions. Founder PhishingLens & Research Intern IIM Shillong.',
      image: '/Founder2.jpg',
      linkedin: 'https://www.linkedin.com/in/sriharsha-meduri/',
    },
  ];

  return (
    <section id="team" className="py-14 sm:py-20 md:py-28 bg-paper/70 backdrop-blur-md border-t border-white/10">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 md:px-12">
        {/* Section heading — fade-up */}
        <div className="text-center mb-12 md:mb-16 fade-up">
          <span className="text-sm font-bold tracking-widest uppercase text-accent mb-3 block">The Builders</span>
          <h2 className="text-3xl sm:text-4xl md:text-5xl font-black text-ink mb-4 leading-tight font-display">
            Meet the Team<br />
            <span className="text-ink-4">Behind OviGuide.</span>
          </h2>
          {/* Subheading — fade-up with delay */}
          <p className="text-base sm:text-lg text-ink-3 max-w-xl mx-auto fade-up fade-up-d1">
            Builders who've seen the broken counselling process up close and decided to fix it with AI and data.
          </p>
        </div>

        {/* Team cards — staggered fade-up on each card individually */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-5 sm:gap-6 md:gap-8 max-w-2xl mx-auto">
          {team.map((member, i) => (
            <div key={i} className={`fade-up fade-up-d${i + 1}`}>
              <TeamMember {...member} />
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default Team;
