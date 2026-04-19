#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="/mnt/apps/ThatsNuts"
SERVICE_NAME="thatsnuts-backend"

cd "$REPO_DIR"

echo "==> Fetching latest"
git fetch origin main

echo "==> Resetting to origin/main"
git checkout main
git reset --hard origin/main

echo "==> Restarting backend"
sudo systemctl restart "$SERVICE_NAME"

echo "==> Service status"
sudo systemctl status "$SERVICE_NAME" --no-pager

echo "==> Health check"
curl -fsS http://127.0.0.1:8002/health
