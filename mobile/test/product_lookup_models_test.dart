import 'package:flutter_test/flutter_test.dart';
import 'package:thats_nuts_mobile/src/models/product_lookup_models.dart';

void main() {
  test('canAddIngredientsFallback is true when lookup misses entirely', () {
    const result = ProductLookupResult(
      found: false,
      product: null,
      ingredientText: null,
      assessmentResult: null,
      matchedIngredients: [],
      explanation: 'Not found.',
    );

    expect(result.canAddIngredientsFallback, isTrue);
  });

  test('canAddIngredientsFallback is true for cannot verify provider results',
      () {
    const result = ProductLookupResult(
      found: true,
      product: LookupProduct(
        barcode: '0016000507661',
        brandName: 'Example Brand',
        productName: 'Example Product',
        imageUrl: null,
        ingredientCoverageStatus: 'missing',
        source: 'open_food_facts',
      ),
      ingredientText: null,
      assessmentResult: 'cannot_verify',
      matchedIngredients: [],
      explanation: 'Need a full ingredient list.',
    );

    expect(result.canAddIngredientsFallback, isTrue);
  });

  test('canAddIngredientsFallback stays false for successful assessed lookups',
      () {
    const result = ProductLookupResult(
      found: true,
      product: LookupProduct(
        barcode: '1234500000000',
        brandName: 'Example Brand',
        productName: 'Plain Snack',
        imageUrl: null,
        ingredientCoverageStatus: 'complete',
        source: 'open_food_facts',
      ),
      ingredientText: 'Corn, Sunflower Oil, Salt',
      assessmentResult: 'no_nut_ingredient_found',
      matchedIngredients: [],
      explanation: 'No nut-linked ingredients were identified.',
    );

    expect(result.canAddIngredientsFallback, isFalse);
  });
}
