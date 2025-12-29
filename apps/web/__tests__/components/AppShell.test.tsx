/**
 * Tests for AppShell component
 */

import { render, screen, fireEvent } from '@testing-library/react';
import { AppShell } from '@/components/AppShell';

// Mock PreviewPane component
jest.mock('@/components/PreviewPane', () => ({
  PreviewPane: () => <div data-testid="preview-pane">Preview Pane</div>,
}));

// Mock ResizableSplit component
jest.mock('@/components/ResizableSplit', () => ({
  ResizableSplit: ({ left, right }: { left: React.ReactNode; right: React.ReactNode }) => (
    <div data-testid="resizable-split">
      <div data-testid="left-pane">{left}</div>
      <div data-testid="right-pane">{right}</div>
    </div>
  ),
}));

describe('AppShell', () => {
  it('renders children content', () => {
    render(
      <AppShell>
        <div data-testid="child-content">Test Content</div>
      </AppShell>
    );
    
    expect(screen.getByTestId('child-content')).toBeInTheDocument();
  });

  it('renders the SeeWee logo/brand', () => {
    render(
      <AppShell>
        <div>Content</div>
      </AppShell>
    );
    
    expect(screen.getByText('SeeWee')).toBeInTheDocument();
  });

  it('renders navigation links', () => {
    render(
      <AppShell>
        <div>Content</div>
      </AppShell>
    );
    
    expect(screen.getByText('Overview')).toBeInTheDocument();
    expect(screen.getByText('Entries')).toBeInTheDocument();
    expect(screen.getByText('Variants')).toBeInTheDocument();
    expect(screen.getByText('Profile')).toBeInTheDocument();
  });

  it('has clickable navigation items', () => {
    render(
      <AppShell>
        <div>Content</div>
      </AppShell>
    );
    
    const entriesLink = screen.getByText('Entries').closest('a');
    expect(entriesLink).toHaveAttribute('href', '/entries');
    
    const variantsLink = screen.getByText('Variants').closest('a');
    expect(variantsLink).toHaveAttribute('href', '/variants');
  });
});

