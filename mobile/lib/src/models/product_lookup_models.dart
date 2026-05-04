import 'ingredient_check_models.dart';

class ProductLookupResult {
  const ProductLookupResult({
    required this.found,
    required this.product,
    required this.ingredientText,
    required this.assessmentResult,
    required this.matchedIngredients,
    required this.explanation,
  });

  final bool found;
  final LookupProduct? product;
  final String? ingredientText;
  final String? assessmentResult;
  final List<MatchedIngredient> matchedIngredients;
  final String explanation;

  bool get canAddIngredientsFallback {
    final hasUsableIngredientText =
        ingredientText != null && ingredientText!.trim().isNotEmpty;
    if (!found) {
      return true;
    }
    if (assessmentResult == 'cannot_verify') {
      return true;
    }
    return !hasUsableIngredientText &&
        (product?.ingredientCoverageStatus == 'missing' ||
            product?.ingredientCoverageStatus == 'unknown');
  }

  factory ProductLookupResult.fromJson(Map<String, dynamic> json) {
    final items = json['matched_ingredients'] as List<dynamic>? ?? const [];
    final productJson = json['product'] as Map<String, dynamic>?;

    return ProductLookupResult(
      found: json['found'] as bool? ?? false,
      product: productJson == null ? null : LookupProduct.fromJson(productJson),
      ingredientText: json['ingredient_text'] as String?,
      assessmentResult: json['assessment_result'] as String?,
      matchedIngredients: items
          .map((item) =>
              MatchedIngredient.fromJson(item as Map<String, dynamic>))
          .toList(),
      explanation: json['explanation'] as String? ?? 'No explanation returned.',
    );
  }
}

class LookupProduct {
  const LookupProduct({
    required this.barcode,
    required this.brandName,
    required this.productName,
    required this.imageUrl,
    required this.ingredientCoverageStatus,
    required this.source,
  });

  final String barcode;
  final String? brandName;
  final String? productName;
  final String? imageUrl;
  final String? ingredientCoverageStatus;
  final String source;

  factory LookupProduct.fromJson(Map<String, dynamic> json) {
    return LookupProduct(
      barcode: json['barcode'] as String? ?? '',
      brandName: json['brand_name'] as String?,
      productName: json['product_name'] as String?,
      imageUrl: json['image_url'] as String?,
      ingredientCoverageStatus: json['ingredient_coverage_status'] as String?,
      source: json['source'] as String? ?? 'unknown',
    );
  }
}
