import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:thats_nuts_mobile/src/models/scan_history_models.dart';
import 'package:thats_nuts_mobile/src/screens/history_screen.dart';
import 'package:thats_nuts_mobile/src/services/thats_nuts_api_client.dart';

class FakeHistoryApiClient extends ThatsNutsApiClient {
  FakeHistoryApiClient({
    required this.response,
    this.throwError = false,
  });

  final ScanHistoryResponse response;
  final bool throwError;

  @override
  Future<ScanHistoryResponse> fetchScanHistory({int limit = 20}) async {
    if (throwError) {
      throw const ThatsNutsApiException('Backend unavailable.');
    }
    return response;
  }
}

void main() {
  testWidgets('renders recent scan history entries',
      (WidgetTester tester) async {
    final apiClient = FakeHistoryApiClient(
      response: ScanHistoryResponse(
        items: [
          ScanHistoryItem(
            scanType: 'barcode_lookup',
            barcode: '012345678905',
            productName: 'Sample Lotion',
            brandName: 'Test Brand',
            productSource: 'text_scan',
            submittedIngredientText: 'Water, sweet almond oil, glycerin',
            assessmentStatus: 'contains_nut_ingredient',
            explanation: 'Matched sweet almond oil.',
            matchedIngredientSummary: 'sweet almond oil',
            createdAt: DateTime.parse('2026-04-03T12:30:00Z'),
          ),
          ScanHistoryItem(
            scanType: 'manual_ingredient_check',
            barcode: null,
            productName: null,
            brandName: null,
            productSource: null,
            submittedIngredientText:
                'Water, Glycerin, Prunus Amygdalus Dulcis Oil',
            assessmentStatus: 'contains_nut_ingredient',
            explanation: 'Matched almond oil.',
            matchedIngredientSummary: 'Prunus Amygdalus Dulcis Oil',
            createdAt: DateTime.parse('2026-04-03T12:20:00Z'),
          ),
          ScanHistoryItem(
            scanType: 'barcode_lookup',
            barcode: '9999999999999',
            productName: null,
            brandName: null,
            productSource: null,
            submittedIngredientText: null,
            assessmentStatus: 'cannot_verify',
            explanation: 'No product record was found.',
            matchedIngredientSummary: null,
            createdAt: DateTime.parse('2026-04-03T12:10:00Z'),
          ),
        ],
      ),
    );

    await tester.pumpWidget(
      MaterialApp(
        home: HistoryScreen(
          apiClient: apiClient,
        ),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('Recent History'), findsOneWidget);
    expect(find.text('Sample Lotion'), findsOneWidget);
    expect(find.text('Barcode: 012345678905'), findsOneWidget);
    expect(find.text('Manual enrichment'), findsOneWidget);
    expect(
      find.text('Saved from manually captured ingredients for this barcode.'),
      findsOneWidget,
    );
    expect(find.text('Nut ingredient found'), findsNWidgets(2));
    expect(find.text('Matched sweet almond oil.'), findsOneWidget);
    expect(find.text('Matched: sweet almond oil'), findsOneWidget);
    expect(find.text('Manual ingredient check'), findsOneWidget);
    expect(find.text('Water, Glycerin, Prunus Amygdalus Dulcis Oil'),
        findsOneWidget);
    await tester.scrollUntilVisible(
      find.text('Barcode: 9999999999999'),
      250,
      scrollable: find.byType(Scrollable),
    );
    await tester.pumpAndSettle();
    expect(find.text('Barcode lookup'), findsNWidgets(2));
    expect(find.text('Barcode: 9999999999999'), findsOneWidget);
  });

  testWidgets('renders empty state when there is no scan history',
      (WidgetTester tester) async {
    final apiClient = FakeHistoryApiClient(
      response: const ScanHistoryResponse(items: []),
    );

    await tester.pumpWidget(
      MaterialApp(
        home: HistoryScreen(
          apiClient: apiClient,
        ),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.textContaining('No scan history yet.'), findsOneWidget);
  });
}
