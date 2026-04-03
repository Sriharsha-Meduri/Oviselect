import { useEffect } from 'react';

/**
 * Observes all scroll-reveal elements (.fade-up, .fade-left, .fade-right, .fade-scale)
 * and adds .is-visible once they enter the viewport. Each element animates once and is
 * then unobserved so the animation never resets on scroll-back.
 *
 * Call this hook once in the root App component.
 */
export function useScrollReveal(): void {
  useEffect(() => {
    const selector = '.fade-up, .fade-left, .fade-right, .fade-scale';

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add('is-visible');
            observer.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.1, rootMargin: '0px 0px -40px 0px' }
    );

    const elements = document.querySelectorAll(selector);
    elements.forEach((el) => observer.observe(el));

    return () => observer.disconnect();
  }, []);
}

