#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
export LIRA_FACE_HOST="${LIRA_FACE_HOST:-0.0.0.0}"
export LIRA_FACE_PORT="${LIRA_FACE_PORT:-8787}"
echo "Lira face supervisor — http://${LIRA_FACE_HOST}:${LIRA_FACE_PORT}/face.html"
exec python3 face_supervisor.py