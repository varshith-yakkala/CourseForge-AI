import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { BrowserRouter } from 'react-router-dom';
import LoginPage from '../pages/LoginPage';

// Mock the auth store
vi.mock('@/store/useAuthStore', () => ({
  useAuthStore: () => vi.fn()
}));

// Mock the notification store
vi.mock('@/store/useNotificationStore', () => ({
  useNotificationStore: () => vi.fn()
}));

describe('LoginPage Forms', () => {
  it('prevents submission if required fields are empty', () => {
    render(
      <BrowserRouter>
        <LoginPage />
      </BrowserRouter>
    );
    
    const emailInput = screen.getByLabelText(/Email address/i);
    const passwordInput = screen.getByLabelText(/Password/i);
    const submitButton = screen.getByRole('button', { name: /Log in/i });

    expect(emailInput).toBeRequired();
    expect(passwordInput).toBeRequired();
    expect(passwordInput).toHaveAttribute('minLength', '8');
  });
});
