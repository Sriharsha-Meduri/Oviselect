import React from 'react';
import { Target } from 'lucide-react';

const Footer: React.FC = () => {
  return (
    <footer className="bg-black/60 backdrop-blur-xl text-[#F5F0E8] py-12 sm:py-16 md:py-20 rounded-t-2xl sm:rounded-t-[2.5rem] md:rounded-t-[3rem] mt-4 sm:mt-6 md:mt-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 md:px-12">

        {/* Top: CTA + Email — simple fade-up on footer inner content, no delay */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-12 sm:mb-16 fade-up">
          <div className="mb-8 md:mb-0">
            {/* Logo */}
            <div className="flex items-center gap-2.5 mb-4">
              <div className="w-8 h-8 bg-white rounded-lg flex items-center justify-center shadow-lg shadow-white/30">
                <Target size={16} className="text-[#1a1a1a]" />
              </div>
              <span className="text-xl font-bold tracking-tight font-display text-[#F5F0E8]">
                Ovi<span className="text-white">Guide</span>
              </span>
            </div>
            <p className="text-sm sm:text-base text-[#D4CFC8]/60 max-w-xs leading-relaxed">
              The AI counselling OS for engineering admissions in India. From rank to right college — intelligently.
            </p>
          </div>

          {/* Email Signup */}
          <div className="flex flex-col sm:flex-row gap-3 w-full md:w-auto">
            <input
              type="email"
              placeholder="Enter your email"
              className="bg-white/10 border border-white/10 rounded-full px-5 py-3 text-sm text-[#F5F0E8] placeholder-white/30 focus:outline-none focus:border-white transition-colors duration-300 w-full sm:w-80"
            />
            <button className="bg-white hover:bg-white/90 text-[#1a1a1a] px-7 py-3 rounded-full font-bold text-sm transition-all duration-300 hover:-translate-y-0.5 whitespace-nowrap shadow-lg shadow-white/20 hover:shadow-white/40">
              Join Waitlist
            </button>
          </div>
        </div>

        {/* Links Grid — fade-up */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6 sm:gap-8 md:gap-10 border-t border-white/10 pt-10 sm:pt-12 fade-up">
          <div>
            <h4 className="font-bold text-sm mb-4 sm:mb-5 text-[#F5F0E8]">Product</h4>
            <ul className="space-y-3 text-[#D4CFC8]/50 text-sm">
              <li><a href="#how-it-works" className="hover:text-white transition-colors duration-200">How It Works</a></li>
              <li><a href="#features" className="hover:text-white transition-colors duration-200">Features</a></li>
              <li><a href="#" className="hover:text-white transition-colors duration-200">Prediction Engine</a></li>
              <li><a href="#" className="hover:text-white transition-colors duration-200">Counselling Copilot</a></li>
            </ul>
          </div>
          <div>
            <h4 className="font-bold text-sm mb-4 sm:mb-5 text-[#F5F0E8]">Counselling</h4>
            <ul className="space-y-3 text-[#D4CFC8]/50 text-sm">
              <li><a href="#" className="hover:text-white transition-colors duration-200">JoSAA Guide</a></li>
              <li><a href="#" className="hover:text-white transition-colors duration-200">State CETs</a></li>
              <li><a href="#" className="hover:text-white transition-colors duration-200">COMEDK</a></li>
              <li><a href="#" className="hover:text-white transition-colors duration-200">WBJEE</a></li>
            </ul>
          </div>
          <div>
            <h4 className="font-bold text-sm mb-4 sm:mb-5 text-[#F5F0E8]">Company</h4>
            <ul className="space-y-3 text-[#D4CFC8]/50 text-sm">
              <li><a href="#about-us" className="hover:text-white transition-colors duration-200">About</a></li>
              <li><a href="#team" className="hover:text-white transition-colors duration-200">Team</a></li>
              <li><a href="#" className="hover:text-white transition-colors duration-200">Blog</a></li>
              <li><a href="#" className="hover:text-white transition-colors duration-200">Careers</a></li>
            </ul>
          </div>
          <div>
            <h4 className="font-bold text-sm mb-4 sm:mb-5 text-[#F5F0E8]">Legal</h4>
            <ul className="space-y-3 text-[#D4CFC8]/50 text-sm">
              <li><a href="#faq" className="hover:text-white transition-colors duration-200">FAQ</a></li>
              <li><a href="#" className="hover:text-white transition-colors duration-200">Privacy Policy</a></li>
              <li><a href="#" className="hover:text-white transition-colors duration-200">Terms of Service</a></li>
            </ul>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="mt-10 sm:mt-12 pt-6 border-t border-white/5 flex flex-col md:flex-row justify-between items-center text-[#D4CFC8]/30 text-xs sm:text-sm gap-3">
          <p>© 2026 OviGuide Inc. (by Team Oviqo). All rights reserved.</p>
          <div className="flex gap-5">
            <a href="https://www.linkedin.com/company/oviqo" target="_blank" rel="noopener noreferrer" className="hover:text-white transition-colors duration-200">LinkedIn</a>
            <a href="https://www.instagram.com/oviqo_/" target="_blank" rel="noopener noreferrer" className="hover:text-white transition-colors duration-200">Instagram</a>
            <a href="https://www.youtube.com/@Oviqolabs" target="_blank" rel="noopener noreferrer" className="hover:text-white transition-colors duration-200">YouTube</a>
          </div>
        </div>

      </div>
    </footer>
  );
};

export default Footer;
