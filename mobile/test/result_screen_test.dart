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
      explanation:
          'Detected an almond-linked ingredient in this product: sweet almond oil.',
      matchedIngredients: [
        MatchedIngredient(
          originalText: 'sweet almond oil) (almond)',
          normalizedName: 'almond oil',
          nutSource: 'almond',
          confidence: 'high',
          displayName: 'sweet almond oil',
          reason:
              'Matched to known almond-linked ingredient terms: almond oil.',
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
    expect(find.text('Nut ingredients detected'), findsNWidgets(2));
    expect(find.text('1 flagged ingredient'), findsNWidgets(2));
    expect(find.text('Quick Summary'), findsOneWidget);
    expect(find.text('What to do next'), findsOneWidget);
    expect(find.text('Next step'), findsOneWidget);
    await tester.scrollUntilVisible(
      find.text('Product'),
      200,
      scrollable: find.byType(Scrollable),
    );
    await tester.pumpAndSettle();
    expect(find.text('Product'), findsOneWidget);
    expect(find.text('Product name'), findsOneWidget);
    expect(find.text('Sample Lotion'), findsOneWidget);
    expect(find.text('Test Brand'), findsOneWidget);
    expect(find.byKey(const Key('result-product-photo-card')), findsOneWidget);
    expect(find.text('No product photo available.'), findsOneWidget);
    expect(find.text('012345678905'), findsOneWidget);
    expect(find.text('Partial ingredient coverage'), findsOneWidget);
    expect(find.text('Ingredient coverage'), findsOneWidget);
    await tester.scrollUntilVisible(
      find.text('Flagged Ingredients'),
      250,
      scrollable: find.byType(Scrollable),
    );
    await tester.pumpAndSettle();
    expect(find.text('Flagged Ingredients'), findsOneWidget);
    expect(find.text('sweet almond oil'), findsOneWidget);
    expect(find.text('sweet almond oil) (almond)'), findsNothing);
    expect(find.text('Normalized as almond oil'), findsOneWidget);
    expect(find.text('Almond'), findsOneWidget);
    expect(find.text('High confidence'), findsOneWidget);

    await tester.drag(find.byType(ListView), const Offset(0, -500));
    await tester.pumpAndSettle();

    expect(find.byKey(const Key('result-primary-action')), findsOneWidget);
    expect(find.text('Scan Again'), findsOneWidget);
    expect(find.text('Back'), findsOneWidget);
  });

  testWidgets('renders product photo image when image URL is present',
      (WidgetTester tester) async {
    const imageUrl =
        'https://images.openfoodfacts.org/images/products/301/762/042/2003/front_en.820.400.jpg';
    const result = ProductLookupResult(
      found: true,
      product: LookupProduct(
        barcode: '3017620422003',
        brandName: 'Nutella',
        productName: 'Nutella',
        imageUrl: imageUrl,
        ingredientCoverageStatus: 'complete',
        source: 'open_food_facts',
      ),
      ingredientText: 'Sucre, huile de palme, NOISETTES 13%',
      assessmentResult: 'contains_nut_ingredient',
      explanation: 'Detected hazelnut.',
      matchedIngredients: [],
    );

    await tester.pumpWidget(
      MaterialApp(
        home: ResultScreen.forProductLookup(
          barcode: '3017620422003',
          result: result,
        ),
      ),
    );

    await tester.scrollUntilVisible(
      find.byKey(const Key('result-product-photo-card')),
      250,
      scrollable: find.byType(Scrollable),
    );

    expect(find.byKey(const Key('result-product-photo-card')), findsOneWidget);
    final image = tester.widget<Image>(
      find.byKey(const Key('result-product-photo-image')),
    );
    expect(image.image, isA<NetworkImage>());
    expect((image.image as NetworkImage).url, imageUrl);
    expect(find.text('No product photo available.'), findsNothing);
  });

  testWidgets('renders product photo placeholder when image URL is missing',
      (WidgetTester tester) async {
    const result = ProductLookupResult(
      found: true,
      product: LookupProduct(
        barcode: '3017620422003',
        brandName: 'Nutella',
        productName: 'Nutella',
        imageUrl: '',
        ingredientCoverageStatus: 'complete',
        source: 'open_food_facts',
      ),
      ingredientText: 'Sucre, huile de palme',
      assessmentResult: 'no_nut_ingredient_found',
      explanation:
          'No nut-linked ingredients were identified in the ingredient list provided.',
      matchedIngredients: [],
    );

    await tester.pumpWidget(
      MaterialApp(
        home: ResultScreen.forProductLookup(
          barcode: '3017620422003',
          result: result,
        ),
      ),
    );

    await tester.scrollUntilVisible(
      find.byKey(const Key('result-product-photo-card')),
      250,
      scrollable: find.byType(Scrollable),
    );

    expect(find.byKey(const Key('result-product-photo-card')), findsOneWidget);
    expect(find.text('No product photo available.'), findsOneWidget);
    expect(find.byKey(const Key('result-product-photo-image')), findsNothing);
  });

  testWidgets('renders cannot verify state with no matches clearly',
      (WidgetTester tester) async {
    const result = IngredientCheckResult(
      status: 'cannot_verify',
      explanation:
          'A full, usable ingredient list is required to verify this product safely.',
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
    expect(find.text('REVIEW FIRST'), findsOneWidget);
    expect(find.text('Cannot verify'), findsAtLeastNWidgets(2));
    expect(find.text('What to do next'), findsOneWidget);
    expect(
      find.text(
        'A full, usable ingredient list is required to verify this product safely.',
      ),
      findsOneWidget,
    );
    await tester.scrollUntilVisible(
      find.text('No matched ingredients returned.'),
      250,
      scrollable: find.byType(Scrollable),
    );
    await tester.pumpAndSettle();
    expect(find.text('No matched ingredients returned.'), findsOneWidget);
    await tester.drag(find.byType(ListView), const Offset(0, -400));
    await tester.pumpAndSettle();

    expect(find.text('Check Another Ingredient List'), findsOneWidget);
    expect(find.text('Back'), findsOneWidget);
  });

  testWidgets('shows barcode enrichment fallback action when provided',
      (WidgetTester tester) async {
    var tapped = false;
    const result = ProductLookupResult(
      found: false,
      product: null,
      ingredientText: null,
      assessmentResult: null,
      matchedIngredients: [],
      explanation:
          'No product record with a usable ingredient list was found for this barcode.',
    );

    await tester.pumpWidget(
      MaterialApp(
        home: ResultScreen.forProductLookup(
          barcode: '9999999999999',
          result: result,
          fallbackActionLabel: 'Add Ingredients for This Barcode',
          onFallbackAction: (context) async {
            tapped = true;
          },
        ),
      ),
    );

    await tester.scrollUntilVisible(
      find.byKey(const Key('result-fallback-action')),
      250,
      scrollable: find.byType(Scrollable),
    );
    await tester.pumpAndSettle();
    expect(find.byKey(const Key('result-fallback-action')), findsOneWidget);
    expect(find.text('Add Ingredients for This Barcode'), findsOneWidget);

    await tester.tap(find.byKey(const Key('result-fallback-action')));
    await tester.pump();

    expect(tapped, isTrue);
  });

  testWidgets(
      'shows barcode enrichment fallback action for cannot verify lookup',
      (WidgetTester tester) async {
    var tapped = false;
    const result = ProductLookupResult(
      found: true,
      product: LookupProduct(
        barcode: '0016000507661',
        brandName: 'Test Brand',
        productName: 'Example Product',
        imageUrl: null,
        ingredientCoverageStatus: 'missing',
        source: 'open_food_facts',
      ),
      ingredientText: null,
      assessmentResult: 'cannot_verify',
      matchedIngredients: [],
      explanation:
          'Product data was returned by the configured open_food_facts provider. This record did not include a full, usable ingredient list. A full, usable ingredient list is required to verify this product safely.',
    );

    await tester.pumpWidget(
      MaterialApp(
        home: ResultScreen.forProductLookup(
          barcode: '0016000507661',
          result: result,
          fallbackActionLabel: 'Add Ingredients for This Barcode',
          onFallbackAction: (context) async {
            tapped = true;
          },
        ),
      ),
    );

    await tester.scrollUntilVisible(
      find.byKey(const Key('result-fallback-action')),
      250,
      scrollable: find.byType(Scrollable),
    );
    await tester.pumpAndSettle();
    expect(find.byKey(const Key('result-fallback-action')), findsOneWidget);

    await tester.tap(find.byKey(const Key('result-fallback-action')));
    await tester.pump();

    expect(tapped, isTrue);
  });

  testWidgets('shows manual enrichment label for enriched barcode results',
      (WidgetTester tester) async {
    const result = ProductLookupResult(
      found: true,
      product: LookupProduct(
        barcode: '012345678905',
        brandName: 'Test Brand',
        productName: 'Sample Lotion',
        imageUrl: null,
        ingredientCoverageStatus: 'complete',
        source: 'manual_entry',
      ),
      ingredientText: 'water, sweet almond oil, glycerin',
      assessmentResult: 'contains_nut_ingredient',
      explanation:
          'Detected an almond-linked ingredient in this product: sweet almond oil.',
      matchedIngredients: [],
    );

    await tester.pumpWidget(
      MaterialApp(
        home: ResultScreen.forProductLookup(
          barcode: '012345678905',
          result: result,
        ),
      ),
    );

    expect(find.text('Manual Enrichment'), findsAtLeastNWidgets(1));
    expect(
      find.text(
        'This barcode was previously completed using manually entered ingredients.',
      ),
      findsOneWidget,
    );
  });
}
