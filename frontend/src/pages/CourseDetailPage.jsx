import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Tabs } from '@/components/ui/Tabs';
import { useCourse, useDeleteCourse, useCourseDocument, useRetryDocument, useSearch, useGenerateCourse, useCourseStructure } from '@/api/hooks';
import { Skeleton } from '@/components/ui/Loading';
import { EmptyState } from '@/components/ui/States';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Trash2, AlertCircle, RefreshCw, Search, FileText, Play } from 'lucide-react';
import { useNotificationStore } from '@/store/useNotificationStore';

function CourseStructure({ courseId }) {
  const { data: structure, isLoading } = useCourseStructure(courseId);
  
  if (isLoading) return <Skeleton height="200px" />;
  if (!structure || structure.lessons.length === 0) {
    return <EmptyState title="No lessons found" description="Generate the course to see lessons." />;
  }
  
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-6)' }}>
      {structure.lessons.map(lesson => (
        <div key={lesson.id} style={{ padding: 'var(--space-6)', border: '1px solid var(--border-default)', borderRadius: 'var(--radius-lg)', background: 'var(--bg-secondary)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 'var(--space-2)' }}>
            <h3 className="text-heading-md">Lesson {lesson.order_index + 1}: {lesson.title}</h3>
            <Link to={`/learn/${courseId}/${lesson.id}`}>
              <Button icon={Play} size="sm">Start Lesson</Button>
            </Link>
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
  const [searchResults, setSearchResults] = useState(null);

  const handleDelete = async () => {
    if (window.confirm('Are you sure you want to delete this course?')) {
      try {
        await deleteCourse.mutateAsync(id);
        addNotification({ title: 'Course deleted', message: 'The course has been removed.', type: 'success' });
        navigate('/courses');
      } catch (error) {
        addNotification({ title: 'Delete failed', message: 'Failed to delete the course.', type: 'error' });
      }
    }
  };
  
  const handleRetry = async () => {
    if (!document) return;
    try {
      await retryDocument.mutateAsync(document.id);
      addNotification({ title: 'Indexing retried', message: 'The document has been re-queued for indexing.', type: 'info' });
    } catch (error) {
      addNotification({ title: 'Retry failed', message: 'Could not retry indexing.', type: 'error' });
    }
  };
  
  const handleGenerate = async () => {
    try {
      await generateCourse.mutateAsync(id);
      addNotification({ title: 'Generation Started', message: 'The course blueprint is being generated.', type: 'info' });
    } catch (error) {
      addNotification({ title: 'Generation failed', message: 'Failed to start course generation.', type: 'error' });
    }
  };
  
  const handleSearch = async (e) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;
    try {
      const res = await searchApi.mutateAsync({ query: searchQuery, courseId: id });
      setSearchResults(res.results);
    } catch (error) {
      addNotification({ title: 'Search failed', message: 'Could not execute search.', type: 'error' });
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
        <div style={{ display: 'flex', gap: 'var(--space-4)' }}>
          {document && document.index_status === 'ready' && course.status === 'processing' && (
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

      {document && document.index_status === 'processing' && (
        <div style={{ padding: 'var(--space-6)', background: 'var(--bg-secondary)', borderRadius: 'var(--radius-lg)', marginBottom: 'var(--space-8)', textAlign: 'center' }}>
          <RefreshCw className="text-brand" style={{ animation: 'spin 2s linear infinite', marginBottom: 'var(--space-4)' }} size={32} />
          <h3 className="text-heading-sm">Processing Document</h3>
          <p className="text-body-sm text-secondary">We are currently indexing your PDF (InsightForge-AI).</p>
        </div>
      )}
      
      {course.status === 'generating_outline' && (
        <div style={{ padding: 'var(--space-6)', background: 'var(--bg-secondary)', borderRadius: 'var(--radius-lg)', marginBottom: 'var(--space-8)', textAlign: 'center' }}>
          <RefreshCw className="text-brand" style={{ animation: 'spin 2s linear infinite', marginBottom: 'var(--space-4)' }} size={32} />
          <h3 className="text-heading-sm">Generating Blueprint</h3>
          <p className="text-body-sm text-secondary">Designing your course structure, topics, and lessons...</p>
        </div>
      )}
      
      {course.status === 'error' && (
        <div style={{ padding: 'var(--space-6)', border: '1px solid var(--color-danger)', borderRadius: 'var(--radius-lg)', marginBottom: 'var(--space-8)', display: 'flex', alignItems: 'flex-start', gap: 'var(--space-4)' }}>
          <AlertCircle style={{ color: 'var(--color-danger)' }} size={24} />
          <div>
            <h3 className="text-heading-sm" style={{ color: 'var(--color-danger)' }}>Generation Failed</h3>
            <p className="text-body-sm text-secondary">{course.generation_error || 'There was a problem generating the course.'}</p>
            <Button size="sm" variant="outline" style={{ marginTop: 'var(--space-4)' }} onClick={handleGenerate} isLoading={generateCourse.isPending}>Try Again</Button>
          </div>
        </div>
      )}

      {document && document.index_status === 'ready' && (
        <div style={{ marginBottom: 'var(--space-8)' }}>
          <form onSubmit={handleSearch} style={{ display: 'flex', gap: 'var(--space-4)', marginBottom: 'var(--space-6)' }}>
            <div style={{ flex: 1 }}>
              <Input 
                placeholder="Ask a question or search the document..." 
                value={searchQuery}
                onChange={e => setSearchQuery(e.target.value)}
              />
            </div>
            <Button type="submit" icon={Search} isLoading={searchApi.isPending}>Search</Button>
          </form>
          
          {searchResults && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
              <h3 className="text-heading-sm">Search Results ({searchResults.length})</h3>
              {searchResults.length === 0 ? (
                <p className="text-body-sm text-secondary">No results found in the document.</p>
              ) : (
                searchResults.map((res, i) => (
                  <div key={i} style={{ padding: 'var(--space-4)', background: 'var(--bg-secondary)', borderRadius: 'var(--radius-md)' }}>
                    <p className="text-body-sm" style={{ marginBottom: 'var(--space-2)' }}>"{res.content}"</p>
                    <div style={{ display: 'flex', gap: 'var(--space-4)', fontSize: '12px', color: 'var(--text-secondary)' }}>
                      <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}><FileText size={14}/> Page {res.page || '?'}</span>
                      <span>Relevance: {(res.score * 100).toFixed(1)}%</span>
                    </div>
                  </div>
                ))
              )}
            </div>
          )}
        </div>
      )}

      <Tabs 
        tabs={[
          { id: 'lessons', label: 'Lessons' },
          { id: 'quiz', label: 'Quizzes' },
          { id: 'flashcards', label: 'Flashcards' }
        ]} 
      />
      
      <div style={{ marginTop: 'var(--space-6)' }}>
        {course.status === 'ready' ? (
          <CourseStructure courseId={course.id} />
        ) : (
          <div style={{ padding: 'var(--space-8)', border: '1px dashed var(--border-default)', borderRadius: 'var(--radius-lg)', textAlign: 'center' }}>
            <p className="text-secondary">Course structure has not been generated yet.</p>
          </div>
        )}
      </div>
    </div>
  );
}
