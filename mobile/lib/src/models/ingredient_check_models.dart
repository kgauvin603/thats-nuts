class IngredientCheckResult {
  const IngredientCheckResult({
    required this.status,
    required this.matchedIngredients,
    required this.explanation,
  });

  final String status;
  final List<MatchedIngredient> matchedIngredients;
  final String explanation;

  factory IngredientCheckResult.fromJson(Map<String, dynamic> json) {
    final items = json['matched_ingredients'] as List<dynamic>? ?? const [];
    return IngredientCheckResult(
      status: json['status'] as String? ?? 'cannot_verify',
      matchedIngredients: items
          .map((item) =>
              MatchedIngredient.fromJson(item as Map<String, dynamic>))
          .toList(),
      explanation: json['explanation'] as String? ?? 'No explanation returned.',
    );
  }
}

class MatchedIngredient {
  const MatchedIngredient({
    required this.originalText,
    required this.normalizedName,
    required this.nutSource,
    required this.confidence,
    required this.reason,
    this.displayName,
  });

  final String originalText;
  final String normalizedName;
  final String nutSource;
  final String confidence;
  final String reason;
  final String? displayName;

  factory MatchedIngredient.fromJson(Map<String, dynamic> json) {
    return MatchedIngredient(
      originalText: json['original_text'] as String? ?? '',
      normalizedName: json['normalized_name'] as String? ?? '',
      nutSource: json['nut_source'] as String? ?? '',
      confidence: json['confidence'] as String? ?? '',
      reason: json['reason'] as String? ?? '',
      displayName: json['display_name'] as String?,
    );
  }
}
