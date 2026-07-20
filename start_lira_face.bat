@echo off
title Lira Face — supervisor
cd /d "%~dp0"
set LIRA_FACE_HOST=0.0.0.0
set LIRA_FACE_PORT=8787
echo Starting face supervisor (auto-restart on crash)
echo Copy lira_host.json.example to lira_host.json for new host URL
echo Open: http://localhost:8787/face.html
echo Leave THIS window open.
python face_supervisor.py
pause