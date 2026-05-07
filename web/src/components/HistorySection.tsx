import { useEffect, useState } from 'react';
import {
  fetchInconsistentBarcodeSummary,
  fetchMissedBarcodeSummary,
  fetchScanHistory,
} from '../lib/api';
import {
  toInconsistentBarcodeEntries,
  toHistoryEntries,
  toMissedBarcodeEntries,
  type HistoryEntry,
  type InconsistentBarcodeEntry,
  type MissedBarcodeEntry,
} from '../lib/history';
import { ProductImageCard } from './ProductImageCard';

export function HistorySection() {
  const [entries, setEntries] = useState<HistoryEntry[]>([]);
  const [inconsistent, setInconsistent] = useState<InconsistentBarcodeEntry[]>([]);
  const [misses, setMisses] = useState<MissedBarcodeEntry[]>([]);
  const [isHistoryLoading, setIsHistoryLoading] = useState(true);
  const [historyError, setHistoryError] = useState(false);
  const [isInconsistentLoading, setIsInconsistentLoading] = useState(true);
  const [inconsistentError, setInconsistentError] = useState(false);
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

  async function loadInconsistent() {
    setIsInconsistentLoading(true);
    setInconsistentError(false);

    try {
      const response = await fetchInconsistentBarcodeSummary();
      setInconsistent(toInconsistentBarcodeEntries(response));
    } catch {
      setInconsistentError(true);
    } finally {
      setIsInconsistentLoading(false);
    }
  }

  async function refreshAll() {
    await Promise.all([loadHistory(), loadInconsistent(), loadMisses()]);
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

      <section className="history-subsection">
        <div className="history-subsection-header">
          <div>
            <span className="eyebrow">Visible history</span>
            <h2>Recent successful checks</h2>
            <p className="history-caption">
              Successful barcode lookups, barcode enrichments, and manual ingredient
              checks that returned useful product or ingredient context.
            </p>
          </div>
        </div>

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

      <section className="history-subsection verification-section">
        <div className="history-subsection-header">
          <div>
            <span className="eyebrow">Source review</span>
            <h2>Needs verification</h2>
            <p className="history-caption">
              These barcodes returned source data that looked inconsistent, so
              That’s Nuts did not treat them as verified product results.
            </p>
          </div>
        </div>

        {isInconsistentLoading ? (
          <div className="history-state-card">
            <p>Loading verification group...</p>
          </div>
        ) : null}

        {!isInconsistentLoading && inconsistentError ? (
          <div className="history-state-card">
            <p>Verification group could not be loaded.</p>
          </div>
        ) : null}

        {!isInconsistentLoading && !inconsistentError && inconsistent.length === 0 ? (
          <div className="history-state-card">
            <p>No verification-needed barcode groups yet.</p>
          </div>
        ) : null}

        {!isInconsistentLoading && !inconsistentError && inconsistent.length > 0 ? (
          <div className="missed-barcode-list">
            {inconsistent.map((entry) => (
              <article className="missed-barcode-card" key={entry.id}>
                <div className="missed-barcode-meta">
                  <strong>{entry.barcode}</strong>
                  <div className="pill-list">
                    <span className="pill">{entry.count} inconsistent lookups</span>
                    <span className="pill">First seen {entry.firstSeenAt}</span>
                    <span className="pill">Last seen {entry.lastSeenAt}</span>
                  </div>
                </div>
                {entry.latestSource ? (
                  <p className="history-inline-note">Latest source: {entry.latestSource}</p>
                ) : null}
                <p>{entry.latestExplanation || 'No explanation was returned.'}</p>
              </article>
            ))}
          </div>
        ) : null}
      </section>

      <section className="history-subsection missed-barcode-panel">
        <div className="history-subsection-header">
          <div>
            <span className="eyebrow">Operational telemetry</span>
            <h2>Unresolved barcode scans</h2>
            <p className="history-caption">
              Repeated barcode lookups that still do not resolve to a usable product
              record. These stay separate from user-facing result history.
            </p>
          </div>
        </div>

        {isMissesLoading ? (
          <div className="history-state-card">
            <p>Loading unresolved barcode summary...</p>
          </div>
        ) : null}

        {!isMissesLoading && missesError ? (
          <div className="history-state-card">
            <p>Unresolved barcode summary could not be loaded.</p>
          </div>
        ) : null}

        {!isMissesLoading && !missesError && misses.length === 0 ? (
          <div className="history-state-card">
            <p>No unresolved barcode misses yet.</p>
          </div>
        ) : null}

        {!isMissesLoading && !missesError && misses.length > 0 ? (
          <div className="missed-barcode-list">
            {misses.map((entry) => (
              <article className="missed-barcode-card" key={entry.id}>
                <div className="missed-barcode-meta">
                  <strong>{entry.barcode}</strong>
                  <div className="pill-list">
                    <span className="pill">{entry.missCount} misses</span>
                    <span className="pill">First seen {entry.firstSeenAt}</span>
                    <span className="pill">Last seen {entry.lastSeenAt}</span>
                  </div>
                </div>
                <p>{entry.latestExplanation || 'No explanation was returned.'}</p>
              </article>
            ))}
          </div>
        ) : null}
      </section>
    </section>
  );
}
