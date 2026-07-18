import os

files = {
    'frontend/src/components/ui/Card.jsx': '''
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
        cf-card--,
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
'''.lstrip(),

    'frontend/src/components/ui/Card.css': '''
.cf-card {
  border-radius: var(--radius-md);
  padding: 20px;
  background-color: var(--bg-surface);
  border: 1px solid var(--border-subtle);
  box-shadow: var(--shadow-sm);
  transition: all var(--duration-fast) var(--ease-default);
}

/* Variants */
.cf-card--elevated {
  background-color: var(--bg-elevated);
  box-shadow: var(--shadow-md);
}

.cf-card--outlined {
  background-color: transparent;
  border: 1px solid var(--border-default);
  box-shadow: none;
}

.cf-card--ghost {
  background-color: transparent;
  border: none;
  box-shadow: none;
  padding: 0;
}
.cf-card--ghost.cf-card--hover:hover {
  background-color: var(--bg-surface);
  padding: 20px;
}

.cf-card--glass {
  background-color: rgba(22, 22, 40, 0.6);
  backdrop-filter: blur(20px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.08);
}

/* Hover effect */
.cf-card--hover:not(.cf-card--ghost):hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-lg);
  border-color: var(--border-default);
}
'''.lstrip(),

    'frontend/src/components/ui/Badge.jsx': '''
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
        cf-badge--,
        cf-badge--,
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
'''.lstrip(),

    'frontend/src/components/ui/Badge.css': '''
.cf-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  border-radius: var(--radius-xs);
  font-weight: 500;
  white-space: nowrap;
}

/* Sizes */
.cf-badge--sm { height: 20px; padding: 0 6px; font-size: 10px; }
.cf-badge--md { height: 24px; padding: 0 8px; font-size: 12px; }
.cf-badge--lg { height: 28px; padding: 0 10px; font-size: 14px; }

/* Variants */
.cf-badge--default { background-color: var(--bg-overlay); color: var(--text-secondary); }
.cf-badge--brand   { background-color: rgba(124, 114, 255, 0.15); color: var(--color-brand-400); }
.cf-badge--success { background-color: rgba(22, 192, 130, 0.15); color: var(--color-success-400); }
.cf-badge--warning { background-color: rgba(245, 158, 11, 0.15); color: var(--color-warning-400); }
.cf-badge--danger  { background-color: rgba(244, 63, 94, 0.15); color: var(--color-danger-400); }
.cf-badge--info    { background-color: rgba(59, 159, 245, 0.15); color: var(--color-info-400); }

/* Status Dot */
.cf-badge-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background-color: currentColor;
}
.cf-badge-dot--pulse {
  animation: pulse 1.5s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}
'''.lstrip(),

    'frontend/src/components/ui/Progress.jsx': '''
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
      <div className={cn('cf-progress-track', cf-progress-track--)}>
        <div 
          className="cf-progress-fill" 
          style={{ width: ${percentage}% }}
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
'''.lstrip(),

    'frontend/src/components/ui/Progress.css': '''
.cf-progress-wrapper {
  display: flex;
  flex-direction: column;
  gap: 4px;
  width: 100%;
}

.cf-progress-track {
  width: 100%;
  background-color: var(--bg-overlay);
  border-radius: var(--radius-full);
  overflow: hidden;
}

/* Sizes */
.cf-progress-track--xs { height: 2px; }
.cf-progress-track--sm { height: 4px; }
.cf-progress-track--md { height: 6px; }
.cf-progress-track--lg { height: 16px; } /* Thicker for inside labels */

.cf-progress-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--color-brand-600), var(--color-brand-400));
  border-radius: var(--radius-full);
  transition: width 600ms var(--ease-default);
  display: flex;
  align-items: center;
  justify-content: flex-end;
  padding-right: 8px;
}

.cf-progress-label-inside {
  font-size: 10px;
  font-weight: 600;
  color: white;
  line-height: 1;
}

.cf-progress-label-below {
  font-size: var(--text-label-sm);
  color: var(--text-muted);
  align-self: flex-end;
}
'''.lstrip()
}

for path, content in files.items():
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

print("Card, Badge, Progress components created successfully.")
