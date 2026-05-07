import { useId, useRef, useState, type ChangeEvent } from 'react';
import { uploadProductPhoto } from '../lib/api';

interface ProductPhotoUploadProps {
  barcode: string;
  accessibleLabel?: string;
  buttonLabel?: string;
  helperText?: string;
  overwrite?: boolean;
  showStatus?: boolean;
  successText?: string;
  variant?: 'panel' | 'inline';
  onUploaded: (imageUrl: string, message: string) => void;
  onUploadError?: (message: string) => void;
}

export function ProductPhotoUpload({
  barcode,
  accessibleLabel,
  buttonLabel = 'Add product photo',
  helperText = 'Add a product photo to make this saved enrichment easier to recognize.',
  overwrite = false,
  showStatus = true,
  successText = 'Product photo saved.',
  variant = 'panel',
  onUploaded,
  onUploadError,
}: ProductPhotoUploadProps) {
  const inputId = useId();
  const inputRef = useRef<HTMLInputElement | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  async function handleFileChange(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    event.target.value = '';
    if (!file) {
      return;
    }

    setIsUploading(true);
    setErrorMessage(null);
    setSuccessMessage(null);

    try {
      const response = await uploadProductPhoto(barcode, file, overwrite);
      const message = response.message || successText;
      onUploaded(response.image_url, message);
      setSuccessMessage(message);
    } catch (error) {
      const message =
        error instanceof Error && error.message
          ? error.message
          : 'Photo could not be uploaded. Please try again.';
      setErrorMessage(message);
      onUploadError?.(message);
    } finally {
      setIsUploading(false);
    }
  }

  function openFilePicker() {
    if (!isUploading) {
      inputRef.current?.click();
    }
  }

  if (variant === 'inline') {
    return (
      <div className="photo-upload-inline-action">
        <button
          aria-label={accessibleLabel || `${buttonLabel} for barcode ${barcode}`}
          className="photo-upload-link"
          onClick={openFilePicker}
          type="button"
        >
          {isUploading ? 'Uploading photo...' : buttonLabel}
        </button>
        <input
          accept="image/*"
          capture="environment"
          className="visually-hidden-input"
          data-testid="product-photo-input"
          disabled={isUploading}
          id={inputId}
          onChange={handleFileChange}
          ref={inputRef}
          type="file"
        />
        {showStatus && successMessage ? (
          <p className="photo-upload-success">{successMessage}</p>
        ) : null}
        {showStatus && errorMessage ? <p className="photo-upload-error">{errorMessage}</p> : null}
      </div>
    );
  }

  return (
    <div className="photo-upload-panel">
      <p className="photo-upload-helper">{helperText}</p>
      <p className="photo-upload-format-note">JPEG, PNG, or WebP. HEIC is not supported yet.</p>
      <div className="photo-upload-actions">
        <button
          aria-label={accessibleLabel || `Add product photo for barcode ${barcode}`}
          className="button button-secondary photo-upload-button"
          onClick={openFilePicker}
          type="button"
        >
          {isUploading ? 'Uploading photo...' : buttonLabel}
        </button>
        <input
          accept="image/*"
          capture="environment"
          className="visually-hidden-input"
          data-testid="product-photo-input"
          disabled={isUploading}
          id={inputId}
          onChange={handleFileChange}
          ref={inputRef}
          type="file"
        />
      </div>
      {showStatus && successMessage ? <p className="photo-upload-success">{successMessage}</p> : null}
      {showStatus && errorMessage ? <p className="photo-upload-error">{errorMessage}</p> : null}
    </div>
  );
}
