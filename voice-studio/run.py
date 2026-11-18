"""Start Local Voice Studio and open it in the browser.

    python run.py              # opens http://127.0.0.1:7860
    python run.py --port 8000 --no-browser
    python run.py --prefetch   # download all models now (needs internet once)
"""
from __future__ import annotations

import argparse
import logging
import os
import sys
import threading
import time
import warnings
import webbrowser

# Kokoro falls back to CPU for ops Apple's GPU backend lacks.
os.environ.setdefault("PYTORCH_ENABLE_MPS_FALLBACK", "1")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
warnings.filterwarnings("ignore")


def _offline_if_cached() -> None:
    """Once models are downloaded, stop the libraries from phoning home."""
    try:
        from huggingface_hub import try_to_load_from_cache

        needed = [
            ("hexgrad/Kokoro-82M", "kokoro-v1_0.pth"),
            ("ResembleAI/chatterbox", "t3_cfg.safetensors"),
        ]
        if all(isinstance(try_to_load_from_cache(r, f), str) for r, f in needed):
            os.environ.setdefault("HF_HUB_OFFLINE", "1")
    except Exception:
        pass


def main() -> None:
    ap = argparse.ArgumentParser(description="Local Voice Studio")
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=int(os.environ.get("VOICE_STUDIO_PORT", 7860)))
    ap.add_argument("--no-browser", action="store_true")
    ap.add_argument("--prefetch", action="store_true", help="download every model, then exit")
    ap.add_argument("--skip-multilingual", action="store_true", help="with --prefetch: skip the 23-language cloning model")
    args = ap.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(message)s", datefmt="%H:%M:%S")

    if args.prefetch:
        from app.engines import EngineManager

        em = EngineManager()
        print(f"Device: {em.device}")
        steps = ["kokoro", "clone_en"] + ([] if args.skip_multilingual else ["clone_multi"])
        for s in steps:
            print(f"Downloading / loading: {s} ...", flush=True)
            em.warm([s])
        print("All models are downloaded. The app now works offline.")
        return

    _offline_if_cached()
    import uvicorn

    url = f"http://{args.host}:{args.port}"
    if not args.no_browser:
        threading.Thread(target=lambda: (time.sleep(2.5), webbrowser.open(url)), daemon=True).start()
    print(f"\n  Local Voice Studio is running at {url}\n  Keep this window open. Press Ctrl+C to stop.\n", flush=True)
    uvicorn.run("app.server:app", host=args.host, port=args.port, log_level="warning")


if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    main()
