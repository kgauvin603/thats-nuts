import { FormEvent, useState } from 'react';

interface IngredientFormProps {
  disabled: boolean;
  onSubmit: (ingredientText: string) => Promise<void>;
  onLockedAttempt: () => void;
}

export function IngredientForm({
  disabled,
  onSubmit,
  onLockedAttempt,
}: IngredientFormProps) {
  const [ingredientText, setIngredientText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (disabled) {
      onLockedAttempt();
      return;
    }

    const trimmed = ingredientText.trim();
    if (!trimmed) {
      setError('Paste ingredients before submitting.');
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
    <form className="tool-card" id="ingredient-checker" onSubmit={handleSubmit}>
      <div className="tool-card-header">
        <span className="eyebrow">Manual ingredient review</span>
        <h2>Paste ingredients</h2>
        <p>
          Send the ingredient text to the backend rules engine without duplicating
          any product-safety logic in the browser.
        </p>
      </div>
      <label className="field">
        <span>Ingredient list</span>
        <textarea
          disabled={disabled || isLoading}
          name="ingredients"
          onChange={(event) => setIngredientText(event.target.value)}
          placeholder="Sugar, palm oil, hazelnuts 13%, skim milk powder..."
          rows={8}
          value={ingredientText}
        />
      </label>
      <button className="button button-secondary" disabled={disabled || isLoading} type="submit">
        {isLoading ? 'Reviewing...' : 'Check ingredients'}
      </button>
      {error ? <p className="field-error">{error}</p> : null}
      <p className="tool-note">
        The frontend calls <code>POST /check-ingredients</code>, matching the
        existing backend route.
      </p>
    </form>
  );
}
