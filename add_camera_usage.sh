#!/usr/bin/env bash
set -euo pipefail

PLIST="${1:-$HOME/Projects/thats-nuts/mobile/ios/Runner/Info.plist}"
KEY="NSCameraUsageDescription"
VALUE="This app uses the camera to scan product barcodes."

if [[ ! -f "$PLIST" ]]; then
  echo "Error: Info.plist not found at: $PLIST" >&2
  exit 1
fi

echo "Using plist: $PLIST"

cp "$PLIST" "${PLIST}.bak.$(date +%Y%m%d_%H%M%S)"

if /usr/libexec/PlistBuddy -c "Print :$KEY" "$PLIST" >/dev/null 2>&1; then
  echo "$KEY already exists. Updating value..."
  /usr/libexec/PlistBuddy -c "Set :$KEY $VALUE" "$PLIST"
else
  echo "$KEY not found. Adding it..."
  /usr/libexec/PlistBuddy -c "Add :$KEY string $VALUE" "$PLIST"
fi

echo "Done. Current value:"
q!/usr/libexec/PlistBuddy -c "Print :$KEY" "$PLIST"
