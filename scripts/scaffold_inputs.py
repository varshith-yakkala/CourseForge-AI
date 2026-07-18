import os

files = {
    'frontend/src/components/ui/Button.jsx': '''
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
        cf-button--,
        cf-button--,
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
'''.lstrip(),

    'frontend/src/components/ui/Button.css': '''
.cf-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-2);
  border-radius: var(--radius-sm);
  font-family: inherit;
  font-weight: 500;
  transition: all var(--duration-fast) var(--ease-default);
  cursor: pointer;
  white-space: nowrap;
}

.cf-button:disabled {
  opacity: 0.4;
  cursor: not-allowed;
  pointer-events: none;
}

/* Sizes */
.cf-button--xs { height: 28px; padding: 0 10px; font-size: var(--text-label-sm); }
.cf-button--sm { height: 32px; padding: 0 12px; font-size: var(--text-label-md); }
.cf-button--md { height: 36px; padding: 0 16px; font-size: var(--text-label-md); }
.cf-button--lg { height: 42px; padding: 0 20px; font-size: var(--text-label-lg); }
.cf-button--xl { height: 50px; padding: 0 24px; font-size: var(--text-body-sm); }

/* Icons */
.cf-button-icon {
  width: 1em;
  height: 1em;
  flex-shrink: 0;
}

/* Spinner */
.cf-button-spinner {
  width: 1em;
  height: 1em;
  flex-shrink: 0;
  animation: spin 1s linear infinite;
}

/* Variants */
.cf-button--primary {
  background-color: var(--color-brand-500);
  color: #fff;
  border: none;
}
.cf-button--primary:hover {
  background-color: var(--color-brand-400);
  transform: translateY(-1px);
  box-shadow: var(--shadow-brand);
}
.cf-button--primary:active {
  transform: scale(0.97);
  background-color: var(--color-brand-600);
}

.cf-button--secondary {
  background-color: transparent;
  color: var(--color-brand-400);
  border: 1px solid var(--border-brand);
}
.cf-button--secondary:hover {
  background-color: var(--bg-elevated);
  border-color: var(--color-brand-500);
}

.cf-button--ghost {
  background-color: transparent;
  color: var(--text-secondary);
  border: none;
}
.cf-button--ghost:hover {
  background-color: var(--bg-overlay);
  color: var(--text-primary);
}

.cf-button--danger {
  background-color: var(--color-danger-500);
  color: #fff;
  border: none;
}
.cf-button--danger:hover {
  background-color: var(--color-danger-400);
}

.cf-button--muted {
  background-color: var(--bg-overlay);
  color: var(--text-secondary);
  border: 1px solid var(--border-default);
}
.cf-button--muted:hover {
  background-color: var(--bg-elevated);
  color: var(--text-primary);
}
'''.lstrip(),

    'frontend/src/components/ui/Input.jsx': '''
import React, { forwardRef } from 'react';
import { cn } from '@/utils/classNames';
import { AlertCircle } from 'lucide-react';
import './Input.css';

export const Input = forwardRef(({ 
  label, 
  error, 
  helperText, 
  className,
  icon: Icon,
  ...props 
}, ref) => {
  return (
    <div className={cn("cf-input-wrapper", className)}>
      {label && <label className="cf-input-label">{label}</label>}
      <div className="cf-input-container">
        {Icon && <Icon className="cf-input-icon" />}
        <input 
          ref={ref}
          className={cn(
            "cf-input",
            Icon && "cf-input--with-icon",
            error && "cf-input--error"
          )}
          {...props}
        />
      </div>
      {error && (
        <span className="cf-input-error">
          <AlertCircle size={14} /> {error}
        </span>
      )}
      {!error && helperText && (
        <span className="cf-input-helper">{helperText}</span>
      )}
    </div>
  );
});
Input.displayName = 'Input';
'''.lstrip(),

    'frontend/src/components/ui/Input.css': '''
.cf-input-wrapper {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.cf-input-label {
  font-size: var(--text-label-md);
  color: var(--text-secondary);
  font-weight: 500;
}

.cf-input-container {
  position: relative;
  display: flex;
  align-items: center;
}

.cf-input {
  width: 100%;
  height: 40px;
  background-color: var(--bg-surface);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-sm);
  padding: 0 12px;
  font-size: var(--text-body-md);
  color: var(--text-primary);
  transition: all var(--duration-fast) var(--ease-out);
}

.cf-input:focus {
  outline: none;
  border-color: var(--color-brand-500);
  box-shadow: 0 0 0 3px rgba(124, 114, 255, 0.15);
  background-color: var(--bg-elevated);
}

.cf-input--error {
  border-color: var(--color-danger-500);
}

.cf-input--error:focus {
  box-shadow: 0 0 0 3px rgba(244, 63, 94, 0.15);
}

.cf-input:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  background-color: var(--bg-subtle);
}

.cf-input-icon {
  position: absolute;
  left: 12px;
  color: var(--text-muted);
  width: 16px;
  height: 16px;
}

.cf-input--with-icon {
  padding-left: 36px;
}

.cf-input-error {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: var(--text-label-sm);
  color: var(--color-danger-500);
}

.cf-input-helper {
  font-size: var(--text-label-sm);
  color: var(--text-muted);
}
'''.lstrip(),

    'frontend/src/components/ui/TextArea.jsx': '''
import React, { forwardRef } from 'react';
import { cn } from '@/utils/classNames';
import { AlertCircle } from 'lucide-react';
import './Input.css'; /* Reuses input styles where possible */

export const TextArea = forwardRef(({ 
  label, 
  error, 
  helperText, 
  className,
  rows = 4,
  ...props 
}, ref) => {
  return (
    <div className={cn("cf-input-wrapper", className)}>
      {label && <label className="cf-input-label">{label}</label>}
      <textarea 
        ref={ref}
        rows={rows}
        className={cn(
          "cf-input",
          "cf-textarea",
          error && "cf-input--error"
        )}
        {...props}
      />
      {error && (
        <span className="cf-input-error">
          <AlertCircle size={14} /> {error}
        </span>
      )}
      {!error && helperText && (
        <span className="cf-input-helper">{helperText}</span>
      )}
    </div>
  );
});
TextArea.displayName = 'TextArea';
'''.lstrip(),

    'frontend/src/components/ui/Checkbox.jsx': '''
import React, { forwardRef } from 'react';
import { cn } from '@/utils/classNames';
import './Controls.css';

export const Checkbox = forwardRef(({ 
  label, 
  description,
  className,
  ...props 
}, ref) => {
  return (
    <label className={cn("cf-control-wrapper", className)}>
      <div className="cf-checkbox-container">
        <input 
          type="checkbox"
          ref={ref}
          className="cf-checkbox-input sr-only"
          {...props}
        />
        <div className="cf-checkbox-box">
          <svg viewBox="0 0 14 14" fill="none" className="cf-checkbox-icon">
            <path d="M3 7L6 10L11 4" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
        </div>
      </div>
      {(label || description) && (
        <div className="cf-control-text">
          {label && <span className="cf-control-label">{label}</span>}
          {description && <span className="cf-control-desc">{description}</span>}
        </div>
      )}
    </label>
  );
});
Checkbox.displayName = 'Checkbox';
'''.lstrip(),

    'frontend/src/components/ui/Controls.css': '''
.cf-control-wrapper {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  cursor: pointer;
}

.cf-control-text {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.cf-control-label {
  font-size: var(--text-body-md);
  color: var(--text-primary);
  line-height: 20px;
}

.cf-control-desc {
  font-size: var(--text-label-sm);
  color: var(--text-muted);
}

/* Checkbox specific */
.cf-checkbox-container {
  position: relative;
  width: 20px;
  height: 20px;
  flex-shrink: 0;
}

.cf-checkbox-box {
  width: 100%;
  height: 100%;
  border: 1px solid var(--border-strong);
  border-radius: 4px;
  background-color: var(--bg-surface);
  transition: all var(--duration-fast) var(--ease-out);
  display: flex;
  align-items: center;
  justify-content: center;
}

.cf-checkbox-icon {
  width: 14px;
  height: 14px;
  stroke-dasharray: 16;
  stroke-dashoffset: 16;
  transition: stroke-dashoffset 0.2s var(--ease-out);
}

.cf-checkbox-input:checked + .cf-checkbox-box {
  background-color: var(--color-brand-500);
  border-color: var(--color-brand-500);
  color: white;
}

.cf-checkbox-input:checked + .cf-checkbox-box .cf-checkbox-icon {
  stroke-dashoffset: 0;
}

.cf-checkbox-input:focus-visible + .cf-checkbox-box {
  box-shadow: 0 0 0 2px var(--bg-base), 0 0 0 4px var(--color-brand-500);
}

/* Radio specific */
.cf-radio-container {
  position: relative;
  width: 20px;
  height: 20px;
  flex-shrink: 0;
}

.cf-radio-circle {
  width: 100%;
  height: 100%;
  border: 1px solid var(--border-strong);
  border-radius: 50%;
  background-color: var(--bg-surface);
  transition: all var(--duration-fast) var(--ease-out);
  display: flex;
  align-items: center;
  justify-content: center;
}

.cf-radio-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: white;
  transform: scale(0);
  transition: transform 0.2s var(--ease-bounce);
}

.cf-radio-input:checked + .cf-radio-circle {
  background-color: var(--color-brand-500);
  border-color: var(--color-brand-500);
}

.cf-radio-input:checked + .cf-radio-circle .cf-radio-dot {
  transform: scale(1);
}

.cf-radio-input:focus-visible + .cf-radio-circle {
  box-shadow: 0 0 0 2px var(--bg-base), 0 0 0 4px var(--color-brand-500);
}

/* Switch specific */
.cf-switch-container {
  position: relative;
  width: 36px;
  height: 20px;
  flex-shrink: 0;
}

.cf-switch-track {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  border-radius: 20px;
  background-color: var(--bg-overlay);
  border: 1px solid var(--border-strong);
  transition: all var(--duration-fast) var(--ease-out);
}

.cf-switch-thumb {
  position: absolute;
  top: 2px;
  left: 2px;
  width: 14px;
  height: 14px;
  border-radius: 50%;
  background-color: white;
  transition: transform 0.2s var(--ease-bounce);
}

.cf-switch-input:checked + .cf-switch-track {
  background-color: var(--color-brand-500);
  border-color: var(--color-brand-500);
}

.cf-switch-input:checked + .cf-switch-track .cf-switch-thumb {
  transform: translateX(16px);
}

.cf-switch-input:focus-visible + .cf-switch-track {
  box-shadow: 0 0 0 2px var(--bg-base), 0 0 0 4px var(--color-brand-500);
}
'''.lstrip(),

    'frontend/src/components/ui/Radio.jsx': '''
import React, { forwardRef } from 'react';
import { cn } from '@/utils/classNames';
import './Controls.css';

export const Radio = forwardRef(({ 
  label, 
  description,
  className,
  ...props 
}, ref) => {
  return (
    <label className={cn("cf-control-wrapper", className)}>
      <div className="cf-radio-container">
        <input 
          type="radio"
          ref={ref}
          className="cf-radio-input sr-only"
          {...props}
        />
        <div className="cf-radio-circle">
          <div className="cf-radio-dot" />
        </div>
      </div>
      {(label || description) && (
        <div className="cf-control-text">
          {label && <span className="cf-control-label">{label}</span>}
          {description && <span className="cf-control-desc">{description}</span>}
        </div>
      )}
    </label>
  );
});
Radio.displayName = 'Radio';
'''.lstrip(),

    'frontend/src/components/ui/Switch.jsx': '''
import React, { forwardRef } from 'react';
import { cn } from '@/utils/classNames';
import './Controls.css';

export const Switch = forwardRef(({ 
  label, 
  description,
  className,
  ...props 
}, ref) => {
  return (
    <label className={cn("cf-control-wrapper", className)}>
      <div className="cf-switch-container">
        <input 
          type="checkbox"
          role="switch"
          ref={ref}
          className="cf-switch-input sr-only"
          {...props}
        />
        <div className="cf-switch-track">
          <div className="cf-switch-thumb" />
        </div>
      </div>
      {(label || description) && (
        <div className="cf-control-text">
          {label && <span className="cf-control-label">{label}</span>}
          {description && <span className="cf-control-desc">{description}</span>}
        </div>
      )}
    </label>
  );
});
Switch.displayName = 'Switch';
'''.lstrip()
}

for path, content in files.items():
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

print("Buttons and Inputs components created successfully.")
