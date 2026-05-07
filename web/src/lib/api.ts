import { DEFAULT_API_BASE_URL } from './constants';
import type {
  IngredientCheckResponse,
  ProductPhotoUploadResponse,
  ProductLookupResponse,
} from './types';
import type {
  GroupedScanHistoryResponse,
  InconsistentBarcodeSummaryResponse,
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

export function fetchGroupedScanHistory(limit = 20) {
  return getJson<GroupedScanHistoryResponse>(`/scan-history/grouped?limit=${limit}`);
}

export function fetchMissedBarcodeSummary(limit = 10) {
  return getJson<MissedBarcodeSummaryResponse>(
    `/scan-history/missed-barcodes?limit=${limit}`,
  );
}

export function fetchInconsistentBarcodeSummary(limit = 10) {
  return getJson<InconsistentBarcodeSummaryResponse>(
    `/scan-history/inconsistent-barcodes?limit=${limit}`,
  );
}

export async function uploadProductPhoto(
  barcode: string,
  file: File,
  overwrite = false,
) {
  const formData = new FormData();
  formData.append('photo', file);

  const response = await fetch(
    `${baseUrl}/products/${encodeURIComponent(barcode)}/photo?overwrite=${overwrite}`,
    {
      method: 'POST',
      body: formData,
    },
  );

  if (!response.ok) {
    let detail = `Backend request failed with status ${response.status}.`;
    try {
      const payload = (await response.json()) as { detail?: string };
      if (payload.detail) {
        detail = payload.detail;
      }
    } catch {
      // Keep the fallback error message when the response is not JSON.
    }
    throw new ApiError(detail);
  }

  return (await response.json()) as ProductPhotoUploadResponse;
}
