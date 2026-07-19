import React from 'react';
import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import FlashcardsPage from '../pages/FlashcardsPage';

vi.mock('react-router-dom', () => ({
  useParams: () => ({ courseId: 'c1' }),
  useNavigate: () => vi.fn(),
}));

vi.mock('../api/hooks', () => ({
  useFlashcards: () => ({
    data: [
      { id: 'fc1', front: 'What is Python?', back: 'Interpreted programming language.' },
    ],
    isLoading: false,
    isError: false,
  }),
  useReviewFlashcard: () => ({
    mutateAsync: vi.fn(),
    isPending: false,
  }),
}));

describe('FlashcardsPage', () => {
  it('renders flashcard front concept correctly', () => {
    const queryClient = new QueryClient();
    render(
      <QueryClientProvider client={queryClient}>
        <FlashcardsPage />
      </QueryClientProvider>
    );

    expect(screen.getByText(/What is Python\?/i)).toBeDefined();
  });
});
