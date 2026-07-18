import React, { forwardRef } from 'react';
import { cn } from '@/utils/classNames';
import './Controls.css';

export const Radio = forwardRef(({ 
  label, 
  description,
  className,
  ...props 
}, ref) => {
  return (
    <label className={cn("cf-control-wrapper", className)}>
      <div className="cf-radio-container">
        <input 
          type="radio"
          ref={ref}
          className="cf-radio-input sr-only"
          {...props}
        />
        <div className="cf-radio-circle">
          <div className="cf-radio-dot" />
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
Radio.displayName = 'Radio';
