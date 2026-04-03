import React from 'react';
import { GoogleOAuthProvider } from '@react-oauth/google';
import { ShaderGradientCanvas, ShaderGradient } from '@shadergradient/react';
import { ThemeProvider } from './contexts/ThemeContext';
import { useScrollReveal } from './hooks/useScrollReveal';
import Navbar from './components/Navbar';
import Hero from './components/Hero';
import Benefits from './components/Benefits';
import HowItWorks from './components/HowItWorks';
import Features from './components/Features';
import About from './components/About';
import Team from './components/Team';
import FAQ from './components/FAQ';
import Footer from './components/Footer';

/** Catches WebGL/Three.js crashes so the rest of the app still renders. */
class ShaderErrorBoundary extends React.Component<
  { children: React.ReactNode },
  { hasError: boolean }
> {
  constructor(props: { children: React.ReactNode }) {
    super(props);
    this.state = { hasError: false };
  }
  static getDerivedStateFromError() {
    return { hasError: true };
  }
  render() {
    if (this.state.hasError) return null;
    return this.props.children;
  }
}

const App: React.FC = () => {
  useScrollReveal();

  const GOOGLE_CLIENT_ID = import.meta.env.VITE_GOOGLE_CLIENT_ID || '457690217048-4s9jvahgvk7dmfrsfrj19qfasbbb5gn5.apps.googleusercontent.com';

  return (
    <GoogleOAuthProvider clientId={GOOGLE_CLIENT_ID}>
    <ThemeProvider>
      {/* Fixed ShaderGradient background */}
      <ShaderErrorBoundary>
      <div style={{ position: 'fixed', inset: 0, zIndex: 0 }}>
        <ShaderGradientCanvas
          style={{ position: 'absolute', inset: 0, pointerEvents: 'none' }}
          pixelDensity={1}
          fov={45}
        >
          <ShaderGradient
            animate="on"
            brightness={0.8}
            cAzimuthAngle={270}
            cDistance={0.5}
            cPolarAngle={180}
            cameraZoom={15.1}
            color1="#73bfc4"
            color2="#ff810a"
            color3="#8da0ce"
            envPreset="city"
            grain="on"
            lightType="env"
            positionX={-0.1}
            positionY={0}
            positionZ={0}
            reflection={0.4}
            rotationX={0}
            rotationY={130}
            rotationZ={70}
            shader="defaults"
            type="sphere"
            uAmplitude={3.2}
            uDensity={0.8}
            uFrequency={5.5}
            uSpeed={0.3}
            uStrength={0.3}
            uTime={0}
            wireframe={false}
          />
        </ShaderGradientCanvas>
      </div>
      </ShaderErrorBoundary>

      {/* Page content above the gradient */}
      <div className="relative z-10 min-h-screen text-ink font-sans selection:bg-accent-light selection:text-accent transition-colors duration-300">
        <Navbar />
        <main>
          <Hero />
          <Benefits />
          <HowItWorks />
          <Features />
          <About />
          <Team />
          <FAQ />
        </main>
        <Footer />
      </div>
    </ThemeProvider>
    </GoogleOAuthProvider>
  );
};

export default App;
