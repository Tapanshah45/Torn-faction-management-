import { fireEvent, render, screen, waitFor } from '@testing-library/react';

import PayoutsPage from '../page';

jest.mock('@/components/layout/Sidebar', () => () => <div data-testid="sidebar" />);
jest.mock('@/lib/safeStorage', () => ({
  safeStorage: {
    getItem: jest.fn(() => 'fake-token'),
  },
}));

describe('PayoutsPage', () => {
  const fetchMock = jest.fn();

  beforeEach(() => {
    fetchMock.mockImplementation((input: string) => {
      if (input.includes('/api/payouts/wars')) {
        return Promise.resolve({
          ok: true,
          json: async () => ([
            {
              war_id: 'rw-101',
              participants: 2,
              total_hits: 150,
              total_respect: '750.00',
              is_active: true,
              last_timestamp: '2026-04-10T10:00:00Z',
            },
          ]),
        });
      }

      if (input.includes('/api/payouts/history')) {
        return Promise.resolve({ ok: true, json: async () => ([]) });
      }

      if (input.includes('/api/payouts/war-contributions/rw-101')) {
        return Promise.resolve({
          ok: true,
          json: async () => ({
            war_id: 'rw-101',
            members: [
              { member_id: 1, member_name: 'A', total_hits: 100, total_respect: '500.00' },
              { member_id: 2, member_name: 'B', total_hits: 50, total_respect: '250.00' },
            ],
          }),
        });
      }

      if (input.includes('/api/payouts/calculate')) {
        return Promise.resolve({
          ok: true,
          json: async () => ({
            id: 1,
            war_id: 'rw-101',
            mode: 'hits',
            total_pool: '600000000.00',
            faction_cut: '10.00',
            distributable_pool: '540000000.00',
            created_at: '2026-04-10T10:15:00Z',
            members: [
              { id: 11, member: 1, name: 'A', hits: 100, respect: '500.00', share_percent: '66.6667', payout: '360000000.00' },
              { id: 12, member: 2, name: 'B', hits: 50, respect: '250.00', share_percent: '33.3333', payout: '180000000.00' },
            ],
          }),
        });
      }

      return Promise.resolve({ ok: false, json: async () => ({ detail: 'Not found' }) });
    });

    global.fetch = fetchMock as unknown as typeof fetch;
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  it('renders required ranked war payout controls', async () => {
    render(<PayoutsPage />);

    await waitFor(() => {
      expect(screen.getByText('Ranked War Payout Calculator')).toBeInTheDocument();
    });

    expect(screen.getByText('Select Ranked War')).toBeInTheDocument();
    expect(screen.getByText('Total Reward Pool')).toBeInTheDocument();
    expect(screen.getByText('Faction Cut %')).toBeInTheDocument();
    expect(screen.getByText('Payout by Hits')).toBeInTheDocument();
    expect(screen.getByText('Payout by Respect')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Generate Payout Sheet' })).toBeInTheDocument();
  });

  it('exports CSV after generating payout sheet', async () => {
    const createObjectURL = jest.fn(() => 'blob:test-url');
    const revokeObjectURL = jest.fn();
    Object.defineProperty(window.URL, 'createObjectURL', { value: createObjectURL, writable: true });
    Object.defineProperty(window.URL, 'revokeObjectURL', { value: revokeObjectURL, writable: true });

    const clickMock = jest.fn();
    const originalCreateElement = document.createElement.bind(document);
    const createElementSpy = jest.spyOn(document, 'createElement').mockImplementation((tagName: string) => {
      if (tagName === 'a') {
        return {
          click: clickMock,
          set href(value: string) {},
          set download(value: string) {},
        } as unknown as HTMLAnchorElement;
      }
      return originalCreateElement(tagName);
    });

    render(<PayoutsPage />);

    await waitFor(() => {
      expect(screen.getByRole('button', { name: 'Generate Payout Sheet' })).toBeInTheDocument();
    });

    fireEvent.click(screen.getByRole('button', { name: 'Generate Payout Sheet' }));

    await waitFor(() => {
      expect(screen.getByRole('button', { name: 'Export CSV' })).toBeInTheDocument();
    });

    fireEvent.click(screen.getByRole('button', { name: 'Export CSV' }));

    expect(createObjectURL).toHaveBeenCalled();
    expect(clickMock).toHaveBeenCalled();
    expect(revokeObjectURL).toHaveBeenCalled();

    createElementSpy.mockRestore();
  });
});
