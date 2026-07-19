import React, { useState } from 'react';
import { Bell, Check, Sparkles, AlertTriangle, AlertCircle, Info } from 'lucide-react';
import { useNotifications, useMarkNotificationRead } from '@/api/hooks';
import './NotificationCenter.css';

export function NotificationCenter() {
  const [isOpen, setIsOpen] = useState(false);
  const [priorityFilter, setPriorityFilter] = useState(null);

  const { data: notifications } = useNotifications(priorityFilter);
  const markRead = useMarkNotificationRead();

  const unreadCount = notifications?.filter((n) => !n.is_read).length || 0;

  const handleMarkRead = (id, e) => {
    e.stopPropagation();
    markRead.mutate(id);
  };

  const getPriorityIcon = (priority) => {
    switch (priority) {
      case 'critical':
        return <AlertCircle className="cf-n-icon cf-n-critical" size={16} />;
      case 'high':
        return <AlertTriangle className="cf-n-icon cf-n-high" size={16} />;
      case 'medium':
        return <Sparkles className="cf-n-icon cf-n-medium" size={16} />;
      default:
        return <Info className="cf-n-icon cf-n-low" size={16} />;
    }
  };

  return (
    <div className="cf-notif-center">
      <button
        className="cf-notif-bell-btn"
        onClick={() => setIsOpen(!isOpen)}
        aria-label="Open notifications"
      >
        <Bell size={20} />
        {unreadCount > 0 && <span className="cf-notif-badge">{unreadCount}</span>}
      </button>

      {isOpen && (
        <div className="cf-notif-dropdown">
          <div className="cf-notif-header">
            <h3 className="cf-notif-title">Notifications</h3>
            <div className="cf-notif-filters">
              {[
                { label: 'All', value: null },
                { label: 'Critical', value: 'critical' },
                { label: 'High', value: 'high' },
              ].map((f) => (
                <button
                  key={f.label}
                  className={`cf-n-filter-btn ${priorityFilter === f.value ? 'cf-n-filter--active' : ''}`}
                  onClick={() => setPriorityFilter(f.value)}
                >
                  {f.label}
                </button>
              ))}
            </div>
          </div>

          <div className="cf-notif-list">
            {!notifications || notifications.length === 0 ? (
              <div className="cf-notif-empty">No notifications right now</div>
            ) : (
              notifications.map((n) => (
                <div
                  key={n.id}
                  className={`cf-notif-item ${n.is_read ? 'cf-notif--read' : 'cf-notif--unread'}`}
                >
                  {getPriorityIcon(n.priority)}
                  <div className="cf-notif-body">
                    <div className="cf-notif-item-title">{n.title}</div>
                    {n.body && <div className="cf-notif-item-desc">{n.body}</div>}
                  </div>
                  {!n.is_read && (
                    <button
                      className="cf-notif-check"
                      onClick={(e) => handleMarkRead(n.id, e)}
                      title="Mark as read"
                    >
                      <Check size={14} />
                    </button>
                  )}
                </div>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  );
}
