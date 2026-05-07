import { useEffect, useState } from 'react';
import { RESULT_REMINDER } from '../lib/constants';
import type { UnifiedResult } from '../lib/types';
import { ProductPhotoUpload } from './ProductPhotoUpload';
import { ProductImageCard } from './ProductImageCard';

interface ResultCardProps {
  result: UnifiedResult;
  onPhotoUploaded?: (imageUrl: string) => void;
}

function getStatusMeta(status: UnifiedResult['status']) {
  switch (status) {
    case 'contains_nut_ingredient':
      return {
        tone: 'caution',
        badge: 'Detected',
        heading: 'Nut-linked ingredient detected',
        body: 'A current ruleset match was found. Please slow down and verify the physical label before using or purchasing this product.',
      };
    case 'possible_nut_derived_ingredient':
      return {
        tone: 'review',
        badge: 'Review',
        heading: 'Possible nut-derived ingredient',
        body: 'One or more ingredients may be nut-derived or too generic to interpret safely from the available text alone.',
      };
    case 'no_nut_ingredient_found':
      return {
        tone: 'clear',
        badge: 'No match',
        heading: 'No matched nut-linked ingredient detected',
        body: 'No matched nut-linked ingredient was detected by the current ruleset. Always verify the physical label.',
      };
    default:
      return {
        tone: 'neutral',
        badge: 'Needs review',
        heading: 'Unable to verify safely',
        body: 'A complete, readable ingredient list was not available for reliable review.',
      };
  }
}

export function ResultCard({ result, onPhotoUploaded }: ResultCardProps) {
  const [uploadNotice, setUploadNotice] = useState<{
    tone: 'success' | 'error';
    message: string;
  } | null>(null);
  const meta = getStatusMeta(result.status);
  const hasProductDetails =
    result.mode === 'barcode' &&
    (result.product?.product_name ||
      result.product?.brand_name ||
      result.product?.image_url ||
      result.barcode);
  const shouldOfferPhotoUpload =
    result.mode === 'barcode' &&
    Boolean(result.barcode) &&
    !result.product?.image_url &&
    Boolean(onPhotoUploaded) &&
    (result.sourceLabel === 'enrichment' ||
      result.product?.source === 'manual_entry' ||
      result.product?.source === 'text_scan');

  useEffect(() => {
    setUploadNotice(null);
  }, [result.barcode, result.product?.image_url, result.sourceLabel]);

  return (
    <section aria-live="polite" className="result-card">
      <div className={`result-status result-status-${meta.tone}`}>
        <div>
          <span className="result-badge">{meta.badge}</span>
          <h3>{meta.heading}</h3>
          <p>{meta.body}</p>
        </div>
      </div>

      {hasProductDetails ? (
        <div className="result-grid">
          <ProductImageCard
            imageUrl={result.product?.image_url}
            productName={result.product?.product_name}
            placeholderContent={
              shouldOfferPhotoUpload && result.barcode ? (
                <ProductPhotoUpload
                  accessibleLabel={`Add product photo for barcode ${result.barcode}`}
                  barcode={result.barcode}
                  buttonLabel="Add product photo"
                  onUploaded={(imageUrl, message) => {
                    setUploadNotice({ tone: 'success', message });
                    onPhotoUploaded?.(imageUrl);
                  }}
                  onUploadError={(message) => {
                    setUploadNotice({ tone: 'error', message });
                  }}
                  showStatus={false}
                  variant="placeholder"
                />
              ) : undefined
            }
          />
          <div className="stack">
            <div className="detail-panel">
              <span className="detail-label">Product</span>
              <strong>{result.product?.product_name || 'Unknown product'}</strong>
              <p>{result.product?.brand_name || 'Brand unavailable'}</p>
            </div>
            <div className="detail-panel detail-panel-inline">
              <div>
                <span className="detail-label">Source</span>
                <strong>{result.sourceLabel}</strong>
              </div>
              <div>
                <span className="detail-label">Barcode</span>
                <strong>{result.barcode || 'Unavailable'}</strong>
              </div>
            </div>
          </div>
        </div>
      ) : null}

      {uploadNotice ? (
        <p className={uploadNotice.tone === 'success' ? 'photo-upload-success' : 'photo-upload-error'}>
          {uploadNotice.message}
        </p>
      ) : null}

      <div className="stack">
        <div className="detail-panel">
          <span className="detail-label">Explanation</span>
          <p>{result.explanation}</p>
        </div>

        {result.matchedIngredients.length > 0 ? (
          <div className="detail-panel">
            <span className="detail-label">Matched ingredients</span>
            <div className="chip-list">
              {result.matchedIngredients.map((ingredient) => (
                <article className="ingredient-chip" key={`${ingredient.original_text}-${ingredient.nut_source}`}>
                  <strong>{ingredient.display_name || ingredient.original_text}</strong>
                  <span>Nut source: {ingredient.nut_source}</span>
                  <span>Confidence: {ingredient.confidence}</span>
                  <p>{ingredient.reason}</p>
                </article>
              ))}
            </div>
          </div>
        ) : null}

        {result.unknownTerms.length > 0 ? (
          <div className="detail-panel">
            <span className="detail-label">Unknown terms to review</span>
            <div className="pill-list">
              {result.unknownTerms.map((term) => (
                <span className="pill" key={term}>
                  {term}
                </span>
              ))}
            </div>
          </div>
        ) : null}

        {result.ingredientText ? (
          <div className="detail-panel">
            <span className="detail-label">Reviewed ingredients</span>
            <p className="ingredient-text">{result.ingredientText}</p>
          </div>
        ) : null}

        {result.lookupPath && result.lookupPath.length > 0 ? (
          <details className="detail-panel details-panel">
            <summary>Lookup path</summary>
            <div className="pill-list">
              {result.lookupPath.map((step) => (
                <span className="pill" key={step}>
                  {step}
                </span>
              ))}
            </div>
          </details>
        ) : null}

        <div className="reminder-banner">
          <strong>Safety reminder</strong>
          <p>{RESULT_REMINDER}</p>
        </div>
      </div>
    </section>
  );
}
