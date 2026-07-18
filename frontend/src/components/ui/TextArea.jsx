import React, { forwardRef } from 'react';
import { cn } from '@/utils/classNames';
import { AlertCircle } from 'lucide-react';
import './Input.css'; /* Reuses input styles where possible */

export const TextArea = forwardRef(({ 
  label, 
  error, 
  helperText, 
  className,
  rows = 4,
  ...props 
}, ref) => {
  return (
    <div className={cn("cf-input-wrapper", className)}>
      {label && <label className="cf-input-label">{label}</label>}
      <textarea 
        ref={ref}
        rows={rows}
        className={cn(
          "cf-input",
          "cf-textarea",
          error && "cf-input--error"
        )}
        {...props}
      />
      {error && (
        <span className="cf-input-error">
          <AlertCircle size={14} /> {error}
        </span>
      )}
      {!error && helperText && (
        <span className="cf-input-helper">{helperText}</span>
      )}
    </div>
  );
});
TextArea.displayName = 'TextArea';
