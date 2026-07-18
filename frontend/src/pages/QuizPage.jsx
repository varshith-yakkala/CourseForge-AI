import React from 'react';
import { Button } from '@/components/ui/Button';

export default function QuizPage() {
  return (
    <div style={{ maxWidth: 600, margin: '0 auto', textAlign: 'center' }}>
      <h2 className="text-heading-md" style={{ marginBottom: 'var(--space-8)' }}>Question 1 of 10</h2>
      <div style={{ marginBottom: 'var(--space-8)', fontSize: '1.25rem' }}>
        What is the primary function of the mitochondria in a cell?
      </div>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
        <Button variant="secondary" size="lg">Protein synthesis</Button>
        <Button variant="secondary" size="lg">Energy production</Button>
        <Button variant="secondary" size="lg">Cell division</Button>
        <Button variant="secondary" size="lg">Waste processing</Button>
      </div>
    </div>
  );
}
