import { useEffect, useState } from 'react';
import { fetchScanHistory } from '../lib/api';
import { toHistoryEntries, type HistoryEntry } from '../lib/history';
import { ProductImageCard } from './ProductImageCard';

export function HistorySection() {
  const [entries, setEntries] = useState<HistoryEntry[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(false);

  async function loadHistory() {
    setIsLoading(true);
    setError(false);

    try {
      const response = await fetchScanHistory();
      setEntries(toHistoryEntries(response));
    } catch {
      setError(true);
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    void loadHistory();
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
          onClick={() => void loadHistory()}
          type="button"
        >
          Refresh
        </button>
      </div>

      {isLoading ? (
        <div className="history-state-card">
          <p>Loading history...</p>
        </div>
      ) : null}

      {!isLoading && error ? (
        <div className="history-state-card">
          <p>History could not be loaded. Please try again.</p>
        </div>
      ) : null}

      {!isLoading && !error && entries.length === 0 ? (
        <div className="history-state-card">
          <p>No recent scans yet.</p>
        </div>
      ) : null}

      {!isLoading && !error && entries.length > 0 ? (
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
