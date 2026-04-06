#!/usr/bin/env bash
set -euo pipefail

APP_ROOT="/mnt/apps/ThatsNuts"
BACKEND_ROOT="$APP_ROOT/backend"
RUN_SCRIPT="$APP_ROOT/scripts/run_backend.sh"
LOG_DIR="$APP_ROOT/logs"
LOG_FILE="$LOG_DIR/backend.log"
PID_FILE="$LOG_DIR/backend.pid"
BRANCH="main"
REMOTE="origin"
HEALTH_URL="http://127.0.0.1:8002/health"
SCAN_HISTORY_URL="http://127.0.0.1:8002/scan-history"
COMMIT_MSG="${1:-Sync OEL9 changes and restart backend}"

mkdir -p "$LOG_DIR"

echo "==> App root: $APP_ROOT"
cd "$APP_ROOT"

echo "==> Git status before sync"
git status --short || true

echo "==> Pull latest from $REMOTE/$BRANCH"
git pull --rebase "$REMOTE" "$BRANCH"

echo "==> Stage all changes"
git add -A

if ! git diff --cached --quiet; then
  echo "==> Committing changes"
  git commit -m "$COMMIT_MSG"
  echo "==> Pushing changes to $REMOTE/$BRANCH"
  git push "$REMOTE" "$BRANCH"
else
  echo "==> No local changes to commit"
fi

echo "==> Stopping existing backend processes if present"
pkill -f "uvicorn app.main:app" || true
pkill -f "run_backend.sh" || true

if [[ -f "$PID_FILE" ]]; then
  OLD_PID="$(cat "$PID_FILE" || true)"
  if [[ -n "${OLD_PID:-}" ]] && kill -0 "$OLD_PID" 2>/dev/null; then
    kill "$OLD_PID" || true
    sleep 2
  fi
  rm -f "$PID_FILE"
fi

echo "==> Starting backend in background"
chmod +x "$RUN_SCRIPT"
nohup "$RUN_SCRIPT" > "$LOG_FILE" 2>&1 &
NEW_PID=$!
echo "$NEW_PID" > "$PID_FILE"

echo "==> Waiting for backend health check"
for i in {1..30}; do
  if curl -fsS "$HEALTH_URL" >/dev/null 2>&1; then
    echo "==> Backend is healthy"
    break
  fi
  sleep 2
done

echo "==> Verifying backend endpoints"
curl -i "$HEALTH_URL"
echo
curl -i "$SCAN_HISTORY_URL"
echo

echo "==> Active backend PID: $NEW_PID"
echo "==> Log file: $LOG_FILE"

echo "==> Done"
