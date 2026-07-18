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
