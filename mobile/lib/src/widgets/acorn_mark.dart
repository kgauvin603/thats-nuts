import 'package:flutter/material.dart';

class AcornMark extends StatelessWidget {
  const AcornMark({
    super.key,
    this.size = 52,
  });

  static const assetPath =
      'ios/Runner/Assets.xcassets/AppIcon.appiconset/1024.png';

  final double size;

  @override
  Widget build(BuildContext context) {
    return ClipRRect(
      borderRadius: BorderRadius.circular(size * 0.22),
      child: Image.asset(
        assetPath,
        width: size,
        height: size,
        fit: BoxFit.cover,
        filterQuality: FilterQuality.high,
        semanticLabel: "That's Nuts acorn icon",
      ),
    );
  }
}
