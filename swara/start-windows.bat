@echo off
title Swara
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo Swara is not installed yet. Run install-windows.bat first.
  pause
  exit /b 1
)
".venv\Scripts\python.exe" run.py %*
pause
