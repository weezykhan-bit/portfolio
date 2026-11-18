@echo off
setlocal
title Swara - Install
cd /d "%~dp0"
echo.
echo  ===  Swara installer (Windows)  ===
echo.

rem ---- find Python 3.10 - 3.12 ----
set "PY="
for %%V in (3.12 3.11 3.10) do (
  if not defined PY (
    py -%%V -c "import sys" >nul 2>&1 && set "PY=py -%%V"
  )
)
if not defined PY (
  python -c "import sys; sys.exit(0 if (3,10)<=sys.version_info[:2]<=(3,12) else 1)" >nul 2>&1 && set "PY=python"
)
if not defined PY (
  echo  Python 3.10, 3.11 or 3.12 was not found.
  echo  Install Python 3.12 from https://www.python.org/downloads/windows/
  echo  and tick "Add python.exe to PATH" during setup, then run this again.
  echo.
  pause
  exit /b 1
)
echo  Using %PY%

if not exist ".venv\Scripts\python.exe" (
  echo  Creating virtual environment...
  %PY% -m venv .venv || goto :fail
)
set "VPY=.venv\Scripts\python.exe"
"%VPY%" -m pip install --upgrade pip wheel >nul

rem ---- PyTorch: CUDA build if an NVIDIA GPU is present ----
where nvidia-smi >nul 2>&1
if %errorlevel%==0 (
  echo  NVIDIA GPU detected - installing GPU build of PyTorch ^(about 2.5 GB^)...
  "%VPY%" -m pip install torch==2.6.0 torchaudio==2.6.0 --index-url https://download.pytorch.org/whl/cu124 || goto :fail
) else (
  echo  No NVIDIA GPU found - installing CPU build of PyTorch...
  "%VPY%" -m pip install torch==2.6.0 torchaudio==2.6.0 || goto :fail
)

echo  Installing Swara dependencies...
"%VPY%" -m pip install -r requirements.txt || goto :fail

echo.
echo  Downloading voice and transcription models (one time, about 6 GB)...
"%VPY%" run.py --prefetch || goto :fail

rem ---- desktop + Start menu shortcuts that open Swara without a console window ----
set "TARGET=%~dp0.venv\Scripts\pythonw.exe"
for %%L in ("Desktop" "Programs") do (
  powershell -NoProfile -Command "$d=[Environment]::GetFolderPath('%%~L'); $s=(New-Object -ComObject WScript.Shell).CreateShortcut($d+'\Swara.lnk'); $s.TargetPath='%TARGET%'; $s.Arguments='\"%~dp0run.py\"'; $s.WorkingDirectory='%~dp0'; $s.Description='Swara offline voice studio'; $s.Save()" >nul 2>&1
)

echo.
echo  Done. Open Swara from the desktop or Start menu shortcut.
echo  (start-windows.bat also works and keeps a log window open.)
echo.
pause
exit /b 0

:fail
echo.
echo  Installation failed. Scroll up to see the error.
pause
exit /b 1
