import React from 'react';
import { cn } from '@/utils/classNames';
import { Loader2 } from 'lucide-react';
import './Button.css';

export function Button({ 
  children, 
  variant = 'primary', 
  size = 'md', 
  loading = false,
  isLoading = false, 
  disabled = false, 
  className,
  icon: Icon,
  ...props 
}) {
  const isCurrentlyLoading = loading || isLoading;
  return (
    <button
      className={cn(
        'cf-button',
        `cf-button--${variant}`,
        `cf-button--${size}`,
        isCurrentlyLoading && 'cf-button--loading',
        className
      )}
      disabled={disabled || isCurrentlyLoading}
      {...props}
    >
      {isCurrentlyLoading && <Loader2 className="cf-button-spinner" />}
      {!isCurrentlyLoading && Icon && <Icon className="cf-button-icon" />}
      <span className="cf-button-content">{children}</span>
    </button>
  );
}
