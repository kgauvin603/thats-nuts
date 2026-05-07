import { useId, useRef, useState, type ChangeEvent } from 'react';
import { uploadProductPhoto } from '../lib/api';

interface ProductPhotoUploadProps {
  barcode: string;
  accessibleLabel?: string;
  buttonLabel?: string;
  helperText?: string;
  showStatus?: boolean;
  successText?: string;
  variant?: 'panel' | 'placeholder';
  onUploaded: (imageUrl: string, message: string) => void;
  onUploadError?: (message: string) => void;
}

export function ProductPhotoUpload({
  barcode,
  accessibleLabel,
  buttonLabel = 'Add product photo',
  helperText = 'Add a product photo to make this saved enrichment easier to recognize.',
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
      const response = await uploadProductPhoto(barcode, file);
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

  if (variant === 'placeholder') {
    return (
      <div className="photo-upload-inline">
        <button
          aria-label={accessibleLabel || `Add product photo for barcode ${barcode}`}
          className="product-image-placeholder product-image-placeholder-action"
          onClick={openFilePicker}
          type="button"
        >
          <span aria-hidden="true" className="photo-upload-icon">
            <svg viewBox="0 0 24 24">
              <path d="M8 7.5 9.8 5h4.4L16 7.5h2A2.5 2.5 0 0 1 20.5 10v7A2.5 2.5 0 0 1 18 19.5H6A2.5 2.5 0 0 1 3.5 17v-7A2.5 2.5 0 0 1 6 7.5h2Zm4 2.2A3.6 3.6 0 1 0 12 17a3.6 3.6 0 0 0 0-7.2Zm0 1.8A1.8 1.8 0 1 1 12 15a1.8 1.8 0 0 1 0-3.6Z" />
            </svg>
          </span>
          <strong>{isUploading ? 'Uploading photo...' : buttonLabel}</strong>
          <span>Take or upload a photo</span>
          <span className="photo-upload-format-note">JPEG, PNG, or WebP</span>
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
