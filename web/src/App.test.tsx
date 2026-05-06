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
  getApiBaseUrl: () => 'https://api.thatsnuts.activeadvantage.co',
  lookupProduct: vi.fn(),
}));

describe('App disclaimer gate', () => {
  beforeEach(() => {
    window.localStorage.clear();
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
