# Mobile

Lightweight Flutter client scaffold for Thats Nuts.

## What is included

- app entry point
- home screen
- manual ingredient input screen
- barcode scanner screen
- barcode input screen
- allergy profile screen
- history screen
- result screen
- simple API client wired to:
  - `POST /check-ingredients`
  - `POST /lookup-product`
  - `GET /scan-history`

## Prerequisites

- Flutter SDK installed locally
- backend running on port `8002`

This repository does not include generated platform folders yet because Flutter tooling is not available in this environment. Generate them locally with:

```bash
cd mobile
flutter create .
```

Then restore the files in `lib/` and `pubspec.yaml` from this repo if `flutter create .` overwrites them.

## Install dependencies

```bash
cd mobile
flutter pub get
```

The app now uses `mobile_scanner` for camera-based UPC/EAN scanning.
The mobile client also supports a simple local allergy profile that is sent with ingredient and barcode requests when you enable any profile toggles.
That profile is persisted locally on device and restored when the app starts again.

## Run the app

Use a backend URL appropriate for your simulator or device:

```bash
cd mobile
flutter run --dart-define=API_BASE_URL=http://10.0.2.2:8002
```

Examples:

- Android emulator: `http://10.0.2.2:8002`
- iOS simulator: `http://127.0.0.1:8002`
- physical device: `http://YOUR_LAN_IP:8002`

## Current app flow

1. Open home screen
2. Optionally edit the allergy profile
3. Go to manual ingredient input
4. Paste ingredients
5. Submit to backend
6. View result screen

History flow:

1. Open home screen
2. Go to recent history
3. Pull recent checks from the backend
4. Review product name, barcode, assessment status, explanation, and time

Barcode lookup flow:

1. Open home screen
2. Optionally edit the allergy profile
3. Go to scan barcode
4. Point the camera at a UPC / EAN code
5. App calls the backend lookup endpoint and opens the result screen automatically after a successful scan
6. View normalized product + assessment result

Manual barcode fallback:

1. Open home screen
2. Optionally edit the allergy profile
3. Go to enter barcode manually
4. Type a UPC / EAN code
5. Submit to backend
6. View normalized product + assessment result

## Platform setup notes

This repo still does not include generated Flutter platform folders. Generate them locally first:

```bash
cd mobile
flutter create .
```

After generating platform folders, re-apply the files from this repository if `flutter create .` overwrites `lib/` or `pubspec.yaml`.

### iOS

`mobile_scanner` requires camera access, so add `NSCameraUsageDescription` to `ios/Runner/Info.plist`.

Example:

```xml
<key>NSCameraUsageDescription</key>
<string>This app needs camera access to scan product barcodes.</string>
```

### Android

The default Android setup should work after generating the platform folders. If you want the unbundled ML Kit scanner to reduce app size, add the optional flag below to `android/gradle.properties`.

Optional:

```properties
dev.steenbakker.mobile_scanner.useUnbundled=true
```

## Assumptions

- Primary supported mobile platforms are Android and iOS.
- Camera scanning depends on the user granting camera permission.
- If camera permission is denied or the scanner fails to initialize, the scanner screen shows a manual barcode fallback and retry guidance.
- If scanning is unavailable, denied, or inconvenient, manual barcode entry remains the fallback.

## What is still placeholder

- generated Android/iOS/web platform files
