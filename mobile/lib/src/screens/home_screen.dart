import 'package:flutter/material.dart';

import '../models/allergy_profile.dart';
import '../services/thats_nuts_api_client.dart';
import 'barcode_input_screen.dart';
import 'barcode_scanner_screen.dart';
import 'history_screen.dart';
import 'manual_ingredient_input_screen.dart';
import 'profile_screen.dart';

class HomeScreen extends StatelessWidget {
  const HomeScreen({
    super.key,
    required this.apiClient,
    required this.allergyProfile,
    required this.onProfileSaved,
  });

  final ThatsNutsApiClient apiClient;
  final AllergyProfile allergyProfile;
  final ValueChanged<AllergyProfile> onProfileSaved;

  void _openProfile(BuildContext context) {
    Navigator.of(context).push(
      MaterialPageRoute<void>(
        builder: (context) => ProfileScreen(
          initialProfile: allergyProfile,
          onProfileSaved: onProfileSaved,
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Thats Nuts'),
        actions: [
          IconButton(
            onPressed: () => _openProfile(context),
            icon: const Icon(Icons.tune_rounded),
            tooltip: 'Allergy Profile',
          ),
        ],
      ),
      body: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          Text(
            'Nut-allergy ingredient checks for skincare and personal care products.',
            style: Theme.of(context).textTheme.titleMedium,
          ),
          const SizedBox(height: 12),
          Text(
            'Start with a manual ingredient list or test a barcode lookup against the backend.',
            style: Theme.of(context).textTheme.bodyMedium,
          ),
          const SizedBox(height: 20),
          Card(
            margin: EdgeInsets.zero,
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Allergy Profile',
                    style: Theme.of(context).textTheme.titleMedium?.copyWith(
                          fontWeight: FontWeight.w700,
                        ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    allergyProfile.hasSelections
                        ? 'Focused on: ${allergyProfile.summary}'
                        : 'No profile selected. Checks will include all supported nut-related ingredients.',
                  ),
                  const SizedBox(height: 12),
                  OutlinedButton(
                    onPressed: () => _openProfile(context),
                    child: const Text('Edit Profile'),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 24),
          SizedBox(
            width: double.infinity,
            child: FilledButton(
              onPressed: () {
                Navigator.of(context).push(
                  MaterialPageRoute<void>(
                    builder: (context) => ManualIngredientInputScreen(
                      apiClient: apiClient,
                      allergyProfile: allergyProfile,
                    ),
                  ),
                );
              },
              child: const Text('Manual Ingredient Check'),
            ),
          ),
          const SizedBox(height: 12),
          SizedBox(
            width: double.infinity,
            child: OutlinedButton(
              onPressed: () {
                Navigator.of(context).push(
                  MaterialPageRoute<void>(
                    builder: (context) => BarcodeScannerScreen(
                      apiClient: apiClient,
                      allergyProfile: allergyProfile,
                    ),
                  ),
                );
              },
              child: const Text('Scan Barcode'),
            ),
          ),
          const SizedBox(height: 12),
          SizedBox(
            width: double.infinity,
            child: OutlinedButton(
              onPressed: () {
                Navigator.of(context).push(
                  MaterialPageRoute<void>(
                    builder: (context) => BarcodeInputScreen(
                      apiClient: apiClient,
                      allergyProfile: allergyProfile,
                    ),
                  ),
                );
              },
              child: const Text('Enter Barcode Manually'),
            ),
          ),
          const SizedBox(height: 12),
          SizedBox(
            width: double.infinity,
            child: OutlinedButton(
              onPressed: () {
                Navigator.of(context).push(
                  MaterialPageRoute<void>(
                    builder: (context) => HistoryScreen(
                      apiClient: apiClient,
                    ),
                  ),
                );
              },
              child: const Text('Recent History'),
            ),
          ),
        ],
      ),
    );
  }
}
