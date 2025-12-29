/**
 * Tests for PreviewPane component
 */

import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { PreviewPane } from '@/components/PreviewPane';

describe('PreviewPane', () => {
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

  it('renders preview header', async () => {
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => [],
    });

    render(<PreviewPane />);
    
    expect(screen.getByText('Live Preview')).toBeInTheDocument();
  });

  it('renders PDF and HTML toggle buttons', async () => {
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => [],
    });

    render(<PreviewPane />);
    
    expect(screen.getByText('PDF')).toBeInTheDocument();
    expect(screen.getByText('HTML')).toBeInTheDocument();
  });

  it('shows message when no variants exist', async () => {
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => [],
    });

    render(<PreviewPane />);
    
    await waitFor(() => {
      expect(screen.getByText('Create a variant to see preview')).toBeInTheDocument();
    });
  });

  it('renders variant selector when variants exist', async () => {
    const mockVariants = [
      { id: 'v1', name: 'Academic CV', updated_at: '2024-01-01' },
      { id: 'v2', name: 'Industry CV', updated_at: '2024-01-02' },
    ];

    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => mockVariants,
    });

    render(<PreviewPane />);
    
    await waitFor(() => {
      expect(screen.getByRole('combobox')).toBeInTheDocument();
    });
    
    expect(screen.getByText('Academic CV')).toBeInTheDocument();
    expect(screen.getByText('Industry CV')).toBeInTheDocument();
  });

  it('switches between PDF and HTML views', async () => {
    const mockVariants = [
      { id: 'v1', name: 'Test CV', updated_at: '2024-01-01' },
    ];

    (global.fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: async () => mockVariants,
    });

    render(<PreviewPane />);
    
    await waitFor(() => {
      expect(screen.getByText('Test CV')).toBeInTheDocument();
    });

    // Click HTML button
    fireEvent.click(screen.getByText('HTML'));
    
    // The HTML button should now be active (has btnPrimary class)
    expect(screen.getByText('HTML').className).toContain('btnPrimary');
  });

  it('has reload button', async () => {
    (global.fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: async () => [],
    });

    render(<PreviewPane />);
    
    // Find reload button by title
    expect(screen.getByTitle('Reload Preview')).toBeInTheDocument();
  });
});

