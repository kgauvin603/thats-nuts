import type {
  IngredientCheckResponse,
  ProductLookupResponse,
  UnifiedResult,
} from './types';

export function fromLookupResponse(
  barcode: string,
  response: ProductLookupResponse,
): UnifiedResult {
  return {
    mode: 'barcode',
    title: response.product?.product_name || 'Barcode review',
    sourceLabel: response.source,
    barcode,
    product: response.product,
    status: response.assessment_result ?? 'cannot_verify',
    matchedIngredients: response.matched_ingredients,
    explanation: response.explanation,
    ingredientText: response.ingredient_text,
    unknownTerms: response.unknown_terms,
    lookupPath: response.lookup_path,
  };
}

export function fromIngredientResponse(
  ingredientText: string,
  response: IngredientCheckResponse,
): UnifiedResult {
  return {
    mode: 'ingredients',
    title: 'Ingredient review',
    sourceLabel: 'manual ingredient check',
    status: response.status,
    matchedIngredients: response.matched_ingredients,
    explanation: response.explanation,
    ingredientText,
    unknownTerms: response.unknown_terms,
  };
}
