/**
 * Lessons API module — Phase 2 implementation.
 */
import apiClient from '@/api/client'

export const lessonsApi = {
  get: (id) => apiClient.get(`/lessons/${id}`),
  getTopic: (id) => apiClient.get(`/topics/${id}`),
  markComplete: (topicId) => apiClient.post(`/progress/event`, { entity_type: 'topic', entity_id: topicId, status: 'completed' }),
}
