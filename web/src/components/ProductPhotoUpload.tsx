import { useId, useState, type ChangeEvent } from 'react';
import { ApiError, uploadProductPhoto } from '../lib/api';

interface ProductPhotoUploadProps {
  barcode: string;
  buttonLabel?: string;
  helperText?: string;
  successText?: string;
  onUploaded: (imageUrl: string) => void;
}

export function ProductPhotoUpload({
  barcode,
  buttonLabel = 'Add product photo',
  helperText = 'Add a product photo to make this saved enrichment easier to recognize.',
  successText = 'Product photo saved.',
  onUploaded,
}: ProductPhotoUploadProps) {
  const inputId = useId();
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
      onUploaded(response.image_url);
      setSuccessMessage(response.message || successText);
    } catch (error) {
      const message =
        error instanceof ApiError
          ? error.message
          : 'Product photo upload failed. Please try again.';
      setErrorMessage(message);
    } finally {
      setIsUploading(false);
    }
  }

  return (
    <div className="photo-upload-panel">
      <p className="photo-upload-helper">{helperText}</p>
      <div className="photo-upload-actions">
        <label className="button button-secondary photo-upload-button" htmlFor={inputId}>
          {isUploading ? 'Uploading photo...' : buttonLabel}
        </label>
        <input
          accept="image/*"
          capture="environment"
          className="visually-hidden-input"
          disabled={isUploading}
          id={inputId}
          onChange={handleFileChange}
          type="file"
        />
      </div>
      {successMessage ? <p className="photo-upload-success">{successMessage}</p> : null}
      {errorMessage ? <p className="photo-upload-error">{errorMessage}</p> : null}
    </div>
  );
}
