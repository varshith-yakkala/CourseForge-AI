import React, { forwardRef } from 'react';
import { cn } from '@/utils/classNames';
import './Controls.css';

export const Switch = forwardRef(({ 
  label, 
  description,
  className,
  ...props 
}, ref) => {
  return (
    <label className={cn("cf-control-wrapper", className)}>
      <div className="cf-switch-container">
        <input 
          type="checkbox"
          role="switch"
          ref={ref}
          className="cf-switch-input sr-only"
          {...props}
        />
        <div className="cf-switch-track">
          <div className="cf-switch-thumb" />
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
Switch.displayName = 'Switch';
