import 'dart:convert';

import 'package:shared_preferences/shared_preferences.dart';

import '../models/allergy_profile.dart';

class AllergyProfileStore {
  const AllergyProfileStore();

  static const _storageKey = 'allergy_profile';

  Future<AllergyProfile> load() async {
    final preferences = await SharedPreferences.getInstance();
    final rawValue = preferences.getString(_storageKey);

    if (rawValue == null || rawValue.isEmpty) {
      return const AllergyProfile();
    }

    try {
      final decoded = jsonDecode(rawValue);
      if (decoded is Map<String, dynamic>) {
        return AllergyProfile.fromJson(decoded);
      }
      if (decoded is Map) {
        return AllergyProfile.fromJson(
          decoded.map(
            (key, value) => MapEntry(key.toString(), value),
          ),
        );
      }
    } catch (_) {
      return const AllergyProfile();
    }

    return const AllergyProfile();
  }

  Future<void> save(AllergyProfile profile) async {
    final preferences = await SharedPreferences.getInstance();

    if (!profile.hasSelections) {
      await preferences.remove(_storageKey);
      return;
    }

    await preferences.setString(
      _storageKey,
      jsonEncode(profile.toStorageJson()),
    );
  }
}
