import os

files = {
    'frontend/src/components/layout/Sidebar.jsx': '''
import React from 'react';
import { NavLink } from 'react-router-dom';
import { cn } from '@/utils/classNames';
import { useUIStore } from '@/store/useUIStore';
import { LayoutDashboard, BookOpen, Search, BarChart3, Settings, Bookmark, Menu, ChevronLeft } from 'lucide-react';
import './Sidebar.css';

const NAV_ITEMS = [
  { icon: LayoutDashboard, label: 'Dashboard', path: '/dashboard' },
  { icon: BookOpen, label: 'Courses', path: '/courses' },
  { icon: Search, label: 'Search', path: '/search' },
  { icon: BarChart3, label: 'Analytics', path: '/analytics' },
];

const BOTTOM_ITEMS = [
  { icon: Bookmark, label: 'Bookmarks', path: '/bookmarks' },
  { icon: Settings, label: 'Settings', path: '/settings' },
];

export function Sidebar() {
  const isCollapsed = useUIStore((state) => state.isSidebarCollapsed);
  const toggleSidebar = useUIStore((state) => state.toggleSidebar);

  return (
    <aside className={cn('cf-sidebar', isCollapsed && 'cf-sidebar--collapsed')}>
      <div className="cf-sidebar-header">
        <div className="cf-sidebar-logo">
          <div className="cf-sidebar-logo-icon">C</div>
          <span className="cf-sidebar-logo-text">CourseForge AI</span>
        </div>
        <button className="cf-sidebar-toggle" onClick={toggleSidebar} aria-label="Toggle Sidebar">
          {isCollapsed ? <Menu size={18} /> : <ChevronLeft size={18} />}
        </button>
      </div>

      <nav className="cf-sidebar-nav">
        {NAV_ITEMS.map((item) => (
          <NavLink 
            key={item.path} 
            to={item.path}
            className={({ isActive }) => cn('cf-sidebar-item', isActive && 'cf-sidebar-item--active')}
            title={isCollapsed ? item.label : undefined}
          >
            <item.icon className="cf-sidebar-item-icon" />
            <span className="cf-sidebar-item-label">{item.label}</span>
          </NavLink>
        ))}
      </nav>

      <div className="cf-sidebar-spacer" />

      <nav className="cf-sidebar-nav cf-sidebar-nav--bottom">
        {BOTTOM_ITEMS.map((item) => (
          <NavLink 
            key={item.path} 
            to={item.path}
            className={({ isActive }) => cn('cf-sidebar-item', isActive && 'cf-sidebar-item--active')}
            title={isCollapsed ? item.label : undefined}
          >
            <item.icon className="cf-sidebar-item-icon" />
            <span className="cf-sidebar-item-label">{item.label}</span>
          </NavLink>
        ))}
      </nav>
    </aside>
  );
}
'''.lstrip(),

    'frontend/src/components/layout/Sidebar.css': '''
.cf-sidebar {
  width: var(--sidebar-width);
  height: 100vh;
  background-color: var(--bg-subtle);
  border-right: 1px solid var(--border-subtle);
  display: flex;
  flex-direction: column;
  transition: width var(--duration-moderate) var(--ease-default);
  overflow: hidden;
  flex-shrink: 0;
  position: sticky;
  top: 0;
  z-index: 100;
}

.cf-sidebar--collapsed {
  width: var(--sidebar-collapsed-width);
}

.cf-sidebar-header {
  height: var(--topbar-height);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 16px;
  border-bottom: 1px solid var(--border-subtle);
}

.cf-sidebar-logo {
  display: flex;
  align-items: center;
  gap: 12px;
  overflow: hidden;
}

.cf-sidebar-logo-icon {
  width: 32px;
  height: 32px;
  border-radius: var(--radius-sm);
  background: linear-gradient(135deg, var(--color-brand-400) 0%, var(--color-brand-600) 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  flex-shrink: 0;
}

.cf-sidebar-logo-text {
  font-weight: 600;
  color: var(--text-primary);
  white-space: nowrap;
  opacity: 1;
  transition: opacity var(--duration-fast) var(--ease-out);
}

.cf-sidebar--collapsed .cf-sidebar-logo-text {
  opacity: 0;
  pointer-events: none;
}

.cf-sidebar-toggle {
  color: var(--text-muted);
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: var(--radius-sm);
  transition: all var(--duration-fast) var(--ease-out);
  flex-shrink: 0;
}

.cf-sidebar-toggle:hover {
  background-color: var(--bg-overlay);
  color: var(--text-primary);
}

.cf-sidebar--collapsed .cf-sidebar-header {
  justify-content: center;
  padding: 0;
}

.cf-sidebar--collapsed .cf-sidebar-logo {
  display: none;
}

.cf-sidebar-nav {
  padding: 16px 12px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.cf-sidebar-spacer {
  flex: 1;
}

.cf-sidebar-item {
  display: flex;
  align-items: center;
  height: 36px;
  padding: 0 12px;
  border-radius: var(--radius-sm);
  color: var(--text-secondary);
  text-decoration: none;
  gap: 12px;
  transition: all var(--duration-fast) var(--ease-out);
  white-space: nowrap;
  overflow: hidden;
  border-left: 2px solid transparent;
}

.cf-sidebar-item:hover {
  background-color: var(--bg-overlay);
  color: var(--text-primary);
}

.cf-sidebar-item--active {
  background-color: rgba(124, 114, 255, 0.12);
  border-left-color: var(--color-brand-500);
  color: var(--color-brand-400);
}

.cf-sidebar-item-icon {
  width: 20px;
  height: 20px;
  flex-shrink: 0;
  stroke-width: 1.5px;
}

.cf-sidebar-item-label {
  font-size: var(--text-body-sm);
  font-weight: 500;
  transition: opacity var(--duration-fast) var(--ease-out);
}

.cf-sidebar--collapsed .cf-sidebar-item {
  padding: 0;
  justify-content: center;
  border-left: none; /* or keep it, but it moves icon off-center */
}

.cf-sidebar--collapsed .cf-sidebar-item--active {
  background-color: rgba(124, 114, 255, 0.12);
  border-left: 2px solid var(--color-brand-500);
  padding-left: 2px; /* adjust for border */
}

.cf-sidebar--collapsed .cf-sidebar-item-label {
  display: none;
}
'''.lstrip(),

    'frontend/src/components/layout/TopNav.jsx': '''
import React from 'react';
import { cn } from '@/utils/classNames';
import { useUIStore } from '@/store/useUIStore';
import { useAuthStore } from '@/store/useAuthStore';
import { Menu, Search, Bell } from 'lucide-react';
import { Avatar } from '@/components/ui/Avatar';
import { Dropdown } from '@/components/ui/Dropdown';
import './TopNav.css';

export function TopNav() {
  const setMobileMenu = useUIStore((state) => state.setMobileMenu);
  const setCommandPalette = useUIStore((state) => state.setCommandPalette);
  const user = useAuthStore((state) => state.user);
  const logout = useAuthStore((state) => state.logout);

  const userMenuItems = [
    { label: 'Profile Settings', onClick: () => console.log('Profile') },
    { divider: true },
    { label: 'Log out', danger: true, onClick: logout },
  ];

  return (
    <header className="cf-topnav">
      <div className="cf-topnav-left">
        <button 
          className="cf-topnav-mobile-toggle" 
          onClick={() => setMobileMenu(true)}
          aria-label="Open Mobile Menu"
        >
          <Menu size={20} />
        </button>
        <div className="cf-topnav-breadcrumbs">
          {/* Breadcrumbs will go here in next step */}
        </div>
      </div>
      
      <div className="cf-topnav-right">
        <button 
          className="cf-topnav-action"
          onClick={() => setCommandPalette(true)}
          aria-label="Search"
        >
          <Search size={18} />
          <span className="cf-topnav-kbd">⌘K</span>
        </button>
        
        <button className="cf-topnav-action cf-topnav-action--icon">
          <Bell size={18} />
        </button>

        <Dropdown 
          trigger={<div className="cf-topnav-avatar"><Avatar name={user?.full_name || 'User'} size="sm" /></div>}
          items={userMenuItems}
        />
      </div>
    </header>
  );
}
'''.lstrip(),

    'frontend/src/components/layout/TopNav.css': '''
.cf-topnav {
  height: var(--topbar-height);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 var(--space-6);
  background-color: var(--bg-base);
  border-bottom: 1px solid var(--border-subtle);
  position: sticky;
  top: 0;
  z-index: 90;
}

.cf-topnav-left, .cf-topnav-right {
  display: flex;
  align-items: center;
  gap: var(--space-4);
}

.cf-topnav-mobile-toggle {
  display: none;
  color: var(--text-secondary);
}

@media (max-width: 768px) {
  .cf-topnav-mobile-toggle {
    display: flex;
  }
}

.cf-topnav-action {
  display: flex;
  align-items: center;
  gap: 8px;
  height: 32px;
  padding: 0 12px;
  background-color: var(--bg-surface);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-sm);
  color: var(--text-secondary);
  font-size: var(--text-label-sm);
  transition: all var(--duration-fast) var(--ease-out);
}

.cf-topnav-action:hover {
  background-color: var(--bg-elevated);
  color: var(--text-primary);
  border-color: var(--border-strong);
}

.cf-topnav-action--icon {
  padding: 0;
  width: 32px;
  justify-content: center;
  background-color: transparent;
  border-color: transparent;
}
.cf-topnav-action--icon:hover {
  background-color: var(--bg-overlay);
}

.cf-topnav-kbd {
  font-family: var(--font-mono);
  background-color: var(--bg-overlay);
  padding: 2px 4px;
  border-radius: 4px;
  font-size: 10px;
  color: var(--text-muted);
}

.cf-topnav-avatar {
  cursor: pointer;
  transition: transform var(--duration-fast) var(--ease-out);
}
.cf-topnav-avatar:hover {
  transform: scale(1.05);
}
'''.lstrip(),

    'frontend/src/components/layout/AppLayout.jsx': '''
import React from 'react';
import { Outlet } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { TopNav } from './TopNav';
import { ToastContainer } from '@/components/ui/Toast';
import './AppLayout.css';

export function AppLayout() {
  return (
    <div className="cf-app-layout">
      <Sidebar />
      <div className="cf-app-main">
        <TopNav />
        <main className="cf-app-content">
          <Outlet />
        </main>
      </div>
      <ToastContainer />
      {/* MobileNav and CommandPalette will be added here */}
    </div>
  );
}
'''.lstrip(),

    'frontend/src/components/layout/AppLayout.css': '''
.cf-app-layout {
  display: flex;
  min-height: 100vh;
  width: 100%;
  background-color: var(--bg-base);
}

.cf-app-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0; /* Important for preventing flex children from overflowing */
}

.cf-app-content {
  flex: 1;
  padding: var(--space-8);
  width: 100%;
  max-width: var(--content-max-width);
  margin: 0 auto;
}

@media (max-width: 768px) {
  .cf-app-content {
    padding: var(--space-4);
    padding-bottom: calc(var(--space-4) + 60px); /* Space for mobile nav */
  }
}
'''.lstrip()
}

for path, content in files.items():
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

print("AppLayout, Sidebar, TopNav created successfully.")
