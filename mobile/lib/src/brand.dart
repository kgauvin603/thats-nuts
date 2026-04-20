import 'package:flutter/material.dart';

const String kAppName = "That's Nuts!";

class BrandColors {
  static const Color mossy = Color(0xFFD7D6BF);
  static const Color olive = Color(0xFF9BA27D);
  static const Color harvest = Color(0xFFB8875A);
  static const Color honey = Color(0xFFD6B184);
  static const Color bark = Color(0xFFA0714A);
  static const Color acorn = Color(0xFF8C6A3D);
  static const Color copper = Color(0xFFC85D36);

  static const Color background = Color(0xFFF3EDE4);
  static const Color surface = Color(0xFFEBDCC6);
  static const Color surfaceAlt = Color(0xFFF0E6DB);
  static const Color panelAccent = Color(0xFFD4C18D);
  static const Color border = Color(0xFFD2BDA4);
  static const Color ink = Color(0xFF3D2B1F);

  static const Color danger = Color(0xFFC85D36);
  static const Color dangerSurface = Color(0xFFF8E0D6);
  static const Color warning = Color(0xFFD68544);
  static const Color warningSurface = Color(0xFFF8E9D6);
  static const Color success = Color(0xFF7A7B33);
  static const Color successSurface = Color(0xFFEEF0D8);
  static const Color neutralSurface = Color(0xFFF4EBDD);

  static const LinearGradient warmAccentGradient = LinearGradient(
    colors: [
      Color(0xFFE9C18B),
      harvest,
    ],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );
}
