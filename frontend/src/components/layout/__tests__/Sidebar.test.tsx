import { render, screen } from '@testing-library/react';
import Sidebar from '../Sidebar';
import { usePathname } from 'next/navigation';

// Mock next/navigation
jest.mock('next/navigation', () => ({
  usePathname: jest.fn(),
}));

describe('Sidebar Component', () => {
  it('renders all navigation links', () => {
    (usePathname as jest.Mock).mockReturnValue('/');

    render(<Sidebar />);

    expect(screen.getByText('War Room')).toBeInTheDocument();
    expect(screen.getByText('Dashboard')).toBeInTheDocument();
    expect(screen.getByText('Members')).toBeInTheDocument();
    expect(screen.getByText('Live Chain')).toBeInTheDocument();
    expect(screen.getByText('War Analytics')).toBeInTheDocument();
    expect(screen.getByText('Alerts')).toBeInTheDocument();
    expect(screen.getByText('Settings')).toBeInTheDocument();
    expect(screen.getByText('Logout')).toBeInTheDocument();
  });
});
