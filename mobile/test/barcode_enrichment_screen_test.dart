import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:thats_nuts_mobile/src/models/allergy_profile.dart';
import 'package:thats_nuts_mobile/src/models/ingredient_check_models.dart';
import 'package:thats_nuts_mobile/src/models/product_lookup_models.dart';
import 'package:thats_nuts_mobile/src/screens/barcode_enrichment_screen.dart';
import 'package:thats_nuts_mobile/src/services/ingredient_image_picker.dart';
import 'package:thats_nuts_mobile/src/services/thats_nuts_api_client.dart';

class FakeBarcodeEnrichmentApiClient extends ThatsNutsApiClient {
  FakeBarcodeEnrichmentApiClient({
    required this.response,
  });

  final ProductLookupResult response;
  String? capturedBarcode;
  String? capturedIngredientText;
  String? capturedProductName;
  String? capturedBrandName;
  AllergyProfile? capturedProfile;

  @override
  Future<ProductLookupResult> enrichProduct(
    String barcode, {
    required String ingredientText,
    String? productName,
    String? brandName,
    String? source,
    AllergyProfile? allergyProfile,
  }) async {
    capturedBarcode = barcode;
    capturedIngredientText = ingredientText;
    capturedProductName = productName;
    capturedBrandName = brandName;
    capturedProfile = allergyProfile;
    return response;
  }
}

class FakeIngredientImagePicker implements IngredientImagePicker {
  FakeIngredientImagePicker({
    this.nextImage,
  });

  final PickedIngredientImage? nextImage;

  @override
  Future<PickedIngredientImage?> pickImage(IngredientImageSource source) async {
    return nextImage == null
        ? null
        : PickedIngredientImage(
            fileName: nextImage!.fileName,
            path: nextImage!.path,
            source: source,
          );
  }
}

void main() {
  testWidgets('renders enrichment form and submits to backend',
      (WidgetTester tester) async {
    final apiClient = FakeBarcodeEnrichmentApiClient(
      response: const ProductLookupResult(
        found: true,
        product: LookupProduct(
          barcode: '9999999999999',
          brandName: 'Saved Brand',
          productName: 'Saved Product',
          imageUrl: null,
          ingredientCoverageStatus: 'complete',
          source: 'manual_entry',
        ),
        ingredientText: 'Water, Glycerin, Prunus Amygdalus Dulcis Oil',
        assessmentResult: 'contains_nut_ingredient',
        matchedIngredients: [
          MatchedIngredient(
            originalText: 'Prunus Amygdalus Dulcis Oil',
            normalizedName: 'almond oil',
            nutSource: 'almond',
            confidence: 'high',
            reason: 'Direct almond-derived ingredient match.',
          ),
        ],
        explanation: 'Matched 1 ingredient linked to nut allergy risk.',
      ),
    );

    await tester.pumpWidget(
      MaterialApp(
        home: BarcodeEnrichmentScreen(
          apiClient: apiClient,
          allergyProfile: const AllergyProfile(almond: true),
          barcode: '9999999999999',
          initialProductName: 'Saved Product',
          initialBrandName: 'Saved Brand',
          imagePicker: FakeIngredientImagePicker(
            nextImage: const PickedIngredientImage(
              fileName: 'label.png',
              path: '/tmp/label.png',
              source: IngredientImageSource.camera,
            ),
          ),
        ),
      ),
    );

    expect(find.text('Add Ingredients for Barcode'), findsOneWidget);
    expect(find.text('9999999999999'), findsOneWidget);
    expect(find.text('Capture Options'), findsOneWidget);
    expect(find.text('Take Photo'), findsOneWidget);
    expect(find.text('Choose Photo'), findsOneWidget);
    expect(
      find.text(
        'Tip: On iPhone, tap the text field and use text scan to capture ingredients from the label.',
      ),
      findsOneWidget,
    );
    await tester.tap(find.text('Take Photo'));
    await tester.pumpAndSettle();
    expect(find.text('label.png'), findsOneWidget);
    expect(find.text('Camera photo attached'), findsOneWidget);

    await tester.enterText(
      find.widgetWithText(TextField, 'Ingredient Text'),
      'Water, Glycerin, Prunus Amygdalus Dulcis Oil',
    );
    final saveButton =
        find.widgetWithText(FilledButton, 'Save Ingredients for This Barcode');
    await tester.scrollUntilVisible(
      saveButton,
      250,
      scrollable: find.byType(Scrollable).first,
    );
    await tester.pumpAndSettle();
    await tester.tap(saveButton);
    await tester.pumpAndSettle();

    expect(apiClient.capturedBarcode, '9999999999999');
    expect(
      apiClient.capturedIngredientText,
      'Water, Glycerin, Prunus Amygdalus Dulcis Oil',
    );
    expect(apiClient.capturedProductName, 'Saved Product');
    expect(apiClient.capturedBrandName, 'Saved Brand');
    expect(apiClient.capturedProfile?.almond, isTrue);
    expect(find.text('Contains nut ingredient'), findsOneWidget);
    expect(find.text('Scan Again'), findsOneWidget);
  });
}
