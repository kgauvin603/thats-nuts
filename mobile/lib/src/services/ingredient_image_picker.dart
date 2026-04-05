import 'package:image_picker/image_picker.dart';

enum IngredientImageSource {
  camera,
  library,
}

class PickedIngredientImage {
  const PickedIngredientImage({
    required this.fileName,
    required this.path,
    required this.source,
  });

  final String fileName;
  final String path;
  final IngredientImageSource source;
}

abstract class IngredientImagePicker {
  Future<PickedIngredientImage?> pickImage(IngredientImageSource source);
}

class DeviceIngredientImagePicker implements IngredientImagePicker {
  DeviceIngredientImagePicker({
    ImagePicker? picker,
  }) : _picker = picker ?? ImagePicker();

  final ImagePicker _picker;

  @override
  Future<PickedIngredientImage?> pickImage(IngredientImageSource source) async {
    final xFile = await _picker.pickImage(
      source: source == IngredientImageSource.camera
          ? ImageSource.camera
          : ImageSource.gallery,
    );
    if (xFile == null) {
      return null;
    }

    final fileName =
        xFile.name.isNotEmpty ? xFile.name : xFile.path.split('/').last;
    return PickedIngredientImage(
      fileName: fileName,
      path: xFile.path,
      source: source,
    );
  }
}
