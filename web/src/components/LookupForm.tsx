import { FormEvent, useState } from 'react';

interface LookupFormProps {
  disabled: boolean;
  onSubmit: (barcode: string) => Promise<void>;
  onLockedAttempt: () => void;
}

export function LookupForm({
  disabled,
  onSubmit,
  onLockedAttempt,
}: LookupFormProps) {
  const [barcode, setBarcode] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (disabled) {
      onLockedAttempt();
      return;
    }

    const trimmed = barcode.trim();
    if (!trimmed) {
      setError('Enter a barcode before submitting.');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      await onSubmit(trimmed);
    } catch (submissionError) {
      setError(
        submissionError instanceof Error
          ? submissionError.message
          : 'Something went wrong while contacting the backend.',
      );
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <form className="tool-card" id="barcode-checker" onSubmit={handleSubmit}>
      <div className="tool-card-header">
        <span className="eyebrow">Barcode review</span>
        <h2>Check a barcode</h2>
        <p>
          Use the public That’s Nuts API to look up product details, ingredient text,
          and current rule matches.
        </p>
      </div>
      <label className="field">
        <span>Barcode</span>
        <input
          disabled={disabled || isLoading}
          inputMode="numeric"
          name="barcode"
          onChange={(event) => setBarcode(event.target.value)}
          placeholder="3017620422003"
          value={barcode}
        />
      </label>
      <button className="button button-primary" disabled={disabled || isLoading} type="submit">
        {isLoading ? 'Checking...' : 'Check barcode'}
      </button>
      {error ? <p className="field-error">{error}</p> : null}
      <p className="tool-note">
        Validation example: barcode <code>3017620422003</code> should return a
        Nutella product lookup via Open Food Facts with a hazelnut match.
      </p>
    </form>
  );
}
