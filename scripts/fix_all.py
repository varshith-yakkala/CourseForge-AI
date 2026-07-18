import os

files = {
    'frontend/src/components/ui/Button.jsx': """
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
""".lstrip(),

    'frontend/src/components/ui/Card.jsx': """
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
        `cf-card--${variant}`,
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
""".lstrip(),

    'frontend/src/components/ui/Badge.jsx': """
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
        `cf-badge--${variant}`,
        `cf-badge--${size}`,
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
""".lstrip(),

    'frontend/src/components/ui/Progress.jsx': """
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
      <div className={cn('cf-progress-track', `cf-progress-track--${size}`)}>
        <div 
          className="cf-progress-fill" 
          style={{ width: `${percentage}%` }}
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
""".lstrip(),

    'frontend/src/components/ui/Tabs.jsx': """
import React, { useState } from 'react';
import { cn } from '@/utils/classNames';
import './Tabs.css';

export function Tabs({ 
  tabs, 
  activeTab, 
  onChange, 
  variant = 'line', // 'line', 'pill', 'button'
  size = 'md',      // 'sm', 'md', 'lg'
  className
}) {
  const [internalTab, setInternalTab] = useState(tabs[0]?.id);
  const currentTab = activeTab !== undefined ? activeTab : internalTab;

  const handleTabClick = (id) => {
    setInternalTab(id);
    if (onChange) onChange(id);
  };

  return (
    <div className={cn('cf-tabs-wrapper', `cf-tabs--${variant}`, `cf-tabs--${size}`, className)}>
      <div className="cf-tabs-list" role="tablist">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            role="tab"
            aria-selected={currentTab === tab.id}
            className={cn('cf-tab', currentTab === tab.id && 'cf-tab--active')}
            onClick={() => handleTabClick(tab.id)}
            disabled={tab.disabled}
          >
            {tab.icon && <tab.icon className="cf-tab-icon" />}
            <span>{tab.label}</span>
          </button>
        ))}
      </div>
    </div>
  );
}
""".lstrip(),

    'frontend/src/components/ui/Modal.jsx': """
import React, { useEffect, useRef } from 'react';
import { cn } from '@/utils/classNames';
import { X } from 'lucide-react';
import './Modal.css';

export function Modal({ 
  isOpen, 
  onClose, 
  title, 
  children,
  footer,
  size = 'md', // 'sm', 'md', 'lg', 'xl', 'full'
  className
}) {
  const overlayRef = useRef(null);

  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }
    return () => {
      document.body.style.overflow = '';
    };
  }, [isOpen]);

  useEffect(() => {
    const handleEsc = (e) => {
      if (e.key === 'Escape' && isOpen) onClose();
    };
    window.addEventListener('keydown', handleEsc);
    return () => window.removeEventListener('keydown', handleEsc);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const handleOverlayClick = (e) => {
    if (e.target === overlayRef.current) onClose();
  };

  return (
    <div 
      className="cf-modal-overlay" 
      ref={overlayRef} 
      onClick={handleOverlayClick}
      role="dialog"
      aria-modal="true"
    >
      <div className={cn('cf-modal-content', `cf-modal--${size}`, className)}>
        {(title || onClose) && (
          <div className="cf-modal-header">
            {title && <h3 className="cf-modal-title">{title}</h3>}
            {onClose && (
              <button className="cf-modal-close" onClick={onClose} aria-label="Close">
                <X size={20} />
              </button>
            )}
          </div>
        )}
        <div className="cf-modal-body">
          {children}
        </div>
        {footer && (
          <div className="cf-modal-footer">
            {footer}
          </div>
        )}
      </div>
    </div>
  );
}
""".lstrip(),

    'frontend/src/components/ui/Tooltip.jsx': """
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
""".lstrip(),

    'frontend/src/components/ui/Dropdown.jsx': """
import React, { useState, useRef, useEffect } from 'react';
import { cn } from '@/utils/classNames';
import './Dropdown.css';

export function Dropdown({ trigger, items, position = 'bottom-right' }) {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef(null);

  useEffect(() => {
    const handleClickOutside = (e) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  return (
    <div className="cf-dropdown-wrapper" ref={dropdownRef}>
      <div onClick={() => setIsOpen(!isOpen)}>{trigger}</div>
      {isOpen && (
        <div className={cn('cf-dropdown-menu', `cf-dropdown--${position}`)}>
          {items.map((item, index) => {
            if (item.divider) return <div key={`div-${index}`} className="cf-dropdown-divider" />;
            return (
              <button
                key={index}
                className={cn('cf-dropdown-item', item.danger && 'cf-dropdown-item--danger')}
                onClick={() => {
                  if (item.onClick) item.onClick();
                  setIsOpen(false);
                }}
              >
                {item.icon && <item.icon className="cf-dropdown-icon" />}
                {item.label}
              </button>
            );
          })}
        </div>
      )}
    </div>
  );
}
""".lstrip(),

    'frontend/src/components/ui/Toast.jsx': """
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
""".lstrip(),

    'frontend/src/components/ui/Avatar.jsx': """
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
""".lstrip(),

    'frontend/src/components/ui/Loading.jsx': """
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
""".lstrip(),

    'frontend/src/components/ui/States.jsx': """
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
""".lstrip(),
    'frontend/src/components/layout/Sidebar.jsx': """
import React from 'react';
import { NavLink } from 'react-router-dom';
import { cn } from '@/utils/classNames';
import { useUIStore } from '@/store/useUIStore';
import { LayoutDashboard, BookOpen, Search, BarChart3, Settings, Bookmark, Menu, ChevronLeft } from 'lucide-react';
import './Sidebar.css';

const NAV_ITEMS = [
  { icon: LayoutDashboard, label: 'Dashboard', path: '/dashboard' },
  { icon: BookOpen, label: 'Courses', path: '/courses' },
  { icon: Search, label: 'Search', path: '/search' },
  { icon: BarChart3, label: 'Analytics', path: '/analytics' },
];

const BOTTOM_ITEMS = [
  { icon: Bookmark, label: 'Bookmarks', path: '/bookmarks' },
  { icon: Settings, label: 'Settings', path: '/settings' },
];

export function Sidebar() {
  const isCollapsed = useUIStore((state) => state.isSidebarCollapsed);
  const toggleSidebar = useUIStore((state) => state.toggleSidebar);

  return (
    <aside className={cn('cf-sidebar', isCollapsed && 'cf-sidebar--collapsed')}>
      <div className="cf-sidebar-header">
        <div className="cf-sidebar-logo">
          <div className="cf-sidebar-logo-icon">C</div>
          <span className="cf-sidebar-logo-text">CourseForge AI</span>
        </div>
        <button className="cf-sidebar-toggle" onClick={toggleSidebar} aria-label="Toggle Sidebar">
          {isCollapsed ? <Menu size={18} /> : <ChevronLeft size={18} />}
        </button>
      </div>

      <nav className="cf-sidebar-nav">
        {NAV_ITEMS.map((item) => (
          <NavLink 
            key={item.path} 
            to={item.path}
            className={({ isActive }) => cn('cf-sidebar-item', isActive && 'cf-sidebar-item--active')}
            title={isCollapsed ? item.label : undefined}
          >
            <item.icon className="cf-sidebar-item-icon" />
            <span className="cf-sidebar-item-label">{item.label}</span>
          </NavLink>
        ))}
      </nav>

      <div className="cf-sidebar-spacer" />

      <nav className="cf-sidebar-nav cf-sidebar-nav--bottom">
        {BOTTOM_ITEMS.map((item) => (
          <NavLink 
            key={item.path} 
            to={item.path}
            className={({ isActive }) => cn('cf-sidebar-item', isActive && 'cf-sidebar-item--active')}
            title={isCollapsed ? item.label : undefined}
          >
            <item.icon className="cf-sidebar-item-icon" />
            <span className="cf-sidebar-item-label">{item.label}</span>
          </NavLink>
        ))}
      </nav>
    </aside>
  );
}
""".lstrip(),
    'frontend/src/components/layout/MobileNav.jsx': """
import React from 'react';
import { NavLink } from 'react-router-dom';
import { cn } from '@/utils/classNames';
import { LayoutDashboard, BookOpen, Search, Settings } from 'lucide-react';
import './MobileNav.css';

const NAV_ITEMS = [
  { icon: LayoutDashboard, label: 'Home', path: '/dashboard' },
  { icon: BookOpen, label: 'Courses', path: '/courses' },
  { icon: Search, label: 'Search', path: '/search' },
  { icon: Settings, label: 'Settings', path: '/settings' },
];

export function MobileNav() {
  return (
    <nav className="cf-mobile-nav">
      {NAV_ITEMS.map((item) => (
        <NavLink
          key={item.path}
          to={item.path}
          className={({ isActive }) => cn('cf-mobile-item', isActive && 'cf-mobile-item--active')}
        >
          <item.icon className="cf-mobile-icon" />
          <span className="cf-mobile-label">{item.label}</span>
        </NavLink>
      ))}
    </nav>
  );
}
""".lstrip(),
    'frontend/src/components/layout/TopNav.jsx': """
import React from 'react';
import { cn } from '@/utils/classNames';
import { useUIStore } from '@/store/useUIStore';
import { useAuthStore } from '@/store/useAuthStore';
import { Menu, Search, Bell } from 'lucide-react';
import { Avatar } from '@/components/ui/Avatar';
import { Dropdown } from '@/components/ui/Dropdown';
import { Breadcrumb } from './Breadcrumb';
import './TopNav.css';

export function TopNav() {
  const setMobileMenu = useUIStore((state) => state.setMobileMenu);
  const setCommandPalette = useUIStore((state) => state.setCommandPalette);
  const user = useAuthStore((state) => state.user);
  const logout = useAuthStore((state) => state.logout);

  const userMenuItems = [
    { label: 'Profile Settings', onClick: () => console.log('Profile') },
    { divider: true },
    { label: 'Log out', danger: true, onClick: logout },
  ];

  return (
    <header className="cf-topnav">
      <div className="cf-topnav-left">
        <button 
          className="cf-topnav-mobile-toggle" 
          onClick={() => setMobileMenu(true)}
          aria-label="Open Mobile Menu"
        >
          <Menu size={20} />
        </button>
        <div className="cf-topnav-breadcrumbs">
          <Breadcrumb />
        </div>
      </div>
      
      <div className="cf-topnav-right">
        <button 
          className="cf-topnav-action"
          onClick={() => setCommandPalette(true)}
          aria-label="Search"
        >
          <Search size={18} />
          <span className="cf-topnav-kbd">⌘K</span>
        </button>
        
        <button className="cf-topnav-action cf-topnav-action--icon">
          <Bell size={18} />
        </button>

        <Dropdown 
          trigger={<div className="cf-topnav-avatar"><Avatar name={user?.full_name || 'User'} size="sm" /></div>}
          items={userMenuItems}
        />
      </div>
    </header>
  );
}
""".lstrip(),
}

for path, content in files.items():
    file_path = os.path.join(r"C:\Users\varsh\OneDrive\Desktop\2-2\pro", path.replace('/', '\\'))
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

print("Files fixed successfully.")
