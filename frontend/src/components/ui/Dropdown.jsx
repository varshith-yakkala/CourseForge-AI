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
