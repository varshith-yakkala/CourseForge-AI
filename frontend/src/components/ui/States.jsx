import React from 'react';
import { cn } from '@/utils/classNames';
import { AlertCircle } from 'lucide-react';
import './States.css';

export function EmptyState({ 
  title, 
  description, 
  icon: Icon,
  action,
  className
}) {
  return (
    <div className={cn('cf-empty-state', className)}>
      {Icon && (
        <div className="cf-empty-state-icon">
          <Icon size={48} />
        </div>
      )}
      <h3 className="cf-empty-state-title">{title}</h3>
      {description && <p className="cf-empty-state-desc">{description}</p>}
      {action && <div className="cf-empty-state-action">{action}</div>}
    </div>
  );
}

export function ErrorState({ 
  title = "Something went wrong", 
  description = "An error occurred while loading this content.", 
  action,
  className
}) {
  return (
    <div className={cn('cf-error-state', className)}>
      <div className="cf-error-state-icon">
        <AlertCircle size={32} />
      </div>
      <h3 className="cf-error-state-title">{title}</h3>
      <p className="cf-error-state-desc">{description}</p>
      {action && <div className="cf-error-state-action">{action}</div>}
    </div>
  );
}
