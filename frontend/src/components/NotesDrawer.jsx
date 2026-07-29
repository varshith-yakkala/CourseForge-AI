import React, { useState, useEffect } from 'react';
import { X, Plus, Trash2, Pin, Tag, Search, Highlighter } from 'lucide-react';
import { notesApi } from '../api/services';

const COLORS = [
  { id: 'yellow', hex: '#fef08a' },
  { id: 'green', hex: '#bbf7d0' },
  { id: 'blue', hex: '#bfdbfe' },
  { id: 'pink', hex: '#fbcfe8' },
];

export function NotesDrawer({ isOpen, onClose, courseId, lessonId }) {
  const [notes, setNotes] = useState([]);
  const [loading, setLoading] = useState(false);
  const [newContent, setNewContent] = useState('');
  const [highlightText, setHighlightText] = useState('');
  const [selectedColor, setSelectedColor] = useState('yellow');
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    if (isOpen && courseId) {
      fetchNotes();
    }
  }, [isOpen, courseId, lessonId]);

  const fetchNotes = async () => {
    setLoading(true);
    try {
      const data = await notesApi.getCourseNotes(courseId, lessonId);
      setNotes(data);
    } catch (err) {
      console.error("Failed to fetch notes:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async (e) => {
    e.preventDefault();
    if (!newContent.trim()) return;
    try {
      const created = await notesApi.createNote({
        course_id: courseId,
        lesson_id: lessonId,
        content: newContent.trim(),
        highlight_text: highlightText.trim() || null,
        color: selectedColor,
      });
      setNotes([created, ...notes]);
      setNewContent('');
      setHighlightText('');
    } catch (err) {
      console.error("Failed to create note:", err);
    }
  };

  const handleDelete = async (noteId) => {
    try {
      await notesApi.deleteNote(noteId);
      setNotes(notes.filter(n => n.id !== noteId));
    } catch (err) {
      console.error("Failed to delete note:", err);
    }
  };

  const handleTogglePin = async (note) => {
    try {
      const updated = await notesApi.updateNote(note.id, { is_pinned: !note.is_pinned });
      setNotes(notes.map(n => n.id === note.id ? updated : n));
    } catch (err) {
      console.error("Failed to pin note:", err);
    }
  };

  if (!isOpen) return null;

  const filteredNotes = notes.filter(n => 
    n.content.toLowerCase().includes(searchQuery.toLowerCase()) ||
    (n.highlight_text && n.highlight_text.toLowerCase().includes(searchQuery.toLowerCase()))
  );

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      right: 0,
      bottom: 0,
      width: '380px',
      background: '#0f172a',
      borderLeft: '1px solid #334155',
      zIndex: 1000,
      display: 'flex',
      flexDirection: 'column',
      color: '#f8fafc',
      boxShadow: '-4px 0 20px rgba(0,0,0,0.5)',
    }}>
      {/* Header */}
      <div style={{ padding: '16px', borderBottom: '1px solid #334155', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Highlighter style={{ color: '#38bdf8', width: '20px', height: '20px' }} />
          <h3 style={{ margin: 0, fontSize: '1.1rem' }}>Notes & Highlights</h3>
        </div>
        <button onClick={onClose} style={{ background: 'none', border: 'none', color: '#94a3b8', cursor: 'pointer' }}>
          <X style={{ width: '20px', height: '20px' }} />
        </button>
      </div>

      {/* Note Creation */}
      <form onSubmit={handleCreate} style={{ padding: '16px', borderBottom: '1px solid #334155' }}>
        <input 
          type="text" 
          placeholder="Optional highlight excerpt..." 
          value={highlightText}
          onChange={(e) => setHighlightText(e.target.value)}
          style={{ width: '100%', padding: '8px', marginBottom: '8px', borderRadius: '6px', border: '1px solid #334155', background: '#1e293b', color: '#fff', fontSize: '0.85rem' }}
        />
        <textarea
          rows={3}
          placeholder="Type your note content here..."
          value={newContent}
          onChange={(e) => setNewContent(e.target.value)}
          style={{ width: '100%', padding: '8px', borderRadius: '6px', border: '1px solid #334155', background: '#1e293b', color: '#fff', fontSize: '0.9rem', resize: 'vertical' }}
        />
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '10px' }}>
          <div style={{ display: 'flex', gap: '6px' }}>
            {COLORS.map(c => (
              <button
                key={c.id}
                type="button"
                onClick={() => setSelectedColor(c.id)}
                style={{
                  width: '18px',
                  height: '18px',
                  borderRadius: '50%',
                  background: c.hex,
                  border: selectedColor === c.id ? '2px solid #fff' : 'none',
                  cursor: 'pointer',
                }}
              />
            ))}
          </div>
          <button
            type="submit"
            style={{
              padding: '6px 12px',
              borderRadius: '6px',
              border: 'none',
              background: '#38bdf8',
              color: '#0f172a',
              fontWeight: 600,
              fontSize: '0.85rem',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '4px',
            }}
          >
            <Plus style={{ width: '14px', height: '14px' }} /> Save Note
          </button>
        </div>
      </form>

      {/* Search */}
      <div style={{ padding: '12px 16px', borderBottom: '1px solid #334155' }}>
        <div style={{ position: 'relative' }}>
          <Search style={{ position: 'absolute', left: '10px', top: '8px', width: '16px', height: '16px', color: '#64748b' }} />
          <input
            type="text"
            placeholder="Search notes..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            style={{ width: '100%', padding: '6px 10px 6px 32px', borderRadius: '6px', border: '1px solid #334155', background: '#1e293b', color: '#fff', fontSize: '0.85rem' }}
          />
        </div>
      </div>

      {/* Notes List */}
      <div style={{ flex: 1, overflowY: 'auto', padding: '16px', display: 'flex', flexDirection: 'column', gap: '12px' }}>
        {loading && <div style={{ color: '#94a3b8', fontSize: '0.9rem' }}>Loading notes...</div>}
        {!loading && filteredNotes.length === 0 && (
          <div style={{ color: '#64748b', fontSize: '0.85rem', textAlign: 'center', marginTop: '20px' }}>
            No notes yet. Add one above!
          </div>
        )}
        {filteredNotes.map(n => {
          const colorHex = COLORS.find(c => c.id === n.color)?.hex || '#fef08a';
          return (
            <div
              key={n.id}
              style={{
                background: '#1e293b',
                borderRadius: '8px',
                padding: '12px',
                borderLeft: `4px solid ${colorHex}`,
                position: 'relative',
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '6px' }}>
                <span style={{ fontSize: '0.75rem', color: '#64748b' }}>
                  {new Date(n.created_at).toLocaleDateString()}
                </span>
                <div style={{ display: 'flex', gap: '6px' }}>
                  <button onClick={() => handleTogglePin(n)} style={{ background: 'none', border: 'none', color: n.is_pinned ? '#38bdf8' : '#64748b', cursor: 'pointer' }}>
                    <Pin style={{ width: '14px', height: '14px' }} />
                  </button>
                  <button onClick={() => handleDelete(n.id)} style={{ background: 'none', border: 'none', color: '#ef4444', cursor: 'pointer' }}>
                    <Trash2 style={{ width: '14px', height: '14px' }} />
                  </button>
                </div>
              </div>
              {n.highlight_text && (
                <div style={{ fontStyle: 'italic', fontSize: '0.8rem', color: '#cbd5e1', background: 'rgba(255,255,255,0.05)', padding: '6px', borderRadius: '4px', marginBottom: '6px' }}>
                  "{n.highlight_text}"
                </div>
              )}
              <div style={{ fontSize: '0.9rem', lineHeight: 1.5, color: '#f8fafc' }}>
                {n.content}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
