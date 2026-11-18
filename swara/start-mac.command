#!/usr/bin/env bash
cd "$(dirname "$0")"
if [ ! -x .venv/bin/python ]; then
  echo "Swara is not installed yet. Run install-mac.command first."
  read -r -p "Press Enter to close." _; exit 1
fi
exec .venv/bin/python run.py "$@"
