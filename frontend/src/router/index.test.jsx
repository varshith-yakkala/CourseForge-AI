import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import AppRouter from '@/router'

describe('AppRouter', () => {
  it('renders the 404 page for unknown routes', () => {
    render(
      <MemoryRouter initialEntries={['/unknown-random-route']}>
        <AppRouter />
      </MemoryRouter>
    )
    
    expect(screen.getByText("This page doesn't exist")).toBeInTheDocument()
  })

  it('redirects unauthenticated users to login from protected routes', () => {
    render(
      <MemoryRouter initialEntries={['/dashboard']}>
        <AppRouter />
      </MemoryRouter>
    )
    
    // Should see the login page because of ProtectedRoute
    expect(screen.getByText('Log in to your account')).toBeInTheDocument()
  })
})
