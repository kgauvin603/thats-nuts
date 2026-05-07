import { afterEach, describe, expect, it, vi } from 'vitest';
import {
  fetchGroupedScanHistory,
  fetchInconsistentBarcodeSummary,
  fetchMissedBarcodeSummary,
  getApiBaseUrl,
  lookupProduct,
  uploadProductPhoto,
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

  it('fetches grouped successful history from the expected backend route', async () => {
    const fetchMock = vi
      .spyOn(globalThis, 'fetch')
      .mockResolvedValue(new Response(JSON.stringify({ items: [] }), { status: 200 }));

    await fetchGroupedScanHistory(10);

    expect(fetchMock).toHaveBeenCalledWith(
      'https://api.thatsnuts.activeadvantage.co/scan-history/grouped?limit=10',
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

  it('posts product photo uploads to the expected backend route', async () => {
    const fetchMock = vi
      .spyOn(globalThis, 'fetch')
      .mockResolvedValue(
        new Response(
          JSON.stringify({
            barcode: '5555555555555',
            image_url: 'https://api.thatsnuts.activeadvantage.co/uploads/product_photos/demo.png',
            updated: true,
            message: 'Product photo saved.',
          }),
          { status: 200 },
        ),
      );

    await uploadProductPhoto(
      '5555555555555',
      new File(['image'], 'photo.png', { type: 'image/png' }),
    );

    expect(fetchMock).toHaveBeenCalledWith(
      'https://api.thatsnuts.activeadvantage.co/products/5555555555555/photo?overwrite=false',
      expect.objectContaining({
        method: 'POST',
        body: expect.any(FormData),
      }),
    );
  });

  it('posts overwrite=true when replacing a saved product photo', async () => {
    const fetchMock = vi
      .spyOn(globalThis, 'fetch')
      .mockResolvedValue(
        new Response(
          JSON.stringify({
            barcode: '5555555555555',
            image_url: 'https://api.thatsnuts.activeadvantage.co/uploads/product_photos/demo.png',
            updated: true,
            message: 'Product photo saved.',
          }),
          { status: 200 },
        ),
      );

    await uploadProductPhoto(
      '5555555555555',
      new File(['image'], 'photo.png', { type: 'image/png' }),
      true,
    );

    expect(fetchMock).toHaveBeenCalledWith(
      'https://api.thatsnuts.activeadvantage.co/products/5555555555555/photo?overwrite=true',
      expect.objectContaining({
        method: 'POST',
        body: expect.any(FormData),
      }),
    );
  });

  it('translates network fetch failures into a helpful upload message', async () => {
    vi.spyOn(console, 'error').mockImplementation(() => undefined);
    vi.spyOn(globalThis, 'fetch').mockRejectedValue(new TypeError('Failed to fetch'));

    await expect(
      uploadProductPhoto(
        '5555555555555',
        new File(['image'], 'photo.png', { type: 'image/png' }),
      ),
    ).rejects.toThrow(
      'Upload request could not reach the API. Please check network/CORS or try again.',
    );
  });
});
