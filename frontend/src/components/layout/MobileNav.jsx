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
