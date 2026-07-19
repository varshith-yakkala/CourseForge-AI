import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  useAnalytics,
  useRecommendations,
  useUserAchievements,
  useExportSummary,
} from '@/api/hooks';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import { Skeleton } from '@/components/ui/Loading';
import { MarkdownViewer } from '@/components/ui/MarkdownViewer';
import { Modal } from '@/components/ui/Modal';
import {
  Award,
  Zap,
  Clock,
  BookOpen,
  CheckCircle2,
  AlertTriangle,
  Download,
  Sparkles,
  ArrowRight,
  TrendingUp,
  FileText,
} from 'lucide-react';
import './AnalyticsPage.css';

export default function AnalyticsPage() {
  const { courseId } = useParams();
  const navigate = useNavigate();

  const [isExportOpen, setIsExportOpen] = useState(false);

  const { data: analytics, isLoading: isAnalyticsLoading } = useAnalytics(courseId);
  const { data: recommendations, isLoading: isRecsLoading } = useRecommendations(courseId);
  const { data: achievements } = useUserAchievements();
  const { data: exportData, refetch: refetchExport, isFetching: isExporting } = useExportSummary(courseId);

  const handleExportClick = async () => {
    setIsExportOpen(true);
    refetchExport();
  };

  if (isAnalyticsLoading) {
    return (
      <div className="cf-analytics-container">
        <Skeleton height="40px" width="250px" style={{ marginBottom: '24px' }} />
        <Skeleton height="150px" width="100%" style={{ marginBottom: '24px' }} />
        <Skeleton height="200px" width="100%" />
      </div>
    );
  }

  return (
    <div className="cf-analytics-container">
      <div className="cf-analytics-header">
        <div>
          <h1 className="cf-analytics-title">Learning Analytics & Intelligence</h1>
          <p className="cf-analytics-sub">Performance metrics, streak tracking, and AI revision recommendations.</p>
        </div>

        <Button icon={Download} variant="outline" onClick={handleExportClick}>
          Export Summary Report
        </Button>
      </div>

      {/* Primary Metrics Grid */}
      <div className="cf-metrics-grid">
        <Card className="cf-metric-card">
          <div className="cf-metric-header">
            <BookOpen className="cf-metric-icon text-brand" size={20} />
            <span className="cf-metric-label">Progress Completion</span>
          </div>
          <div className="cf-metric-value">{analytics?.overall_progress_pct || 0}%</div>
          <div className="cf-metric-sub">{analytics?.completed_lessons || 0} of {analytics?.total_lessons || 0} Lessons Completed</div>
        </Card>

        <Card className="cf-metric-card">
          <div className="cf-metric-header">
            <Award className="cf-metric-icon text-warning" size={20} />
            <span className="cf-metric-label">Avg Quiz Score</span>
          </div>
          <div className="cf-metric-value">{analytics?.avg_quiz_score || 0}%</div>
          <div className="cf-metric-sub">{analytics?.passed_quizzes || 0} of {analytics?.total_quizzes || 0} Quizzes Passed</div>
        </Card>

        <Card className="cf-metric-card">
          <div className="cf-metric-header">
            <TrendingUp className="cf-metric-icon text-success" size={20} />
            <span className="cf-metric-label">Flashcard Mastery</span>
          </div>
          <div className="cf-metric-value">{analytics?.flashcard_retention_pct || 0}%</div>
          <div className="cf-metric-sub">{analytics?.mastered_flashcards || 0} of {analytics?.total_flashcards || 0} Cards Mastered</div>
        </Card>

        <Card className="cf-metric-card">
          <div className="cf-metric-header">
            <Zap className="cf-metric-icon text-danger" size={20} />
            <span className="cf-metric-label">Learning Streak</span>
          </div>
          <div className="cf-metric-value">{analytics?.learning_streak_days || 1} Days</div>
          <div className="cf-metric-sub">Active Daily Streak ⚡</div>
        </Card>
      </div>

      {/* AI Dynamic Revision Recommendations Panel */}
      <Card className="cf-recs-card">
        <div className="cf-recs-header">
          <Sparkles className="cf-brand-icon" size={20} />
          <h2 className="cf-recs-title">Personalized AI Revision Plan</h2>
        </div>

        <div className="cf-recs-list">
          {recommendations?.map((rec, idx) => (
            <div key={idx} className={`cf-rec-item cf-rec--${rec.priority}`}>
              <div className="cf-rec-info">
                <span className={`cf-priority-badge cf-priority--${rec.priority}`}>{rec.priority} Priority</span>
                <h4 className="cf-rec-item-title">{rec.title}</h4>
                <p className="cf-rec-reason">{rec.reason}</p>
              </div>

              <Button
                size="sm"
                variant="outline"
                icon={ArrowRight}
                onClick={() => navigate(rec.action_url)}
              >
                Start Revision
              </Button>
            </div>
          ))}
        </div>
      </Card>

      {/* Weak & Strong Topics */}
      <div className="cf-topics-grid">
        <Card className="cf-topic-box">
          <div className="cf-topic-box-header text-danger">
            <AlertTriangle size={18} /> <h3>Weak Topics Needing Practice</h3>
          </div>

          {!analytics?.weak_topics || analytics.weak_topics.length === 0 ? (
            <p className="cf-topic-empty">No weak topics identified! Outstanding performance.</p>
          ) : (
            <ul className="cf-topic-list">
              {analytics.weak_topics.map((wt, i) => (
                <li key={i} className="cf-topic-item">
                  <span>{wt.title}</span>
                  <span className="cf-badge-fail">{wt.score_pct}% Score</span>
                </li>
              ))}
            </ul>
          )}
        </Card>

        <Card className="cf-topic-box">
          <div className="cf-topic-box-header text-success">
            <CheckCircle2 size={18} /> <h3>Strong Topics Mastered</h3>
          </div>

          {!analytics?.strong_topics || analytics.strong_topics.length === 0 ? (
            <p className="cf-topic-empty">Complete more quizzes to unveil your strong topics.</p>
          ) : (
            <ul className="cf-topic-list">
              {analytics.strong_topics.map((st, i) => (
                <li key={i} className="cf-topic-item">
                  <span>{st.title}</span>
                  <span className="cf-badge-pass">{st.score_pct}% Score</span>
                </li>
              ))}
            </ul>
          )}
        </Card>
      </div>

      {/* Gamification Achievements Grid */}
      <div className="cf-achievements-section">
        <h2 className="cf-section-title">Unlocked Achievements & Badges</h2>
        <div className="cf-achievements-grid">
          {achievements?.map((badge) => (
            <Card key={badge.id} className="cf-badge-card">
              <div className="cf-badge-icon-wrapper">
                <Award size={24} className="cf-badge-award-icon" />
              </div>
              <div className="cf-badge-details">
                <h4 className="cf-badge-name">{badge.title}</h4>
                <p className="cf-badge-desc">{badge.description}</p>
              </div>
            </Card>
          ))}
        </div>
      </div>

      {/* Export Summary Modal */}
      <Modal isOpen={isExportOpen} onClose={() => setIsExportOpen(false)} title="Export Learning Summary Report">
        {isExporting ? (
          <Skeleton height="200px" width="100%" />
        ) : (
          <div>
            <div className="cf-export-preview">
              <MarkdownViewer content={exportData?.markdown_content} />
            </div>
            <div style={{ marginTop: '16px', display: 'flex', justifyContent: 'flex-end', gap: '8px' }}>
              <Button variant="outline" onClick={() => setIsExportOpen(false)}>Close</Button>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
}
