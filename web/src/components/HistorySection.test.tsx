import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { HistorySection } from './HistorySection';

const fetchScanHistory = vi.fn();
const fetchInconsistentBarcodeSummary = vi.fn();
const fetchMissedBarcodeSummary = vi.fn();

vi.mock('../lib/api', () => ({
  fetchInconsistentBarcodeSummary: (...args: unknown[]) =>
    fetchInconsistentBarcodeSummary(...args),
  fetchMissedBarcodeSummary: (...args: unknown[]) =>
    fetchMissedBarcodeSummary(...args),
  fetchScanHistory: (...args: unknown[]) => fetchScanHistory(...args),
}));

describe('HistorySection', () => {
  beforeEach(() => {
    fetchScanHistory.mockReset();
    fetchInconsistentBarcodeSummary.mockReset();
    fetchMissedBarcodeSummary.mockReset();
  });

  it('renders a loading state before history arrives', () => {
    fetchScanHistory.mockReturnValue(new Promise(() => undefined));
    fetchInconsistentBarcodeSummary.mockReturnValue(new Promise(() => undefined));
    fetchMissedBarcodeSummary.mockReturnValue(new Promise(() => undefined));

    render(<HistorySection />);

    expect(screen.getByText('Loading history...')).toBeInTheDocument();
  });

  it('renders an empty state when no history is returned', async () => {
    fetchScanHistory.mockResolvedValue({ items: [] });
    fetchInconsistentBarcodeSummary.mockResolvedValue({ items: [] });
    fetchMissedBarcodeSummary.mockResolvedValue({ items: [] });

    render(<HistorySection />);

    await waitFor(() => {
      expect(screen.getByText('No recent scans yet.')).toBeInTheDocument();
      expect(
        screen.getByText('No verification-needed barcode groups yet.'),
      ).toBeInTheDocument();
    });
  });

  it('renders an error state when loading fails', async () => {
    fetchScanHistory.mockRejectedValue(new Error('boom'));
    fetchInconsistentBarcodeSummary.mockResolvedValue({ items: [] });
    fetchMissedBarcodeSummary.mockResolvedValue({ items: [] });

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
    fetchInconsistentBarcodeSummary.mockResolvedValue({ items: [] });
    fetchMissedBarcodeSummary.mockResolvedValue({ items: [] });

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
    fetchInconsistentBarcodeSummary.mockResolvedValue({ items: [] });
    fetchMissedBarcodeSummary.mockResolvedValue({ items: [] });

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
    fetchInconsistentBarcodeSummary.mockResolvedValue({ items: [] });
    fetchMissedBarcodeSummary.mockResolvedValue({ items: [] });

    render(<HistorySection />);

    await waitFor(() => {
      expect(fetchScanHistory).toHaveBeenCalledTimes(1);
      expect(fetchInconsistentBarcodeSummary).toHaveBeenCalledTimes(1);
      expect(fetchMissedBarcodeSummary).toHaveBeenCalledTimes(1);
    });

    await user.click(screen.getByRole('button', { name: 'Refresh' }));

    await waitFor(() => {
      expect(fetchScanHistory).toHaveBeenCalledTimes(2);
      expect(fetchInconsistentBarcodeSummary).toHaveBeenCalledTimes(2);
      expect(fetchMissedBarcodeSummary).toHaveBeenCalledTimes(2);
    });
  });

  it('renders grouped inconsistent barcode entries once per barcode', async () => {
    fetchScanHistory.mockResolvedValue({ items: [] });
    fetchInconsistentBarcodeSummary.mockResolvedValue({
      items: [
        {
          barcode: '0041167055106',
          count: 2,
          first_seen_at: '2026-05-07T10:30:00Z',
          last_seen_at: '2026-05-07T12:30:00Z',
          latest_explanation:
            'A product record was found, but the lookup source returned inconsistent product details.',
          latest_source: 'open_beauty_facts_inconsistent',
          product_quality_status: 'inconsistent',
        },
      ],
    });
    fetchMissedBarcodeSummary.mockResolvedValue({ items: [] });

    render(<HistorySection />);

    await waitFor(() => {
      expect(screen.getByText('0041167055106')).toBeInTheDocument();
    });

    expect(screen.getByText('2 inconsistent lookups')).toBeInTheDocument();
    expect(screen.getByText('Latest source: open_beauty_facts_inconsistent')).toBeInTheDocument();
  });

  it('renders unresolved barcode summary entries', async () => {
    fetchScanHistory.mockResolvedValue({ items: [] });
    fetchInconsistentBarcodeSummary.mockResolvedValue({ items: [] });
    fetchMissedBarcodeSummary.mockResolvedValue({
      items: [
        {
          barcode: '9999999999999',
          miss_count: 3,
          first_seen_at: '2026-05-07T11:30:00Z',
          last_seen_at: '2026-05-07T12:30:00Z',
          latest_explanation:
            'No product record with a usable ingredient list was found for this barcode.',
        },
      ],
    });

    render(<HistorySection />);

    await waitFor(() => {
      expect(screen.getByText('9999999999999')).toBeInTheDocument();
    });

    expect(screen.getByText('3 misses')).toBeInTheDocument();
    expect(
      screen.getByText(
        'No product record with a usable ingredient list was found for this barcode.',
      ),
    ).toBeInTheDocument();
  });

  it('renders unresolved barcode summary empty state', async () => {
    fetchScanHistory.mockResolvedValue({ items: [] });
    fetchInconsistentBarcodeSummary.mockResolvedValue({ items: [] });
    fetchMissedBarcodeSummary.mockResolvedValue({ items: [] });

    render(<HistorySection />);

    await waitFor(() => {
      expect(
        screen.getByText('No unresolved barcode misses yet.'),
      ).toBeInTheDocument();
    });
  });

  it('renders unresolved barcode summary error state', async () => {
    fetchScanHistory.mockResolvedValue({ items: [] });
    fetchInconsistentBarcodeSummary.mockResolvedValue({ items: [] });
    fetchMissedBarcodeSummary.mockRejectedValue(new Error('boom'));

    render(<HistorySection />);

    await waitFor(() => {
      expect(
        screen.getByText('Unresolved barcode summary could not be loaded.'),
      ).toBeInTheDocument();
    });
  });

  it('renders inconsistent section error state cleanly', async () => {
    fetchScanHistory.mockResolvedValue({ items: [] });
    fetchInconsistentBarcodeSummary.mockRejectedValue(new Error('boom'));
    fetchMissedBarcodeSummary.mockResolvedValue({ items: [] });

    render(<HistorySection />);

    await waitFor(() => {
      expect(
        screen.getByText('Verification group could not be loaded.'),
      ).toBeInTheDocument();
    });
  });

  it('renders sections in the required order', async () => {
    fetchScanHistory.mockResolvedValue({ items: [] });
    fetchInconsistentBarcodeSummary.mockResolvedValue({ items: [] });
    fetchMissedBarcodeSummary.mockResolvedValue({ items: [] });

    render(<HistorySection />);

    await waitFor(() => {
      expect(screen.getByText('Recent successful checks')).toBeInTheDocument();
    });

    const headings = screen.getAllByRole('heading', { level: 2 }).map((node) => node.textContent);
    const successfulIndex = headings.indexOf('Recent successful checks');
    const verificationIndex = headings.indexOf('Needs verification');
    const unresolvedIndex = headings.indexOf('Unresolved barcode scans');

    expect(successfulIndex).toBeGreaterThan(-1);
    expect(verificationIndex).toBeGreaterThan(successfulIndex);
    expect(unresolvedIndex).toBeGreaterThan(verificationIndex);
  });
});
