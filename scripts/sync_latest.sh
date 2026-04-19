#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="${1:-$HOME/Projects/thats-nuts}"

cd "$REPO_DIR"

echo "==> Repo: $REPO_DIR"

# Refuse to run if a merge/rebase is already in progress
if [ -d .git/rebase-merge ] || [ -d .git/rebase-apply ] || [ -f .git/MERGE_HEAD ]; then
  echo "ERROR: Git rebase/merge already in progress."
  echo "Resolve or abort it first:"
  echo "  git rebase --abort"
  echo "  git merge --abort"
  exit 1
fi

echo "==> Stashing local changes (if any)"
STASH_NAME="auto-sync-$(date +%Y%m%d-%H%M%S)"
git stash push -u -m "$STASH_NAME" >/dev/null 2>&1 || true

echo "==> Fetching latest from origin/main"
git fetch origin main

echo "==> Resetting local main to origin/main"
git checkout main
git reset --hard origin/main

echo "==> Restoring stashed local changes (if any)"
if git stash list | grep -q "$STASH_NAME"; then
  if ! git stash pop; then
    echo
    echo "WARNING: Stash pop had conflicts."
    echo "Your code is at latest origin/main, but local changes need manual resolution."
    exit 2
  fi
fi

echo
echo "==> Done"
git status --short
git log --oneline -3
