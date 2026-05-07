import { render, screen } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import { ResultCard } from './ResultCard';

vi.mock('../lib/api', () => ({
  uploadProductPhoto: vi.fn(),
  ApiError: class ApiError extends Error {},
}));

describe('ResultCard', () => {
  it('uses the image placeholder as the add-photo button for enrichment results without an image', () => {
    render(
      <ResultCard
        onPhotoUploaded={vi.fn()}
        result={{
          mode: 'barcode',
          title: 'Demo Lotion',
          sourceLabel: 'enrichment',
          barcode: '5555555555555',
          product: {
            barcode: '5555555555555',
            product_name: 'Demo Lotion',
            brand_name: 'Demo Brand',
            image_url: null,
            ingredient_text: 'Water, Sweet Almond Oil',
            ingredient_coverage_status: 'complete',
            source: 'text_scan',
          },
          status: 'contains_nut_ingredient',
          matchedIngredients: [],
          explanation: 'Sweet almond oil was detected.',
          ingredientText: 'Water, Sweet Almond Oil',
          unknownTerms: [],
          lookupPath: [],
        }}
      />,
    );

    expect(
      screen.getByRole('button', {
        name: 'Add product photo for barcode 5555555555555',
      }),
    ).toBeInTheDocument();
    expect(screen.getByText('Take or upload a photo')).toBeInTheDocument();
  });

  it('does not show the upload placeholder when an image already exists', () => {
    render(
      <ResultCard
        onPhotoUploaded={vi.fn()}
        result={{
          mode: 'barcode',
          title: 'Nutella',
          sourceLabel: 'open_food_facts',
          barcode: '3017620422003',
          product: {
            barcode: '3017620422003',
            product_name: 'Nutella',
            brand_name: 'Ferrero',
            image_url: 'https://images.example.invalid/nutella.jpg',
            ingredient_text: 'Sugar, Hazelnuts',
            ingredient_coverage_status: 'complete',
            source: 'open_food_facts',
          },
          status: 'contains_nut_ingredient',
          matchedIngredients: [],
          explanation: 'Hazelnut was detected.',
          ingredientText: 'Sugar, Hazelnuts',
          unknownTerms: [],
          lookupPath: [],
        }}
      />,
    );

    expect(
      screen.queryByRole('button', {
        name: 'Add product photo for barcode 3017620422003',
      }),
    ).not.toBeInTheDocument();
  });
});
