import React from 'react';
import { Outlet } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { TopNav } from './TopNav';
import { ToastContainer } from '@/components/ui/Toast';
import { CommandPalette } from './CommandPalette';
import { MobileNav } from './MobileNav';
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
      <CommandPalette />
      <MobileNav />
    </div>
  );
}
