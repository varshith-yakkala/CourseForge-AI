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
