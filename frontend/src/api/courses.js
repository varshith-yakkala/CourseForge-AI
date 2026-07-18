/**
 * Courses API module — Phase 2 implementation.
 */
import apiClient from '@/api/client'

export const coursesApi = {
  list: () => apiClient.get('/courses'),
  get: (id) => apiClient.get(`/courses/${id}`),
  upload: (formData) => apiClient.post('/courses/upload', formData, { headers: { 'Content-Type': 'multipart/form-data' } }),
  getStatus: (id) => apiClient.get(`/courses/${id}/status`),
  update: (id, data) => apiClient.put(`/courses/${id}`, data),
  delete: (id) => apiClient.delete(`/courses/${id}`),
  getStructure: (id) => apiClient.get(`/courses/${id}/structure`),
}
