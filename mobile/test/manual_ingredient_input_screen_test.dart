import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:thats_nuts_mobile/src/models/allergy_profile.dart';
import 'package:thats_nuts_mobile/src/screens/manual_ingredient_input_screen.dart';
import 'package:thats_nuts_mobile/src/services/thats_nuts_api_client.dart';

class FakeManualIngredientApiClient extends ThatsNutsApiClient {}

void main() {
  testWidgets(
      'renders a standard editable text field and iPhone text scan hint',
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
    expect(
      find.text(
        'Tip: On iPhone, tap the text field and use text scan to capture ingredients from the label.',
      ),
      findsOneWidget,
    );
    final textField =
        tester.widget<TextField>(find.widgetWithText(TextField, 'Ingredients'));
    expect(textField.readOnly, isFalse);
    expect(textField.enabled, isNot(false));
    expect(textField.expands, isTrue);
    expect(find.text('Check Ingredients'), findsOneWidget);
  });

  testWidgets('ingredient field receives focus and starts text input on tap',
      (WidgetTester tester) async {
    await tester.pumpWidget(
      MaterialApp(
        home: ManualIngredientInputScreen(
          apiClient: FakeManualIngredientApiClient(),
          allergyProfile: const AllergyProfile(),
        ),
      ),
    );

    await tester.tap(find.byType(TextField));
    await tester.pump();

    final editableText = tester.widget<EditableText>(find.byType(EditableText));
    expect(editableText.focusNode.hasFocus, isTrue);
    expect(tester.testTextInput.hasAnyClients, isTrue);
  });
}
