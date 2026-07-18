import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { coursesApi, documentsApi, searchApi } from './services';

// Course Hooks
export const useCourses = () => {
  return useQuery({
    queryKey: ['courses'],
    queryFn: coursesApi.getAll,
    // Poll every 5s if any course is processing
    refetchInterval: (query) => {
      const isProcessing = query.state?.data?.some(c => c.status === 'processing' || c.status === 'generating_outline');
      return isProcessing ? 5000 : false;
    }
  });
};

export const useCourse = (id) => {
  return useQuery({
    queryKey: ['courses', id],
    queryFn: () => coursesApi.getById(id),
    enabled: !!id,
    refetchInterval: (query) => {
      return (query.state?.data?.status === 'processing' || query.state?.data?.status === 'generating_outline') ? 3000 : false;
    }
  });
};

export const useCreateCourse = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: coursesApi.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['courses'] });
    },
  });
};

export const useDeleteCourse = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: coursesApi.delete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['courses'] });
    },
  });
};

export const useGenerateCourse = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: coursesApi.generate,
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['courses', data.id] });
      queryClient.invalidateQueries({ queryKey: ['courses'] });
    },
  });
};

export const useCourseStructure = (id) => {
  return useQuery({
    queryKey: ['courses', id, 'structure'],
    queryFn: () => coursesApi.getStructure(id),
    enabled: !!id,
  });
};

// Document Hooks
export const useUploadDocument = () => {
  return useMutation({
    mutationFn: ({ courseId, file, onUploadProgress }) => 
      documentsApi.upload(courseId, file, onUploadProgress),
  });
};

export const useCourseDocument = (courseId) => {
  return useQuery({
    queryKey: ['documents', 'course', courseId],
    queryFn: () => documentsApi.getByCourseId(courseId),
    enabled: !!courseId,
    refetchInterval: (query) => {
      return query.state?.data?.index_status === 'processing' || query.state?.data?.index_status === 'pending' ? 3000 : false;
    }
  });
};

export const useDocument = (id) => {
  return useQuery({
    queryKey: ['documents', id],
    queryFn: () => documentsApi.getById(id),
    enabled: !!id,
    refetchInterval: (query) => {
      return query.state?.data?.index_status === 'processing' || query.state?.data?.index_status === 'pending' ? 3000 : false;
    }
  });
};

export const useRetryDocument = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: documentsApi.retry,
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['documents', data.id] });
      queryClient.invalidateQueries({ queryKey: ['courses'] });
    },
  });
};

// Search Hooks
export const useSearch = () => {
  return useMutation({
    mutationFn: ({ query, courseId }) => searchApi.search(query, courseId),
  });
};
