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
          <div key={toast.id} className={cn('cf-toast', `cf-toast--${toast.type || 'info'}`)}>
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
