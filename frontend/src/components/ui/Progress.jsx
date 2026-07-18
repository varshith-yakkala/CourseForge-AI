import React, { forwardRef } from 'react';
import { cn } from '@/utils/classNames';
import './Progress.css';

export const Progress = forwardRef(({ 
  value = 0, 
  max = 100,
  size = 'md',
  label,
  labelPosition = 'none', // 'none', 'below', 'inside'
  className,
  ...props 
}, ref) => {
  const percentage = Math.min(Math.max((value / max) * 100, 0), 100);

  return (
    <div className={cn("cf-progress-wrapper", className)} ref={ref} {...props}>
      <div className={cn('cf-progress-track', `cf-progress-track--${size}`)}>
        <div 
          className="cf-progress-fill" 
          style={{ width: `${percentage}%` }}
        >
          {labelPosition === 'inside' && size === 'lg' && percentage > 15 && (
            <span className="cf-progress-label-inside">{Math.round(percentage)}%</span>
          )}
        </div>
      </div>
      {labelPosition === 'below' && label && (
        <span className="cf-progress-label-below">{label}</span>
      )}
    </div>
  );
});
Progress.displayName = 'Progress';
