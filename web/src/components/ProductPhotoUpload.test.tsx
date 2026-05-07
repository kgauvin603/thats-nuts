import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it, vi } from 'vitest';
import { ProductPhotoUpload } from './ProductPhotoUpload';

const uploadProductPhoto = vi.fn();

vi.mock('../lib/api', () => ({
  ApiError: class ApiError extends Error {},
  uploadProductPhoto: (...args: unknown[]) => uploadProductPhoto(...args),
}));

describe('ProductPhotoUpload', () => {
  it('shows a success state after upload succeeds', async () => {
    const user = userEvent.setup();
    uploadProductPhoto.mockResolvedValue({
      barcode: '5555555555555',
      image_url: 'https://api.thatsnuts.activeadvantage.co/uploads/product_photos/demo.png',
      updated: true,
      message: 'Product photo saved.',
    });

    render(
      <ProductPhotoUpload
        barcode="5555555555555"
        onUploaded={vi.fn()}
      />,
    );

    await user.upload(
      screen.getByTestId('product-photo-input'),
      new File(['image'], 'photo.png', { type: 'image/png' }),
    );

    await waitFor(() => {
      expect(screen.getByText('Product photo saved.')).toBeInTheDocument();
    });
  });

  it('shows an error state after upload fails', async () => {
    const user = userEvent.setup();
    uploadProductPhoto.mockReset();
    uploadProductPhoto.mockRejectedValue(new Error('upload failed'));

    render(
      <ProductPhotoUpload
        barcode="5555555555555"
        onUploaded={vi.fn()}
      />,
    );

    await user.upload(
      screen.getByTestId('product-photo-input'),
      new File(['image'], 'photo.png', { type: 'image/png' }),
    );

    await waitFor(() => {
      expect(
        screen.getByText('Photo could not be uploaded. Please try again.'),
      ).toBeInTheDocument();
    });
  });

  it('renders a clickable placeholder target variant', () => {
    render(
      <ProductPhotoUpload
        barcode="5555555555555"
        onUploaded={vi.fn()}
        variant="placeholder"
      />,
    );

    expect(
      screen.getByRole('button', { name: 'Add product photo for barcode 5555555555555' }),
    ).toBeInTheDocument();
    expect(screen.getByText('Take or upload a photo')).toBeInTheDocument();
  });
});
