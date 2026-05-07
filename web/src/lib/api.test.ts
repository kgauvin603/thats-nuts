import { afterEach, describe, expect, it, vi } from 'vitest';
import {
  fetchInconsistentBarcodeSummary,
  fetchMissedBarcodeSummary,
  getApiBaseUrl,
  lookupProduct,
} from './api';

describe('api configuration', () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('uses the production API by default', () => {
    expect(getApiBaseUrl()).toBe('https://api.thatsnuts.activeadvantage.co');
  });

  it('posts barcode lookups to the expected backend route', async () => {
    const fetchMock = vi
      .spyOn(globalThis, 'fetch')
      .mockResolvedValue(
        new Response(
          JSON.stringify({
            found: true,
            source: 'open_food_facts',
            lookup_path: [],
            product: null,
            assessment_result: 'cannot_verify',
            matched_ingredients: [],
            explanation: 'ok',
            unknown_terms: [],
          }),
          { status: 200 },
        ),
      );

    await lookupProduct('3017620422003');

    expect(fetchMock).toHaveBeenCalledWith(
      'https://api.thatsnuts.activeadvantage.co/lookup-product',
      expect.objectContaining({
        method: 'POST',
      }),
    );
  });

  it('fetches missed barcode telemetry from the expected backend route', async () => {
    const fetchMock = vi
      .spyOn(globalThis, 'fetch')
      .mockResolvedValue(new Response(JSON.stringify({ items: [] }), { status: 200 }));

    await fetchMissedBarcodeSummary(10);

    expect(fetchMock).toHaveBeenCalledWith(
      'https://api.thatsnuts.activeadvantage.co/scan-history/missed-barcodes?limit=10',
    );
  });

  it('fetches inconsistent barcode telemetry from the expected backend route', async () => {
    const fetchMock = vi
      .spyOn(globalThis, 'fetch')
      .mockResolvedValue(new Response(JSON.stringify({ items: [] }), { status: 200 }));

    await fetchInconsistentBarcodeSummary(10);

    expect(fetchMock).toHaveBeenCalledWith(
      'https://api.thatsnuts.activeadvantage.co/scan-history/inconsistent-barcodes?limit=10',
    );
  });
});
