class ScanHistoryResponse {
  const ScanHistoryResponse({
    required this.items,
  });

  final List<ScanHistoryItem> items;

  factory ScanHistoryResponse.fromJson(Map<String, dynamic> json) {
    final items = json['items'] as List<dynamic>? ?? const [];
    return ScanHistoryResponse(
      items: items
          .map((item) => ScanHistoryItem.fromJson(item as Map<String, dynamic>))
          .toList(),
    );
  }
}

class ScanHistoryItem {
  const ScanHistoryItem({
    required this.scanType,
    required this.barcode,
    required this.productName,
    required this.brandName,
    required this.assessmentStatus,
    required this.explanation,
    required this.matchedIngredientSummary,
    required this.createdAt,
  });

  final String scanType;
  final String? barcode;
  final String? productName;
  final String? brandName;
  final String assessmentStatus;
  final String? explanation;
  final String? matchedIngredientSummary;
  final DateTime createdAt;

  factory ScanHistoryItem.fromJson(Map<String, dynamic> json) {
    return ScanHistoryItem(
      scanType: json['scan_type'] as String? ?? 'manual_ingredient_check',
      barcode: json['barcode'] as String?,
      productName: json['product_name'] as String?,
      brandName: json['brand_name'] as String?,
      assessmentStatus: json['assessment_status'] as String? ?? 'cannot_verify',
      explanation: json['explanation'] as String?,
      matchedIngredientSummary: json['matched_ingredient_summary'] as String?,
      createdAt: DateTime.tryParse(json['created_at'] as String? ?? '') ?? DateTime.fromMillisecondsSinceEpoch(0),
    );
  }
}
