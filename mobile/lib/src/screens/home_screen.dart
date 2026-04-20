import 'package:flutter/material.dart';

import '../brand.dart';
import '../models/allergy_profile.dart';
import '../services/scan_history_refresh_controller.dart';
import '../services/thats_nuts_api_client.dart';
import '../widgets/acorn_mark.dart';
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
    required this.historyRefreshController,
    required this.onProfileSaved,
  });

  final ThatsNutsApiClient apiClient;
  final AllergyProfile allergyProfile;
  final ScanHistoryRefreshController historyRefreshController;
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

  void _openManualCheck(BuildContext context) {
    Navigator.of(context).push(
      MaterialPageRoute<void>(
        builder: (context) => ManualIngredientInputScreen(
          apiClient: apiClient,
          allergyProfile: allergyProfile,
          historyRefreshController: historyRefreshController,
        ),
      ),
    );
  }

  void _openBarcodeScanner(BuildContext context) {
    Navigator.of(context).push(
      MaterialPageRoute<void>(
        builder: (context) => BarcodeScannerScreen(
          apiClient: apiClient,
          allergyProfile: allergyProfile,
          historyRefreshController: historyRefreshController,
        ),
      ),
    );
  }

  void _openBarcodeInput(BuildContext context) {
    Navigator.of(context).push(
      MaterialPageRoute<void>(
        builder: (context) => BarcodeInputScreen(
          apiClient: apiClient,
          allergyProfile: allergyProfile,
          historyRefreshController: historyRefreshController,
        ),
      ),
    );
  }

  void _openHistory(BuildContext context) {
    Navigator.of(context).push(
      MaterialPageRoute<void>(
        builder: (context) => HistoryScreen(
          apiClient: apiClient,
          historyRefreshController: historyRefreshController,
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;

    return Scaffold(
      appBar: AppBar(
        title: const Text(kAppName),
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
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 20),
            decoration: BoxDecoration(
              color: BrandColors.surface,
              borderRadius: BorderRadius.circular(28),
              gradient: const LinearGradient(
                colors: [
                  BrandColors.surfaceAlt,
                  BrandColors.panelAccent,
                ],
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
              ),
              border: Border.all(color: BrandColors.border),
              boxShadow: const [
                BoxShadow(
                  color: Color(0x14000000),
                  blurRadius: 22,
                  offset: Offset(0, 10),
                ),
              ],
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Container(
                  width: 64,
                  height: 64,
                  decoration: BoxDecoration(
                    gradient: BrandColors.warmAccentGradient,
                    borderRadius: BorderRadius.circular(20),
                    boxShadow: const [
                      BoxShadow(
                        color: Color(0x16000000),
                        blurRadius: 16,
                        offset: Offset(0, 6),
                      ),
                    ],
                  ),
                  child: const Center(
                    child: AcornMark(size: 38),
                  ),
                ),
                const SizedBox(height: 18),
                Text(
                  'Check labels quickly.',
                  style: textTheme.headlineSmall,
                ),
                const SizedBox(height: 8),
                Text(
                  'Identify nut ingredients in beauty, skincare, cosmetics — and packaged foods too.',
                  style: textTheme.bodyMedium?.copyWith(
                    height: 1.4,
                    color: Theme.of(context).colorScheme.onSurfaceVariant,
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 16),
          Card(
            margin: EdgeInsets.zero,
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
              child: Row(
                children: [
                  Container(
                    width: 36,
                    height: 36,
                    decoration: BoxDecoration(
                      color: BrandColors.surfaceAlt,
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: const Icon(Icons.tune_rounded, size: 20),
                  ),
                  const SizedBox(width: 10),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Text(
                          'Allergy Profile',
                          style:
                              Theme.of(context).textTheme.titleSmall?.copyWith(
                                    fontWeight: FontWeight.w700,
                                  ),
                        ),
                        Text(
                          allergyProfile.hasSelections
                              ? allergyProfile.summary
                              : 'All supported nut-related ingredients',
                          style:
                              Theme.of(context).textTheme.bodySmall?.copyWith(
                                    color: Theme.of(context)
                                        .colorScheme
                                        .onSurfaceVariant,
                                  ),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(width: 12),
                  OutlinedButton(
                    onPressed: () => _openProfile(context),
                    style: OutlinedButton.styleFrom(
                      minimumSize: const Size(0, 40),
                      padding: const EdgeInsets.symmetric(
                        horizontal: 14,
                        vertical: 8,
                      ),
                    ),
                    child: const Text('Edit'),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 24),
          SizedBox(
            width: double.infinity,
            child: FilledButton.icon(
              onPressed: () => _openManualCheck(context),
              icon: const Icon(Icons.fact_check_rounded),
              label: const Text('Enter Ingredients'),
            ),
          ),
          const SizedBox(height: 12),
          SizedBox(
            width: double.infinity,
            child: ElevatedButton.icon(
              onPressed: () => _openBarcodeScanner(context),
              icon: const Icon(Icons.qr_code_scanner_rounded),
              label: const Text('Scan Barcode'),
            ),
          ),
          const SizedBox(height: 12),
          SizedBox(
            width: double.infinity,
            child: OutlinedButton.icon(
              onPressed: () => _openBarcodeInput(context),
              icon: const Icon(Icons.keyboard_rounded),
              label: const Text('Enter Barcode Manually'),
            ),
          ),
          const SizedBox(height: 12),
          SizedBox(
            width: double.infinity,
            child: OutlinedButton.icon(
              onPressed: () => _openHistory(context),
              icon: const Icon(Icons.history_rounded),
              label: const Text('Recent History'),
            ),
          ),
        ],
      ),
    );
  }
}
