import React, { forwardRef } from 'react';
import { cn } from '@/utils/classNames';
import './Card.css';

export const Card = forwardRef(({ 
  children, 
  variant = 'default',
  hover = false,
  className,
  ...props 
}, ref) => {
  return (
    <div 
      ref={ref}
      className={cn(
        'cf-card',
        `cf-card--${variant}`,
        hover && 'cf-card--hover',
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
});
Card.displayName = 'Card';
