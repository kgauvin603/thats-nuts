#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BACKEND_DIR="$REPO_ROOT/backend"
VENV_DIR="$BACKEND_DIR/.venv"
REQUIREMENTS_FILE="$BACKEND_DIR/requirements.txt"
REQUIREMENTS_STAMP="$VENV_DIR/.requirements.sha256"
ENV_FILE="${APP_ENV_FILE:-$BACKEND_DIR/.env}"

if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 is required but was not found on PATH." >&2
  exit 1
fi

if [ -f "$ENV_FILE" ]; then
  set -a
  # shellcheck disable=SC1090
  source "$ENV_FILE"
  set +a
fi

APP_HOST="${APP_HOST:-0.0.0.0}"
APP_PORT="${APP_PORT:-${PORT:-8002}}"
APP_RELOAD="${APP_RELOAD:-false}"
APP_LOG_LEVEL="${APP_LOG_LEVEL:-info}"
INSTALL_DEPS="${INSTALL_DEPS:-true}"

mkdir -p "$BACKEND_DIR"

if [ ! -d "$VENV_DIR" ]; then
  python3 -m venv "$VENV_DIR"
fi

# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"

requirements_hash() {
  python3 - "$REQUIREMENTS_FILE" <<'PY'
from pathlib import Path
import hashlib
import sys

path = Path(sys.argv[1])
print(hashlib.sha256(path.read_bytes()).hexdigest())
PY
}

if [ "$INSTALL_DEPS" = "true" ]; then
  current_hash="$(requirements_hash)"
  installed_hash=""

  if [ -f "$REQUIREMENTS_STAMP" ]; then
    installed_hash="$(cat "$REQUIREMENTS_STAMP")"
  fi

  if [ "$current_hash" != "$installed_hash" ]; then
    python3 -m pip install -r "$REQUIREMENTS_FILE"
    printf '%s' "$current_hash" > "$REQUIREMENTS_STAMP"
  fi
fi

cd "$BACKEND_DIR"

uvicorn_args=(
  "app.main:app"
  "--host" "$APP_HOST"
  "--port" "$APP_PORT"
  "--log-level" "$APP_LOG_LEVEL"
)

if [ "$APP_RELOAD" = "true" ]; then
  uvicorn_args+=("--reload")
fi

echo "Starting Thats Nuts backend on ${APP_HOST}:${APP_PORT}"
exec python3 -m uvicorn "${uvicorn_args[@]}"
