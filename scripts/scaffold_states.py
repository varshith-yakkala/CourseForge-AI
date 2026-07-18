import os

files = {
    'frontend/src/components/ui/Toast.jsx': '''
import React from 'react';
import { cn } from '@/utils/classNames';
import { useNotificationStore } from '@/store/useNotificationStore';
import { X, CheckCircle, AlertCircle, Info, AlertTriangle } from 'lucide-react';
import './Toast.css';

const icons = {
  success: CheckCircle,
  error: AlertCircle,
  info: Info,
  warning: AlertTriangle
};

export function ToastContainer() {
  const notifications = useNotificationStore((state) => state.notifications);
  const removeNotification = useNotificationStore((state) => state.removeNotification);

  return (
    <div className="cf-toast-container" aria-live="polite">
      {notifications.map((toast) => {
        const Icon = icons[toast.type || 'info'];
        return (
          <div key={toast.id} className={cn('cf-toast', cf-toast--)}>
            <div className="cf-toast-icon-wrapper">
              <Icon size={20} className="cf-toast-icon" />
            </div>
            <div className="cf-toast-content">
              {toast.title && <h4 className="cf-toast-title">{toast.title}</h4>}
              {toast.message && <p className="cf-toast-message">{toast.message}</p>}
            </div>
            <button 
              className="cf-toast-close" 
              onClick={() => removeNotification(toast.id)}
              aria-label="Close"
            >
              <X size={16} />
            </button>
          </div>
        );
      })}
    </div>
  );
}
'''.lstrip(),

    'frontend/src/components/ui/Toast.css': '''
.cf-toast-container {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: var(--z-toast);
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-width: 360px;
  width: calc(100vw - 40px);
}

.cf-toast {
  display: flex;
  align-items: flex-start;
  padding: 12px 16px;
  background-color: var(--bg-surface);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-lg);
  animation: slideInRight var(--duration-moderate) var(--ease-bounce);
  position: relative;
  overflow: hidden;
}

/* Accent bar */
.cf-toast::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 4px;
}

.cf-toast--success::before { background-color: var(--color-success-500); }
.cf-toast--error::before { background-color: var(--color-danger-500); }
.cf-toast--warning::before { background-color: var(--color-warning-500); }
.cf-toast--info::before { background-color: var(--color-brand-500); }

.cf-toast-icon-wrapper {
  margin-right: 12px;
  margin-top: 2px;
}

.cf-toast--success .cf-toast-icon { color: var(--color-success-400); }
.cf-toast--error .cf-toast-icon { color: var(--color-danger-400); }
.cf-toast--warning .cf-toast-icon { color: var(--color-warning-400); }
.cf-toast--info .cf-toast-icon { color: var(--color-brand-400); }

.cf-toast-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.cf-toast-title {
  margin: 0;
  font-size: var(--text-label-md);
  color: var(--text-primary);
  font-weight: 600;
}

.cf-toast-message {
  margin: 0;
  font-size: var(--text-body-sm);
  color: var(--text-secondary);
}

.cf-toast-close {
  color: var(--text-muted);
  margin-left: 12px;
  padding: 4px;
  border-radius: var(--radius-sm);
  transition: all var(--duration-fast) var(--ease-out);
}
.cf-toast-close:hover {
  color: var(--text-primary);
  background-color: var(--bg-overlay);
}
'''.lstrip(),

    'frontend/src/components/ui/Avatar.jsx': '''
import React, { useState } from 'react';
import { cn } from '@/utils/classNames';
import './Avatar.css';

export function Avatar({ src, name, size = 'md', className }) {
  const [error, setError] = useState(false);
  const initials = name ? name.split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase() : '?';

  return (
    <div className={cn('cf-avatar', cf-avatar--, className)}>
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
'''.lstrip(),

    'frontend/src/components/ui/Avatar.css': '''
.cf-avatar {
  border-radius: var(--radius-full);
  background-color: var(--bg-overlay);
  border: 1px solid var(--border-default);
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  flex-shrink: 0;
  color: var(--text-secondary);
}

/* Sizes */
.cf-avatar--xs { width: 24px; height: 24px; font-size: 10px; font-weight: 500; }
.cf-avatar--sm { width: 32px; height: 32px; font-size: 12px; font-weight: 500; }
.cf-avatar--md { width: 40px; height: 40px; font-size: 14px; font-weight: 600; }
.cf-avatar--lg { width: 48px; height: 48px; font-size: 16px; font-weight: 600; }
.cf-avatar--xl { width: 64px; height: 64px; font-size: 20px; font-weight: 600; }
.cf-avatar--2xl { width: 96px; height: 96px; font-size: 32px; font-weight: 700; }

.cf-avatar-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.cf-avatar-initials {
  line-height: 1;
}
'''.lstrip(),

    'frontend/src/components/ui/Loading.jsx': '''
import React from 'react';
import { cn } from '@/utils/classNames';
import { Loader2 } from 'lucide-react';
import './Loading.css';

export function Spinner({ size = 'md', className, color }) {
  const styles = color ? { color } : {};
  return (
    <Loader2 
      className={cn('cf-spinner', cf-spinner--, className)} 
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
'''.lstrip(),

    'frontend/src/components/ui/Loading.css': '''
/* Spinner */
.cf-spinner {
  animation: spin 1s linear infinite;
  color: var(--text-muted);
}
.cf-spinner--sm { width: 16px; height: 16px; }
.cf-spinner--md { width: 24px; height: 24px; }
.cf-spinner--lg { width: 32px; height: 32px; }
.cf-spinner--xl { width: 48px; height: 48px; }

/* Skeleton */
.cf-skeleton {
  background: var(--bg-overlay);
  background: linear-gradient(
    90deg,
    var(--bg-overlay) 0%,
    var(--bg-elevated) 20%,
    var(--bg-overlay) 40%,
    var(--bg-overlay) 100%
  );
  background-size: 800px 100%;
  animation: shimmer 1.5s linear infinite;
  border-radius: var(--radius-sm);
}

@media (prefers-reduced-motion: reduce) {
  .cf-skeleton {
    animation: none;
    background: var(--bg-overlay);
  }
}
'''.lstrip(),

    'frontend/src/components/ui/States.jsx': '''
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
'''.lstrip(),

    'frontend/src/components/ui/States.css': '''
.cf-empty-state, .cf-error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: var(--space-12) var(--space-6);
  background-color: var(--bg-surface);
  border: 1px dashed var(--border-default);
  border-radius: var(--radius-lg);
  width: 100%;
}

.cf-empty-state-icon {
  color: var(--color-brand-500);
  margin-bottom: var(--space-4);
  opacity: 0.8;
  background: radial-gradient(circle, rgba(124, 114, 255, 0.15) 0%, transparent 70%);
  padding: var(--space-4);
  border-radius: 50%;
}

.cf-error-state-icon {
  color: var(--color-danger-500);
  margin-bottom: var(--space-4);
  background: radial-gradient(circle, rgba(244, 63, 94, 0.15) 0%, transparent 70%);
  padding: var(--space-3);
  border-radius: 50%;
}

.cf-empty-state-title, .cf-error-state-title {
  margin: 0 0 var(--space-2) 0;
  font-size: var(--text-heading-sm);
  color: var(--text-primary);
  font-weight: 600;
}

.cf-empty-state-desc, .cf-error-state-desc {
  margin: 0;
  font-size: var(--text-body-md);
  color: var(--text-secondary);
  max-width: 400px;
}

.cf-empty-state-action, .cf-error-state-action {
  margin-top: var(--space-6);
}
'''.lstrip()
}

for path, content in files.items():
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

print("Toast, Avatar, Loading/States created successfully.")
