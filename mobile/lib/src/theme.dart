import 'package:flutter/material.dart';

import 'brand.dart';

ThemeData buildThatsNutsTheme() {
  const colorScheme = ColorScheme(
    brightness: Brightness.light,
    primary: BrandColors.harvest,
    onPrimary: Colors.white,
    secondary: BrandColors.olive,
    onSecondary: Colors.white,
    error: BrandColors.copper,
    onError: Colors.white,
    surface: BrandColors.surface,
    onSurface: BrandColors.ink,
    primaryContainer: BrandColors.honey,
    onPrimaryContainer: Colors.white,
    secondaryContainer: BrandColors.mossy,
    onSecondaryContainer: BrandColors.ink,
    errorContainer: BrandColors.dangerSurface,
    onErrorContainer: BrandColors.ink,
  );

  final baseTextTheme =
      Typography.material2021(platform: TargetPlatform.iOS).black.apply(
            bodyColor: BrandColors.ink,
            displayColor: BrandColors.ink,
          );

  return ThemeData(
    useMaterial3: true,
    colorScheme: colorScheme,
    scaffoldBackgroundColor: BrandColors.background,
    canvasColor: BrandColors.background,
    textTheme: baseTextTheme.copyWith(
      headlineMedium: baseTextTheme.headlineMedium?.copyWith(
        fontWeight: FontWeight.w800,
        letterSpacing: -0.4,
      ),
      titleLarge: baseTextTheme.titleLarge?.copyWith(
        fontWeight: FontWeight.w800,
        letterSpacing: -0.3,
      ),
      titleMedium: baseTextTheme.titleMedium?.copyWith(
        fontWeight: FontWeight.w700,
      ),
      bodyMedium: baseTextTheme.bodyMedium?.copyWith(
        height: 1.45,
      ),
    ),
    appBarTheme: const AppBarTheme(
      backgroundColor: Colors.transparent,
      foregroundColor: BrandColors.ink,
      elevation: 0,
      scrolledUnderElevation: 0,
      centerTitle: false,
      titleTextStyle: TextStyle(
        color: BrandColors.ink,
        fontSize: 26,
        fontWeight: FontWeight.w800,
        letterSpacing: -0.4,
      ),
    ),
    cardTheme: CardThemeData(
      color: BrandColors.surface,
      elevation: 0,
      margin: EdgeInsets.zero,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(22),
        side: const BorderSide(color: BrandColors.border),
      ),
    ),
    filledButtonTheme: FilledButtonThemeData(
      style: FilledButton.styleFrom(
        backgroundColor: BrandColors.harvest,
        foregroundColor: Colors.white,
        minimumSize: const Size.fromHeight(56),
        padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(18),
        ),
        textStyle: const TextStyle(
          fontWeight: FontWeight.w700,
          fontSize: 16,
        ),
      ),
    ),
    outlinedButtonTheme: OutlinedButtonThemeData(
      style: OutlinedButton.styleFrom(
        foregroundColor: BrandColors.harvest,
        minimumSize: const Size.fromHeight(56),
        padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
        side: const BorderSide(color: BrandColors.border, width: 1.2),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(18),
        ),
        textStyle: const TextStyle(
          fontWeight: FontWeight.w700,
          fontSize: 15,
        ),
      ),
    ),
    inputDecorationTheme: InputDecorationTheme(
      filled: true,
      fillColor: BrandColors.surface,
      contentPadding: const EdgeInsets.symmetric(horizontal: 18, vertical: 16),
      border: OutlineInputBorder(
        borderRadius: BorderRadius.circular(18),
        borderSide: const BorderSide(color: BrandColors.border),
      ),
      enabledBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(18),
        borderSide: const BorderSide(color: BrandColors.border),
      ),
      focusedBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(18),
        borderSide: const BorderSide(color: BrandColors.harvest, width: 1.4),
      ),
      errorBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(18),
        borderSide: const BorderSide(color: BrandColors.copper),
      ),
      focusedErrorBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(18),
        borderSide: const BorderSide(color: BrandColors.copper, width: 1.4),
      ),
    ),
    chipTheme: ChipThemeData(
      backgroundColor: BrandColors.surfaceAlt,
      selectedColor: BrandColors.mossy,
      secondarySelectedColor: BrandColors.mossy,
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 8),
      labelStyle: const TextStyle(
        color: BrandColors.ink,
        fontWeight: FontWeight.w600,
      ),
      side: const BorderSide(color: BrandColors.border),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(14),
      ),
    ),
    dividerTheme: const DividerThemeData(
      color: BrandColors.border,
      thickness: 1,
      space: 1,
    ),
  );
}
