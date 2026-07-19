import React from 'react';
import { Link } from 'react-router-dom';
import { Clock, RefreshCw, MessageSquare, CheckCircle, Sparkles } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import './LessonHeader.css';

export function LessonHeader({
  course,
  lesson,
  progress,
  onRegenerate,
  isRegenerating,
  onOpenTutor,
}) {
  const isCompleted = progress?.completed;
  const progressPercent = progress?.completion_percentage || (isCompleted ? 100 : 0);

  return (
    <header className="cf-lesson-header">
      <div className="cf-lesson-header-top">
        <nav className="cf-lesson-breadcrumbs" aria-label="Breadcrumb">
          <Link to="/courses">Courses</Link>
          <span className="cf-breadcrumb-sep">/</span>
          <Link to={`/courses/${course?.id}`}>{course?.title || 'Course'}</Link>
          <span className="cf-breadcrumb-sep">/</span>
          <span className="cf-breadcrumb-current">{lesson?.title || 'Lesson'}</span>
        </nav>

        <div className="cf-lesson-header-actions">
          <Button
            variant="outline"
            size="sm"
            icon={MessageSquare}
            onClick={onOpenTutor}
          >
            Ask AI Tutor
          </Button>

          {lesson?.status === 'ready' && (
            <Button
              variant="ghost"
              size="sm"
              icon={RefreshCw}
              onClick={onRegenerate}
              isLoading={isRegenerating}
              title={`Version ${lesson.version || 1}. Click to regenerate.`}
            >
              v{lesson.version || 1} Regenerate
            </Button>
          )}
        </div>
      </div>

      <div className="cf-lesson-header-main">
        <h1 className="cf-lesson-title">{lesson?.title}</h1>
        <div className="cf-lesson-meta">
          <span className="cf-lesson-badge">
            <Clock size={14} /> {lesson?.estimated_duration_min || 15} min read
          </span>
          {isCompleted ? (
            <span className="cf-lesson-badge cf-badge-success">
              <CheckCircle size={14} /> Completed
            </span>
          ) : (
            <span className="cf-lesson-badge cf-badge-info">
              <Sparkles size={14} /> Interactive Lesson
            </span>
          )}
        </div>
      </div>

      <div className="cf-lesson-progress-container">
        <div className="cf-lesson-progress-bar">
          <div
            className="cf-lesson-progress-fill"
            style={{ width: `${progressPercent}%` }}
          />
        </div>
        <span className="cf-lesson-progress-text">{progressPercent}% Completed</span>
      </div>
    </header>
  );
}
