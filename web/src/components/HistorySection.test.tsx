import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { HistorySection } from './HistorySection';

const fetchScanHistory = vi.fn();

vi.mock('../lib/api', () => ({
  fetchScanHistory: (...args: unknown[]) => fetchScanHistory(...args),
}));

describe('HistorySection', () => {
  beforeEach(() => {
    fetchScanHistory.mockReset();
  });

  it('renders a loading state before history arrives', () => {
    fetchScanHistory.mockReturnValue(new Promise(() => undefined));

    render(<HistorySection />);

    expect(screen.getByText('Loading history...')).toBeInTheDocument();
  });

  it('renders an empty state when no history is returned', async () => {
    fetchScanHistory.mockResolvedValue({ items: [] });

    render(<HistorySection />);

    await waitFor(() => {
      expect(screen.getByText('No recent scans yet.')).toBeInTheDocument();
    });
  });

  it('renders an error state when loading fails', async () => {
    fetchScanHistory.mockRejectedValue(new Error('boom'));

    render(<HistorySection />);

    await waitFor(() => {
      expect(
        screen.getByText('History could not be loaded. Please try again.'),
      ).toBeInTheDocument();
    });
  });

  it('renders product history details including barcode and image when present', async () => {
    fetchScanHistory.mockResolvedValue({
      items: [
        {
          scan_type: 'barcode_lookup',
          barcode: '3017620422003',
          product_name: 'Nutella',
          brand_name: 'Ferrero',
          image_url:
            'https://images.openfoodfacts.org/images/products/301/762/042/2003/front_en.820.400.jpg',
          product_source: 'open_food_facts',
          submitted_ingredient_text: null,
          assessment_status: 'contains_nut_ingredient',
          explanation: 'Hazelnut was detected.',
          matched_ingredient_summary: 'NOISETTES 13%',
          created_at: '2026-05-07T11:30:00Z',
        },
      ],
    });

    render(<HistorySection />);

    await waitFor(() => {
      expect(screen.getByText('Nutella')).toBeInTheDocument();
    });

    expect(screen.getByText('3017620422003')).toBeInTheDocument();
    expect(screen.getByText('Nut ingredients detected')).toBeInTheDocument();
    expect(screen.getByText('NOISETTES 13%')).toBeInTheDocument();
    expect(screen.getByAltText('Nutella')).toBeInTheDocument();
  });

  it('renders barcode enrichment and manual ingredient entries cleanly', async () => {
    fetchScanHistory.mockResolvedValue({
      items: [
        {
          scan_type: 'barcode_enrichment',
          barcode: '5555555555555',
          product_name: 'Demo Lotion',
          brand_name: 'Demo Brand',
          image_url: null,
          product_source: 'text_scan',
          submitted_ingredient_text: 'Water, Sweet Almond Oil',
          assessment_status: 'contains_nut_ingredient',
          explanation: 'Sweet almond oil was detected.',
          matched_ingredient_summary: 'Sweet Almond Oil',
          created_at: '2026-05-07T11:31:00Z',
        },
        {
          scan_type: 'manual_ingredient_check',
          barcode: null,
          product_name: null,
          brand_name: null,
          image_url: null,
          product_source: null,
          submitted_ingredient_text: 'Water, Glycerin',
          assessment_status: 'no_nut_ingredient_found',
          explanation: 'No match found.',
          matched_ingredient_summary: null,
          created_at: '2026-05-07T11:32:00Z',
        },
      ],
    });

    render(<HistorySection />);

    await waitFor(() => {
      expect(screen.getByText('Barcode enrichment')).toBeInTheDocument();
    });

    expect(screen.getByText('Manual ingredient check')).toBeInTheDocument();
    expect(screen.getByText('Demo Lotion')).toBeInTheDocument();
    expect(screen.getByText('Water, Sweet Almond Oil')).toBeInTheDocument();
    expect(screen.getByText('Water, Glycerin')).toBeInTheDocument();
  });

  it('refreshes history when the refresh button is pressed', async () => {
    const user = userEvent.setup();
    fetchScanHistory.mockResolvedValue({ items: [] });

    render(<HistorySection />);

    await waitFor(() => {
      expect(fetchScanHistory).toHaveBeenCalledTimes(1);
    });

    await user.click(screen.getByRole('button', { name: 'Refresh' }));

    await waitFor(() => {
      expect(fetchScanHistory).toHaveBeenCalledTimes(2);
    });
  });
});
