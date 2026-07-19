import React from 'react';
import './LearningHeatmap.css';

export function LearningHeatmap({ data = [] }) {
  return (
    <div className="cf-heatmap-wrapper">
      <div className="cf-heatmap-header">
        <span className="cf-heatmap-title">30-Day Activity Heatmap</span>
        <div className="cf-heatmap-legend">
          <span>Less</span>
          <span className="cf-heat-cell cf-heat-0" />
          <span className="cf-heat-cell cf-heat-1" />
          <span className="cf-heat-cell cf-heat-2" />
          <span className="cf-heat-cell cf-heat-3" />
          <span className="cf-heat-cell cf-heat-4" />
          <span>More</span>
        </div>
      </div>

      <div className="cf-heatmap-grid">
        {data.map((item, idx) => (
          <div
            key={idx}
            className={`cf-heat-cell cf-heat-${item.intensity}`}
            title={`${item.date}: ${item.count} mins learned`}
          />
        ))}
      </div>
    </div>
  );
}
