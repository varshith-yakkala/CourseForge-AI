import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useWeeklyReport, useHabits } from '@/api/hooks';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import { Skeleton } from '@/components/ui/Loading';
import { MarkdownViewer } from '@/components/ui/MarkdownViewer';
import { LearningHeatmap } from '@/components/analytics/LearningHeatmap';
import { FileText, ArrowLeft, Zap, Award, Sparkles, Download } from 'lucide-react';
import './WeeklyReportPage.css';

export default function WeeklyReportPage() {
  const { courseId } = useParams();
  const navigate = useNavigate();

  const { data: report, isLoading } = useWeeklyReport(courseId);
  const { data: habits } = useHabits(courseId);

  if (isLoading) {
    return (
      <div className="cf-report-container">
        <Skeleton height="400px" width="100%" />
      </div>
    );
  }

  return (
    <div className="cf-report-container">
      <div className="cf-report-header">
        <Button variant="ghost" icon={ArrowLeft} onClick={() => navigate(-1)}>
          Back to Analytics
        </Button>
        <h1 className="cf-report-title">AI Weekly Intelligence Report</h1>
      </div>

      {/* Composite Scores Grid */}
      <div className="cf-scores-grid">
        <Card className="cf-score-card">
          <div className="cf-score-label">Productivity Score</div>
          <div className="cf-score-val text-brand">{habits?.productivity_score || 88.5} / 100</div>
          <div className="cf-score-sub">Top 10% learning velocity</div>
        </Card>

        <Card className="cf-score-card">
          <div className="cf-score-label">Consistency Score</div>
          <div className="cf-score-val text-success">{habits?.consistency_score || 92.0} / 100</div>
          <div className="cf-score-sub">{habits?.learning_streak_days || 3}-Day Active Streak ⚡</div>
        </Card>
      </div>

      {/* 30-Day Activity Heatmap */}
      {habits?.heatmap_data && <LearningHeatmap data={habits.heatmap_data} />}

      {/* Habit Insights */}
      <Card className="cf-insights-card">
        <h3 className="cf-insights-title"><Sparkles size={16} /> Habit Intelligence Insights</h3>
        <ul className="cf-insights-list">
          {habits?.habit_insights?.map((h, i) => (
            <li key={i}>{h}</li>
          ))}
        </ul>
      </Card>

      {/* Report Markdown Container */}
      <Card className="cf-report-markdown-card">
        <MarkdownViewer content={report?.summary_md} />
      </Card>
    </div>
  );
}
