import 'package:flutter_test/flutter_test.dart';
import 'package:thats_nuts_mobile/src/models/scan_history_models.dart';

void main() {
  test('parses scan history response payload', () {
    final response = ScanHistoryResponse.fromJson({
      'items': [
        {
          'scan_type': 'barcode_lookup',
          'barcode': '012345678905',
          'product_name': 'Sample Lotion',
          'brand_name': 'Test Brand',
          'submitted_ingredient_text': 'Water, sweet almond oil, glycerin',
          'assessment_status': 'contains_nut_ingredient',
          'explanation': 'Matched sweet almond oil.',
          'matched_ingredient_summary': 'sweet almond oil',
          'created_at': '2026-04-03T12:30:00Z',
        },
      ],
    });

    expect(response.items, hasLength(1));
    expect(response.items.first.productName, 'Sample Lotion');
    expect(response.items.first.submittedIngredientText,
        'Water, sweet almond oil, glycerin');
    expect(response.items.first.assessmentStatus, 'contains_nut_ingredient');
    expect(response.items.first.createdAt.toUtc().year, 2026);
  });
}
