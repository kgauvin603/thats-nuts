import { afterEach, describe, expect, it, vi } from 'vitest';
import { getApiBaseUrl, lookupProduct } from './api';

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
});
