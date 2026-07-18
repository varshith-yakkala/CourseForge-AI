import os

files = {
    'frontend/src/components/layout/CommandPalette.jsx': '''
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
'''.lstrip(),

    'frontend/src/components/layout/CommandPalette.css': '''
.cf-command-palette {
  padding: 0;
  overflow: hidden;
}

.cf-command-palette .cf-modal-body {
  padding: 0;
}

.cf-command-header {
  display: flex;
  align-items: center;
  padding: 0 16px;
  border-bottom: 1px solid var(--border-subtle);
}

.cf-command-icon {
  color: var(--text-muted);
}

.cf-command-input {
  flex: 1;
  height: 56px;
  background: transparent;
  border: none;
  outline: none;
  padding: 0 12px;
  font-size: var(--text-body-lg);
  color: var(--text-primary);
}

.cf-command-input::placeholder {
  color: var(--text-muted);
}

.cf-command-list {
  max-height: 300px;
  overflow-y: auto;
  padding: 8px;
}

.cf-command-item {
  display: flex;
  align-items: center;
  width: 100%;
  padding: 12px 16px;
  background: transparent;
  border-radius: var(--radius-sm);
  color: var(--text-secondary);
  font-size: var(--text-body-md);
  transition: all var(--duration-fast) var(--ease-out);
}

.cf-command-item:hover, .cf-command-item:focus {
  background-color: var(--bg-overlay);
  color: var(--text-primary);
  outline: none;
}

.cf-command-item-icon {
  margin-right: 12px;
  color: var(--text-muted);
}

.cf-command-item:hover .cf-command-item-icon {
  color: var(--text-primary);
}

.cf-command-empty {
  padding: 32px;
  text-align: center;
  color: var(--text-muted);
  font-size: var(--text-body-md);
}
'''.lstrip(),

    'frontend/src/components/layout/MobileNav.jsx': '''
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
'''.lstrip(),

    'frontend/src/components/layout/MobileNav.css': '''
.cf-mobile-nav {
  display: none;
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  height: 60px;
  background-color: var(--bg-surface);
  border-top: 1px solid var(--border-subtle);
  z-index: 100;
  padding-bottom: env(safe-area-inset-bottom);
}

@media (max-width: 768px) {
  .cf-mobile-nav {
    display: flex;
    justify-content: space-around;
    align-items: center;
  }
}

.cf-mobile-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 4px;
  width: 100%;
  height: 100%;
  color: var(--text-muted);
  transition: color var(--duration-fast) var(--ease-out);
}

.cf-mobile-icon {
  width: 20px;
  height: 20px;
}

.cf-mobile-label {
  font-size: 10px;
  font-weight: 500;
}

.cf-mobile-item--active {
  color: var(--color-brand-400);
}
'''.lstrip(),

    'frontend/src/components/layout/Footer.jsx': '''
import React from 'react';
import './Footer.css';

export function Footer() {
  return (
    <footer className="cf-footer">
      <div className="cf-footer-content container">
        <div className="cf-footer-logo">CourseForge AI</div>
        <div className="cf-footer-links">
          <a href="#">Privacy</a>
          <a href="#">Terms</a>
          <a href="#">Help</a>
        </div>
      </div>
    </footer>
  );
}
'''.lstrip(),

    'frontend/src/components/layout/Footer.css': '''
.cf-footer {
  width: 100%;
  border-top: 1px solid var(--border-subtle);
  background-color: var(--bg-base);
  padding: 32px 0;
  margin-top: auto;
}

.cf-footer-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.cf-footer-logo {
  font-weight: 700;
  color: var(--text-secondary);
}

.cf-footer-links {
  display: flex;
  gap: 24px;
}

.cf-footer-links a {
  color: var(--text-muted);
  font-size: var(--text-label-sm);
}

.cf-footer-links a:hover {
  color: var(--text-primary);
}
'''.lstrip(),

    'frontend/src/components/layout/Breadcrumb.jsx': '''
import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { ChevronRight, Home } from 'lucide-react';
import './Breadcrumb.css';

export function Breadcrumb({ customPath }) {
  const location = useLocation();
  const paths = location.pathname.split('/').filter(Boolean);

  // Auto-generate breadcrumbs if customPath isn't provided
  const breadcrumbs = customPath || paths.map((path, index) => {
    const url = /;
    return {
      label: path.charAt(0).toUpperCase() + path.slice(1).replace('-', ' '),
      url
    };
  });

  return (
    <nav className="cf-breadcrumb" aria-label="Breadcrumb">
      <ol className="cf-breadcrumb-list">
        <li className="cf-breadcrumb-item">
          <Link to="/dashboard" className="cf-breadcrumb-link">
            <Home size={14} />
          </Link>
        </li>
        {breadcrumbs.map((bc, idx) => (
          <React.Fragment key={bc.url}>
            <ChevronRight size={14} className="cf-breadcrumb-separator" />
            <li className="cf-breadcrumb-item">
              {idx === breadcrumbs.length - 1 ? (
                <span className="cf-breadcrumb-current" aria-current="page">
                  {bc.label}
                </span>
              ) : (
                <Link to={bc.url} className="cf-breadcrumb-link">
                  {bc.label}
                </Link>
              )}
            </li>
          </React.Fragment>
        ))}
      </ol>
    </nav>
  );
}
'''.lstrip(),

    'frontend/src/components/layout/Breadcrumb.css': '''
.cf-breadcrumb {
  display: flex;
  align-items: center;
}

.cf-breadcrumb-list {
  display: flex;
  align-items: center;
  gap: 8px;
  list-style: none;
  margin: 0;
  padding: 0;
}

.cf-breadcrumb-item {
  display: flex;
  align-items: center;
}

.cf-breadcrumb-link {
  color: var(--text-muted);
  font-size: var(--text-label-md);
  font-weight: 500;
  display: flex;
  align-items: center;
  transition: color var(--duration-fast) var(--ease-out);
}

.cf-breadcrumb-link:hover {
  color: var(--text-primary);
}

.cf-breadcrumb-separator {
  color: var(--border-strong);
}

.cf-breadcrumb-current {
  color: var(--text-primary);
  font-size: var(--text-label-md);
  font-weight: 500;
}
'''.lstrip()
}

for path, content in files.items():
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

print("CommandPalette, MobileNav, Footer, Breadcrumb created successfully.")
