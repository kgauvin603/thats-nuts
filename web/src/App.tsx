import { useEffect, useState } from 'react';
import { AcornMark } from './components/AcornMark';
import { IngredientForm } from './components/IngredientForm';
import { LookupForm } from './components/LookupForm';
import { ResultCard } from './components/ResultCard';
import { SafetyDisclaimerModal } from './components/SafetyDisclaimerModal';
import { checkIngredients, getApiBaseUrl, lookupProduct } from './lib/api';
import { APP_NAME } from './lib/constants';
import { acceptDisclaimer, hasAcceptedDisclaimer } from './lib/disclaimer';
import { fromIngredientResponse, fromLookupResponse } from './lib/result';
import type { UnifiedResult } from './lib/types';

function App() {
  const [isDisclaimerAccepted, setIsDisclaimerAccepted] = useState(false);
  const [hasExited, setHasExited] = useState(false);
  const [result, setResult] = useState<UnifiedResult | null>(null);

  useEffect(() => {
    setIsDisclaimerAccepted(hasAcceptedDisclaimer());
  }, []);

  function handleAcceptDisclaimer() {
    acceptDisclaimer();
    setIsDisclaimerAccepted(true);
    setHasExited(false);
  }

  function handleExit() {
    setHasExited(true);

    if (window.history.length > 1) {
      window.history.back();
      return;
    }

    window.location.replace('about:blank');
  }

  function handleLockedAttempt() {
    setHasExited(false);
  }

  async function submitBarcode(barcode: string) {
    const response = await lookupProduct(barcode);
    setResult(fromLookupResponse(barcode, response));
  }

  async function submitIngredients(ingredientText: string) {
    const response = await checkIngredients(ingredientText);
    setResult(fromIngredientResponse(ingredientText, response));
  }

  return (
    <div className="page-shell">
      {!isDisclaimerAccepted ? (
        <SafetyDisclaimerModal
          onAccept={handleAcceptDisclaimer}
          onExit={handleExit}
        />
      ) : null}

      <header className="hero-card">
        <div className="hero-copy">
          <div className="brand-lockup">
            <div className="brand-mark-shell">
              <AcornMark />
            </div>
            <div>
              <span className="eyebrow">Allergy-aware ingredient support</span>
              <h1>{APP_NAME}</h1>
            </div>
          </div>
          <p className="hero-lead">
            Allergy-aware ingredient and barcode review with a warm, simple flow
            that helps you pause, check, and verify.
          </p>
          <div className="hero-actions">
            <a className="button button-primary" href="#barcode-checker">
              Check a barcode
            </a>
            <a className="button button-secondary" href="#ingredient-checker">
              Paste ingredients
            </a>
          </div>
          <p className="hero-caption">
            That’sNuts is informational only. Final product safety decisions are
            always yours.
          </p>
        </div>
        <aside className="hero-panel">
          <div className="mini-card">
            <span className="detail-label">How it works</span>
            <ol>
              <li>Scan or enter a barcode.</li>
              <li>Review the product and ingredients.</li>
              <li>Verify the physical label before use.</li>
            </ol>
          </div>
          <div className="mini-card mini-card-muted">
            <span className="detail-label">API</span>
            <p>{getApiBaseUrl()}</p>
          </div>
        </aside>
      </header>

      <main className="content-grid">
        <section className="info-card">
          <span className="eyebrow">A calm companion</span>
          <h2>Readable product-safety guidance</h2>
          <p>
            This site mirrors the That’sNuts mobile app’s tone: warm, trustworthy,
            and careful about uncertainty. When a match appears, the UI stays calm.
            When no match appears, the language stays cautious.
          </p>
        </section>

        <section className="tools-grid" aria-label="That’sNuts tools">
          <LookupForm
            disabled={!isDisclaimerAccepted}
            onLockedAttempt={handleLockedAttempt}
            onSubmit={submitBarcode}
          />
          <IngredientForm
            disabled={!isDisclaimerAccepted}
            onLockedAttempt={handleLockedAttempt}
            onSubmit={submitIngredients}
          />
        </section>

        {hasExited && !isDisclaimerAccepted ? (
          <section className="info-card">
            <span className="eyebrow">Session closed</span>
            <h2>Safety notice not accepted</h2>
            <p>
              The companion tools remain unavailable until the required safety
              notice is accepted.
            </p>
          </section>
        ) : null}

        {result ? <ResultCard result={result} /> : null}
      </main>
    </div>
  );
}

export default App;
