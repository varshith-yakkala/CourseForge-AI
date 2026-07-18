/**
 * Analytics API module — Phase 2 implementation.
 */
import apiClient from '@/api/client'

export const analyticsApi = {
  getDashboardStats: () => apiClient.get('/analytics/dashboard'),
  getHeatmap: () => apiClient.get('/analytics/heatmap'),
  getTopicPerformance: (courseId) => apiClient.get(`/analytics/courses/${courseId}/performance`),
}
