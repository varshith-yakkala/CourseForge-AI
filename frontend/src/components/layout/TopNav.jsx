import React from 'react';
import { cn } from '@/utils/classNames';
import { useUIStore } from '@/store/useUIStore';
import { useAuthStore } from '@/store/useAuthStore';
import { Menu, Search, Bell } from 'lucide-react';
import { Avatar } from '@/components/ui/Avatar';
import { Dropdown } from '@/components/ui/Dropdown';
import { Breadcrumb } from './Breadcrumb';
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
          <Breadcrumb />
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
