/**
 * Export API module — Phase 3 implementation.
 */
import apiClient from '@/api/client'

export const exportApi = {
  exportPdf: (courseId) => apiClient.post(`/export/${courseId}/pdf`),
  exportMarkdown: (courseId) => apiClient.post(`/export/${courseId}/markdown`),
  getStatus: (exportId) => apiClient.get(`/export/${exportId}/status`),
}
