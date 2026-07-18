import { create } from 'zustand';

export const useUIStore = create((set) => ({
  isSidebarCollapsed: false,
  isMobileMenuOpen: false,
  isCommandPaletteOpen: false,
  toggleSidebar: () => set((state) => ({ isSidebarCollapsed: !state.isSidebarCollapsed })),
  setMobileMenu: (isOpen) => set({ isMobileMenuOpen: isOpen }),
  setCommandPalette: (isOpen) => set({ isCommandPaletteOpen: isOpen }),
}));
