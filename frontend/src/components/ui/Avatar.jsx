import React, { useState } from 'react';
import { cn } from '@/utils/classNames';
import './Avatar.css';

export function Avatar({ src, name, size = 'md', className }) {
  const [error, setError] = useState(false);
  const initials = name ? name.split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase() : '?';

  return (
    <div className={cn('cf-avatar', `cf-avatar--${size}`, className)}>
      {!error && src ? (
        <img 
          src={src} 
          alt={name || 'Avatar'} 
          className="cf-avatar-image" 
          onError={() => setError(true)}
        />
      ) : (
        <span className="cf-avatar-initials">{initials}</span>
      )}
    </div>
  );
}
