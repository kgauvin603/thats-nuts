import 'package:flutter/material.dart';

import '../models/allergy_profile.dart';
import '../services/thats_nuts_api_client.dart';
import 'result_screen.dart';

class ManualIngredientInputScreen extends StatefulWidget {
  const ManualIngredientInputScreen({
    super.key,
    required this.apiClient,
    required this.allergyProfile,
  });

  static const routeName = '/manual-input';

  final ThatsNutsApiClient apiClient;
  final AllergyProfile allergyProfile;

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
    return Scaffold(
      appBar: AppBar(
        title: const Text('Manual Ingredient Check'),
      ),
      body: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Enter the ingredient list.',
              style: Theme.of(context).textTheme.titleMedium,
            ),
            const SizedBox(height: 8),
            Text(
              widget.allergyProfile.hasSelections
                  ? 'Profile: ${widget.allergyProfile.summary}'
                  : 'Profile: checking all supported nut-related ingredients.',
              style: Theme.of(context).textTheme.bodySmall,
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
                  labelText: 'Ingredients',
                  alignLabelWithHint: true,
                  hintText:
                      'Water, Glycerin, Prunus Amygdalus Dulcis Oil, Fragrance',
                  border: OutlineInputBorder(),
                ),
              ),
            ),
            const SizedBox(height: 8),
            Text(
              'On iPhone, use text scan right from the field.',
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    color: Theme.of(context).colorScheme.onSurfaceVariant,
                  ),
            ),
            if (_errorMessage != null) ...[
              const SizedBox(height: 12),
              Text(
                _errorMessage!,
                style: TextStyle(
                  color: Theme.of(context).colorScheme.error,
                ),
              ),
            ],
            const SizedBox(height: 16),
            SizedBox(
              width: double.infinity,
              child: FilledButton(
                onPressed: _isSubmitting ? null : _submit,
                child:
                    Text(_isSubmitting ? 'Checking...' : 'Check Ingredients'),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
