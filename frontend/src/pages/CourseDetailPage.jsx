import React, { useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { Tabs } from '@/components/ui/Tabs';
import { useCourse, useDeleteCourse, useCourseDocument, useRetryDocument, useSearch, useGenerateCourse, useCourseStructure } from '@/api/hooks';
import { Skeleton } from '@/components/ui/Loading';
import { EmptyState } from '@/components/ui/States';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Trash2, AlertCircle, RefreshCw, Search, FileText, Play, Layers, TrendingUp } from 'lucide-react';
import { useNotificationStore } from '@/store/useNotificationStore';
import { extractApiError } from '@/utils/errorUtils';

import { QuizModal } from '@/components/QuizModal';
import { HelpCircle, Sparkles, ChevronDown, ChevronUp } from 'lucide-react';

function CourseStructure({ courseId, onOpenQuiz, onGenerate, isGenerating }) {
  const { data: structure, isLoading } = useCourseStructure(courseId);
  
  if (isLoading) return <Skeleton height="200px" />;
  if (!structure || structure.lessons.length === 0) {
    return (
      <div style={{ padding: '36px', textAlign: 'center', background: 'var(--bg-secondary)', borderRadius: '12px', border: '1px solid var(--border-default)', margin: '16px 0' }}>
        <Play size={44} style={{ color: '#38bdf8', marginBottom: '12px' }} />
        <h3 className="text-heading-md" style={{ marginBottom: '8px' }}>Course Blueprint Ready To Generate!</h3>
        <p className="text-body-sm text-secondary" style={{ marginBottom: '24px', maxWidth: '500px', margin: '0 auto 24px auto' }}>
          Your uploaded PDF has been successfully indexed into the RAG store. Click below to synthesize custom lessons, topics, and interactive quizzes!
        </p>
        <Button variant="primary" icon={Play} size="lg" onClick={onGenerate} isLoading={isGenerating}>
          Generate Course Blueprint
        </Button>
      </div>
    );
  }

  
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-6)' }}>
      {structure.lessons.map(lesson => (
        <div key={lesson.id} style={{ padding: 'var(--space-6)', border: '1px solid var(--border-default)', borderRadius: 'var(--radius-lg)', background: 'var(--bg-secondary)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 'var(--space-2)' }}>
            <h3 className="text-heading-md">Lesson {lesson.order_index + 1}: {lesson.title}</h3>
            <div style={{ display: 'flex', gap: '8px' }}>
              <Button icon={HelpCircle} variant="outline" size="sm" onClick={() => onOpenQuiz(lesson)}>
                Take Quiz
              </Button>
              <Link to={`/learn/${courseId}/${lesson.id}`}>
                <Button icon={Play} size="sm">Start Lesson</Button>
              </Link>
            </div>
          </div>
          <p className="text-body-md text-secondary" style={{ marginBottom: 'var(--space-4)' }}>{lesson.summary}</p>
          
          <div style={{ paddingLeft: 'var(--space-6)', borderLeft: '2px solid var(--border-default)' }}>
            {lesson.topics.map(topic => (
              <div key={topic.id} style={{ marginBottom: 'var(--space-4)' }}>
                <h4 className="text-heading-sm" style={{ marginBottom: 'var(--space-1)' }}>{topic.title}</h4>
                <p className="text-body-sm text-secondary">{topic.content}</p>
                {topic.subtopics && topic.subtopics.length > 0 && (
                  <ul style={{ marginTop: 'var(--space-2)', paddingLeft: 'var(--space-4)', listStyleType: 'circle' }}>
                    {topic.subtopics.map(sub => (
                      <li key={sub.id} className="text-body-sm">{sub.title}</li>
                    ))}
                  </ul>
                )}
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}


export default function CourseDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { data: course, isLoading: courseLoading, isError: courseError } = useCourse(id);
  const { data: document, isLoading: docLoading } = useCourseDocument(id);
  
  const deleteCourse = useDeleteCourse();
  const retryDocument = useRetryDocument();
  const searchApi = useSearch();
  const generateCourse = useGenerateCourse();
  const addNotification = useNotificationStore(s => s.addNotification);
  
  const [searchQuery, setSearchQuery] = useState('');
  const [aiSearchResult, setAiSearchResult] = useState(null);
  const [isSearching, setIsSearching] = useState(false);
  const [showSources, setShowSources] = useState(false);
  const [activeTab, setActiveTab] = useState('lessons');
  const [quizLesson, setQuizLesson] = useState(null);

  const handleDelete = async () => {
    if (window.confirm('Are you sure you want to delete this course?')) {
      try {
        await deleteCourse.mutateAsync(id);
        addNotification({ title: 'Course deleted', message: 'The course has been removed.', type: 'success' });
        navigate('/courses');
      } catch (error) {
        addNotification({ title: 'Delete failed', message: extractApiError(error), type: 'error' });
      }
    }
  };
  
  const handleRetry = async () => {
    if (!document) return;
    try {
      await retryDocument.mutateAsync(document.id);
      addNotification({ title: 'Indexing retried', message: 'The document has been re-queued for indexing.', type: 'info' });
    } catch (error) {
      addNotification({ title: 'Retry failed', message: extractApiError(error), type: 'error' });
    }
  };
  
  const handleGenerate = async () => {
    try {
      await generateCourse.mutateAsync(id);
      addNotification({ title: 'Generation Started', message: 'The course blueprint is being generated.', type: 'info' });
    } catch (error) {
      addNotification({ title: 'Generation failed', message: extractApiError(error), type: 'error' });
    }
  };
  
  const handleSearch = async (e) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;
    setIsSearching(true);
    setAiSearchResult(null);
    try {
      const { searchApi: searchServiceApi } = await import('@/api/services');
      const res = await searchServiceApi.aiSearch(searchQuery.trim(), id);
      setAiSearchResult(res);
    } catch (error) {
      addNotification({ title: 'AI Search failed', message: extractApiError(error), type: 'error' });
    } finally {
      setIsSearching(false);
    }
  };

  if (courseLoading) {
    return (
      <div>
        <Skeleton height="40px" width="50%" style={{ marginBottom: 'var(--space-4)' }} />
        <Skeleton height="20px" width="30%" style={{ marginBottom: 'var(--space-8)' }} />
        <Skeleton height="300px" width="100%" />
      </div>
    );
  }

  if (courseError || !course) {
    return <EmptyState title="Course not found" description="The requested course could not be loaded." />;
  }
  
  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 'var(--space-6)' }}>
        <div>
          <h1 className="text-heading-lg" style={{ marginBottom: 'var(--space-2)' }}>{course.title}</h1>
          <p className="text-body-md text-secondary">{course.description || 'No description available.'}</p>
        </div>
        <div style={{ display: 'flex', gap: 'var(--space-3)' }}>
          <Button variant="outline" icon={FileText} onClick={() => {
            const input = document.createElement('input');
            input.type = 'file';
            input.accept = 'application/pdf';
            input.onchange = async (e) => {
              const file = e.target.files[0];
              if (file) {
                try {
                  const { documentsApi } = await import('@/api/services');
                  await documentsApi.upload(id, file);
                  addNotification({ title: 'PDF Uploaded', message: 'New document added and indexed into course RAG store.', type: 'success' });
                  window.location.reload();
                } catch (err) {
                  addNotification({ title: 'Upload failed', message: extractApiError(err), type: 'error' });
                }
              }
            };
            input.click();
          }}>
            Add Document
          </Button>
          <Link to={`/flashcards/${id}`}>
            <Button variant="outline" icon={Layers}>Flashcards</Button>
          </Link>
          <Link to={`/analytics/${id}`}>
            <Button variant="outline" icon={TrendingUp}>Analytics</Button>
          </Link>
          {document && document.index_status === 'ready' && (
            <Button variant="primary" icon={Play} onClick={handleGenerate} isLoading={generateCourse.isPending}>
              Generate Course Blueprint
            </Button>
          )}
          <Button variant="danger" icon={Trash2} onClick={handleDelete} isLoading={deleteCourse.isPending}>
            Delete
          </Button>
        </div>
      </div>

      <div style={{ display: 'flex', gap: 'var(--space-4)', marginBottom: 'var(--space-8)' }}>
        <span className="text-body-sm text-secondary">Course Status: <strong>{course.status}</strong></span>
        <span className="text-body-sm text-secondary">Difficulty: <strong>{course.difficulty || 'TBD'}</strong></span>
        <span className="text-body-sm text-secondary">Duration: <strong>{course.estimated_duration_min ? `${course.estimated_duration_min} mins` : 'TBD'}</strong></span>
        {document && (
          <span className="text-body-sm text-secondary" style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
            Doc Status: 
            {document.index_status === 'ready' && <span className="text-brand">Indexed</span>}
            {(document.index_status === 'pending' || document.index_status === 'processing') && <span className="text-warning">Indexing...</span>}
            {document.index_status === 'error' && <span style={{ color: 'var(--color-danger)' }}>Failed</span>}
            {document.index_status === 'error' && (
              <Button size="sm" variant="outline" icon={RefreshCw} onClick={handleRetry} isLoading={retryDocument.isPending}>
                Retry
              </Button>
            )}
          </span>
        )}
      </div>

      {/* AI Synthesized Search Form */}
      {document && document.index_status === 'ready' && (
        <div style={{ marginBottom: 'var(--space-8)' }}>
          <form onSubmit={handleSearch} style={{ display: 'flex', gap: 'var(--space-4)', marginBottom: 'var(--space-6)' }}>
            <div style={{ flex: 1 }}>
              <Input 
                placeholder="Ask Course AI anything about your PDFs (Synthesized LLM Answer)..." 
                value={searchQuery}
                onChange={e => setSearchQuery(e.target.value)}
              />
            </div>
            <Button type="submit" icon={Sparkles} isLoading={isSearching}>Ask AI</Button>
          </form>

          {aiSearchResult && (
            <div style={{ background: 'var(--bg-secondary)', border: '1px solid var(--border-default)', borderRadius: 'var(--radius-lg)', padding: 'var(--space-6)', display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
              {/* Summary Card */}
              <div style={{ background: 'rgba(56, 189, 248, 0.1)', borderLeft: '4px solid #38bdf8', padding: '12px 16px', borderRadius: '6px' }}>
                <h4 style={{ margin: '0 0 4px 0', color: '#38bdf8', fontSize: '0.95rem' }}>Direct AI Summary</h4>
                <div style={{ fontSize: '1rem', lineHeight: 1.5 }}>{aiSearchResult.summary}</div>
              </div>

              {/* Detailed Breakdown */}
              <div>
                <h4 style={{ margin: '0 0 8px 0', fontSize: '0.95rem', color: 'var(--text-secondary)' }}>Synthesized Explanation</h4>
                <div style={{ fontSize: '0.95rem', lineHeight: 1.6, whiteSpace: 'pre-wrap' }}>
                  {aiSearchResult.explanation}
                </div>
              </div>

              {/* Key Points */}
              {aiSearchResult.key_points && aiSearchResult.key_points.length > 0 && (
                <div>
                  <h4 style={{ margin: '0 0 6px 0', fontSize: '0.95rem', color: 'var(--text-secondary)' }}>Key Points</h4>
                  <ul style={{ margin: 0, paddingLeft: '20px', lineHeight: 1.6 }}>
                    {aiSearchResult.key_points.map((pt, i) => (
                      <li key={i}>{pt}</li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Collapsible Retrieved Sources */}
              <div style={{ border: '1px solid var(--border-default)', borderRadius: '8px', overflow: 'hidden' }}>
                <button
                  onClick={() => setShowSources(!showSources)}
                  style={{
                    width: '100%',
                    padding: '10px 14px',
                    background: 'var(--bg-primary)',
                    border: 'none',
                    color: 'var(--text-secondary)',
                    display: 'flex',
                    justify: 'space-between',
                    alignItems: 'center',
                    cursor: 'pointer',
                    fontSize: '0.85rem',
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <FileText size={16} />
                    <span>View Retrieved RAG Context Chunks ({aiSearchResult.retrieved_sources?.length || 0})</span>
                  </div>
                  {showSources ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
                </button>

                {showSources && (
                  <div style={{ padding: '14px', background: 'var(--bg-secondary)', display: 'flex', flexDirection: 'column', gap: '10px' }}>
                    {aiSearchResult.retrieved_sources?.map((src) => (
                      <div key={src.source_id} style={{ background: 'var(--bg-primary)', padding: '10px', borderRadius: '6px', fontSize: '0.85rem' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', color: '#38bdf8', marginBottom: '4px', fontWeight: 600 }}>
                          <span>📄 {src.file_name} {src.page ? `(Page ${src.page})` : ''}</span>
                          <span>Score: {src.similarity_score}</span>
                        </div>
                        <div style={{ color: 'var(--text-secondary)', fontStyle: 'italic' }}>
                          "{src.snippet}"
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Tabs */}
      <Tabs 
        activeTab={activeTab}
        onChange={setActiveTab}
        tabs={[
          { id: 'lessons', label: 'Lessons' },
          { id: 'quiz', label: 'Quizzes' },
          { id: 'flashcards', label: 'Flashcards' }
        ]} 
      />
      
      <div style={{ marginTop: 'var(--space-6)' }}>
        {course.status === 'ready' ? (
          activeTab === 'lessons' ? (
            <CourseStructure
              courseId={course.id}
              onOpenQuiz={(lesson) => setQuizLesson(lesson)}
              onGenerate={handleGenerate}
              isGenerating={generateCourse.isPending}
            />
          ) : activeTab === 'quiz' ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              <div style={{ padding: '20px', background: 'var(--bg-secondary)', borderRadius: '12px', border: '1px solid var(--border-default)' }}>
                <h3 className="text-heading-md" style={{ marginBottom: '8px' }}>AI Quiz Generator & Practice</h3>
                <p className="text-body-sm text-secondary" style={{ marginBottom: '16px' }}>Select any lesson below to generate and take an interactive quiz (MCQ, True/False, Fill-in, Short Answer).</p>
              </div>
              <CourseStructure
                courseId={course.id}
                onOpenQuiz={(lesson) => setQuizLesson(lesson)}
                onGenerate={handleGenerate}
                isGenerating={generateCourse.isPending}
              />
            </div>

          ) : (
            <div style={{ padding: '30px', textAlign: 'center', background: 'var(--bg-secondary)', borderRadius: '12px', border: '1px solid var(--border-default)' }}>
              <Layers size={48} className="text-brand" style={{ marginBottom: '16px' }} />
              <h3 className="text-heading-md" style={{ marginBottom: '8px' }}>Course Flashcard Deck</h3>
              <p className="text-body-sm text-secondary" style={{ marginBottom: '20px' }}>Active recall powered by SuperMemo SM-2 spaced repetition.</p>
              <Link to={`/flashcards/${id}`}>
                <Button variant="primary" icon={Layers} size="lg">Study Flashcards Now</Button>
              </Link>
            </div>
          )
        ) : (
          <div style={{ padding: 'var(--space-8)', border: '1px dashed var(--border-default)', borderRadius: 'var(--radius-lg)', textAlign: 'center' }}>
            <p className="text-secondary">Course structure has not been generated yet.</p>
          </div>
        )}
      </div>

      {quizLesson && (
        <QuizModal
          isOpen={!!quizLesson}
          onClose={() => setQuizLesson(null)}
          courseId={id}
          lessonId={quizLesson.id}
          lessonTitle={quizLesson.title}
        />
      )}
    </div>
  );
}

