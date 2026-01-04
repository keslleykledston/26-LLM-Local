#!/bin/bash
set -e

REQ_FILE="/app/requirements.txt"
HASH_FILE="/home/appuser/.local/.requirements_hash"

if [ -f "$REQ_FILE" ]; then
  current_hash=$(sha256sum "$REQ_FILE" | awk '{print $1}')
  if [ ! -f "$HASH_FILE" ] || [ "$current_hash" != "$(cat "$HASH_FILE")" ]; then
    echo "📦 Installing Python dependencies..."
    pip install --no-cache-dir --user -r "$REQ_FILE"
    echo "$current_hash" > "$HASH_FILE"
  fi
fi

exec "$@"
