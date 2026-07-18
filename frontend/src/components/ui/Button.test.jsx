import React from 'react';
import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { Button } from './Button';

describe('Button', () => {
  it('renders children correctly', () => {
    render(<Button>Click me</Button>);
    expect(screen.getByText('Click me')).toBeInTheDocument();
  });

  it('applies variant classes correctly', () => {
    const { container } = render(<Button variant="danger">Delete</Button>);
    expect(container.firstChild).toHaveClass('cf-button--danger');
  });

  it('is disabled when loading', () => {
    render(<Button loading>Submit</Button>);
    const button = screen.getByRole('button');
    expect(button).toBeDisabled();
    expect(button).toHaveClass('cf-button--loading');
  });
});
