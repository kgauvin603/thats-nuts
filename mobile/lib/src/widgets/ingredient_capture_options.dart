import 'package:flutter/material.dart';

import '../brand.dart';
import '../services/ingredient_image_picker.dart';

class IngredientCaptureOptions extends StatelessWidget {
  const IngredientCaptureOptions({
    super.key,
    required this.onTakePhoto,
    required this.onChoosePhoto,
    this.attachedImage,
    this.onRemovePhoto,
  });

  final VoidCallback onTakePhoto;
  final VoidCallback onChoosePhoto;
  final PickedIngredientImage? attachedImage;
  final VoidCallback? onRemovePhoto;

  String _sourceLabel(IngredientImageSource source) {
    switch (source) {
      case IngredientImageSource.camera:
        return 'Camera photo attached';
      case IngredientImageSource.library:
        return 'Library photo attached';
    }
  }

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;
    final colorScheme = Theme.of(context).colorScheme;

    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: BrandColors.surface,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: BrandColors.border),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Capture Options',
            style: textTheme.titleMedium?.copyWith(
              fontWeight: FontWeight.w800,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            'Type or paste ingredients below, use iPhone text scan in the text field, or add a photo to prepare for OCR once image processing is connected.',
            style: textTheme.bodyMedium?.copyWith(height: 1.4),
          ),
          const SizedBox(height: 12),
          Wrap(
            spacing: 10,
            runSpacing: 10,
            children: [
              OutlinedButton.icon(
                onPressed: onTakePhoto,
                icon: const Icon(Icons.photo_camera_outlined),
                label: const Text('Take Photo'),
              ),
              OutlinedButton.icon(
                onPressed: onChoosePhoto,
                icon: const Icon(Icons.photo_library_outlined),
                label: const Text('Choose Photo'),
              ),
            ],
          ),
          if (attachedImage != null) ...[
            const SizedBox(height: 12),
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(14),
              decoration: BoxDecoration(
                color: colorScheme.surfaceContainerHighest,
                borderRadius: BorderRadius.circular(16),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    _sourceLabel(attachedImage!.source),
                    style: textTheme.labelLarge?.copyWith(
                      color: colorScheme.onSurfaceVariant,
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    attachedImage!.fileName,
                    style: textTheme.bodyMedium?.copyWith(
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    'Photo capture is ready on the device, but OCR/image upload is not connected yet. Use text scan or type ingredients into the field below for this release.',
                    style: textTheme.bodySmall?.copyWith(height: 1.35),
                  ),
                  if (onRemovePhoto != null) ...[
                    const SizedBox(height: 8),
                    TextButton.icon(
                      onPressed: onRemovePhoto,
                      icon: const Icon(Icons.close_rounded),
                      label: const Text('Remove Photo'),
                    ),
                  ],
                ],
              ),
            ),
          ],
        ],
      ),
    );
  }
}
