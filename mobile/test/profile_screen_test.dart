import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:thats_nuts_mobile/src/models/allergy_profile.dart';
import 'package:thats_nuts_mobile/src/screens/profile_screen.dart';

void main() {
  testWidgets('applies selected allergy profile', (WidgetTester tester) async {
    AllergyProfile? savedProfile;

    await tester.pumpWidget(
      MaterialApp(
        home: ProfileScreen(
          initialProfile: const AllergyProfile(),
          onProfileSaved: (profile) {
            savedProfile = profile;
          },
        ),
      ),
    );

    await tester.tap(find.text('Almond'));
    await tester.pumpAndSettle();
    await tester.scrollUntilVisible(
      find.text('Argan'),
      250,
      scrollable: find.byType(Scrollable),
    );
    await tester.pumpAndSettle();
    await tester.tap(find.text('Argan'));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Apply Profile'));
    await tester.pumpAndSettle();

    expect(savedProfile, isNotNull);
    expect(savedProfile!.almond, isTrue);
    expect(savedProfile!.argan, isTrue);
    expect(savedProfile!.peanut, isFalse);
  });

  testWidgets('clear resets all selected values', (WidgetTester tester) async {
    AllergyProfile? savedProfile;

    await tester.pumpWidget(
      MaterialApp(
        home: ProfileScreen(
          initialProfile: const AllergyProfile(
            almond: true,
            argan: true,
          ),
          onProfileSaved: (profile) {
            savedProfile = profile;
          },
        ),
      ),
    );

    await tester.tap(find.text('Clear'));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Apply Profile'));
    await tester.pumpAndSettle();

    expect(savedProfile, isNotNull);
    expect(savedProfile!.hasSelections, isFalse);
  });
}
