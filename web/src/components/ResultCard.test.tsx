import { render, screen } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import { ResultCard } from './ResultCard';

vi.mock('../lib/api', () => ({
  uploadProductPhoto: vi.fn(),
  ApiError: class ApiError extends Error {},
}));

describe('ResultCard', () => {
  it('shows the add-photo prompt for enrichment results without an image', () => {
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

    expect(screen.getByText('Add a product photo?')).toBeInTheDocument();
    expect(
      screen.getByText(
        'Take or upload a photo so this enriched record is easier to identify later.',
      ),
    ).toBeInTheDocument();
    expect(
      screen.getByLabelText('Take or upload product photo'),
    ).toBeInTheDocument();
  });
});
