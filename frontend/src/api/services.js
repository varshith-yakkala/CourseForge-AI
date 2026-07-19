import { apiClient } from './client';

export const authApi = {
  login: async (credentials) => {
    const { data } = await apiClient.post('/auth/login', credentials);
    return data;
  },
  register: async (userData) => {
    const { data } = await apiClient.post('/auth/register', userData);
    return data;
  },
  getMe: async () => {
    const { data } = await apiClient.get('/auth/me');
    return data;
  },
};

export const coursesApi = {
  getAll: async () => {
    const { data } = await apiClient.get('/courses');
    return data;
  },
  getById: async (id) => {
    const { data } = await apiClient.get(`/courses/${id}`);
    return data;
  },
  create: async (courseData) => {
    const { data } = await apiClient.post('/courses', courseData);
    return data;
  },
  update: async (id, courseData) => {
    const { data } = await apiClient.put(`/courses/${id}`, courseData);
    return data;
  },
  delete: async (id) => {
    await apiClient.delete(`/courses/${id}`);
    return id;
  },
  generate: async (id) => {
    const { data } = await apiClient.post(`/courses/${id}/generate`);
    return data;
  },
  getStructure: async (id) => {
    const { data } = await apiClient.get(`/courses/${id}/structure`);
    return data;
  }
};

export const documentsApi = {
  upload: async (courseId, file, onUploadProgress) => {
    const formData = new FormData();
    formData.append('course_id', courseId);
    formData.append('file', file);
    
    const { data } = await apiClient.post('/documents/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress,
    });
    return data;
  },
  getById: async (id) => {
    const { data } = await apiClient.get(`/documents/${id}`);
    return data;
  },
  getByCourseId: async (courseId) => {
    const { data } = await apiClient.get(`/documents/course/${courseId}`);
    return data;
  },
  retry: async (id) => {
    const { data } = await apiClient.post(`/documents/${id}/retry`);
    return data;
  },
};

export const searchApi = {
  search: async (query, courseId = null) => {
    const { data } = await apiClient.post('/search', { query, course_id: courseId });
    return data;
  },
};

export const lessonsApi = {
  getLesson: async (courseId, lessonId) => {
    const { data } = await apiClient.get(`/courses/${courseId}/lessons/${lessonId}`);
    return data;
  },
  generate: async (courseId, lessonId) => {
    const { data } = await apiClient.post(`/courses/${courseId}/lessons/${lessonId}/generate`);
    return data;
  },
  regenerate: async (courseId, lessonId) => {
    const { data } = await apiClient.post(`/courses/${courseId}/lessons/${lessonId}/regenerate`);
    return data;
  },
  updateProgress: async (courseId, lessonId, progressData) => {
    const { data } = await apiClient.post(`/courses/${courseId}/lessons/${lessonId}/progress`, progressData);
    return data;
  },
  getCourseProgress: async (courseId) => {
    const { data } = await apiClient.get(`/courses/${courseId}/progress`);
    return data;
  },
  askTutor: async (courseId, lessonId, question) => {
    const { data } = await apiClient.post(`/courses/${courseId}/lessons/${lessonId}/ask`, { question });
    return data;
  },
};

