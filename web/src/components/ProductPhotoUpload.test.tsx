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

  it('passes overwrite=true when replacing a saved product photo', async () => {
    const user = userEvent.setup();
    uploadProductPhoto.mockReset();
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
        overwrite
        variant="inline"
      />,
    );

    await user.upload(
      screen.getByTestId('product-photo-input'),
      new File(['image'], 'photo.png', { type: 'image/png' }),
    );

    await waitFor(() => {
      expect(uploadProductPhoto).toHaveBeenCalledWith(
        '5555555555555',
        expect.any(File),
        true,
      );
    });
  });

  it('shows the returned informational message when the backend reports updated=false', async () => {
    const user = userEvent.setup();
    uploadProductPhoto.mockReset();
    uploadProductPhoto.mockResolvedValue({
      barcode: '5555555555555',
      image_url: 'https://api.thatsnuts.activeadvantage.co/uploads/product_photos/existing.jpg',
      updated: false,
      message: 'This saved product already has an image. Use replace photo to update it.',
    });

    render(
      <ProductPhotoUpload
        barcode="5555555555555"
        onUploaded={vi.fn()}
      />,
    );

    await user.upload(
      screen.getByTestId('product-photo-input'),
      new File(['image'], 'photo.jpg', { type: 'image/jpeg' }),
    );

    await waitFor(() => {
      expect(
        screen.getByText('This saved product already has an image. Use replace photo to update it.'),
      ).toBeInTheDocument();
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
        screen.getByText('upload failed'),
      ).toBeInTheDocument();
    });
  });

  it('shows a HEIC-specific rejection message from the backend', async () => {
    const user = userEvent.setup();
    uploadProductPhoto.mockReset();
    uploadProductPhoto.mockRejectedValue(
      new Error(
        'HEIC photos are not supported yet. Please choose Most Compatible/JPEG or upload a JPEG, PNG, or WebP.',
      ),
    );

    render(
      <ProductPhotoUpload
        barcode="5555555555555"
        onUploaded={vi.fn()}
      />,
    );

    await user.upload(
      screen.getByTestId('product-photo-input'),
      new File(['image'], 'photo.heic', { type: 'image/heic' }),
    );

    await waitFor(() => {
      expect(
        screen.getByText(
          'HEIC photos are not supported yet. Please choose Most Compatible/JPEG or upload a JPEG, PNG, or WebP.',
        ),
      ).toBeInTheDocument();
    });
  });

  it('shows a friendly network-reachability message when the backend cannot be reached', async () => {
    const user = userEvent.setup();
    uploadProductPhoto.mockReset();
    uploadProductPhoto.mockRejectedValue(
      new Error(
        'Upload request could not reach the API. Please check network/CORS or try again.',
      ),
    );

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
        screen.getByText(
          'Upload request could not reach the API. Please check network/CORS or try again.',
        ),
      ).toBeInTheDocument();
    });
  });
});
