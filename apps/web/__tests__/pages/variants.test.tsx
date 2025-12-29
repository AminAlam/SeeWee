/**
 * Tests for Variants page
 */

import { render, screen, waitFor } from '@testing-library/react';
import VariantsPage from '@/app/variants/page';

// Mock dnd-kit
jest.mock('@dnd-kit/core', () => ({
  DndContext: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  DragOverlay: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  closestCenter: jest.fn(),
  KeyboardSensor: jest.fn(),
  PointerSensor: jest.fn(),
  useSensor: jest.fn(() => ({})),
  useSensors: jest.fn(() => []),
  useDroppable: jest.fn(() => ({ setNodeRef: jest.fn(), isOver: false })),
}));

jest.mock('@dnd-kit/sortable', () => ({
  SortableContext: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  sortableKeyboardCoordinates: jest.fn(),
  useSortable: jest.fn(() => ({
    attributes: {},
    listeners: {},
    setNodeRef: jest.fn(),
    transform: null,
    transition: null,
    isDragging: false,
  })),
  verticalListSortingStrategy: jest.fn(),
  arrayMove: jest.fn((arr, from, to) => {
    const result = [...arr];
    const [removed] = result.splice(from, 1);
    result.splice(to, 0, removed);
    return result;
  }),
}));

jest.mock('@dnd-kit/utilities', () => ({
  CSS: {
    Transform: {
      toString: jest.fn(() => ''),
    },
  },
}));

describe('VariantsPage', () => {
  const mockVariants = [
    {
      id: 'v1',
      name: 'Academic CV',
      rules: {},
      sections: ['education', 'publications'],
      has_layout: false,
      created_at: '2024-01-01',
      updated_at: '2024-01-01',
    },
  ];

  const mockEntries = [
    {
      id: 'e1',
      type: 'education',
      data: { school: 'MIT', degree: 'PhD' },
      tags: [],
    },
  ];

  const mockLayout = {
    variant_id: 'v1',
    sections: {},
  };

  beforeEach(() => {
    (global.fetch as jest.Mock)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockVariants,
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockEntries,
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockLayout,
      });
  });

  it('renders page title', async () => {
    render(<VariantsPage />);
    
    expect(screen.getByText('Variant Builder')).toBeInTheDocument();
  });

  it('renders subtitle with instructions', async () => {
    render(<VariantsPage />);
    
    expect(screen.getByText(/Drag entries into sections/)).toBeInTheDocument();
  });

  it('loads and displays variants', async () => {
    render(<VariantsPage />);
    
    await waitFor(() => {
      expect(screen.getByText('Academic CV')).toBeInTheDocument();
    });
  });

  it('has new variant button', async () => {
    render(<VariantsPage />);
    
    expect(screen.getByText('+ New')).toBeInTheDocument();
  });

  it('has save button', async () => {
    render(<VariantsPage />);
    
    expect(screen.getByText('Save')).toBeInTheDocument();
  });

  it('has export button', async () => {
    render(<VariantsPage />);
    
    expect(screen.getByText('Export')).toBeInTheDocument();
  });

  it('shows entry library', async () => {
    render(<VariantsPage />);
    
    await waitFor(() => {
      expect(screen.getByText('Entry Library')).toBeInTheDocument();
    });
  });

  it('has search in library', async () => {
    render(<VariantsPage />);
    
    expect(screen.getByPlaceholderText('Search...')).toBeInTheDocument();
  });

  it('shows add section buttons', async () => {
    render(<VariantsPage />);
    
    await waitFor(() => {
      expect(screen.getByText('Add section:')).toBeInTheDocument();
    });
  });
});

