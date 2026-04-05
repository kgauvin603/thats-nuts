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

The app now uses `mobile_scanner` for camera-based UPC/EAN scanning and `image_picker` for ingredient-photo capture.
The mobile client also supports a simple local allergy profile that is sent with ingredient and barcode requests when you enable any profile toggles.
That profile is persisted locally on device and restored when the app starts again.
Manual ingredient capture currently supports:

- typing or pasting ingredient text
- iPhone built-in text scan from the text field
- taking a photo
- choosing a photo from the library

Photo capture is wired on-device, but OCR/image upload for ingredient extraction is not connected yet. For now, use the text field as the source of truth after taking or choosing a photo.

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

## iPhone demo script

Use this for a short, reliable operator demo on iPhone.

Prerequisites:

- backend running via `./scripts/run_backend.sh`
- demo barcodes loaded with `backend/.venv/bin/python scripts/load_demo_barcodes.py`
- iPhone and backend host on the same network
- app started with `flutter run --dart-define=API_BASE_URL=http://YOUR_LAN_IP:8002`

Backend URL check:

1. Open `http://YOUR_LAN_IP:8002/health` in Safari on the iPhone.
2. Confirm the page returns a healthy response before opening the app demo.

Demo flow:

1. Open the app and tap `Edit Profile`.
2. Turn on one simple profile option such as `Almond`, then save.
3. Tap `Manual Ingredient Check`.
4. In the text field, either paste ingredients or on iPhone tap into the field and use built-in text scan from the keyboard/text-entry flow to capture the label text.
5. Use a sample ingredient list such as `Water, Glycerin, Prunus Amygdalus Dulcis Oil` and tap `Check Ingredients`.
6. Point out the status, explanation, matched ingredient, and bottom action buttons on the result screen.
7. Go back, tap `Scan Barcode`, and scan demo barcode `9900000000001` for a positive match.
8. Optionally scan `9900000000003` to show a clear result or `9900000000004` to show `cannot_verify`.
9. Open `Recent History` and confirm the manual ingredient check and barcode lookup both appear.

If a barcode is not found:

- Explain that the current app still records the lookup in recent history.
- Use `Enter Barcode Manually` if camera scanning is inconvenient.
- Continue the demo with one of the seeded demo barcodes: `9900000000001`, `9900000000003`, or `9900000000004`.

## Current app flow

1. Open home screen
2. Optionally edit the allergy profile
3. Go to manual ingredient input
4. Paste ingredients
5. Submit to backend
6. View result screen

Manual ingredient capture options:

1. Open manual ingredient input
2. Either type/paste ingredients, use iPhone text scan in the text field, take a photo, or choose a photo
3. If you add a photo, keep entering ingredients in the text field for now because OCR is not connected yet
4. Submit to backend

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

`mobile_scanner` and `image_picker` require camera access, and library selection needs photo-library access. Add these keys to `ios/Runner/Info.plist`.

Example:

```xml
<key>NSCameraUsageDescription</key>
<string>This app needs camera access to scan product barcodes.</string>
<key>NSPhotoLibraryUsageDescription</key>
<string>This app needs photo library access so you can choose ingredient label photos.</string>
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
