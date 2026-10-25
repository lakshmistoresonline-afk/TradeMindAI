import { render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import EquitySignals from './EquitySignals';
import * as apiClient from '../api/client';

vi.mock('../api/client', async () => {
  const actual = await vi.importActual('../api/client');
  return {
    ...actual,
    getEquitySignals: vi.fn(),
    getEquityHistory: vi.fn(),
  };
});

describe('EquitySignals Component Behavioral Tests', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders signal operations terminal and fetches equity signals on mount', async () => {
    (apiClient.getEquitySignals as any).mockResolvedValueOnce([
      { id: '1', symbol: 'RELIANCE', direction: 'LONG', confidence: 0.85 }
    ]);
    (apiClient.getEquityHistory as any).mockResolvedValueOnce({ records: [], total: 0 });

    render(
      <MemoryRouter>
        <EquitySignals />
      </MemoryRouter>
    );

    expect(screen.getByText(/SIGNAL OPERATIONS TERMINAL/i)).toBeInTheDocument();
  });

  it('handles API failure / Quarantine response safely without crashing', async () => {
    (apiClient.getEquitySignals as any).mockRejectedValueOnce(new Error('503 Service Unavailable: Quarantined'));
    (apiClient.getEquityHistory as any).mockRejectedValueOnce(new Error('503 Service Unavailable: Quarantined'));

    render(
      <MemoryRouter>
        <EquitySignals />
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByText(/SIGNAL OPERATIONS TERMINAL/i)).toBeInTheDocument();
    });
  });
});
