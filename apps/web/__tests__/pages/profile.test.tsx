/**
 * Tests for Profile page
 */

import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import ProfilePage from '@/app/profile/page';

describe('ProfilePage', () => {
  const mockProfile = {
    data: {
      personal: { full_name: 'John Doe' },
      links: {
        email: 'john@example.com',
        phone: '+1234567890',
        github: 'https://github.com/johndoe',
        linkedin: 'https://linkedin.com/in/johndoe',
      },
      content: {
        summary: 'Experienced engineer',
        tagline: 'Building great software',
      },
    },
    created_at: '2024-01-01',
    updated_at: '2024-01-01',
  };

  beforeEach(() => {
    (global.fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: async () => mockProfile,
    });
  });

  it('renders page title', async () => {
    render(<ProfilePage />);
    
    expect(screen.getByText('Profile')).toBeInTheDocument();
  });

  it('loads and displays profile data', async () => {
    render(<ProfilePage />);
    
    await waitFor(() => {
      expect(screen.getByDisplayValue('John Doe')).toBeInTheDocument();
    });
    
    expect(screen.getByDisplayValue('john@example.com')).toBeInTheDocument();
  });

  it('has personal section', async () => {
    render(<ProfilePage />);
    
    await waitFor(() => {
      expect(screen.getByText('Personal')).toBeInTheDocument();
    });
  });

  it('has links section', async () => {
    render(<ProfilePage />);
    
    await waitFor(() => {
      expect(screen.getByText('Links & Contact')).toBeInTheDocument();
    });
  });

  it('has full name input', async () => {
    render(<ProfilePage />);
    
    await waitFor(() => {
      expect(screen.getByText('Full name')).toBeInTheDocument();
    });
  });

  it('has email input', async () => {
    render(<ProfilePage />);
    
    await waitFor(() => {
      expect(screen.getByText('Email')).toBeInTheDocument();
    });
  });

  it('has GitHub input', async () => {
    render(<ProfilePage />);
    
    await waitFor(() => {
      expect(screen.getByText('GitHub URL')).toBeInTheDocument();
    });
  });

  it('has LinkedIn input', async () => {
    render(<ProfilePage />);
    
    await waitFor(() => {
      expect(screen.getByText('LinkedIn URL')).toBeInTheDocument();
    });
  });

  it('has save button', async () => {
    render(<ProfilePage />);
    
    expect(screen.getByText('Save')).toBeInTheDocument();
  });

  it('has reload button', async () => {
    render(<ProfilePage />);
    
    expect(screen.getByText('Reload')).toBeInTheDocument();
  });

  it('shows completeness score', async () => {
    render(<ProfilePage />);
    
    await waitFor(() => {
      // Check for completeness badge
      const badge = screen.getByText(/\/5/);
      expect(badge).toBeInTheDocument();
    });
  });

  it('allows editing full name', async () => {
    const user = userEvent.setup();
    render(<ProfilePage />);
    
    await waitFor(() => {
      expect(screen.getByDisplayValue('John Doe')).toBeInTheDocument();
    });

    const nameInput = screen.getByDisplayValue('John Doe');
    await user.clear(nameInput);
    await user.type(nameInput, 'Jane Doe');
    
    expect(screen.getByDisplayValue('Jane Doe')).toBeInTheDocument();
  });

  it('calls save endpoint on save button click', async () => {
    const user = userEvent.setup();
    render(<ProfilePage />);
    
    await waitFor(() => {
      expect(screen.getByDisplayValue('John Doe')).toBeInTheDocument();
    });

    const saveButton = screen.getByText('Save');
    await user.click(saveButton);
    
    // Check that fetch was called with PUT method
    await waitFor(() => {
      const putCalls = (global.fetch as jest.Mock).mock.calls.filter(
        call => call[1]?.method === 'PUT'
      );
      expect(putCalls.length).toBeGreaterThan(0);
    });
  });
});

