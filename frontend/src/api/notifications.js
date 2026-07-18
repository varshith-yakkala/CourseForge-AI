/**
 * Notifications API module — Phase 2 implementation.
 */
import apiClient from '@/api/client'

export const notificationsApi = {
  list: () => apiClient.get('/notifications'),
  markRead: (id) => apiClient.patch(`/notifications/${id}/read`),
  markAllRead: () => apiClient.patch('/notifications/read-all'),
  delete: (id) => apiClient.delete(`/notifications/${id}`),
}
