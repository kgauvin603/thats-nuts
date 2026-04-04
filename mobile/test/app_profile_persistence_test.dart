import 'package:flutter_test/flutter_test.dart';
import 'package:thats_nuts_mobile/src/app.dart';
import 'package:thats_nuts_mobile/src/models/allergy_profile.dart';
import 'package:thats_nuts_mobile/src/services/allergy_profile_store.dart';

class FakeAllergyProfileStore extends AllergyProfileStore {
  const FakeAllergyProfileStore(this.profile);

  final AllergyProfile profile;

  @override
  Future<AllergyProfile> load() async => profile;

  @override
  Future<void> save(AllergyProfile profile) async {}
}

void main() {
  testWidgets('loads saved allergy profile when the app starts', (WidgetTester tester) async {
    await tester.pumpWidget(
      const ThatsNutsApp(
        profileStore: FakeAllergyProfileStore(
          AllergyProfile(
            almond: true,
            argan: true,
          ),
        ),
      ),
    );

    await tester.pumpAndSettle();

    expect(find.textContaining('Focused on: Almond, Argan'), findsOneWidget);
    expect(find.text('Manual Ingredient Check'), findsOneWidget);
  });
}
