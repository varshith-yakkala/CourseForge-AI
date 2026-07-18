import React from 'react';
import { Card } from '@/components/ui/Card';

export default function AnalyticsPage() {
  return (
    <div>
      <h1 className="text-heading-lg" style={{ marginBottom: 'var(--space-6)' }}>Analytics</h1>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 'var(--space-4)' }}>
        <Card>
          <div className="text-label-md text-secondary">Courses Completed</div>
          <div className="text-display-lg">0</div>
        </Card>
        <Card>
          <div className="text-label-md text-secondary">Quizzes Passed</div>
          <div className="text-display-lg">0</div>
        </Card>
        <Card>
          <div className="text-label-md text-secondary">Study Time (hrs)</div>
          <div className="text-display-lg">0</div>
        </Card>
      </div>
    </div>
  );
}
