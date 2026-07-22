import React, { useState, useEffect, useMemo } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  useLesson,
  useCourse,
  useCourseStructure,
  useCourseProgress,
  useUpdateProgress,
  useRegenerateLesson,
} from '@/api/hooks';
import { MarkdownViewer } from '@/components/ui/MarkdownViewer';
import { LessonSidebar } from '@/components/lesson/LessonSidebar';
import { LessonHeader } from '@/components/lesson/LessonHeader';
import { LessonTutorPanel } from '@/components/lesson/LessonTutorPanel';
import { Skeleton } from '@/components/ui/Loading';
import { EmptyState } from '@/components/ui/States';
import { Button } from '@/components/ui/Button';
import { useNotificationStore } from '@/store/useNotificationStore';
import { extractApiError } from '@/utils/errorUtils';
import {
  ChevronLeft,
  ChevronRight,
  CheckCircle,
  AlertCircle,
  RefreshCw,
  Play,
  List,
} from 'lucide-react';
import './LessonViewerPage.css';

export default function LessonViewerPage() {
  const { courseId, lessonId } = useParams();
  const navigate = useNavigate();
  const addNotification = useNotificationStore((s) => s.addNotification);

  const { data: course } = useCourse(courseId);
  const { data: structure } = useCourseStructure(courseId);
  const { data: progressOverview } = useCourseProgress(courseId);
  const {
    data: lesson,
    isLoading: lessonLoading,
    isError: lessonError,
    refetch: refetchLesson,
  } = useLesson(courseId, lessonId);

  const updateProgress = useUpdateProgress();
  const regenerateLesson = useRegenerateLesson();

  const [isTutorOpen, setIsTutorOpen] = useState(false);
  const [startTime] = useState(Date.now());

  // Map progress entries by lesson_id for quick lookup in sidebar
  const progressMap = useMemo(() => {
    if (!progressOverview?.lessons_progress) return {};
    return progressOverview.lessons_progress.reduce((acc, p) => {
      if (p.lesson_id) acc[p.lesson_id] = p;
      return acc;
    }, {});
  }, [progressOverview]);

  const currentLessonProgress = progressMap[lessonId];

  // Derive previous and next lessons for bottom navigation
  const { prevLesson, nextLesson } = useMemo(() => {
    if (!structure?.lessons) return { prevLesson: null, nextLesson: null };
    const currentIndex = structure.lessons.findIndex((l) => l.id === lessonId);
    if (currentIndex === -1) return { prevLesson: null, nextLesson: null };

    return {
      prevLesson: currentIndex > 0 ? structure.lessons[currentIndex - 1] : null,
      nextLesson:
        currentIndex < structure.lessons.length - 1
          ? structure.lessons[currentIndex + 1]
          : null,
    };
  }, [structure, lessonId]);

  // Extract Table of Contents headings from Markdown content
  const tableOfContents = useMemo(() => {
    if (!lesson?.content_markdown) return [];
    const lines = lesson.content_markdown.split('\n');
    const headings = [];
    lines.forEach((line) => {
      if (line.startsWith('## ')) {
        const text = line.replace('## ', '').trim();
        headings.push({ level: 2, text, id: text.toLowerCase().replace(/[^\w]+/g, '-') });
      }
    });
    return headings;
  }, [lesson?.content_markdown]);

  // Track lesson open and time spent
  useEffect(() => {
    if (courseId && lessonId) {
      updateProgress.mutate({
        courseId,
        lessonId,
        progressData: {
          status: 'in_progress',
          completed: false,
          completion_percentage: currentLessonProgress?.completed ? 100 : 50,
          time_spent_sec: 10,
        },
      });
    }
  }, [courseId, lessonId]);

  const handleMarkComplete = async () => {
    try {
      await updateProgress.mutateAsync({
        courseId,
        lessonId,
        progressData: {
          status: 'completed',
          completed: true,
          completion_percentage: 100,
          time_spent_sec: Math.round((Date.now() - startTime) / 1000),
        },
      });
      addNotification({
        title: 'Lesson Completed!',
        message: 'Great job! Progress updated.',
        type: 'success',
      });

      if (nextLesson) {
        navigate(`/learn/${courseId}/${nextLesson.id}`);
      }
    } catch (err) {
      addNotification({
        title: 'Update Failed',
        message: extractApiError(err),
        type: 'error',
      });
    }
  };

  const handleRegenerate = async () => {
    try {
      await regenerateLesson.mutateAsync({ courseId, lessonId });
      addNotification({
        title: 'Regeneration Started',
        message: 'Generating new lesson version...',
        type: 'info',
      });
    } catch (err) {
      addNotification({
        title: 'Regeneration Failed',
        message: extractApiError(err),
        type: 'error',
      });
    }
  };

  const handleGenerateClick = async () => {
    refetchLesson();
  };

  return (
    <div className="cf-lesson-viewer-layout">
      {/* Left Navigation Sidebar */}
      <LessonSidebar structure={structure} progressMap={progressMap} />

      {/* Main Content Area */}
      <main className="cf-lesson-viewer-main">
        <div className="cf-lesson-viewer-container">
          <LessonHeader
            course={course}
            lesson={lesson}
            progress={currentLessonProgress}
            onRegenerate={handleRegenerate}
            isRegenerating={regenerateLesson.isPending}
            onOpenTutor={() => setIsTutorOpen(true)}
          />

          {/* Lifecycle State: LOADING SKELETON */}
          {lessonLoading && (
            <div className="cf-lesson-skeleton">
              <Skeleton height="32px" width="60%" style={{ marginBottom: '16px' }} />
              <Skeleton height="20px" width="40%" style={{ marginBottom: '32px' }} />
              <Skeleton height="200px" width="100%" style={{ marginBottom: '24px' }} />
              <Skeleton height="150px" width="100%" />
            </div>
          )}

          {/* Lifecycle State: ERROR */}
          {!lessonLoading && (lessonError || lesson?.status === 'failed') && (
            <div className="cf-lesson-error-card">
              <AlertCircle size={32} className="cf-error-icon" />
              <h3>Lesson Generation Failed</h3>
              <p>{lesson?.generation_error || 'An error occurred while generating this lesson.'}</p>
              <Button icon={RefreshCw} onClick={handleRegenerate} isLoading={regenerateLesson.isPending}>
                Retry Generation
              </Button>
            </div>
          )}

          {/* Lifecycle State: PENDING */}
          {!lessonLoading && lesson?.status === 'pending' && (
            <div className="cf-lesson-pending-card">
              <Play size={40} className="cf-brand-icon" />
              <h2>Ready to Learn "{lesson.title}"?</h2>
              <p>Click below to generate this interactive lesson on-demand using AI & RAG context.</p>
              <Button icon={Play} size="lg" onClick={handleGenerateClick}>
                Generate Lesson Content
              </Button>
            </div>
          )}

          {/* Lifecycle State: GENERATING */}
          {!lessonLoading && lesson?.status === 'generating' && (
            <div className="cf-lesson-generating-card">
              <RefreshCw size={40} className="cf-spin-icon text-brand" />
              <h2>Generating Lesson Content...</h2>
              <p>CourseForge is retrieving PDF context and synthesizing your custom lesson.</p>
              <Skeleton height="180px" width="100%" style={{ marginTop: '24px' }} />
            </div>
          )}

          {/* Lifecycle State: READY (RENDER MARKDOWN) */}
          {!lessonLoading && lesson?.status === 'ready' && lesson?.content_markdown && (
            <div className="cf-lesson-content-grid">
              <article className="cf-lesson-article">
                <MarkdownViewer content={lesson.content_markdown} />
              </article>

              {/* Table of Contents Sidebar */}
              {tableOfContents.length > 0 && (
                <aside className="cf-lesson-toc">
                  <div className="cf-toc-header">
                    <List size={16} /> <span>Table of Contents</span>
                  </div>
                  <ul className="cf-toc-list">
                    {tableOfContents.map((h, i) => (
                      <li key={i} className="cf-toc-item">
                        <a href={`#${h.id}`}>{h.text}</a>
                      </li>
                    ))}
                  </ul>
                </aside>
              )}
            </div>
          )}

          {/* Footer Navigation Controls */}
          <footer className="cf-lesson-footer">
            <div>
              {prevLesson && (
                <Button
                  variant="outline"
                  icon={ChevronLeft}
                  onClick={() => navigate(`/learn/${courseId}/${prevLesson.id}`)}
                >
                  Previous: {prevLesson.title}
                </Button>
              )}
            </div>

            <div className="cf-lesson-footer-right">
              <Button
                variant="primary"
                icon={CheckCircle}
                onClick={handleMarkComplete}
                isLoading={updateProgress.isPending}
              >
                {currentLessonProgress?.completed ? 'Marked Completed' : 'Complete & Continue'}
              </Button>

              {nextLesson && (
                <Button
                  variant="secondary"
                  onClick={() => navigate(`/learn/${courseId}/${nextLesson.id}`)}
                >
                  Next Lesson <ChevronRight size={16} />
                </Button>
              )}
            </div>
          </footer>
        </div>
      </main>

      {/* Scoped AI Tutor Slide-Over Panel */}
      <LessonTutorPanel
        isOpen={isTutorOpen}
        onClose={() => setIsTutorOpen(false)}
        courseId={courseId}
        lessonId={lessonId}
        lessonTitle={lesson?.title}
      />
    </div>
  );
}
