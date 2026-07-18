import os

files = {
    'frontend/src/utils/classNames.js': '''
import { clsx } from "clsx";

export function cn(...inputs) {
  return clsx(inputs);
}
'''.lstrip(),

    'frontend/src/hooks/useMediaQuery.js': '''
import { useState, useEffect } from "react";

export function useMediaQuery(query) {
  const [matches, setMatches] = useState(false);

  useEffect(() => {
    const media = window.matchMedia(query);
    if (media.matches !== matches) {
      setMatches(media.matches);
    }
    const listener = () => setMatches(media.matches);
    window.addEventListener("resize", listener);
    return () => window.removeEventListener("resize", listener);
  }, [matches, query]);

  return matches;
}
'''.lstrip(),

    'frontend/src/store/useThemeStore.js': '''
import { create } from 'zustand';

export const useThemeStore = create((set) => ({
  theme: 'dark', // MVP default is dark
  setTheme: (theme) => {
    document.documentElement.setAttribute('data-theme', theme);
    set({ theme });
  },
  toggleTheme: () => set((state) => {
    const newTheme = state.theme === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', newTheme);
    return { theme: newTheme };
  })
}));
'''.lstrip(),

    'frontend/src/store/useUIStore.js': '''
import { create } from 'zustand';

export const useUIStore = create((set) => ({
  isSidebarCollapsed: false,
  isMobileMenuOpen: false,
  isCommandPaletteOpen: false,
  toggleSidebar: () => set((state) => ({ isSidebarCollapsed: !state.isSidebarCollapsed })),
  setMobileMenu: (isOpen) => set({ isMobileMenuOpen: isOpen }),
  setCommandPalette: (isOpen) => set({ isCommandPaletteOpen: isOpen }),
}));
'''.lstrip(),

    'frontend/src/store/useNotificationStore.js': '''
import { create } from 'zustand';

export const useNotificationStore = create((set) => ({
  notifications: [],
  addNotification: (notification) => {
    const id = Date.now().toString();
    set((state) => ({
      notifications: [{ ...notification, id }, ...state.notifications]
    }));
    if (notification.duration !== Infinity) {
      setTimeout(() => {
        set((state) => ({
          notifications: state.notifications.filter((n) => n.id !== id)
        }));
      }, notification.duration || 4000);
    }
  },
  removeNotification: (id) => set((state) => ({
    notifications: state.notifications.filter((n) => n.id !== id)
  }))
}));
'''.lstrip(),

    'frontend/src/store/useAuthStore.js': '''
import { create } from 'zustand';

export const useAuthStore = create((set) => ({
  user: null,
  token: null,
  isAuthenticated: false,
  login: (userData, token) => set({ user: userData, token, isAuthenticated: true }),
  logout: () => set({ user: null, token: null, isAuthenticated: false }),
}));
'''.lstrip()
}

for path, content in files.items():
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

print("Stores and utilities created successfully.")
