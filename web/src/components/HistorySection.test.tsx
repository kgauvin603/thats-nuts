import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { HistorySection } from './HistorySection';

const fetchGroupedScanHistory = vi.fn();
const fetchInconsistentBarcodeSummary = vi.fn();
const fetchMissedBarcodeSummary = vi.fn();
const uploadProductPhoto = vi.fn();

vi.mock('../lib/api', () => ({
  ApiError: class ApiError extends Error {},
  fetchGroupedScanHistory: (...args: unknown[]) => fetchGroupedScanHistory(...args),
  fetchInconsistentBarcodeSummary: (...args: unknown[]) =>
    fetchInconsistentBarcodeSummary(...args),
  fetchMissedBarcodeSummary: (...args: unknown[]) =>
    fetchMissedBarcodeSummary(...args),
  uploadProductPhoto: (...args: unknown[]) => uploadProductPhoto(...args),
}));

describe('HistorySection', () => {
  beforeEach(() => {
    fetchGroupedScanHistory.mockReset();
    fetchInconsistentBarcodeSummary.mockReset();
    fetchMissedBarcodeSummary.mockReset();
    uploadProductPhoto.mockReset();
  });

  it('renders a loading state before history arrives', () => {
    fetchGroupedScanHistory.mockReturnValue(new Promise(() => undefined));
    fetchInconsistentBarcodeSummary.mockReturnValue(new Promise(() => undefined));
    fetchMissedBarcodeSummary.mockReturnValue(new Promise(() => undefined));

    render(<HistorySection />);

    expect(screen.getByText('Loading history...')).toBeInTheDocument();
  });

  it('renders an empty state when no history is returned', async () => {
    fetchGroupedScanHistory.mockResolvedValue({ items: [] });
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
    fetchGroupedScanHistory.mockRejectedValue(new Error('boom'));
    fetchInconsistentBarcodeSummary.mockResolvedValue({ items: [] });
    fetchMissedBarcodeSummary.mockResolvedValue({ items: [] });

    render(<HistorySection />);

    await waitFor(() => {
      expect(
        screen.getByText('History could not be loaded. Please try again.'),
      ).toBeInTheDocument();
    });
  });

  it('renders grouped successful barcode history with count and image when present', async () => {
    fetchGroupedScanHistory.mockResolvedValue({
      items: [
        {
          scan_type: 'barcode_lookup',
          grouped_scan_type: 'barcode_lookup',
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
          scan_count: 3,
          first_seen_at: '2026-05-07T10:30:00Z',
          last_seen_at: '2026-05-07T11:30:00Z',
          latest_explanation: 'Hazelnut was detected.',
          latest_source: 'open_food_facts',
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
    expect(screen.getByText('3 successful scans')).toBeInTheDocument();
    expect(screen.getByText('NOISETTES 13%')).toBeInTheDocument();
    expect(screen.getByAltText('Nutella')).toBeInTheDocument();
  });

  it('renders barcode enrichment and manual ingredient entries cleanly', async () => {
    fetchGroupedScanHistory.mockResolvedValue({
      items: [
        {
          scan_type: 'barcode_enrichment',
          grouped_scan_type: 'barcode_enrichment',
          barcode: '5555555555555',
          product_name: 'Demo Lotion',
          brand_name: 'Demo Brand',
          image_url: null,
          product_source: 'text_scan',
          submitted_ingredient_text: 'Water, Sweet Almond Oil',
          assessment_status: 'contains_nut_ingredient',
          explanation: 'Sweet almond oil was detected.',
          matched_ingredient_summary: 'Sweet Almond Oil',
          scan_count: 2,
          first_seen_at: '2026-05-07T11:00:00Z',
          last_seen_at: '2026-05-07T11:31:00Z',
          latest_explanation: 'Sweet almond oil was detected.',
          latest_source: 'text_scan',
        },
        {
          scan_type: 'manual_ingredient_check',
          grouped_scan_type: 'manual_ingredient_check',
          barcode: null,
          product_name: null,
          brand_name: null,
          image_url: null,
          product_source: null,
          submitted_ingredient_text: 'Water, Glycerin',
          assessment_status: 'no_nut_ingredient_found',
          explanation: 'No match found.',
          matched_ingredient_summary: null,
          scan_count: 1,
          first_seen_at: '2026-05-07T11:32:00Z',
          last_seen_at: '2026-05-07T11:32:00Z',
          latest_explanation: 'No match found.',
          latest_source: null,
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
    expect(
      screen.getByRole('button', { name: 'Add product photo for barcode 5555555555555' }),
    ).toBeInTheDocument();
    expect(screen.queryAllByText('Add product photo')).toHaveLength(1);
  });

  it('uploads a product photo from a no-image enrichment history entry', async () => {
    const user = userEvent.setup();
    fetchGroupedScanHistory.mockResolvedValue({
      items: [
        {
          scan_type: 'barcode_enrichment',
          grouped_scan_type: 'barcode_enrichment',
          barcode: '5555555555555',
          product_name: 'Demo Lotion',
          brand_name: 'Demo Brand',
          image_url: null,
          product_source: 'text_scan',
          submitted_ingredient_text: 'Water, Sweet Almond Oil',
          assessment_status: 'contains_nut_ingredient',
          explanation: 'Sweet almond oil was detected.',
          matched_ingredient_summary: 'Sweet Almond Oil',
          scan_count: 2,
          first_seen_at: '2026-05-07T11:00:00Z',
          last_seen_at: '2026-05-07T11:31:00Z',
          latest_explanation: 'Sweet almond oil was detected.',
          latest_source: 'text_scan',
        },
      ],
    });
    fetchInconsistentBarcodeSummary.mockResolvedValue({ items: [] });
    fetchMissedBarcodeSummary.mockResolvedValue({ items: [] });
    uploadProductPhoto.mockResolvedValue({
      barcode: '5555555555555',
      image_url: 'https://api.thatsnuts.activeadvantage.co/uploads/product_photos/demo.png',
      updated: true,
      message: 'Product photo saved.',
    });

    render(<HistorySection />);

    const input = await screen.findByTestId('product-photo-input');
    await user.upload(
      input,
      new File(['image'], 'photo.png', { type: 'image/png' }),
    );

    await waitFor(() => {
      expect(uploadProductPhoto).toHaveBeenCalledWith(
        '5555555555555',
        expect.any(File),
      );
    });
    await waitFor(() => {
      expect(screen.getByAltText('Demo Lotion')).toBeInTheDocument();
    expect(screen.getByText('Product photo saved.')).toBeInTheDocument();
    });
  });

  it('renders an upload error message when photo upload fails', async () => {
    const user = userEvent.setup();
    fetchGroupedScanHistory.mockResolvedValue({
      items: [
        {
          scan_type: 'barcode_enrichment',
          grouped_scan_type: 'barcode_enrichment',
          barcode: '5555555555555',
          product_name: 'Demo Lotion',
          brand_name: 'Demo Brand',
          image_url: null,
          product_source: 'text_scan',
          submitted_ingredient_text: 'Water, Sweet Almond Oil',
          assessment_status: 'contains_nut_ingredient',
          explanation: 'Sweet almond oil was detected.',
          matched_ingredient_summary: 'Sweet Almond Oil',
          scan_count: 2,
          first_seen_at: '2026-05-07T11:00:00Z',
          last_seen_at: '2026-05-07T11:31:00Z',
          latest_explanation: 'Sweet almond oil was detected.',
          latest_source: 'text_scan',
        },
      ],
    });
    fetchInconsistentBarcodeSummary.mockResolvedValue({ items: [] });
    fetchMissedBarcodeSummary.mockResolvedValue({ items: [] });
    uploadProductPhoto.mockRejectedValue(new Error('upload failed'));

    render(<HistorySection />);

    const input = await screen.findByTestId('product-photo-input');
    await user.upload(
      input,
      new File(['image'], 'photo.png', { type: 'image/png' }),
    );

    await waitFor(() => {
      expect(
        screen.getByText('upload failed'),
      ).toBeInTheDocument();
    });
  });

  it('does not show upload controls for records without a barcode or with an image', async () => {
    fetchGroupedScanHistory.mockResolvedValue({
      items: [
        {
          scan_type: 'manual_ingredient_check',
          grouped_scan_type: 'manual_ingredient_check',
          barcode: null,
          product_name: null,
          brand_name: null,
          image_url: null,
          product_source: null,
          submitted_ingredient_text: 'Water, Glycerin',
          assessment_status: 'no_nut_ingredient_found',
          explanation: 'No match found.',
          matched_ingredient_summary: null,
          scan_count: 1,
          first_seen_at: '2026-05-07T11:32:00Z',
          last_seen_at: '2026-05-07T11:32:00Z',
          latest_explanation: 'No match found.',
          latest_source: null,
        },
        {
          scan_type: 'barcode_lookup',
          grouped_scan_type: 'barcode_lookup',
          barcode: '3017620422003',
          product_name: 'Nutella',
          brand_name: 'Ferrero',
          image_url: 'https://images.example.invalid/nutella.jpg',
          product_source: 'open_food_facts',
          submitted_ingredient_text: null,
          assessment_status: 'contains_nut_ingredient',
          explanation: 'Hazelnut was detected.',
          matched_ingredient_summary: 'NOISETTES 13%',
          scan_count: 2,
          first_seen_at: '2026-05-07T10:30:00Z',
          last_seen_at: '2026-05-07T11:30:00Z',
          latest_explanation: 'Hazelnut was detected.',
          latest_source: 'open_food_facts',
        },
      ],
    });
    fetchInconsistentBarcodeSummary.mockResolvedValue({ items: [] });
    fetchMissedBarcodeSummary.mockResolvedValue({ items: [] });

    render(<HistorySection />);

    await waitFor(() => {
      expect(screen.getByText('Nutella')).toBeInTheDocument();
    });

    expect(
      screen.queryByRole('button', { name: 'Add product photo for barcode 3017620422003' }),
    ).not.toBeInTheDocument();
    expect(
      screen.queryByRole('button', { name: /Add product photo for barcode/i }),
    ).not.toBeInTheDocument();
  });

  it('does not show upload controls in inconsistent or unresolved sections', async () => {
    fetchGroupedScanHistory.mockResolvedValue({ items: [] });
    fetchInconsistentBarcodeSummary.mockResolvedValue({
      items: [
        {
          barcode: '0041167055106',
          count: 2,
          first_seen_at: '2026-05-07T10:30:00Z',
          last_seen_at: '2026-05-07T12:30:00Z',
          latest_explanation: 'Inconsistent product details.',
          latest_source: 'open_beauty_facts_inconsistent',
          product_quality_status: 'inconsistent',
        },
      ],
    });
    fetchMissedBarcodeSummary.mockResolvedValue({
      items: [
        {
          barcode: '9999999999999',
          miss_count: 3,
          first_seen_at: '2026-05-07T11:30:00Z',
          last_seen_at: '2026-05-07T12:30:00Z',
          latest_explanation: 'No product record with a usable ingredient list was found.',
        },
      ],
    });

    render(<HistorySection />);

    await waitFor(() => {
      expect(screen.getByText('0041167055106')).toBeInTheDocument();
      expect(screen.getByText('9999999999999')).toBeInTheDocument();
    });

    expect(
      screen.queryByRole('button', { name: /Add product photo for barcode/i }),
    ).not.toBeInTheDocument();
  });

  it('refreshes history when the refresh button is pressed', async () => {
    const user = userEvent.setup();
    fetchGroupedScanHistory.mockResolvedValue({ items: [] });
    fetchInconsistentBarcodeSummary.mockResolvedValue({ items: [] });
    fetchMissedBarcodeSummary.mockResolvedValue({ items: [] });

    render(<HistorySection />);

    await waitFor(() => {
      expect(fetchGroupedScanHistory).toHaveBeenCalledTimes(1);
      expect(fetchInconsistentBarcodeSummary).toHaveBeenCalledTimes(1);
      expect(fetchMissedBarcodeSummary).toHaveBeenCalledTimes(1);
    });

    await user.click(screen.getByRole('button', { name: 'Refresh' }));

    await waitFor(() => {
      expect(fetchGroupedScanHistory).toHaveBeenCalledTimes(2);
      expect(fetchInconsistentBarcodeSummary).toHaveBeenCalledTimes(2);
      expect(fetchMissedBarcodeSummary).toHaveBeenCalledTimes(2);
    });
  });

  it('renders grouped inconsistent barcode entries once per barcode', async () => {
    fetchGroupedScanHistory.mockResolvedValue({ items: [] });
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
    fetchGroupedScanHistory.mockResolvedValue({ items: [] });
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
    fetchGroupedScanHistory.mockResolvedValue({ items: [] });
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
    fetchGroupedScanHistory.mockResolvedValue({ items: [] });
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
    fetchGroupedScanHistory.mockResolvedValue({ items: [] });
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
    fetchGroupedScanHistory.mockResolvedValue({ items: [] });
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
