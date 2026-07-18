import { describe, it, expect, beforeEach } from 'vitest';
import { useAuthStore } from '../store/useAuthStore';

describe('useAuthStore', () => {
  beforeEach(() => {
    // Reset store state before each test
    useAuthStore.setState({ user: null, token: null, isAuthenticated: false });
  });

  it('should start with default state', () => {
    const state = useAuthStore.getState();
    expect(state.user).toBeNull();
    expect(state.token).toBeNull();
    expect(state.isAuthenticated).toBe(false);
  });

  it('should authenticate user on login', () => {
    const { login } = useAuthStore.getState();
    const mockUser = { id: 1, name: 'Test User' };
    const mockToken = 'jwt-token';
    
    login(mockUser, mockToken);
    
    const state = useAuthStore.getState();
    expect(state.user).toEqual(mockUser);
    expect(state.token).toBe(mockToken);
    expect(state.isAuthenticated).toBe(true);
  });

  it('should clear state on logout', () => {
    const { login, logout } = useAuthStore.getState();
    login({ id: 1 }, 'token');
    
    logout();
    
    const state = useAuthStore.getState();
    expect(state.user).toBeNull();
    expect(state.token).toBeNull();
    expect(state.isAuthenticated).toBe(false);
  });
});
