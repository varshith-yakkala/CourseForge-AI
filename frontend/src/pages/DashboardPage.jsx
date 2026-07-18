import React, { useState } from 'react';
import { EmptyState } from '@/components/ui/States';
import { Button } from '@/components/ui/Button';
import { Skeleton } from '@/components/ui/Loading';
import { UploadModal } from '@/components/ui/UploadModal';
import { Plus } from 'lucide-react';
import { useCourses } from '@/api/hooks';
import { Link } from 'react-router-dom';

export default function DashboardPage() {
  const { data: courses, isLoading, isError } = useCourses();
  const [isUploadOpen, setIsUploadOpen] = useState(false);

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--space-8)' }}>
        <h1 className="text-heading-lg">Dashboard</h1>
        <Button icon={Plus} onClick={() => setIsUploadOpen(true)}>New Course</Button>
      </div>
      
      {isLoading ? (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: 'var(--space-6)' }}>
          {[1, 2, 3].map(i => (
             <div key={i} style={{ border: '1px solid var(--border-default)', padding: 'var(--space-4)', borderRadius: 'var(--radius-md)' }}>
               <Skeleton height="20px" width="70%" style={{ marginBottom: 'var(--space-2)' }} />
               <Skeleton height="14px" width="40%" style={{ marginBottom: 'var(--space-4)' }} />
             </div>
          ))}
        </div>
      ) : isError ? (
        <EmptyState title="Error loading dashboard" description="Failed to load your courses." />
      ) : courses && courses.length > 0 ? (
        <div>
          <h2 className="text-heading-md" style={{ marginBottom: 'var(--space-4)' }}>Recent Courses</h2>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: 'var(--space-6)' }}>
            {courses.slice(0, 3).map(course => (
              <Link to={`/courses/${course.id}`} key={course.id} style={{ textDecoration: 'none', color: 'inherit' }}>
                <div style={{ 
                  border: '1px solid var(--border-default)', 
                  padding: 'var(--space-4)', 
                  borderRadius: 'var(--radius-md)',
                  background: 'var(--bg-secondary)',
                  transition: 'transform 0.2s ease',
                }}
                onMouseEnter={(e) => e.currentTarget.style.transform = 'translateY(-2px)'}
                onMouseLeave={(e) => e.currentTarget.style.transform = 'translateY(0)'}
                >
                  <h3 className="text-heading-sm" style={{ marginBottom: 'var(--space-2)' }}>{course.title}</h3>
                  <p className="text-body-sm text-secondary">Status: {course.status}</p>
                </div>
              </Link>
            ))}
          </div>
        </div>
      ) : (
        <EmptyState 
          title="No courses yet"
          description="Upload a PDF to generate your first interactive learning course."
          action={<Button icon={Plus} onClick={() => setIsUploadOpen(true)}>Upload PDF</Button>}
        />
      )}
      
      <UploadModal isOpen={isUploadOpen} onClose={() => setIsUploadOpen(false)} />
    </div>
  );
}
