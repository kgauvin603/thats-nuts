import { fireEvent, render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { ProductImageCard } from './ProductImageCard';

describe('ProductImageCard', () => {
  it('renders the product image when a URL is present', () => {
    render(
      <ProductImageCard
        imageUrl="https://images.example.invalid/nutella.jpg"
        productName="Nutella"
      />,
    );

    expect(screen.getByAltText('Nutella')).toBeInTheDocument();
  });

  it('shows a placeholder when the image fails to load', () => {
    const view = render(
      <ProductImageCard
        imageUrl="https://images.example.invalid/missing.jpg"
        productName="Nutella"
      />,
    );

    fireEvent.error(view.getByAltText('Nutella'));

    expect(screen.getByLabelText('Product image placeholder')).toBeInTheDocument();
  });

  it('renders custom placeholder content when provided', () => {
    render(
      <ProductImageCard
        imageUrl={null}
        placeholderContent={<button type="button">Add product photo</button>}
        productName="Nutella"
      />,
    );

    expect(screen.getByRole('button', { name: 'Add product photo' })).toBeInTheDocument();
  });
});
