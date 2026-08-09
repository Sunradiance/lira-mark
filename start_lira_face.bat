@echo off
title Lira Face — supervisor
cd /d "%~dp0"
set LIRA_FACE_HOST=0.0.0.0
set LIRA_FACE_PORT=8787
rem no-lag: auto-reply on face (full model). Primary-only: set LIRA_FACE_PRIMARY_ONLY=1
set LIRA_FACE_AUTO_REPLY=1
set LIRA_FACE_MODEL=grok-3
echo Starting face supervisor (auto-restart on crash)
echo Face fast path: AUTO_REPLY on model=%LIRA_FACE_MODEL%
echo Copy lira_host.json.example to lira_host.json for new host URL
echo Open: http://localhost:8787/face.html
echo Leave THIS window open.
python face_supervisor.py
pause