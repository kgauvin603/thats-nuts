import type { IngredientCheckStatus } from './types';

export interface ScanHistoryResponse {
  items: ScanHistoryItem[];
}

export interface GroupedScanHistoryResponse {
  items: GroupedScanHistoryItem[];
}

export interface MissedBarcodeSummaryResponse {
  items: MissedBarcodeSummaryItem[];
}

export interface InconsistentBarcodeSummaryResponse {
  items: InconsistentBarcodeSummaryItem[];
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

export interface GroupedScanHistoryItem {
  scan_type: 'manual_ingredient_check' | 'barcode_lookup' | 'barcode_enrichment';
  grouped_scan_type: 'manual_ingredient_check' | 'barcode_lookup' | 'barcode_enrichment';
  barcode?: string | null;
  product_name?: string | null;
  brand_name?: string | null;
  image_url?: string | null;
  product_source?: string | null;
  submitted_ingredient_text?: string | null;
  assessment_status: IngredientCheckStatus;
  explanation?: string | null;
  matched_ingredient_summary?: string | null;
  scan_count?: number | null;
  first_seen_at: string;
  last_seen_at: string;
  latest_explanation?: string | null;
  latest_source?: string | null;
}

export interface MissedBarcodeSummaryItem {
  barcode: string;
  miss_count: number;
  first_seen_at: string;
  last_seen_at: string;
  latest_explanation?: string | null;
}

export interface InconsistentBarcodeSummaryItem {
  barcode: string;
  count: number;
  first_seen_at: string;
  last_seen_at: string;
  latest_explanation?: string | null;
  latest_source?: string | null;
  product_quality_status: 'inconsistent';
}

export interface HistoryEntry {
  id: string;
  rawScanType: ScanHistoryItem['scan_type'];
  scanType: string;
  createdAt: string;
  firstSeenAt?: string;
  lastSeenAt?: string;
  scanCount?: number;
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

export interface InconsistentBarcodeEntry {
  id: string;
  barcode: string;
  count: number;
  firstSeenAt: string;
  lastSeenAt: string;
  latestExplanation?: string;
  latestSource?: string;
  productQualityStatus: 'inconsistent';
}

export function toHistoryEntries(response: ScanHistoryResponse): HistoryEntry[] {
  return response.items.map((item, index) => ({
    id: `${item.created_at}-${item.barcode || item.scan_type}-${index}`,
    rawScanType: item.scan_type,
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

export function toGroupedHistoryEntries(
  response: GroupedScanHistoryResponse,
): HistoryEntry[] {
  return response.items.map((item, index) => ({
    id: `${item.grouped_scan_type}-${item.barcode || item.last_seen_at}-${index}`,
    rawScanType: item.grouped_scan_type,
    scanType: formatScanType(item.grouped_scan_type),
    createdAt: formatDateTime(item.last_seen_at),
    firstSeenAt: formatDateTime(item.first_seen_at),
    lastSeenAt: formatDateTime(item.last_seen_at),
    scanCount: item.scan_count ?? 1,
    barcode: item.barcode ?? undefined,
    productName: item.product_name ?? undefined,
    brandName: item.brand_name ?? undefined,
    imageUrl: item.image_url ?? undefined,
    assessmentLabel: formatAssessment(item.assessment_status),
    explanation: item.latest_explanation ?? item.explanation ?? undefined,
    matchedSummary: item.matched_ingredient_summary ?? undefined,
    submittedIngredientText: item.submitted_ingredient_text ?? undefined,
    productSource: item.latest_source ?? item.product_source ?? undefined,
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

export function toInconsistentBarcodeEntries(
  response: InconsistentBarcodeSummaryResponse,
): InconsistentBarcodeEntry[] {
  return response.items.map((item) => ({
    id: `${item.barcode}-${item.last_seen_at}`,
    barcode: item.barcode,
    count: item.count,
    firstSeenAt: formatDateTime(item.first_seen_at),
    lastSeenAt: formatDateTime(item.last_seen_at),
    latestExplanation: item.latest_explanation ?? undefined,
    latestSource: item.latest_source ?? undefined,
    productQualityStatus: item.product_quality_status,
  }));
}
