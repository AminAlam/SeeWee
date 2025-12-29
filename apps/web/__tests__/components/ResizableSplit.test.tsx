/**
 * Tests for ResizableSplit component
 */

import { render, screen, fireEvent } from '@testing-library/react';
import { ResizableSplit } from '@/components/ResizableSplit';

describe('ResizableSplit', () => {
  beforeEach(() => {
    // Mock localStorage
    const mockLocalStorage: Record<string, string> = {};
    jest.spyOn(Storage.prototype, 'getItem').mockImplementation(
      (key) => mockLocalStorage[key] || null
    );
    jest.spyOn(Storage.prototype, 'setItem').mockImplementation(
      (key, value) => { mockLocalStorage[key] = value; }
    );
  });

  it('renders left pane content', () => {
    render(
      <ResizableSplit
        storageKey="test.split"
        left={<div data-testid="left">Left Content</div>}
        right={<div data-testid="right">Right Content</div>}
      />
    );
    
    expect(screen.getByTestId('left')).toBeInTheDocument();
    expect(screen.getByText('Left Content')).toBeInTheDocument();
  });

  it('renders right pane content', () => {
    render(
      <ResizableSplit
        storageKey="test.split"
        left={<div data-testid="left">Left Content</div>}
        right={<div data-testid="right">Right Content</div>}
      />
    );
    
    expect(screen.getByTestId('right')).toBeInTheDocument();
    expect(screen.getByText('Right Content')).toBeInTheDocument();
  });

  it('renders only left pane when right is null', () => {
    render(
      <ResizableSplit
        storageKey="test.split"
        left={<div data-testid="left">Left Content</div>}
        right={null}
      />
    );
    
    expect(screen.getByTestId('left')).toBeInTheDocument();
    // Gutter should not be present when right is null
    expect(screen.queryByRole('separator')).not.toBeInTheDocument();
  });

  it('renders resize gutter', () => {
    render(
      <ResizableSplit
        storageKey="test.split"
        left={<div>Left</div>}
        right={<div>Right</div>}
      />
    );
    
    expect(screen.getByRole('separator')).toBeInTheDocument();
  });

  it('gutter has col-resize cursor', () => {
    render(
      <ResizableSplit
        storageKey="test.split"
        left={<div>Left</div>}
        right={<div>Right</div>}
      />
    );
    
    const gutter = screen.getByRole('separator');
    expect(gutter).toHaveStyle({ cursor: 'col-resize' });
  });

  it('saves ratio to localStorage', () => {
    const setItemSpy = jest.spyOn(Storage.prototype, 'setItem');
    
    render(
      <ResizableSplit
        storageKey="test.split"
        left={<div>Left</div>}
        right={<div>Right</div>}
      />
    );
    
    expect(setItemSpy).toHaveBeenCalledWith('test.split', expect.any(String));
  });

  it('loads ratio from localStorage', () => {
    const getItemSpy = jest.spyOn(Storage.prototype, 'getItem');
    
    render(
      <ResizableSplit
        storageKey="test.split"
        left={<div>Left</div>}
        right={<div>Right</div>}
      />
    );
    
    expect(getItemSpy).toHaveBeenCalledWith('test.split');
  });
});

