import 'package:flutter/material.dart';

import '../models/allergy_profile.dart';
import '../services/scan_history_refresh_controller.dart';
import '../services/thats_nuts_api_client.dart';
import 'result_screen.dart';

class BarcodeEnrichmentScreen extends StatefulWidget {
  const BarcodeEnrichmentScreen({
    super.key,
    required this.apiClient,
    required this.allergyProfile,
    required this.historyRefreshController,
    required this.barcode,
    this.initialProductName,
    this.initialBrandName,
  });

  final ThatsNutsApiClient apiClient;
  final AllergyProfile allergyProfile;
  final ScanHistoryRefreshController historyRefreshController;
  final String barcode;
  final String? initialProductName;
  final String? initialBrandName;

  @override
  State<BarcodeEnrichmentScreen> createState() =>
      _BarcodeEnrichmentScreenState();
}

class _BarcodeEnrichmentScreenState extends State<BarcodeEnrichmentScreen> {
  late final TextEditingController _productNameController;
  late final TextEditingController _brandNameController;
  final TextEditingController _ingredientController = TextEditingController();
  bool _isSubmitting = false;
  String? _errorMessage;

  @override
  void initState() {
    super.initState();
    _productNameController =
        TextEditingController(text: widget.initialProductName ?? '');
    _brandNameController =
        TextEditingController(text: widget.initialBrandName ?? '');
  }

  @override
  void dispose() {
    _productNameController.dispose();
    _brandNameController.dispose();
    _ingredientController.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    final ingredientText = _ingredientController.text.trim();
    if (ingredientText.isEmpty) {
      setState(() {
        _errorMessage = 'Enter ingredients before saving this barcode.';
      });
      return;
    }

    setState(() {
      _isSubmitting = true;
      _errorMessage = null;
    });

    try {
      final result = await widget.apiClient.enrichProduct(
        widget.barcode,
        ingredientText: ingredientText,
        productName: _productNameController.text,
        brandName: _brandNameController.text,
        source: 'manual_entry',
        allergyProfile: widget.allergyProfile,
      );
      widget.historyRefreshController.markChanged();
      if (!mounted) {
        return;
      }
      await Navigator.of(context).pushReplacement(
        MaterialPageRoute<void>(
          builder: (context) => ResultScreen.forProductLookup(
            barcode: widget.barcode,
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
        _errorMessage =
            'Something went wrong while saving ingredients for this barcode.';
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
    final textTheme = Theme.of(context).textTheme;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Add Ingredients for This Barcode'),
      ),
      body: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Save ingredients for this barcode for future lookups.',
                style: textTheme.titleMedium,
              ),
              const SizedBox(height: 8),
              Text(
                widget.allergyProfile.hasSelections
                    ? 'Profile: ${widget.allergyProfile.summary}'
                    : 'Profile: checking all supported nut-related ingredients.',
                style: textTheme.bodySmall,
              ),
              const SizedBox(height: 16),
              InputDecorator(
                decoration: const InputDecoration(
                  labelText: 'Barcode',
                  border: OutlineInputBorder(),
                ),
                child: SelectableText(
                  widget.barcode,
                  style: textTheme.bodyLarge,
                ),
              ),
              const SizedBox(height: 12),
              TextField(
                controller: _productNameController,
                decoration: const InputDecoration(
                  labelText: 'Product Name (Optional)',
                  border: OutlineInputBorder(),
                ),
              ),
              const SizedBox(height: 12),
              TextField(
                controller: _brandNameController,
                decoration: const InputDecoration(
                  labelText: 'Brand (Optional)',
                  border: OutlineInputBorder(),
                ),
              ),
              const SizedBox(height: 16),
              SizedBox(
                height: 280,
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Expanded(
                      child: TextField(
                        controller: _ingredientController,
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
                      'Use the iPhone text scan control in the field if needed.',
                      style: textTheme.bodySmall?.copyWith(
                        color: Theme.of(context).colorScheme.onSurfaceVariant,
                      ),
                    ),
                  ],
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
                  child: Text(
                    _isSubmitting ? 'Saving...' : 'Save Barcode Ingredients',
                  ),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}
