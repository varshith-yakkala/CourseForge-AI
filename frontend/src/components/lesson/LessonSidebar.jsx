import React from 'react';
import { Link, useParams } from 'react-router-dom';
import { CheckCircle2, Circle, Clock, ChevronRight, BookOpen } from 'lucide-react';
import './LessonSidebar.css';

export function LessonSidebar({ structure, progressMap = {} }) {
  const { courseId, lessonId } = useParams();

  if (!structure || !structure.lessons) return null;

  return (
    <aside className="cf-lesson-sidebar">
      <div className="cf-lesson-sidebar-header">
        <Link to={`/courses/${courseId}`} className="cf-lesson-sidebar-back">
          &larr; Back to Course Overview
        </Link>
        <h2 className="cf-lesson-sidebar-title">{structure.course_title || 'Course Contents'}</h2>
      </div>

      <nav className="cf-lesson-sidebar-nav">
        {structure.lessons.map((lesson, index) => {
          const isActive = lesson.id === lessonId;
          const isCompleted = progressMap[lesson.id]?.completed;
          const isGenerating = lesson.status === 'generating';

          return (
            <div key={lesson.id} className="cf-sidebar-lesson-group">
              <Link
                to={`/learn/${courseId}/${lesson.id}`}
                className={`cf-sidebar-lesson-link ${isActive ? 'cf-sidebar-lesson-link--active' : ''}`}
              >
                <div className="cf-sidebar-lesson-status">
                  {isCompleted ? (
                    <CheckCircle2 size={18} className="cf-icon-completed" />
                  ) : (
                    <Circle size={18} className="cf-icon-pending" />
                  )}
                </div>
                <div className="cf-sidebar-lesson-info">
                  <span className="cf-sidebar-lesson-num">Lesson {index + 1}</span>
                  <span className="cf-sidebar-lesson-name">{lesson.title}</span>
                </div>
                {isActive && <ChevronRight size={16} className="cf-sidebar-active-indicator" />}
              </Link>

              {isActive && lesson.topics && lesson.topics.length > 0 && (
                <div className="cf-sidebar-topic-list">
                  {lesson.topics.map((t, tIdx) => (
                    <div key={t.id} className="cf-sidebar-topic-item">
                      <span className="cf-sidebar-topic-dot">•</span>
                      <span className="cf-sidebar-topic-title">{t.title}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          );
        })}
      </nav>
    </aside>
  );
}
