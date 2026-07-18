import React from 'react';
import { cn } from '@/utils/classNames';
import { Loader2 } from 'lucide-react';
import './Loading.css';

export function Spinner({ size = 'md', className, color }) {
  const styles = color ? { color } : {};
  return (
    <Loader2 
      className={cn('cf-spinner', `cf-spinner--${size}`, className)} 
      style={styles}
    />
  );
}

export function Skeleton({ className, width, height, circle = false, ...props }) {
  const styles = {
    width: width || '100%',
    height: height || '1em',
    borderRadius: circle ? '50%' : undefined
  };

  return (
    <div 
      className={cn('cf-skeleton', className)} 
      style={styles}
      {...props}
    />
  );
}
