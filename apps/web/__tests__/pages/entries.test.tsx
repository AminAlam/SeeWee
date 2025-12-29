/**
 * Tests for Entries page
 */

import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import EntriesPage from '@/app/entries/page';

describe('EntriesPage', () => {
  const mockEntries = [
    {
      id: 'e1',
      type: 'experience',
      data: { role: 'Software Engineer', company: 'Tech Corp' },
      tags: ['work'],
      created_at: '2024-01-01',
      updated_at: '2024-01-01',
    },
    {
      id: 'e2',
      type: 'education',
      data: { school: 'MIT', degree: 'BSc CS' },
      tags: ['school'],
      created_at: '2024-01-01',
      updated_at: '2024-01-01',
    },
  ];

  const mockSchemas = {
    experience: {
      type: 'experience',
      label: 'Experience',
      fields: [
        { name: 'role', label: 'Role', type: 'text' },
        { name: 'company', label: 'Company', type: 'text' },
      ],
      default: { role: '', company: '' },
    },
    education: {
      type: 'education',
      label: 'Education',
      fields: [
        { name: 'school', label: 'School', type: 'text' },
        { name: 'degree', label: 'Degree', type: 'text' },
      ],
      default: { school: '', degree: '' },
    },
  };

  beforeEach(() => {
    (global.fetch as jest.Mock)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockEntries,
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockSchemas,
      });
  });

  it('renders page title', async () => {
    render(<EntriesPage />);
    
    expect(screen.getByText('Entries')).toBeInTheDocument();
  });

  it('loads and displays entries', async () => {
    render(<EntriesPage />);
    
    await waitFor(() => {
      expect(screen.getByText('Software Engineer')).toBeInTheDocument();
    });
    
    expect(screen.getByText('MIT')).toBeInTheDocument();
  });

  it('shows entry type badges', async () => {
    render(<EntriesPage />);
    
    await waitFor(() => {
      expect(screen.getByText('experience')).toBeInTheDocument();
      expect(screen.getByText('education')).toBeInTheDocument();
    });
  });

  it('has search input', async () => {
    render(<EntriesPage />);
    
    await waitFor(() => {
      expect(screen.getByPlaceholderText('Search...')).toBeInTheDocument();
    });
  });

  it('has type filter dropdown', async () => {
    render(<EntriesPage />);
    
    await waitFor(() => {
      expect(screen.getByText('All types')).toBeInTheDocument();
    });
  });

  it('filters entries by search query', async () => {
    const user = userEvent.setup();
    render(<EntriesPage />);
    
    await waitFor(() => {
      expect(screen.getByText('Software Engineer')).toBeInTheDocument();
    });

    const searchInput = screen.getByPlaceholderText('Search...');
    await user.type(searchInput, 'MIT');
    
    await waitFor(() => {
      expect(screen.queryByText('Software Engineer')).not.toBeInTheDocument();
      expect(screen.getByText('MIT')).toBeInTheDocument();
    });
  });

  it('has form for creating entries', async () => {
    render(<EntriesPage />);
    
    await waitFor(() => {
      expect(screen.getByText('New Entry')).toBeInTheDocument();
    });
  });

  it('has create button', async () => {
    render(<EntriesPage />);
    
    await waitFor(() => {
      expect(screen.getByText('Create')).toBeInTheDocument();
    });
  });

  it('has delete buttons for entries', async () => {
    render(<EntriesPage />);
    
    await waitFor(() => {
      const deleteButtons = screen.getAllByText('Delete');
      expect(deleteButtons.length).toBeGreaterThan(0);
    });
  });
});

