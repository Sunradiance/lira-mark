@echo off
title Lira Face Server :8787
cd /d C:\project\lira-mark
echo Starting face server on http://localhost:8787/face.html?mode=particles
python face_server.py
pause