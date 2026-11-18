#!/usr/bin/env bash
# Voice Studio installer for macOS (also works on Linux).
set -euo pipefail
cd "$(dirname "$0")"
echo
echo "  ===  Voice Studio installer  ==="
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

echo "  Installing Voice Studio dependencies..."
"$VPY" -m pip install -r requirements.txt

echo
echo "  Downloading voice models (one time, about 4 GB)..."
"$VPY" run.py --prefetch

chmod +x start-mac.command 2>/dev/null || true
echo
echo "  Done. Double-click start-mac.command to open Voice Studio."
read -r -p "  Press Enter to close." _ || true
