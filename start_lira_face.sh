#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
export LIRA_FACE_HOST="${LIRA_FACE_HOST:-0.0.0.0}"
export LIRA_FACE_PORT="${LIRA_FACE_PORT:-8787}"
export LIRA_FACE_AUTO_REPLY="${LIRA_FACE_AUTO_REPLY:-1}"
export LIRA_FACE_MODEL="${LIRA_FACE_MODEL:-grok-3}"
echo "Lira face supervisor — http://${LIRA_FACE_HOST}:${LIRA_FACE_PORT}/face.html"
echo "Face fast path AUTO_REPLY=${LIRA_FACE_AUTO_REPLY} MODEL=${LIRA_FACE_MODEL}"
exec python3 face_supervisor.py