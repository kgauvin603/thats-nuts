import 'package:flutter/material.dart';

import '../models/allergy_profile.dart';
import '../models/product_lookup_models.dart';
import '../services/thats_nuts_api_client.dart';
import 'barcode_enrichment_screen.dart';
import 'barcode_scanner_screen.dart';
import 'result_screen.dart';

class BarcodeInputScreen extends StatefulWidget {
  const BarcodeInputScreen({
    super.key,
    required this.apiClient,
    required this.allergyProfile,
  });

  static const routeName = '/barcode-input';

  final ThatsNutsApiClient apiClient;
  final AllergyProfile allergyProfile;

  @override
  State<BarcodeInputScreen> createState() => _BarcodeInputScreenState();
}

class _BarcodeInputScreenState extends State<BarcodeInputScreen> {
  final _controller = TextEditingController();
  bool _isSubmitting = false;
  String? _errorMessage;

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    final barcode = _controller.text.trim();
    if (barcode.isEmpty) {
      setState(() {
        _errorMessage = 'Enter a barcode before submitting.';
      });
      return;
    }

    setState(() {
      _isSubmitting = true;
      _errorMessage = null;
    });

    try {
      final result = await widget.apiClient.lookupProduct(
        barcode,
        allergyProfile: widget.allergyProfile,
      );
      if (!mounted) {
        return;
      }
      await _openLookupResult(barcode, result);
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

  Future<void> _openLookupResult(String barcode, ProductLookupResult result) {
    return Navigator.of(context).push(
      MaterialPageRoute<void>(
        builder: (context) => ResultScreen.forProductLookup(
          barcode: barcode,
          result: result,
          fallbackActionLabel: result.canAddIngredientsFallback
              ? 'Add Ingredients for This Barcode'
              : null,
          onFallbackAction: result.canAddIngredientsFallback
              ? (screenContext) => Navigator.of(screenContext).push(
                    MaterialPageRoute<void>(
                      builder: (context) => BarcodeEnrichmentScreen(
                        apiClient: widget.apiClient,
                        allergyProfile: widget.allergyProfile,
                        barcode: barcode,
                        initialProductName: result.product?.productName,
                        initialBrandName: result.product?.brandName,
                      ),
                    ),
                  )
              : null,
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Barcode Lookup'),
      ),
      body: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Enter a UPC or EAN code to look up a product and assess its ingredients.',
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
            TextField(
              controller: _controller,
              keyboardType: TextInputType.number,
              decoration: const InputDecoration(
                hintText: '0001234567890',
                labelText: 'Barcode',
                border: OutlineInputBorder(),
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
                child: Text(_isSubmitting ? 'Looking Up...' : 'Lookup Product'),
              ),
            ),
            const SizedBox(height: 12),
            SizedBox(
              width: double.infinity,
              child: OutlinedButton(
                onPressed: _isSubmitting
                    ? null
                    : () {
                        Navigator.of(context).push(
                          MaterialPageRoute<void>(
                            builder: (context) => BarcodeScannerScreen(
                              apiClient: widget.apiClient,
                              allergyProfile: widget.allergyProfile,
                            ),
                          ),
                        );
                      },
                child: const Text('Use Camera Scanner'),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
