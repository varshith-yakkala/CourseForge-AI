/**
 * Progress API module — Phase 2 implementation.
 */
import apiClient from '@/api/client'

export const progressApi = {
  recordEvent: (data) => apiClient.post('/progress/event', data),
  getCourseProgress: (courseId) => apiClient.get(`/progress/courses/${courseId}`),
}
