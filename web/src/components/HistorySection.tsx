import { useEffect, useState } from 'react';
import { fetchMissedBarcodeSummary, fetchScanHistory } from '../lib/api';
import {
  toHistoryEntries,
  toMissedBarcodeEntries,
  type HistoryEntry,
  type MissedBarcodeEntry,
} from '../lib/history';
import { ProductImageCard } from './ProductImageCard';

export function HistorySection() {
  const [entries, setEntries] = useState<HistoryEntry[]>([]);
  const [misses, setMisses] = useState<MissedBarcodeEntry[]>([]);
  const [isHistoryLoading, setIsHistoryLoading] = useState(true);
  const [historyError, setHistoryError] = useState(false);
  const [isMissesLoading, setIsMissesLoading] = useState(true);
  const [missesError, setMissesError] = useState(false);

  async function loadHistory() {
    setIsHistoryLoading(true);
    setHistoryError(false);

    try {
      const response = await fetchScanHistory();
      setEntries(toHistoryEntries(response));
    } catch {
      setHistoryError(true);
    } finally {
      setIsHistoryLoading(false);
    }
  }

  async function loadMisses() {
    setIsMissesLoading(true);
    setMissesError(false);

    try {
      const response = await fetchMissedBarcodeSummary();
      setMisses(toMissedBarcodeEntries(response));
    } catch {
      setMissesError(true);
    } finally {
      setIsMissesLoading(false);
    }
  }

  async function refreshAll() {
    await Promise.all([loadHistory(), loadMisses()]);
  }

  useEffect(() => {
    void refreshAll();
  }, []);

  return (
    <section className="history-section" id="history">
      <div className="history-header">
        <div>
          <span className="eyebrow">Recent activity</span>
          <h2>History</h2>
          <p className="history-caption">
            Recent barcode lookups, barcode enrichments, and manual ingredient
            checks from the backend scan history.
          </p>
        </div>
        <button
          className="button button-secondary"
          onClick={() => void refreshAll()}
          type="button"
        >
          Refresh
        </button>
      </div>

      <section className="history-state-card missed-barcode-panel">
        <div className="missed-barcode-header">
          <div>
            <span className="eyebrow">Operational telemetry</span>
            <h3>Unresolved barcode scans</h3>
            <p className="history-caption">
              Repeated barcode lookups that still do not resolve to a usable product
              record. This panel stays separate from the user-facing result history.
            </p>
          </div>
        </div>

        {isMissesLoading ? <p>Loading unresolved barcode summary...</p> : null}

        {!isMissesLoading && missesError ? (
          <p>Unresolved barcode summary could not be loaded.</p>
        ) : null}

        {!isMissesLoading && !missesError && misses.length === 0 ? (
          <p>No unresolved barcode misses yet.</p>
        ) : null}

        {!isMissesLoading && !missesError && misses.length > 0 ? (
          <div className="missed-barcode-list">
            {misses.map((entry) => (
              <article className="missed-barcode-card" key={entry.id}>
                <div className="missed-barcode-meta">
                  <strong>{entry.barcode}</strong>
                  <div className="pill-list">
                    <span className="pill">{entry.missCount} misses</span>
                    <span className="pill">Last seen {entry.lastSeenAt}</span>
                  </div>
                </div>
                <p>{entry.latestExplanation || 'No explanation was returned.'}</p>
              </article>
            ))}
          </div>
        ) : null}
      </section>

      {isHistoryLoading ? (
        <div className="history-state-card">
          <p>Loading history...</p>
        </div>
      ) : null}

      {!isHistoryLoading && historyError ? (
        <div className="history-state-card">
          <p>History could not be loaded. Please try again.</p>
        </div>
      ) : null}

      {!isHistoryLoading && !historyError && entries.length === 0 ? (
        <div className="history-state-card">
          <p>No recent scans yet.</p>
        </div>
      ) : null}

      {!isHistoryLoading && !historyError && entries.length > 0 ? (
        <div className="history-grid">
          {entries.map((entry) => (
            <article className="history-card" key={entry.id}>
              <div className="history-card-top">
                <ProductImageCard
                  imageUrl={entry.imageUrl}
                  productName={entry.productName || entry.scanType}
                />
                <div className="history-card-summary">
                  <span className="detail-label">{entry.scanType}</span>
                  <h3>{entry.productName || 'Saved scan'}</h3>
                  <p>{entry.brandName || 'Brand unavailable'}</p>
                  <div className="pill-list">
                    <span className="pill">{entry.assessmentLabel}</span>
                    <span className="pill">{entry.createdAt}</span>
                  </div>
                </div>
              </div>

              <div className="history-detail-grid">
                {entry.barcode ? (
                  <div className="detail-panel">
                    <span className="detail-label">Barcode</span>
                    <p>{entry.barcode}</p>
                  </div>
                ) : null}
                {entry.productSource ? (
                  <div className="detail-panel">
                    <span className="detail-label">Source</span>
                    <p>{entry.productSource}</p>
                  </div>
                ) : null}
                {entry.matchedSummary ? (
                  <div className="detail-panel">
                    <span className="detail-label">Matched ingredients</span>
                    <p>{entry.matchedSummary}</p>
                  </div>
                ) : null}
                {entry.submittedIngredientText ? (
                  <div className="detail-panel">
                    <span className="detail-label">Submitted ingredients</span>
                    <p className="ingredient-text">{entry.submittedIngredientText}</p>
                  </div>
                ) : null}
              </div>

              <div className="detail-panel">
                <span className="detail-label">Summary</span>
                <p>{entry.explanation || 'No additional explanation was returned.'}</p>
              </div>
            </article>
          ))}
        </div>
      ) : null}
    </section>
  );
}
