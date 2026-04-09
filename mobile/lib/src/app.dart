import 'package:flutter/material.dart';

import 'brand.dart';
import 'models/allergy_profile.dart';
import 'screens/barcode_input_screen.dart';
import 'screens/barcode_scanner_screen.dart';
import 'screens/history_screen.dart';
import 'screens/home_screen.dart';
import 'screens/manual_ingredient_input_screen.dart';
import 'screens/profile_screen.dart';
import 'services/allergy_profile_store.dart';
import 'services/thats_nuts_api_client.dart';
import 'theme.dart';

class ThatsNutsApp extends StatefulWidget {
  const ThatsNutsApp({
    super.key,
    this.profileStore = const AllergyProfileStore(),
  });

  final AllergyProfileStore profileStore;

  @override
  State<ThatsNutsApp> createState() => _ThatsNutsAppState();
}

class _ThatsNutsAppState extends State<ThatsNutsApp> {
  final ThatsNutsApiClient _apiClient = ThatsNutsApiClient();
  AllergyProfile _allergyProfile = const AllergyProfile();
  bool _isLoadingProfile = true;

  @override
  void initState() {
    super.initState();
    _loadAllergyProfile();
  }

  Future<void> _loadAllergyProfile() async {
    final profile = await widget.profileStore.load();
    if (!mounted) {
      return;
    }
    setState(() {
      _allergyProfile = profile;
      _isLoadingProfile = false;
    });
  }

  void _updateAllergyProfile(AllergyProfile profile) {
    setState(() {
      _allergyProfile = profile;
    });
    widget.profileStore.save(profile);
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoadingProfile) {
      return MaterialApp(
        title: kAppName,
        theme: buildThatsNutsTheme(),
        home: const Scaffold(
          body: Center(
            child: CircularProgressIndicator(),
          ),
        ),
      );
    }

    return MaterialApp(
      title: kAppName,
      theme: buildThatsNutsTheme(),
      home: HomeScreen(
        apiClient: _apiClient,
        allergyProfile: _allergyProfile,
        onProfileSaved: _updateAllergyProfile,
      ),
      routes: {
        ManualIngredientInputScreen.routeName: (context) =>
            ManualIngredientInputScreen(
              apiClient: _apiClient,
              allergyProfile: _allergyProfile,
            ),
        BarcodeInputScreen.routeName: (context) => BarcodeInputScreen(
              apiClient: _apiClient,
              allergyProfile: _allergyProfile,
            ),
        BarcodeScannerScreen.routeName: (context) => BarcodeScannerScreen(
              apiClient: _apiClient,
              allergyProfile: _allergyProfile,
            ),
        HistoryScreen.routeName: (context) => HistoryScreen(
              apiClient: _apiClient,
            ),
        ProfileScreen.routeName: (context) => ProfileScreen(
              initialProfile: _allergyProfile,
              onProfileSaved: _updateAllergyProfile,
            ),
      },
    );
  }
}
