import { describe, it, expect, vi } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useCourseDocument } from '../api/hooks';
import { documentsApi } from '../api/services';

vi.mock('../api/services', () => ({
  documentsApi: {
    getByCourseId: vi.fn(),
  },
}));

describe('useCourseDocument polling', () => {
  it('should poll if status is processing', async () => {
    const queryClient = new QueryClient();
    const wrapper = ({ children }) => (
      <QueryClientProvider client={queryClient}>
        {children}
      </QueryClientProvider>
    );

    documentsApi.getByCourseId.mockResolvedValueOnce({ id: '1', index_status: 'processing' });
    
    const { result } = renderHook(() => useCourseDocument('course1'), { wrapper });
    
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    
    expect(result.current.data.index_status).toBe('processing');
    // React Query refetchInterval will handle the polling based on this data state.
  });
});
