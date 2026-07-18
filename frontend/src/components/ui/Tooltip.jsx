import React, { useState } from 'react';
import { cn } from '@/utils/classNames';
import './Tooltip.css';

export function Tooltip({ children, content, position = 'top' }) {
  const [isVisible, setIsVisible] = useState(false);

  if (!content) return children;

  return (
    <div 
      className="cf-tooltip-wrapper"
      onMouseEnter={() => setIsVisible(true)}
      onMouseLeave={() => setIsVisible(false)}
      onFocus={() => setIsVisible(true)}
      onBlur={() => setIsVisible(false)}
    >
      {children}
      {isVisible && (
        <div className={cn('cf-tooltip-content', `cf-tooltip--${position}`)}>
          {content}
        </div>
      )}
    </div>
  );
}
