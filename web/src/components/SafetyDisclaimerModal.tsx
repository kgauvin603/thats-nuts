import { SAFETY_NOTICE_COPY } from '../lib/constants';

interface SafetyDisclaimerModalProps {
  onAccept: () => void;
  onExit: () => void;
}

export function SafetyDisclaimerModal({
  onAccept,
  onExit,
}: SafetyDisclaimerModalProps) {
  return (
    <div className="modal-backdrop" role="presentation">
      <div
        aria-labelledby="safety-disclaimer-title"
        aria-modal="true"
        className="modal-card"
        role="dialog"
      >
        <span className="eyebrow">Required before use</span>
        <h2 id="safety-disclaimer-title">Important Safety Notice</h2>
        <div className="modal-copy">
          {SAFETY_NOTICE_COPY.split('\n\n').slice(1).map((paragraph) => (
            <p key={paragraph}>{paragraph}</p>
          ))}
        </div>
        <div className="modal-actions">
          <button className="button button-primary" onClick={onAccept} type="button">
            I Understand and Agree
          </button>
          <button className="button button-secondary" onClick={onExit} type="button">
            Exit
          </button>
        </div>
      </div>
    </div>
  );
}
