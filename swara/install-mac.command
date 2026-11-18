#!/usr/bin/env bash
# Swara installer for macOS (also works on Linux).
set -euo pipefail
cd "$(dirname "$0")"
echo
echo "  ===  Swara installer  ==="
echo

PY=""
for c in python3.12 python3.11 python3.10 python3; do
  if command -v "$c" >/dev/null 2>&1 && "$c" -c 'import sys; sys.exit(0 if (3,10)<=sys.version_info[:2]<=(3,12) else 1)' 2>/dev/null; then
    PY="$c"; break
  fi
done
if [ -z "$PY" ]; then
  echo "  Python 3.10–3.12 was not found."
  echo "  Install Python 3.12 from https://www.python.org/downloads/macos/"
  echo "  (or: brew install python@3.12), then run this again."
  read -r -p "  Press Enter to close." _; exit 1
fi
echo "  Using $PY ($($PY --version))"

[ -x .venv/bin/python ] || "$PY" -m venv .venv
VPY=.venv/bin/python
"$VPY" -m pip install --upgrade pip wheel >/dev/null

if [ "$(uname)" = "Linux" ] && command -v nvidia-smi >/dev/null 2>&1; then
  echo "  NVIDIA GPU detected - installing GPU build of PyTorch..."
  "$VPY" -m pip install torch==2.6.0 torchaudio==2.6.0 --index-url https://download.pytorch.org/whl/cu124
else
  # On Apple Silicon the standard build includes the Metal (MPS) GPU backend.
  "$VPY" -m pip install torch==2.6.0 torchaudio==2.6.0
fi

echo "  Installing Swara dependencies..."
"$VPY" -m pip install -r requirements.txt

echo
echo "  Downloading voice and transcription models (one time, about 6 GB)..."
"$VPY" run.py --prefetch

chmod +x start-mac.command 2>/dev/null || true

# A double-clickable Swara.app (no Terminal window). Lives next to this script;
# drag it to the Dock or Applications.
if [ "$(uname)" = "Darwin" ]; then
  HERE="$(pwd)"
  APP="$HERE/Swara.app"
  mkdir -p "$APP/Contents/MacOS" "$APP/Contents/Resources"
  cat > "$APP/Contents/MacOS/Swara" <<SH
#!/bin/bash
cd "$HERE"
exec "$HERE/.venv/bin/python" "$HERE/run.py" >> "$HERE/data/swara.log" 2>&1
SH
  chmod +x "$APP/Contents/MacOS/Swara"
  cat > "$APP/Contents/Info.plist" <<PL
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>CFBundleName</key><string>Swara</string>
  <key>CFBundleDisplayName</key><string>Swara</string>
  <key>CFBundleIdentifier</key><string>app.swara.local</string>
  <key>CFBundleExecutable</key><string>Swara</string>
  <key>CFBundlePackageType</key><string>APPL</string>
  <key>CFBundleShortVersionString</key><string>0.2.0</string>
  <key>NSMicrophoneUsageDescription</key><string>Swara records your voice to clone it or change it. Audio never leaves this Mac.</string>
  <key>NSHighResolutionCapable</key><true/>
</dict></plist>
PL
  mkdir -p data
  echo "  Created Swara.app. Double-click it to open Swara (drag it to your Dock)."
fi

echo
echo "  Done. Open Swara.app (Mac) or double-click start-mac.command."
read -r -p "  Press Enter to close." _ || true
