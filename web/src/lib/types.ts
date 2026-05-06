export type IngredientCheckStatus =
  | 'contains_nut_ingredient'
  | 'possible_nut_derived_ingredient'
  | 'no_nut_ingredient_found'
  | 'cannot_verify';

export interface MatchedIngredient {
  original_text: string;
  normalized_name: string;
  nut_source: string;
  confidence: string;
  reason: string;
  display_name?: string | null;
  detection_basis?: string | null;
  match_strength?: string | null;
  review_recommended?: boolean | null;
}

export interface LookupProduct {
  barcode: string;
  brand_name?: string | null;
  product_name?: string | null;
  image_url?: string | null;
  ingredient_text?: string | null;
  ingredient_coverage_status?: string | null;
  source: string;
}

export interface ProductLookupResponse {
  found: boolean;
  source: string;
  lookup_path: string[];
  product?: LookupProduct | null;
  ingredient_text?: string | null;
  assessment_result?: IngredientCheckStatus | null;
  matched_ingredients: MatchedIngredient[];
  explanation: string;
  ruleset_version?: string | null;
  unknown_terms: string[];
}

export interface IngredientCheckResponse {
  status: IngredientCheckStatus;
  matched_ingredients: MatchedIngredient[];
  explanation: string;
  ruleset_version?: string | null;
  unknown_terms: string[];
}

export interface UnifiedResult {
  mode: 'barcode' | 'ingredients';
  title: string;
  sourceLabel: string;
  barcode?: string;
  product?: LookupProduct | null;
  status: IngredientCheckStatus;
  matchedIngredients: MatchedIngredient[];
  explanation: string;
  ingredientText?: string | null;
  unknownTerms: string[];
  lookupPath?: string[];
}
