import 'package:flutter/material.dart';

import '../models/allergy_profile.dart';
import '../services/ingredient_image_picker.dart';
import '../services/thats_nuts_api_client.dart';
import '../widgets/ingredient_capture_options.dart';
import 'result_screen.dart';

class BarcodeEnrichmentScreen extends StatefulWidget {
  const BarcodeEnrichmentScreen({
    super.key,
    required this.apiClient,
    required this.allergyProfile,
    required this.barcode,
    this.initialProductName,
    this.initialBrandName,
    this.imagePicker = const _DefaultIngredientImagePicker(),
  });

  final ThatsNutsApiClient apiClient;
  final AllergyProfile allergyProfile;
  final String barcode;
  final String? initialProductName;
  final String? initialBrandName;
  final IngredientImagePicker imagePicker;

  @override
  State<BarcodeEnrichmentScreen> createState() =>
      _BarcodeEnrichmentScreenState();
}

class _BarcodeEnrichmentScreenState extends State<BarcodeEnrichmentScreen> {
  late final TextEditingController _productNameController;
  late final TextEditingController _brandNameController;
  final TextEditingController _ingredientController = TextEditingController();
  PickedIngredientImage? _attachedImage;
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
        allergyProfile: widget.allergyProfile,
      );
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

  Future<void> _pickImage(IngredientImageSource source) async {
    try {
      final pickedImage = await widget.imagePicker.pickImage(source);
      if (!mounted || pickedImage == null) {
        return;
      }
      setState(() {
        _attachedImage = pickedImage;
        _errorMessage = null;
      });
    } catch (_) {
      setState(() {
        _errorMessage = source == IngredientImageSource.camera
            ? 'Could not open the camera right now.'
            : 'Could not open the photo library right now.';
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Add Ingredients for Barcode'),
      ),
      body: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Save ingredients for this barcode so future scans can use the label text you captured.',
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
              IngredientCaptureOptions(
                onTakePhoto: () => _pickImage(IngredientImageSource.camera),
                onChoosePhoto: () => _pickImage(IngredientImageSource.library),
                attachedImage: _attachedImage,
                onRemovePhoto: _attachedImage == null
                    ? null
                    : () {
                        setState(() {
                          _attachedImage = null;
                        });
                      },
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
                          labelText: 'Ingredient Text',
                          alignLabelWithHint: true,
                          hintText:
                              'Water, Glycerin, Prunus Amygdalus Dulcis Oil, Fragrance',
                          border: OutlineInputBorder(),
                        ),
                      ),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      'Tip: On iPhone, tap the text field and use text scan to capture ingredients from the label.',
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
                    _isSubmitting
                        ? 'Saving...'
                        : 'Save Ingredients for This Barcode',
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

class _DefaultIngredientImagePicker implements IngredientImagePicker {
  const _DefaultIngredientImagePicker();

  @override
  Future<PickedIngredientImage?> pickImage(IngredientImageSource source) {
    return DeviceIngredientImagePicker().pickImage(source);
  }
}
