import React from 'react';

export default function LessonViewerPage() {
  return (
    <div className="reading-container">
      <h1 className="text-display-xl" style={{ marginBottom: 'var(--space-6)' }}>Lesson Title</h1>
      <div className="text-body-xl" style={{ color: 'var(--text-secondary)' }}>
        <p>This is where the lesson content generated from the PDF will be rendered.</p>
        <p>The reading container restricts the line width to roughly 68 characters for optimal reading experience, as defined in the layout guidelines.</p>
      </div>
    </div>
  );
}
