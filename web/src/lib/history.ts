import type { IngredientCheckStatus } from './types';

export interface ScanHistoryResponse {
  items: ScanHistoryItem[];
}

export interface MissedBarcodeSummaryResponse {
  items: MissedBarcodeSummaryItem[];
}

export interface ScanHistoryItem {
  scan_type: 'manual_ingredient_check' | 'barcode_lookup' | 'barcode_enrichment';
  barcode?: string | null;
  product_name?: string | null;
  brand_name?: string | null;
  image_url?: string | null;
  product_source?: string | null;
  submitted_ingredient_text?: string | null;
  assessment_status: IngredientCheckStatus;
  explanation?: string | null;
  matched_ingredient_summary?: string | null;
  created_at: string;
}

export interface MissedBarcodeSummaryItem {
  barcode: string;
  miss_count: number;
  first_seen_at: string;
  last_seen_at: string;
  latest_explanation?: string | null;
}

export interface HistoryEntry {
  id: string;
  scanType: string;
  createdAt: string;
  barcode?: string;
  productName?: string;
  brandName?: string;
  imageUrl?: string;
  assessmentLabel: string;
  explanation?: string;
  matchedSummary?: string;
  submittedIngredientText?: string;
  productSource?: string;
}

export interface MissedBarcodeEntry {
  id: string;
  barcode: string;
  missCount: number;
  firstSeenAt: string;
  lastSeenAt: string;
  latestExplanation?: string;
}

export function toHistoryEntries(response: ScanHistoryResponse): HistoryEntry[] {
  return response.items.map((item, index) => ({
    id: `${item.created_at}-${item.barcode || item.scan_type}-${index}`,
    scanType: formatScanType(item.scan_type),
    createdAt: formatDateTime(item.created_at),
    barcode: item.barcode ?? undefined,
    productName: item.product_name ?? undefined,
    brandName: item.brand_name ?? undefined,
    imageUrl: item.image_url ?? undefined,
    assessmentLabel: formatAssessment(item.assessment_status),
    explanation: item.explanation ?? undefined,
    matchedSummary: item.matched_ingredient_summary ?? undefined,
    submittedIngredientText: item.submitted_ingredient_text ?? undefined,
    productSource: item.product_source ?? undefined,
  }));
}

function formatScanType(value: ScanHistoryItem['scan_type']) {
  switch (value) {
    case 'barcode_lookup':
      return 'Barcode lookup';
    case 'barcode_enrichment':
      return 'Barcode enrichment';
    default:
      return 'Manual ingredient check';
  }
}

function formatAssessment(value: IngredientCheckStatus) {
  switch (value) {
    case 'contains_nut_ingredient':
      return 'Nut ingredients detected';
    case 'possible_nut_derived_ingredient':
      return 'Review ingredient list';
    case 'no_nut_ingredient_found':
      return 'No nut ingredients found';
    default:
      return 'Cannot verify';
  }
}

function formatDateTime(value: string) {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return new Intl.DateTimeFormat('en-US', {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(date);
}

export function toMissedBarcodeEntries(
  response: MissedBarcodeSummaryResponse,
): MissedBarcodeEntry[] {
  return response.items.map((item) => ({
    id: `${item.barcode}-${item.last_seen_at}`,
    barcode: item.barcode,
    missCount: item.miss_count,
    firstSeenAt: formatDateTime(item.first_seen_at),
    lastSeenAt: formatDateTime(item.last_seen_at),
    latestExplanation: item.latest_explanation ?? undefined,
  }));
}
