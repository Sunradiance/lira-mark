@echo off
title Lira Holo FULL STACK
cd /d C:\project\lira-mark
set LIRA_FACE_AUTO_REPLY=1
set LIRA_FACE_PRIMARY_ONLY=0
set LIRA_FACE_MODEL=grok-3

echo Killing old face processes...
for /f "tokens=2 delims=," %%p in ('tasklist /FI "IMAGENAME eq python.exe" /FO CSV /NH') do (
  wmic process where "ProcessId=%%~p" get CommandLine 2>nul | findstr /i "face_server face_inbox chat_face_bridge face_supervisor" >nul && taskkill /F /PID %%~p >nul 2>&1
)

REM Prefer real Python 3.12 on new PC; fall back to Python314 if present
set "PY=C:\Users\Tilen\AppData\Local\Programs\Python\Python312\python.exe"
if not exist "%PY%" set "PY=C:\Python314\python.exe"
if not exist "%PY%" set "PY=python"

echo Starting face_server with %PY%...
start "LiraFaceServer" /MIN "%PY%" face_server.py
timeout /t 3 /nobreak >nul

echo Starting inbox daemon...
start "LiraFaceInbox" /MIN "%PY%" face_inbox_daemon.py
timeout /t 1 /nobreak >nul

echo Starting bridge...
start "LiraFaceBridge" /MIN "%PY%" chat_face_bridge.py
timeout /t 1 /nobreak >nul

echo.
echo Open: http://127.0.0.1:8787/face.html
echo Health: http://127.0.0.1:8787/api/health
start http://127.0.0.1:8787/face.html
echo.
echo Leave the LiraFace* windows minimized. Close THIS window anytime.
pause
