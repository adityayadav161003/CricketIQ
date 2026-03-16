#!/usr/bin/env sh
# ─────────────────────────────────────────────────────────────────
# CricketIQ Backend — Production Startup Script
# Used by Docker container and Render / Railway / Fly.io deployments.
#
# Environment variables consumed:
#   PORT           (default 8000)
#   WORKERS        (default 2 — adjust for your dyno/instance size)
#   LOG_LEVEL      (default info)
# ─────────────────────────────────────────────────────────────────

set -e

PORT="${PORT:-8000}"
WORKERS="${WORKERS:-2}"
LOG_LEVEL="${LOG_LEVEL:-info}"

echo "Starting CricketIQ API on port $PORT with $WORKERS worker(s)..."

exec uvicorn backend.api.main:app \
  --host 0.0.0.0 \
  --port "$PORT" \
  --workers "$WORKERS" \
  --log-level "$LOG_LEVEL" \
  --no-access-log
