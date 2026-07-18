import React, { forwardRef } from 'react';
import { cn } from '@/utils/classNames';
import './Badge.css';

export const Badge = forwardRef(({ 
  children, 
  variant = 'default',
  size = 'md',
  dot = false,
  className,
  ...props 
}, ref) => {
  return (
    <span 
      ref={ref}
      className={cn(
        'cf-badge',
        `cf-badge--${variant}`,
        `cf-badge--${size}`,
        className
      )}
      {...props}
    >
      {dot && (
        <span className={cn(
          'cf-badge-dot', 
          dot === 'pulse' && 'cf-badge-dot--pulse'
        )} />
      )}
      {children}
    </span>
  );
});
Badge.displayName = 'Badge';
