import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { cn } from '@/utils/classNames';
import { useUIStore } from '@/store/useUIStore';
import { Search, FileText, Settings, BookOpen } from 'lucide-react';
import { Modal } from '@/components/ui/Modal';
import './CommandPalette.css';

const COMMANDS = [
  { id: '1', title: 'Go to Dashboard', icon: BookOpen, path: '/dashboard' },
  { id: '2', title: 'Search Courses', icon: Search, path: '/courses' },
  { id: '3', title: 'View Analytics', icon: FileText, path: '/analytics' },
  { id: '4', title: 'Settings', icon: Settings, path: '/settings' },
];

export function CommandPalette() {
  const isOpen = useUIStore((state) => state.isCommandPaletteOpen);
  const setOpen = useUIStore((state) => state.setCommandPalette);
  const [query, setQuery] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'k' && (e.metaKey || e.ctrlKey)) {
        e.preventDefault();
        setOpen(!isOpen);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, setOpen]);

  const filteredCommands = COMMANDS.filter((cmd) =>
    cmd.title.toLowerCase().includes(query.toLowerCase())
  );

  const handleSelect = (path) => {
    navigate(path);
    setOpen(false);
    setQuery('');
  };

  if (!isOpen) return null;

  return (
    <Modal isOpen={isOpen} onClose={() => setOpen(false)} size="md" className="cf-command-palette">
      <div className="cf-command-header">
        <Search className="cf-command-icon" size={20} />
        <input
          autoFocus
          className="cf-command-input"
          placeholder="Type a command or search..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
      </div>
      <div className="cf-command-list">
        {filteredCommands.length === 0 ? (
          <div className="cf-command-empty">No results found.</div>
        ) : (
          filteredCommands.map((cmd) => (
            <button
              key={cmd.id}
              className="cf-command-item"
              onClick={() => handleSelect(cmd.path)}
            >
              <cmd.icon size={18} className="cf-command-item-icon" />
              <span>{cmd.title}</span>
            </button>
          ))
        )}
      </div>
    </Modal>
  );
}
