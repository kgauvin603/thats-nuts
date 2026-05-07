import { DEFAULT_API_BASE_URL } from './constants';
import type {
  IngredientCheckResponse,
  ProductLookupResponse,
} from './types';
import type {
  MissedBarcodeSummaryResponse,
  ScanHistoryResponse,
} from './history';

export class ApiError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'ApiError';
  }
}

const baseUrl = (import.meta.env.VITE_API_BASE_URL || DEFAULT_API_BASE_URL).replace(
  /\/$/,
  '',
);

async function postJson<TResponse>(
  path: string,
  payload: Record<string, unknown>,
): Promise<TResponse> {
  const response = await fetch(`${baseUrl}${path}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new ApiError(`Backend request failed with status ${response.status}.`);
  }

  return (await response.json()) as TResponse;
}

async function getJson<TResponse>(path: string): Promise<TResponse> {
  const response = await fetch(`${baseUrl}${path}`);

  if (!response.ok) {
    throw new ApiError(`Backend request failed with status ${response.status}.`);
  }

  return (await response.json()) as TResponse;
}

export function getApiBaseUrl() {
  return baseUrl;
}

export function lookupProduct(barcode: string) {
  return postJson<ProductLookupResponse>('/lookup-product', { barcode });
}

export function checkIngredients(ingredientText: string) {
  return postJson<IngredientCheckResponse>('/check-ingredients', {
    ingredient_text: ingredientText,
  });
}

export function fetchScanHistory(limit = 20) {
  return getJson<ScanHistoryResponse>(`/scan-history?limit=${limit}`);
}

export function fetchMissedBarcodeSummary(limit = 10) {
  return getJson<MissedBarcodeSummaryResponse>(
    `/scan-history/missed-barcodes?limit=${limit}`,
  );
}
