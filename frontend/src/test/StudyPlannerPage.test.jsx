import React from 'react';
import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import StudyPlannerPage from '../pages/StudyPlannerPage';

vi.mock('react-router-dom', () => ({
  useParams: () => ({ courseId: 'c1' }),
  useNavigate: () => vi.fn(),
}));

vi.mock('../api/hooks', () => ({
  useCourse: () => ({ data: { title: 'Python 101' }, isLoading: false }),
  usePlannerSchedule: () => ({
    data: {
      daily_goal_min: 30,
      remaining_hours: 4.5,
      remaining_uncompleted_lessons: 3,
      schedule_blocks: [{ day_name: 'Mon', title: 'Study Lesson 1', activity_type: 'lesson', estimated_mins: 30 }],
    },
    isLoading: false,
  }),
  usePredictions: () => ({
    data: { estimated_completion_date: '2026-08-01', on_time_probability_pct: 85, confidence_level: 'High' },
    isLoading: false,
  }),
  useUpdatePlannerPlan: () => ({ mutateAsync: vi.fn(), isPending: false }),
}));

describe('StudyPlannerPage', () => {
  it('renders adaptive study planner headers and predictions correctly', () => {
    const queryClient = new QueryClient();
    render(
      <QueryClientProvider client={queryClient}>
        <StudyPlannerPage />
      </QueryClientProvider>
    );

    expect(screen.getByText(/Adaptive AI Study Planner/i)).toBeDefined();
    expect(screen.getByText(/2026-08-01/i)).toBeDefined();
  });
});
