import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:thats_nuts_mobile/src/models/scan_history_models.dart';
import 'package:thats_nuts_mobile/src/screens/history_screen.dart';
import 'package:thats_nuts_mobile/src/services/scan_history_refresh_controller.dart';
import 'package:thats_nuts_mobile/src/services/thats_nuts_api_client.dart';

class FakeHistoryApiClient extends ThatsNutsApiClient {
  FakeHistoryApiClient({
    required this.response,
    this.throwError = false,
    this.throwParsingError = false,
  });

  ScanHistoryResponse response;
  final bool throwError;
  final bool throwParsingError;
  int requestCount = 0;

  @override
  Future<ScanHistoryResponse> fetchScanHistory({int limit = 20}) async {
    requestCount += 1;
    if (throwError) {
      throw const ThatsNutsApiException('Backend unavailable.');
    }
    if (throwParsingError) {
      throw const FormatException('Invalid response payload.');
    }
    return response;
  }
}

void main() {
  testWidgets('renders recent scan history entries',
      (WidgetTester tester) async {
    final refreshController = ScanHistoryRefreshController();
    final apiClient = FakeHistoryApiClient(
      response: ScanHistoryResponse(
        items: [
          ScanHistoryItem(
            scanType: 'barcode_enrichment',
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
          historyRefreshController: refreshController,
        ),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('Recent History'), findsOneWidget);
    expect(find.text('Sample Lotion'), findsOneWidget);
    expect(find.text('Barcode: 012345678905'), findsOneWidget);
    expect(find.text('Barcode enrichment'), findsOneWidget);
    expect(find.text('Nut ingredients detected'), findsAtLeastNWidgets(1));
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
    expect(find.text('Barcode lookup'), findsOneWidget);
    expect(find.text('Barcode: 9999999999999'), findsOneWidget);
  });

  testWidgets('renders empty state when there is no scan history',
      (WidgetTester tester) async {
    final refreshController = ScanHistoryRefreshController();
    final apiClient = FakeHistoryApiClient(
      response: const ScanHistoryResponse(items: []),
    );

    await tester.pumpWidget(
      MaterialApp(
        home: HistoryScreen(
          apiClient: apiClient,
          historyRefreshController: refreshController,
        ),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.textContaining('No checks yet.'), findsOneWidget);
    expect(find.text('Could not load history'), findsNothing);
  });

  testWidgets('renders error state when the history request fails',
      (WidgetTester tester) async {
    final refreshController = ScanHistoryRefreshController();
    final apiClient = FakeHistoryApiClient(
      response: const ScanHistoryResponse(items: []),
      throwError: true,
    );

    await tester.pumpWidget(
      MaterialApp(
        home: HistoryScreen(
          apiClient: apiClient,
          historyRefreshController: refreshController,
        ),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('Could not load history'), findsOneWidget);
    expect(find.text('Backend unavailable.'), findsOneWidget);
    expect(find.textContaining('No scans yet.'), findsNothing);
  });

  testWidgets('renders error state when the history payload cannot be parsed',
      (WidgetTester tester) async {
    final refreshController = ScanHistoryRefreshController();
    final apiClient = FakeHistoryApiClient(
      response: const ScanHistoryResponse(items: []),
      throwParsingError: true,
    );

    await tester.pumpWidget(
      MaterialApp(
        home: HistoryScreen(
          apiClient: apiClient,
          historyRefreshController: refreshController,
        ),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('Could not load history'), findsOneWidget);
    expect(
      find.text('Something went wrong while loading scan history.'),
      findsOneWidget,
    );
    expect(find.textContaining('No scans yet.'), findsNothing);
  });

  testWidgets('reloads when history refresh is signaled',
      (WidgetTester tester) async {
    final refreshController = ScanHistoryRefreshController();
    final apiClient = FakeHistoryApiClient(
      response: ScanHistoryResponse(
        items: [
          ScanHistoryItem(
            scanType: 'manual_ingredient_check',
            barcode: null,
            productName: null,
            brandName: null,
            productSource: null,
            submittedIngredientText: 'Water',
            assessmentStatus: 'no_nut_ingredient_found',
            explanation: 'No nut-linked ingredients were flagged.',
            matchedIngredientSummary: null,
            createdAt: DateTime.parse('2026-04-03T12:20:00Z'),
          ),
        ],
      ),
    );

    await tester.pumpWidget(
      MaterialApp(
        home: HistoryScreen(
          apiClient: apiClient,
          historyRefreshController: refreshController,
        ),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('Water'), findsOneWidget);
    expect(apiClient.requestCount, 1);

    apiClient.response = ScanHistoryResponse(
      items: [
        ScanHistoryItem(
          scanType: 'barcode_lookup',
          barcode: '0001234567890',
          productName: 'Updated Item',
          brandName: null,
          productSource: null,
          submittedIngredientText: null,
          assessmentStatus: 'cannot_verify',
          explanation: 'No product record was found.',
          matchedIngredientSummary: null,
          createdAt: DateTime.parse('2026-04-03T12:30:00Z'),
        ),
      ],
    );

    refreshController.markChanged();
    await tester.pump();
    await tester.pumpAndSettle();

    expect(apiClient.requestCount, 2);
    expect(find.text('Updated Item'), findsOneWidget);
    expect(find.text('Water'), findsNothing);
  });
}
