import React, { useState } from 'react';
import { 
  Sparkles, BookOpen, Baby, Briefcase, HelpCircle, 
  CheckCircle2, Calculator, ListChecks, AlertTriangle, Loader2 
} from 'lucide-react';
import { lessonsApi } from '../api/services';

const ACTIONS = [
  { id: 'summarize', label: 'Executive Summary', icon: BookOpen, desc: 'Core lesson highlights' },
  { id: 'eli5', label: 'Explain Like I\'m 10', icon: Baby, desc: 'Simplified breakdown' },
  { id: 'examples', label: 'Real-world Examples', icon: Briefcase, desc: 'Practical scenarios' },
  { id: 'interview_questions', label: 'Interview Questions', icon: HelpCircle, desc: 'Technical questions' },
  { id: 'practice_questions', label: 'Practice Exercises', icon: CheckCircle2, desc: 'Interactive practice' },
  { id: 'key_formulas', label: 'Important Formulas', icon: Calculator, desc: 'Rules & equations' },
  { id: 'takeaways', label: 'Key Takeaways', icon: ListChecks, desc: 'Memory bullet points' },
  { id: 'common_mistakes', label: 'Common Mistakes', icon: AlertTriangle, desc: 'Pitfalls & solutions' },
];

export function AIStudyAssistant({ courseId, lessonId, lessonTitle }) {
  const [activeAction, setActiveAction] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleAction = async (actionId) => {
    setActiveAction(actionId);
    setLoading(true);
    setError(null);
    try {
      const data = await lessonsApi.studyAssistant(courseId, lessonId, actionId);
      setResult(data.answer);
    } catch (err) {
      console.error("AI Study Assistant error:", err);
      setError(err?.response?.data?.detail || "Failed to generate AI study output. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      background: 'var(--surface-dark, #1e293b)',
      borderRadius: '12px',
      border: '1px solid var(--border-color, #334155)',
      padding: '20px',
      marginTop: '24px',
      color: '#f8fafc',
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px' }}>
        <Sparkles style={{ color: '#38bdf8', width: '22px', height: '22px' }} />
        <h3 style={{ margin: 0, fontSize: '1.1rem', fontWeight: 600 }}>AI Study Assistant</h3>
      </div>

      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fill, minmax(180px, 1fr))',
        gap: '10px',
        marginBottom: '20px',
      }}>
        {ACTIONS.map((item) => {
          const Icon = item.icon;
          const isSelected = activeAction === item.id;
          return (
            <button
              key={item.id}
              onClick={() => handleAction(item.id)}
              disabled={loading}
              style={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'flex-start',
                padding: '12px',
                borderRadius: '8px',
                border: isSelected ? '1px solid #38bdf8' : '1px solid rgba(255,255,255,0.1)',
                background: isSelected ? 'rgba(56, 189, 248, 0.15)' : 'rgba(255,255,255,0.03)',
                color: '#f8fafc',
                cursor: loading ? 'not-allowed' : 'pointer',
                textAlign: 'left',
                transition: 'all 0.2s ease',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                <Icon style={{ width: '16px', height: '16px', color: '#38bdf8' }} />
                <span style={{ fontWeight: 600, fontSize: '0.85rem' }}>{item.label}</span>
              </div>
              <span style={{ fontSize: '0.75rem', opacity: 0.7 }}>{item.desc}</span>
            </button>
          );
        })}
      </div>

      {loading && (
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', padding: '20px', color: '#38bdf8' }}>
          <Loader2 style={{ animation: 'spin 1s linear infinite', width: '20px', height: '20px' }} />
          <span>Generating AI {ACTIONS.find(a => a.id === activeAction)?.label}...</span>
        </div>
      )}

      {error && (
        <div style={{ padding: '12px', borderRadius: '8px', background: 'rgba(239, 68, 68, 0.1)', color: '#f87171', border: '1px solid #ef4444' }}>
          {error}
        </div>
      )}

      {result && !loading && (
        <div style={{
          background: 'rgba(0,0,0,0.2)',
          borderRadius: '8px',
          padding: '16px',
          borderLeft: '4px solid #38bdf8',
          fontSize: '0.95rem',
          lineHeight: 1.6,
          whiteSpace: 'pre-wrap',
        }}>
          <h4 style={{ margin: '0 0 10px 0', fontSize: '1rem', color: '#38bdf8' }}>
            {ACTIONS.find(a => a.id === activeAction)?.label}
          </h4>
          <div>{result}</div>
        </div>
      )}
    </div>
  );
}
