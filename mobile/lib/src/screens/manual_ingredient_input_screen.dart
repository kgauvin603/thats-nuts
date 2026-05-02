import 'package:flutter/material.dart';

import '../brand.dart';
import '../models/allergy_profile.dart';
import '../services/scan_history_refresh_controller.dart';
import '../services/thats_nuts_api_client.dart';
import 'result_screen.dart';

class ManualIngredientInputScreen extends StatefulWidget {
  const ManualIngredientInputScreen({
    super.key,
    required this.apiClient,
    required this.allergyProfile,
    required this.historyRefreshController,
  });

  static const routeName = '/manual-input';

  final ThatsNutsApiClient apiClient;
  final AllergyProfile allergyProfile;
  final ScanHistoryRefreshController historyRefreshController;

  @override
  State<ManualIngredientInputScreen> createState() =>
      _ManualIngredientInputScreenState();
}

class _ManualIngredientInputScreenState
    extends State<ManualIngredientInputScreen> {
  final _controller = TextEditingController();
  bool _isSubmitting = false;
  String? _errorMessage;

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    final ingredientText = _controller.text.trim();
    if (ingredientText.isEmpty) {
      setState(() {
        _errorMessage = 'Enter ingredients before submitting.';
      });
      return;
    }

    setState(() {
      _isSubmitting = true;
      _errorMessage = null;
    });

    try {
      final result = await widget.apiClient.checkIngredients(
        ingredientText,
        allergyProfile: widget.allergyProfile,
      );
      widget.historyRefreshController.markChanged();
      if (!mounted) {
        return;
      }
      await Navigator.of(context).push(
        MaterialPageRoute<void>(
          builder: (context) => ResultScreen.forIngredientCheck(
            ingredientText: ingredientText,
            result: result,
          ),
        ),
      );
    } on ThatsNutsApiException catch (error) {
      setState(() {
        _errorMessage = error.message;
      });
    } catch (_) {
      setState(() {
        _errorMessage = 'Something went wrong while contacting the backend.';
      });
    } finally {
      if (mounted) {
        setState(() {
          _isSubmitting = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Manual Ingredient Check'),
      ),
      body: Padding(
        padding: const EdgeInsets.all(20),
        child: Card(
          child: Padding(
            padding: const EdgeInsets.all(18),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Paste or type the ingredient list.',
                  style: theme.textTheme.titleMedium,
                ),
                const SizedBox(height: 8),
                Container(
                  width: double.infinity,
                  padding:
                      const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
                  decoration: BoxDecoration(
                    color: BrandColors.surfaceAlt,
                    borderRadius: BorderRadius.circular(16),
                    border: Border.all(color: BrandColors.border),
                  ),
                  child: Text(
                    widget.allergyProfile.hasSelections
                        ? 'Profile: ${widget.allergyProfile.summary}'
                        : 'Profile: checking all supported nut-related ingredients.',
                    style: theme.textTheme.bodySmall,
                  ),
                ),
                const SizedBox(height: 16),
                Expanded(
                  child: TextField(
                    controller: _controller,
                    expands: true,
                    maxLines: null,
                    minLines: null,
                    textAlignVertical: TextAlignVertical.top,
                    decoration: const InputDecoration(
                      labelText: 'Ingredient List',
                      alignLabelWithHint: true,
                      hintText: 'Tap here to paste or scan ingredients.',
                      border: OutlineInputBorder(),
                    ),
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  'Tap inside the box, then use iPhone Text Scan from the keyboard/text field to scan the ingredient label.',
                  style: theme.textTheme.bodySmall?.copyWith(
                    color: theme.colorScheme.onSurfaceVariant,
                  ),
                ),
                if (_errorMessage != null) ...[
                  const SizedBox(height: 12),
                  Text(
                    _errorMessage!,
                    style: TextStyle(
                      color: theme.colorScheme.error,
                    ),
                  ),
                ],
                const SizedBox(height: 16),
                SizedBox(
                  width: double.infinity,
                  child: FilledButton(
                    onPressed: _isSubmitting ? null : _submit,
                    child: Text(
                      _isSubmitting ? 'Checking...' : 'Check Ingredients',
                    ),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
