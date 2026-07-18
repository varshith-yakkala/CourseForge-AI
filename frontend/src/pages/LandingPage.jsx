import React from 'react';
import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/Button';
import { Footer } from '@/components/layout/Footer';

export default function LandingPage() {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      <main style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: 'var(--space-8)', textAlign: 'center' }}>
        <h1 className="text-display-lg" style={{ marginBottom: 'var(--space-4)' }}>CourseForge AI</h1>
        <p className="text-body-xl text-secondary" style={{ maxWidth: 600, marginBottom: 'var(--space-8)' }}>
          Transform any PDF into an interactive learning course with AI.
        </p>
        <div style={{ display: 'flex', gap: 'var(--space-4)' }}>
          <Link to="/register"><Button size="lg">Get Started</Button></Link>
          <Link to="/login"><Button variant="secondary" size="lg">Log In</Button></Link>
        </div>
      </main>
      <Footer />
    </div>
  );
}
