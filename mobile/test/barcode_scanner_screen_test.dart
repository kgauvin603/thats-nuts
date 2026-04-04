import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:thats_nuts_mobile/src/models/allergy_profile.dart';
import 'package:thats_nuts_mobile/src/screens/barcode_scanner_screen.dart';
import 'package:thats_nuts_mobile/src/services/thats_nuts_api_client.dart';

class FakeBarcodeScannerApiClient extends ThatsNutsApiClient {}

void main() {
  testWidgets('renders scanner guidance and fallback actions', (WidgetTester tester) async {
    await tester.pumpWidget(
      MaterialApp(
        home: BarcodeScannerScreen(
          apiClient: FakeBarcodeScannerApiClient(),
          allergyProfile: const AllergyProfile(
            almond: true,
          ),
          scannerPreview: const ColoredBox(
            color: Colors.black,
            child: SizedBox.expand(),
          ),
        ),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('Point the camera at a UPC or EAN barcode.'), findsOneWidget);
    expect(
      find.text(
        'After a successful scan, the app looks up the product and opens the result screen automatically.',
      ),
      findsOneWidget,
    );
    expect(find.text('Profile: Almond'), findsOneWidget);
    expect(find.text('Retry Scanner'), findsOneWidget);
    expect(find.text('Enter Barcode Manually'), findsAtLeastNWidgets(1));
    expect(find.text('Supported formats: UPC-A, UPC-E, EAN-8, EAN-13.'), findsOneWidget);
  });
}
