import React, { useEffect, useRef } from 'react';
import { cn } from '@/utils/classNames';
import { X } from 'lucide-react';
import './Modal.css';

export function Modal({ 
  isOpen, 
  onClose, 
  title, 
  children,
  footer,
  size = 'md', // 'sm', 'md', 'lg', 'xl', 'full'
  className
}) {
  const overlayRef = useRef(null);

  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }
    return () => {
      document.body.style.overflow = '';
    };
  }, [isOpen]);

  useEffect(() => {
    const handleEsc = (e) => {
      if (e.key === 'Escape' && isOpen) onClose();
    };
    window.addEventListener('keydown', handleEsc);
    return () => window.removeEventListener('keydown', handleEsc);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const handleOverlayClick = (e) => {
    if (e.target === overlayRef.current) onClose();
  };

  return (
    <div 
      className="cf-modal-overlay" 
      ref={overlayRef} 
      onClick={handleOverlayClick}
      role="dialog"
      aria-modal="true"
    >
      <div className={cn('cf-modal-content', `cf-modal--${size}`, className)}>
        {(title || onClose) && (
          <div className="cf-modal-header">
            {title && <h3 className="cf-modal-title">{title}</h3>}
            {onClose && (
              <button className="cf-modal-close" onClick={onClose} aria-label="Close">
                <X size={20} />
              </button>
            )}
          </div>
        )}
        <div className="cf-modal-body">
          {children}
        </div>
        {footer && (
          <div className="cf-modal-footer">
            {footer}
          </div>
        )}
      </div>
    </div>
  );
}
