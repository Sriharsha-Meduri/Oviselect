import React, { useState, useEffect } from 'react';
import { Menu, X, Target, LogOut } from 'lucide-react';
import CollegeSearch from './CollegeSearch';

const Navbar: React.FC = () => {
  const [isScrolled, setIsScrolled] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  useEffect(() => {
    const handleScroll = () => setIsScrolled(window.scrollY > 20);
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  // Check login state from localStorage
  useEffect(() => {
    const check = () => {
      try {
        const saved = localStorage.getItem('oviguide_user');
        setIsLoggedIn(!!saved && !!JSON.parse(saved)?.email);
      } catch { setIsLoggedIn(false); }
    };
    check();
    window.addEventListener('storage', check);
    window.addEventListener('oviguide-login', check);
    return () => {
      window.removeEventListener('storage', check);
      window.removeEventListener('oviguide-login', check);
    };
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('oviguide_user');
    setIsLoggedIn(false);
    window.dispatchEvent(new Event('oviguide-logout'));
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleLogoClick = (e: React.MouseEvent) => {
    e.preventDefault();
    if (isLoggedIn) {
      handleLogout();
    } else {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  };

  const links = [
    { label: 'How It Works', href: '#how-it-works' },
    { label: 'Features',     href: '#features'     },
    { label: 'About',        href: '#about-us'      },
    { label: 'Team',         href: '#team'          },
    { label: 'FAQ',          href: '#faq'           },
  ];

  return (
    <nav className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
      isScrolled
        ? 'bg-black/40 backdrop-blur-xl py-3 border-b border-white/10'
        : 'bg-transparent py-5'
    }`}>
      <div className="max-w-7xl mx-auto px-6 md:px-12 flex justify-between items-center">

        <a href="#" onClick={handleLogoClick} className="flex items-center gap-2.5 group cursor-pointer">
          <div className="w-7 h-7 bg-accent rounded-lg flex items-center justify-center shadow-md shadow-accent/25">
            <Target size={14} className="text-paper" />
          </div>
          <span className="text-lg font-semibold tracking-tight text-[#F5F0E8] font-display">
            Ovi<span className="text-white">Guide</span>
          </span>
        </a>

        <div className="hidden md:flex items-center gap-7">
          {links.map(({ label, href }) => (
            <a key={label} href={href}
              className="text-sm text-[#D4CFC8] hover:text-white transition-colors duration-200"
            >{label}</a>
          ))}
        </div>

        <div className="hidden md:flex items-center gap-3">
          <CollegeSearch isLoggedIn={isLoggedIn} />
          {isLoggedIn ? (
            <button
              onClick={handleLogout}
              className="flex items-center gap-2 bg-white/10 hover:bg-white/20 text-[#F5F0E8] px-4 py-2 rounded-full text-sm font-medium transition-all duration-200 border border-white/10"
            >
              <LogOut size={14} /> Logout
            </button>
          ) : (
            <button className="bg-white hover:bg-white/90 text-[#1a1a1a] px-5 py-2.5 rounded-full text-sm font-semibold transition-all duration-200 hover:-translate-y-px shadow-md shadow-white/20">
              Join Waitlist
            </button>
          )}
        </div>

        <div className="md:hidden flex items-center gap-2">
          <button onClick={() => setMobileMenuOpen(!mobileMenuOpen)} className="p-2 rounded-lg">
            {mobileMenuOpen ? <X size={20} className="text-[#F5F0E8]" /> : <Menu size={20} className="text-[#F5F0E8]" />}
          </button>
        </div>
      </div>

      {mobileMenuOpen && (
        <div className="md:hidden absolute top-full left-0 right-0 bg-black/80 backdrop-blur-xl border-b border-white/10 px-6 py-5 flex flex-col gap-1">
          {links.map(({ label, href }) => (
            <a key={label} href={href} onClick={() => setMobileMenuOpen(false)}
              className="py-2.5 text-sm text-[#D4CFC8] hover:text-white transition-colors"
            >{label}</a>
          ))}
          {isLoggedIn ? (
            <button onClick={() => { setMobileMenuOpen(false); handleLogout(); }} className="mt-3 w-full flex items-center justify-center gap-2 bg-white/10 text-[#F5F0E8] py-3 rounded-full text-sm font-medium border border-white/10">
              <LogOut size={14} /> Logout
            </button>
          ) : (
            <button className="mt-3 w-full bg-white text-[#1a1a1a] py-3 rounded-full text-sm font-semibold">
              Join Waitlist
            </button>
          )}
        </div>
      )}
    </nav>
  );
};

export default Navbar;