@echo off
title Lira Face — launcher
cd /d C:\project\lira-mark
echo Starting face server :8787
start "Lira Face Server" cmd /k python face_server.py
timeout /t 2 /nobreak >nul
echo Starting chat bridge Composer -^> face
start "Lira Chat Bridge" cmd /k python chat_face_bridge.py
echo.
echo Open: http://localhost:8787/face.html?mode=particles
echo Health: http://localhost:8787/api/health
echo Leave BOTH windows open.
pause