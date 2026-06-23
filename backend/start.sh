#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
PORT="${PORT:-8000}"
exec gunicorn app.main:app \
  -w 2 \
  -k uvicorn.workers.UvicornWorker \
  -b "0.0.0.0:${PORT}" \
  --timeout 120 \
  --graceful-timeout 30 \
  --access-logfile - \
  --error-logfile -
