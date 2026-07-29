import React, { useState, useEffect } from 'react';
import { Search, X, Sparkles, ChevronDown, ChevronUp, FileText, Loader2, BookOpen } from 'lucide-react';
import { searchApi } from '../api/services';

export function AISearchModal({ isOpen, onClose, courseId }) {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [showSources, setShowSources] = useState(false);
  const [persona, setPersona] = useState('intermediate');
  const [style, setStyle] = useState('detailed');

  useEffect(() => {
    const handleKeyDown = (e) => {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault();
        if (isOpen) onClose();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;
    setLoading(true);
    setResult(null);
    try {
      const data = await searchApi.aiSearch(query.trim(), courseId, persona, style);
      setResult(data);
    } catch (err) {
      console.error("AI Search failed:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      position: 'fixed',
      top: 0, left: 0, right: 0, bottom: 0,
      background: 'rgba(0,0,0,0.75)',
      backdropFilter: 'blur(4px)',
      zIndex: 2000,
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'flex-start',
      paddingTop: '60px',
    }}>
      <div style={{
        background: '#0f172a',
        border: '1px solid #334155',
        borderRadius: '12px',
        width: '90%',
        maxWidth: '750px',
        maxHeight: '85vh',
        display: 'flex',
        flexDirection: 'column',
        boxShadow: '0 20px 50px rgba(0,0,0,0.6)',
        color: '#f8fafc',
        overflow: 'hidden',
      }}>
        {/* Top Bar */}
        <div style={{ padding: '16px', borderBottom: '1px solid #334155', display: 'flex', alignItems: 'center', gap: '10px' }}>
          <Sparkles style={{ color: '#38bdf8', width: '22px', height: '22px' }} />
          <form onSubmit={handleSearch} style={{ flex: 1, display: 'flex', gap: '10px' }}>
            <input
              type="text"
              placeholder="Ask Course AI anything... (Cmd/Ctrl + K)"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              autoFocus
              style={{
                flex: 1,
                background: 'transparent',
                border: 'none',
                color: '#fff',
                fontSize: '1.1rem',
                outline: 'none',
              }}
            />
            <button
              type="submit"
              disabled={loading}
              style={{
                padding: '6px 16px',
                borderRadius: '6px',
                background: '#38bdf8',
                color: '#0f172a',
                border: 'none',
                fontWeight: 600,
                cursor: loading ? 'not-allowed' : 'pointer',
              }}
            >
              Search
            </button>
          </form>
          <button onClick={onClose} style={{ background: 'none', border: 'none', color: '#94a3b8', cursor: 'pointer' }}>
            <X style={{ width: '22px', height: '22px' }} />
          </button>
        </div>

        {/* Persona & Style Selector */}
        <div style={{ padding: '10px 16px', background: '#1e293b', display: 'flex', gap: '16px', alignItems: 'center', borderBottom: '1px solid #334155', fontSize: '0.85rem' }}>
          <div>
            <span style={{ color: '#94a3b8', marginRight: '6px' }}>Level:</span>
            <select value={persona} onChange={(e) => setPersona(e.target.value)} style={{ background: '#0f172a', color: '#fff', border: '1px solid #334155', borderRadius: '4px', padding: '2px 6px' }}>
              <option value="beginner">Beginner</option>
              <option value="intermediate">Intermediate</option>
              <option value="expert">Expert</option>
              <option value="interview">Interview Mode</option>
            </select>
          </div>
          <div>
            <span style={{ color: '#94a3b8', marginRight: '6px' }}>Style:</span>
            <select value={style} onChange={(e) => setStyle(e.target.value)} style={{ background: '#0f172a', color: '#fff', border: '1px solid #334155', borderRadius: '4px', padding: '2px 6px' }}>
              <option value="detailed">Detailed</option>
              <option value="shorter">Concise</option>
              <option value="examples">Use Examples</option>
              <option value="analogies">Use Analogies</option>
            </select>
          </div>
        </div>

        {/* Content Body */}
        <div style={{ flex: 1, overflowY: 'auto', padding: '20px' }}>
          {loading && (
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '10px', padding: '40px', color: '#38bdf8' }}>
              <Loader2 style={{ animation: 'spin 1s linear infinite', width: '24px', height: '24px' }} />
              <span>Synthesizing AI Answer with hybrid RAG context...</span>
            </div>
          )}

          {result && !loading && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              {/* Direct Summary */}
              <div style={{ background: 'rgba(56, 189, 248, 0.1)', borderLeft: '4px solid #38bdf8', padding: '14px', borderRadius: '6px' }}>
                <h4 style={{ margin: '0 0 6px 0', color: '#38bdf8', fontSize: '0.95rem' }}>Direct Summary</h4>
                <div style={{ fontSize: '1rem', lineHeight: 1.5 }}>{result.summary}</div>
              </div>

              {/* Detailed Breakdown */}
              <div style={{ background: '#1e293b', padding: '16px', borderRadius: '8px', border: '1px solid #334155' }}>
                <h4 style={{ margin: '0 0 10px 0', fontSize: '0.95rem', color: '#94a3b8' }}>Synthesized Explanation</h4>
                <div style={{ fontSize: '0.95rem', lineHeight: 1.6, whiteSpace: 'pre-wrap' }}>
                  {result.explanation}
                </div>
              </div>

              {/* Key Points */}
              {result.key_points && result.key_points.length > 0 && (
                <div style={{ background: '#1e293b', padding: '16px', borderRadius: '8px', border: '1px solid #334155' }}>
                  <h4 style={{ margin: '0 0 10px 0', fontSize: '0.95rem', color: '#94a3b8' }}>Key Points</h4>
                  <ul style={{ margin: 0, paddingLeft: '20px', lineHeight: 1.6 }}>
                    {result.key_points.map((pt, i) => (
                      <li key={i} style={{ marginBottom: '4px' }}>{pt}</li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Collapsible Retrieved Sources */}
              <div style={{ border: '1px solid #334155', borderRadius: '8px', overflow: 'hidden' }}>
                <button
                  onClick={() => setShowSources(!showSources)}
                  style={{
                    width: '100%',
                    padding: '12px 16px',
                    background: '#1e293b',
                    border: 'none',
                    color: '#94a3b8',
                    display: 'flex',
                    justify: 'space-between',
                    alignItems: 'center',
                    cursor: 'pointer',
                    fontSize: '0.9rem',
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <FileText style={{ width: '16px', height: '16px' }} />
                    <span>View Retrieved Sources ({result.retrieved_sources?.length || 0} Chunks)</span>
                  </div>
                  {showSources ? <ChevronUp style={{ width: '16px', height: '16px' }} /> : <ChevronDown style={{ width: '16px', height: '16px' }} />}
                </button>

                {showSources && (
                  <div style={{ padding: '16px', background: '#0f172a', display: 'flex', flexDirection: 'column', gap: '12px' }}>
                    {result.retrieved_sources?.map((src) => (
                      <div key={src.source_id} style={{ background: '#1e293b', padding: '12px', borderRadius: '6px', fontSize: '0.85rem' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', color: '#38bdf8', marginBottom: '4px', fontWeight: 600 }}>
                          <span>📄 {src.file_name} {src.page ? `(Page ${src.page})` : ''}</span>
                          <span>Score: {src.similarity_score}</span>
                        </div>
                        <div style={{ color: '#cbd5e1', fontStyle: 'italic', lineHeight: 1.4 }}>
                          "{src.snippet}"
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
