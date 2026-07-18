import os

files = {
    'frontend/src/components/ui/Tabs.jsx': '''
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
  // If activeTab is not controlled by parent, manage it internally
  const [internalTab, setInternalTab] = useState(tabs[0]?.id);
  const currentTab = activeTab !== undefined ? activeTab : internalTab;

  const handleTabClick = (id) => {
    setInternalTab(id);
    if (onChange) onChange(id);
  };

  return (
    <div className={cn('cf-tabs-wrapper', cf-tabs--, cf-tabs--, className)}>
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
'''.lstrip(),

    'frontend/src/components/ui/Tabs.css': '''
.cf-tabs-wrapper {
  width: 100%;
}

.cf-tabs-list {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  position: relative;
}

.cf-tab {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: transparent;
  color: var(--text-secondary);
  font-weight: 500;
  transition: all var(--duration-normal) var(--ease-default);
  cursor: pointer;
  white-space: nowrap;
}

.cf-tab:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.cf-tab-icon {
  width: 16px;
  height: 16px;
}

/* Line Variant */
.cf-tabs--line .cf-tabs-list {
  border-bottom: 1px solid var(--border-subtle);
  gap: var(--space-6);
}
.cf-tabs--line .cf-tab {
  padding: 0 4px var(--space-2) 4px;
  border-bottom: 2px solid transparent;
  margin-bottom: -1px;
}
.cf-tabs--line .cf-tab:hover:not(:disabled) {
  color: var(--text-primary);
}
.cf-tabs--line .cf-tab--active {
  color: var(--text-brand);
  border-bottom-color: var(--color-brand-500);
}

/* Pill Variant */
.cf-tabs--pill .cf-tabs-list {
  background-color: var(--bg-subtle);
  border-radius: var(--radius-md);
  padding: 4px;
  gap: 4px;
  display: inline-flex;
}
.cf-tabs--pill .cf-tab {
  padding: 6px 12px;
  border-radius: var(--radius-sm);
}
.cf-tabs--pill .cf-tab--active {
  background-color: var(--bg-overlay);
  color: var(--text-primary);
  box-shadow: var(--shadow-sm);
}

/* Button Variant */
.cf-tabs--button .cf-tabs-list {
  gap: var(--space-2);
}
.cf-tabs--button .cf-tab {
  padding: 8px 16px;
  border-radius: var(--radius-sm);
  border: 1px solid var(--border-default);
}
.cf-tabs--button .cf-tab--active {
  background-color: var(--bg-surface);
  border-color: var(--color-brand-500);
  color: var(--color-brand-400);
}

/* Sizes */
.cf-tabs--sm .cf-tab { font-size: var(--text-label-sm); }
.cf-tabs--md .cf-tab { font-size: var(--text-label-md); }
.cf-tabs--lg .cf-tab { font-size: var(--text-label-lg); }
'''.lstrip(),

    'frontend/src/components/ui/Modal.jsx': '''
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
      <div className={cn('cf-modal-content', cf-modal--, className)}>
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
'''.lstrip(),

    'frontend/src/components/ui/Modal.css': '''
.cf-modal-overlay {
  position: fixed;
  inset: 0;
  background-color: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(4px);
  z-index: var(--z-modal);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--space-4);
  animation: fadeIn var(--duration-normal) var(--ease-out);
}

.cf-modal-content {
  background-color: var(--bg-surface);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-xl);
  width: 100%;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  animation: fadeInUp var(--duration-moderate) var(--ease-out);
}

.cf-modal--sm { max-width: 400px; }
.cf-modal--md { max-width: 560px; }
.cf-modal--lg { max-width: 720px; }
.cf-modal--xl { max-width: 900px; }
.cf-modal--full {
  max-width: 100%;
  height: 100vh;
  max-height: 100vh;
  border-radius: 0;
  border: none;
}

.cf-modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px;
  border-bottom: 1px solid var(--border-faint);
}

.cf-modal-title {
  font-size: var(--text-heading-sm);
  font-weight: 600;
  margin: 0;
  color: var(--text-primary);
}

.cf-modal-close {
  color: var(--text-muted);
  transition: color var(--duration-fast) var(--ease-out);
  padding: 4px;
  border-radius: var(--radius-sm);
}
.cf-modal-close:hover {
  color: var(--text-primary);
  background-color: var(--bg-overlay);
}

.cf-modal-body {
  padding: 24px;
  overflow-y: auto;
  flex: 1;
}

.cf-modal-footer {
  padding: 16px 24px;
  border-top: 1px solid var(--border-subtle);
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 12px;
}
'''.lstrip(),

    'frontend/src/components/ui/Tooltip.jsx': '''
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
        <div className={cn('cf-tooltip-content', cf-tooltip--)}>
          {content}
        </div>
      )}
    </div>
  );
}
'''.lstrip(),

    'frontend/src/components/ui/Tooltip.css': '''
.cf-tooltip-wrapper {
  position: relative;
  display: inline-flex;
}

.cf-tooltip-content {
  position: absolute;
  background-color: var(--bg-elevated);
  border: 1px solid var(--border-default);
  color: var(--text-primary);
  font-size: var(--text-label-sm);
  padding: 6px 10px;
  border-radius: var(--radius-sm);
  box-shadow: var(--shadow-md);
  white-space: nowrap;
  z-index: var(--z-tooltip);
  pointer-events: none;
  animation: fadeIn var(--duration-fast) var(--ease-out);
}

.cf-tooltip--top {
  bottom: 100%;
  left: 50%;
  transform: translateX(-50%);
  margin-bottom: 8px;
}

.cf-tooltip--bottom {
  top: 100%;
  left: 50%;
  transform: translateX(-50%);
  margin-top: 8px;
}

.cf-tooltip--left {
  right: 100%;
  top: 50%;
  transform: translateY(-50%);
  margin-right: 8px;
}

.cf-tooltip--right {
  left: 100%;
  top: 50%;
  transform: translateY(-50%);
  margin-left: 8px;
}
'''.lstrip(),

    'frontend/src/components/ui/Dropdown.jsx': '''
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
        <div className={cn('cf-dropdown-menu', cf-dropdown--)}>
          {items.map((item, index) => {
            if (item.divider) return <div key={div-} className="cf-dropdown-divider" />;
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
'''.lstrip(),

    'frontend/src/components/ui/Dropdown.css': '''
.cf-dropdown-wrapper {
  position: relative;
  display: inline-block;
}

.cf-dropdown-menu {
  position: absolute;
  background-color: var(--bg-elevated);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-lg);
  padding: 4px;
  min-width: 200px;
  z-index: var(--z-dropdown);
  animation: fadeInDown var(--duration-fast) var(--ease-out);
}

.cf-dropdown--bottom-right {
  top: 100%;
  right: 0;
  margin-top: 8px;
}

.cf-dropdown--bottom-left {
  top: 100%;
  left: 0;
  margin-top: 8px;
}

.cf-dropdown-item {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
  padding: 8px 12px;
  border-radius: var(--radius-sm);
  color: var(--text-primary);
  font-size: var(--text-body-md);
  text-align: left;
  background: transparent;
  transition: background-color var(--duration-fast) var(--ease-out);
}

.cf-dropdown-item:hover {
  background-color: var(--bg-overlay);
}

.cf-dropdown-item--danger {
  color: var(--color-danger-500);
}
.cf-dropdown-item--danger:hover {
  background-color: rgba(244, 63, 94, 0.1);
}

.cf-dropdown-icon {
  width: 16px;
  height: 16px;
  color: var(--text-muted);
}
.cf-dropdown-item--danger .cf-dropdown-icon {
  color: var(--color-danger-500);
}

.cf-dropdown-divider {
  height: 1px;
  background-color: var(--border-subtle);
  margin: 4px 0;
}
'''.lstrip()
}

for path, content in files.items():
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

print("Modal, Tooltip, Dropdown, Tabs created successfully.")
