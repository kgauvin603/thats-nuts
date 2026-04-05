import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:thats_nuts_mobile/src/models/allergy_profile.dart';
import 'package:thats_nuts_mobile/src/screens/manual_ingredient_input_screen.dart';
import 'package:thats_nuts_mobile/src/services/ingredient_image_picker.dart';
import 'package:thats_nuts_mobile/src/services/thats_nuts_api_client.dart';

class FakeManualIngredientApiClient extends ThatsNutsApiClient {}

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
  testWidgets('renders capture options and text scan hint for iPhone users',
      (WidgetTester tester) async {
    await tester.pumpWidget(
      MaterialApp(
        home: ManualIngredientInputScreen(
          apiClient: FakeManualIngredientApiClient(),
          allergyProfile: const AllergyProfile(
            almond: true,
          ),
        ),
      ),
    );

    expect(find.text('Paste the ingredient list from a product label.'),
        findsOneWidget);
    expect(find.text('Profile: Almond'), findsOneWidget);
    expect(find.text('Capture Options'), findsOneWidget);
    expect(find.text('Take Photo'), findsOneWidget);
    expect(find.text('Choose Photo'), findsOneWidget);
    expect(
      find.text(
        'Tip: On iPhone, tap the text field and use text scan to capture ingredients from the label.',
      ),
      findsOneWidget,
    );
    expect(find.text('Check Ingredients'), findsOneWidget);
  });

  testWidgets('shows attached photo note after choosing a photo',
      (WidgetTester tester) async {
    await tester.pumpWidget(
      MaterialApp(
        home: ManualIngredientInputScreen(
          apiClient: FakeManualIngredientApiClient(),
          allergyProfile: const AllergyProfile(),
          imagePicker: FakeIngredientImagePicker(
            nextImage: const PickedIngredientImage(
              fileName: 'ingredients.jpg',
              path: '/tmp/ingredients.jpg',
              source: IngredientImageSource.library,
            ),
          ),
        ),
      ),
    );

    await tester.tap(find.text('Choose Photo'));
    await tester.pumpAndSettle();

    expect(find.text('ingredients.jpg'), findsOneWidget);
    expect(find.text('Library photo attached'), findsOneWidget);
    expect(find.text('Remove Photo'), findsOneWidget);
  });
}
