import React from 'react';
import { cn } from '@/utils/classNames';
import { Loader2 } from 'lucide-react';
import './Button.css';

export function Button({ 
  children, 
  variant = 'primary', 
  size = 'md', 
  loading = false, 
  disabled = false, 
  className,
  icon: Icon,
  ...props 
}) {
  return (
    <button
      className={cn(
        'cf-button',
        `cf-button--${variant}`,
        `cf-button--${size}`,
        loading && 'cf-button--loading',
        className
      )}
      disabled={disabled || loading}
      {...props}
    >
      {loading && <Loader2 className="cf-button-spinner" />}
      {!loading && Icon && <Icon className="cf-button-icon" />}
      <span className="cf-button-content">{children}</span>
    </button>
  );
}
