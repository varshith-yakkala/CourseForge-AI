import React from 'react';
import { NavLink } from 'react-router-dom';
import { cn } from '@/utils/classNames';
import { useUIStore } from '@/store/useUIStore';
import { LayoutDashboard, BookOpen, Search, BarChart3, Settings, Bookmark, Menu, ChevronLeft, Target, Calendar } from 'lucide-react';
import './Sidebar.css';

const NAV_ITEMS = [
  { icon: LayoutDashboard, label: 'Dashboard', path: '/dashboard' },
  { icon: BookOpen, label: 'Courses', path: '/courses' },
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
