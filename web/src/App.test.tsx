import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import App from './App';
import {
  SAFETY_DISCLAIMER_VERSION,
  SAFETY_STORAGE_KEY,
} from './lib/constants';

vi.mock('./lib/api', () => ({
  checkIngredients: vi.fn(),
  fetchScanHistory: vi.fn().mockResolvedValue({ items: [] }),
  getApiBaseUrl: () => 'https://api.thatsnuts.activeadvantage.co',
  lookupProduct: vi.fn(),
}));

function createStorageMock() {
  const store = new Map<string, string>();

  return {
    getItem: (key: string) => store.get(key) ?? null,
    setItem: (key: string, value: string) => {
      store.set(key, value);
    },
    removeItem: (key: string) => {
      store.delete(key);
    },
    clear: () => {
      store.clear();
    },
  };
}

describe('App disclaimer gate', () => {
  beforeEach(() => {
    Object.defineProperty(window, 'localStorage', {
      value: createStorageMock(),
      configurable: true,
    });
  });

  it('shows the mobile app branding in the header', () => {
    render(<App />);

    expect(
      screen.getByRole('heading', { name: 'That’s Nuts' }),
    ).toBeInTheDocument();
    expect(screen.getByAltText('That’s Nuts app icon')).toBeInTheDocument();
    expect(screen.getByRole('link', { name: 'View history' })).toBeInTheDocument();
  });

  it('prevents use before disclaimer acceptance', () => {
    render(<App />);

    expect(screen.getByRole('dialog')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Check barcode' })).toBeDisabled();
    expect(
      screen.getByRole('button', { name: 'Check ingredients' }),
    ).toBeDisabled();
  });

  it('unlocks the tools after acceptance', async () => {
    const user = userEvent.setup();
    render(<App />);

    await user.click(screen.getByRole('button', { name: 'I Understand and Agree' }));

    expect(window.localStorage.getItem(SAFETY_STORAGE_KEY)).toBe(
      SAFETY_DISCLAIMER_VERSION,
    );
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Check barcode' })).toBeEnabled();
  });
});
