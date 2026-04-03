import React, { useState } from 'react';
import { ChevronDown } from 'lucide-react';

interface FAQItemProps {
  question: string;
  answer: string;
  isOpen: boolean;
  onClick: () => void;
  index: number;
}

const FAQItem: React.FC<FAQItemProps> = ({ question, answer, isOpen, onClick, index }) => (
  <div className="border-b border-white/10 last:border-b-0">
    <button
      onClick={onClick}
      className="w-full py-5 sm:py-6 flex items-center justify-between text-left group"
    >
      <div className="flex items-start gap-4 pr-4">
        <span className="text-xs font-black text-accent/60 mt-1 flex-shrink-0 tabular-nums">
          {String(index + 1).padStart(2, '0')}
        </span>
        <h3 className="text-base sm:text-lg font-bold text-ink group-hover:text-accent transition-colors duration-200 leading-snug">
          {question}
        </h3>
      </div>
      <div className={`flex-shrink-0 w-8 h-8 sm:w-9 sm:h-9 rounded-full flex items-center justify-center transition-all duration-300 ${
        isOpen
          ? 'bg-white text-[#1a1a1a] rotate-180'
          : 'bg-white/10 group-hover:bg-white/15'
      }`}>
        <ChevronDown size={16} className={isOpen ? 'text-[#1a1a1a]' : 'text-[#D4CFC8] group-hover:text-white'} />
      </div>
    </button>
    <div className={`overflow-hidden transition-all duration-500 ease-out ${isOpen ? 'max-h-96 pb-5 sm:pb-6' : 'max-h-0'}`}>
      <p className="text-sm sm:text-base text-ink-3 leading-relaxed pl-9 sm:pl-10 pr-4 sm:pr-12">
        {answer}
      </p>
    </div>
  </div>
);

const FAQ: React.FC = () => {
  const [openIndex, setOpenIndex] = useState<number | null>(0);

  const faqs = [
    {
      question: 'Which exams and counselling processes does OviGuide support?',
      answer: 'OviGuide currently supports JoSAA (JEE Main + Advanced), and is expanding rapidly to cover state CETs including MHT CET, AP EAMCET, TS EAMCET, WBJEE, KCET, and COMEDK. All major counselling systems will be unified in one dashboard.',
    },
    {
      question: 'How accurate are OviGuide\'s college admission predictions?',
      answer: 'Our Prediction Engine is trained on 5+ years of historical JoSAA and state CET cutoff data, with 99.1% accuracy on historical matches. We combine probabilistic modeling with round-wise seat availability, category adjustments, and real-time cutoff trends — far more accurate than static cutoff tables.',
    },
    {
      question: 'What does "Freeze, Float, or Slide" mean, and how does OviGuide help?',
      answer: 'These are the three options available to students after each JoSAA allotment round. "Freeze" means you accept your current seat and exit. "Float" means you keep your seat but want an upgrade. "Slide" means you\'re willing to slide to a different institute you prefer. OviGuide\'s Copilot analyzes your specific situation — current seat, upgrade probabilities, risk tolerance — and recommends the best action with clear reasoning.',
    },
    {
      question: 'Is OviGuide useful even if I haven\'t received my JEE results yet?',
      answer: 'Absolutely. You can use OviGuide\'s Scenario Simulator to explore "what if" scenarios by entering estimated ranks before results. This helps you prepare your choice strategy in advance so you\'re not scrambling during the tight counselling window after results are declared.',
    },
    {
      question: 'How does the Truth Engine differ from regular college review sites?',
      answer: 'Regular review sites show curated or biased testimonials. OviGuide\'s Truth Engine aggregates real, unfiltered signals from Reddit threads, LinkedIn posts, Discord servers, anonymous student reports, and placement PDFs — then uses NLP to summarize the consensus view. You get the honest picture: coding culture strength, placement realities, hostel life, and more.',
    },
    {
      question: 'Is OviGuide free to use?',
      answer: 'OviGuide is currently in its pre-launch phase. Early waitlist members will get priority access and exclusive benefits when we launch. We plan to offer a free tier covering core predictions and a premium tier for full optimization, Copilot guidance, and advanced insight access.',
    },
  ];

  return (
    <section id="faq" className="py-14 sm:py-20 md:py-28 bg-paper-2/70 backdrop-blur-md">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 md:px-12">

        {/* Header — section heading gets fade-up */}
        <div className="text-center mb-12 md:mb-16">
          <span className="text-xs sm:text-sm font-bold tracking-widest uppercase text-accent mb-3 block fade-up">Got Questions?</span>
          <h2 className="text-3xl sm:text-4xl md:text-5xl font-black text-ink mb-5 leading-tight font-display fade-up fade-up-d1">
            Frequently Asked<br />
            <span className="text-ink-4">Questions.</span>
          </h2>
          {/* Subheading — fade-up with delay */}
          <p className="text-base sm:text-lg text-ink-3 max-w-xl mx-auto fade-up fade-up-d2">
            Everything you need to know about OviGuide and how it can transform your counselling experience.
          </p>
        </div>

        {/* FAQs — fade-up on the card block */}
        <div className="bg-black/30 border border-white/10 rounded-3xl p-5 sm:p-8 md:p-10 shadow-sm fade-up fade-up-d3 backdrop-blur-sm">
          {faqs.map((faq, i) => (
            <FAQItem
              key={i}
              index={i}
              question={faq.question}
              answer={faq.answer}
              isOpen={openIndex === i}
              onClick={() => setOpenIndex(openIndex === i ? null : i)}
            />
          ))}
        </div>

        {/* Contact CTA — simple fade-up */}
        <div className="text-center mt-10 md:mt-12 fade-up">
          <p className="text-sm sm:text-base text-ink-3 mb-3">
            Still have questions? We love hearing from students.
          </p>
          <button className="text-sm sm:text-base text-accent font-bold hover:underline transition-all duration-300">
            Contact us →
          </button>
        </div>

      </div>
    </section>
  );
};

export default FAQ;
