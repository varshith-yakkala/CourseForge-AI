import React from 'react';
import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { MarkdownViewer } from '../components/ui/MarkdownViewer';

describe('MarkdownViewer', () => {
  it('renders markdown heading and content correctly', () => {
    const markdown = '# Test Heading\n\nThis is a paragraph of **bold** text.';
    render(<MarkdownViewer content={markdown} />);
    
    expect(screen.getByRole('heading', { level: 1, name: 'Test Heading' })).toBeDefined();
    expect(screen.getByText(/paragraph of/i)).toBeDefined();
  });

  it('renders null when content is empty', () => {
    const { container } = render(<MarkdownViewer content="" />);
    expect(container.firstChild).toBeNull();
  });
});
