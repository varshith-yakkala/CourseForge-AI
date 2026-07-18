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
