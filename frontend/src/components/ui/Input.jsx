import React, { forwardRef } from 'react';
import { cn } from '@/utils/classNames';
import { AlertCircle } from 'lucide-react';
import './Input.css';

export const Input = forwardRef(({ 
  label, 
  error, 
  helperText, 
  className,
  icon: Icon,
  ...props 
}, ref) => {
  return (
    <div className={cn("cf-input-wrapper", className)}>
      {label && <label className="cf-input-label">{label}</label>}
      <div className="cf-input-container">
        {Icon && <Icon className="cf-input-icon" />}
        <input 
          ref={ref}
          className={cn(
            "cf-input",
            Icon && "cf-input--with-icon",
            error && "cf-input--error"
          )}
          {...props}
        />
      </div>
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
Input.displayName = 'Input';
