import React, { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { Modal } from './Modal';
import { Button } from './Button';
import { Input } from './Input';
import { Progress } from './Progress';
import { useNotificationStore } from '@/store/useNotificationStore';
import { useCreateCourse, useUploadDocument } from '@/api/hooks';
import { extractApiError } from '@/utils/errorUtils';
import { UploadCloud, FileText } from 'lucide-react';

export function UploadModal({ isOpen, onClose }) {
  const [step, setStep] = useState(1);
  const [courseTitle, setCourseTitle] = useState('');
  const [file, setFile] = useState(null);
  const [uploadProgress, setUploadProgress] = useState(0);
  
  const createCourse = useCreateCourse();
  const uploadDoc = useUploadDocument();
  const addNotification = useNotificationStore(s => s.addNotification);
  const navigate = useNavigate();
  const fileInputRef = useRef(null);

  const reset = () => {
    setStep(1);
    setCourseTitle('');
    setFile(null);
    setUploadProgress(0);
    onClose();
  };

  const handleFileChange = (e) => {
    const selected = e.target.files[0];
    if (selected && selected.type === 'application/pdf') {
      setFile(selected);
      if (!courseTitle) {
        setCourseTitle(selected.name.replace('.pdf', ''));
      }
    } else {
      addNotification({ title: 'Invalid file', message: 'Please select a PDF file.', type: 'error' });
    }
  };

  const handleSubmit = async () => {
    if (!file || !courseTitle) return;
    
    try {
      setStep(2);
      // 1. Create Course
      const course = await createCourse.mutateAsync({ title: courseTitle, is_public: false, language: 'en' });
      
      // 2. Upload Document
      await uploadDoc.mutateAsync({
        courseId: course.id,
        file: file,
        onUploadProgress: (progressEvent) => {
          const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          setUploadProgress(percentCompleted);
        }
      });
      
      addNotification({ title: 'Success', message: 'Course created and document uploaded.', type: 'success' });
      reset();
      navigate(`/courses/${course.id}`);
    } catch (error) {
      addNotification({ 
        title: 'Upload failed', 
        message: extractApiError(error), 
        type: 'error' 
      });
      setStep(1);
      setUploadProgress(0);
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={step === 1 ? reset : undefined} title="Create New Course">
      {step === 1 ? (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
          <div 
            onClick={() => fileInputRef.current?.click()}
            style={{
              border: '2px dashed var(--border-default)',
              borderRadius: 'var(--radius-md)',
              padding: 'var(--space-8)',
              textAlign: 'center',
              cursor: 'pointer',
              background: 'var(--bg-secondary)'
            }}
          >
            <input 
              type="file" 
              accept=".pdf" 
              ref={fileInputRef} 
              onChange={handleFileChange} 
              style={{ display: 'none' }} 
            />
            {file ? (
              <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 'var(--space-2)' }}>
                <FileText size={48} className="text-brand" />
                <span className="text-body-md">{file.name}</span>
                <span className="text-body-sm text-secondary">{(file.size / 1024 / 1024).toFixed(2)} MB</span>
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 'var(--space-2)' }}>
                <UploadCloud size={48} className="text-secondary" />
                <span className="text-body-md">Click or drag PDF to upload</span>
              </div>
            )}
          </div>
          
          <Input 
            label="Course Title" 
            value={courseTitle} 
            onChange={(e) => setCourseTitle(e.target.value)} 
            placeholder="e.g. Introduction to Machine Learning"
          />
          
          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 'var(--space-2)', marginTop: 'var(--space-4)' }}>
            <Button variant="ghost" onClick={reset}>Cancel</Button>
            <Button onClick={handleSubmit} disabled={!file || !courseTitle || createCourse.isPending}>
              {createCourse.isPending ? 'Creating...' : 'Upload & Create'}
            </Button>
          </div>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-6)', padding: 'var(--space-4) 0' }}>
          <div style={{ textAlign: 'center' }}>
            <h3 className="text-heading-sm">Uploading Document</h3>
            <p className="text-body-sm text-secondary">Please wait while we securely upload your PDF.</p>
          </div>
          <Progress value={uploadProgress} size="lg" />
          <p style={{ textAlign: 'center' }} className="text-body-sm">{uploadProgress}%</p>
        </div>
      )}
    </Modal>
  );
}
