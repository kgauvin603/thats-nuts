import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:thats_nuts_mobile/src/models/allergy_profile.dart';
import 'package:thats_nuts_mobile/src/services/allergy_profile_store.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  test('loads default profile when nothing is stored', () async {
    SharedPreferences.setMockInitialValues({});
    const store = AllergyProfileStore();

    final profile = await store.load();

    expect(profile.hasSelections, isFalse);
  });

  test('saves and reloads selected profile fields', () async {
    SharedPreferences.setMockInitialValues({});
    const store = AllergyProfileStore();

    await store.save(
      const AllergyProfile(
        almond: true,
        argan: true,
      ),
    );

    final profile = await store.load();

    expect(profile.almond, isTrue);
    expect(profile.argan, isTrue);
    expect(profile.peanut, isFalse);
  });

  test('clears persisted profile when nothing is selected', () async {
    SharedPreferences.setMockInitialValues({
      'allergy_profile': '{"almond":true}',
    });
    const store = AllergyProfileStore();

    await store.save(const AllergyProfile());

    final profile = await store.load();

    expect(profile.hasSelections, isFalse);
  });
}
