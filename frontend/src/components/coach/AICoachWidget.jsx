import React, { useState } from 'react';
import { Sparkles, X, ChevronUp, Bot } from 'lucide-react';
import { useCoachAdvice } from '@/api/hooks';
import './AICoachWidget.css';

export function AICoachWidget({ courseId = null }) {
  const [isOpen, setIsOpen] = useState(true);
  const [isMinimized, setIsMinimized] = useState(false);

  const { data: coachData } = useCoachAdvice(courseId);

  if (!isOpen || !coachData?.tip) return null;

  return (
    <div className={`cf-coach-widget ${isMinimized ? 'cf-coach--minimized' : ''}`}>
      <div className="cf-coach-widget-header" onClick={() => setIsMinimized(!isMinimized)}>
        <div className="cf-coach-title-group">
          <Bot size={18} className="cf-coach-icon" />
          <span className="cf-coach-name">AI Learning Coach</span>
        </div>
        <div className="cf-coach-controls">
          <button className="cf-coach-btn" onClick={(e) => { e.stopPropagation(); setIsMinimized(!isMinimized); }}>
            <ChevronUp size={16} className={isMinimized ? '' : 'cf-rotate-180'} />
          </button>
          <button className="cf-coach-btn" onClick={(e) => { e.stopPropagation(); setIsOpen(false); }}>
            <X size={16} />
          </button>
        </div>
      </div>

      {!isMinimized && (
        <div className="cf-coach-widget-body">
          <div className="cf-coach-tip">{coachData.tip}</div>
        </div>
      )}
    </div>
  );
}
