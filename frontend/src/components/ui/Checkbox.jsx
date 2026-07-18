import React, { forwardRef } from 'react';
import { cn } from '@/utils/classNames';
import './Controls.css';

export const Checkbox = forwardRef(({ 
  label, 
  description,
  className,
  ...props 
}, ref) => {
  return (
    <label className={cn("cf-control-wrapper", className)}>
      <div className="cf-checkbox-container">
        <input 
          type="checkbox"
          ref={ref}
          className="cf-checkbox-input sr-only"
          {...props}
        />
        <div className="cf-checkbox-box">
          <svg viewBox="0 0 14 14" fill="none" className="cf-checkbox-icon">
            <path d="M3 7L6 10L11 4" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
        </div>
      </div>
      {(label || description) && (
        <div className="cf-control-text">
          {label && <span className="cf-control-label">{label}</span>}
          {description && <span className="cf-control-desc">{description}</span>}
        </div>
      )}
    </label>
  );
});
Checkbox.displayName = 'Checkbox';
