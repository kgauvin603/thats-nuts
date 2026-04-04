import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:thats_nuts_mobile/src/models/ingredient_check_models.dart';
import 'package:thats_nuts_mobile/src/models/product_lookup_models.dart';
import 'package:thats_nuts_mobile/src/screens/result_screen.dart';

void main() {
  testWidgets(
      'renders product lookup result with product details and matched ingredients',
      (
    WidgetTester tester,
  ) async {
    const result = ProductLookupResult(
      found: true,
      product: LookupProduct(
        barcode: '012345678905',
        brandName: 'Test Brand',
        productName: 'Sample Lotion',
        imageUrl: null,
        ingredientCoverageStatus: 'partial',
        source: 'stub',
      ),
      ingredientText: 'water, sweet almond oil, glycerin',
      assessmentResult: 'contains_nut_ingredient',
      explanation: 'Matched sweet almond oil.',
      matchedIngredients: [
        MatchedIngredient(
          originalText: 'sweet almond oil',
          normalizedName: 'almond oil',
          nutSource: 'almond',
          confidence: 'high',
          reason: 'Direct almond-derived ingredient match.',
        ),
      ],
    );

    await tester.pumpWidget(
      MaterialApp(
        home: ResultScreen.forProductLookup(
          barcode: '012345678905',
          result: result,
        ),
      ),
    );

    expect(find.byKey(const Key('result-status-banner')), findsOneWidget);
    expect(find.text('AVOID'), findsOneWidget);
    expect(find.text('Contains nut ingredient'), findsOneWidget);
    expect(find.text('1 flagged ingredient'), findsOneWidget);
    expect(find.text('Product'), findsOneWidget);
    expect(find.text('Sample Lotion'), findsOneWidget);
    expect(find.text('Test Brand'), findsOneWidget);
    expect(find.text('012345678905'), findsOneWidget);
    expect(find.text('Partial ingredient coverage'), findsNWidgets(2));

    expect(find.text('Explanation'), findsOneWidget);
    await tester.scrollUntilVisible(
      find.text('Flagged Ingredients'),
      250,
      scrollable: find.byType(Scrollable),
    );
    await tester.pumpAndSettle();
    expect(find.text('Flagged Ingredients'), findsOneWidget);
    expect(find.text('sweet almond oil'), findsOneWidget);
    expect(find.text('Normalized as almond oil'), findsOneWidget);
    expect(find.text('almond'), findsOneWidget);
    expect(find.text('high'), findsOneWidget);

    await tester.drag(find.byType(ListView), const Offset(0, -500));
    await tester.pumpAndSettle();

    expect(find.byKey(const Key('result-primary-action')), findsOneWidget);
    expect(find.text('Scan Again'), findsOneWidget);
    expect(find.text('Back'), findsOneWidget);
  });

  testWidgets('renders cannot verify state with no matches clearly',
      (WidgetTester tester) async {
    const result = IngredientCheckResult(
      status: 'cannot_verify',
      explanation: 'No ingredient list was available.',
      matchedIngredients: [],
    );

    await tester.pumpWidget(
      MaterialApp(
        home: ResultScreen.forIngredientCheck(
          ingredientText: '',
          result: result,
        ),
      ),
    );

    expect(find.byKey(const Key('result-status-banner')), findsOneWidget);
    expect(find.text('CANNOT CONFIRM'), findsOneWidget);
    expect(find.text('Cannot verify'), findsOneWidget);
    expect(
      find.text(
        'The ingredient data was missing, incomplete, or too vague to assess confidently.',
      ),
      findsOneWidget,
    );
    expect(find.text('No matched ingredients returned.'), findsOneWidget);
    await tester.drag(find.byType(ListView), const Offset(0, -400));
    await tester.pumpAndSettle();

    expect(find.text('Check Another Ingredient List'), findsOneWidget);
    expect(find.text('Back'), findsOneWidget);
  });
}
