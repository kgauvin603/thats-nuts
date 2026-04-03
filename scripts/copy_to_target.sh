#!/usr/bin/env bash
set -euo pipefail

if [ $# -ne 1 ]; then
  echo "Usage: $0 /mnt/apps/ThatsNuts"
  exit 1
fi

TARGET="$1"
mkdir -p "$TARGET"
rsync -av --delete ./ "$TARGET"/
