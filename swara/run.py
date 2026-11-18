"""Start Swara.

    python run.py              # opens Swara in its own app window
    python run.py --browser    # use your web browser instead
    python run.py --prefetch   # download every model now (needs internet once)
"""
from __future__ import annotations

import argparse
import logging
import os
import socket
import sys
import threading
import time
import warnings

os.environ.setdefault("PYTORCH_ENABLE_MPS_FALLBACK", "1")  # Apple GPU: fall back to CPU for missing ops
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
os.environ.setdefault("HF_HUB_DISABLE_TELEMETRY", "1")
warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

MODEL_FILES = [
    ("hexgrad/Kokoro-82M", "kokoro-v1_0.pth"),
    ("ResembleAI/chatterbox", "t3_cfg.safetensors"),
    ("ResembleAI/chatterbox", "s3gen.pt"),
    ("Systran/faster-whisper-small", "model.bin"),
    ("mobiuslabsgmbh/faster-whisper-large-v3-turbo", "model.bin"),
]


def _offline_if_cached() -> None:
    """Once every model is downloaded, stop the libraries from checking the internet."""
    try:
        from huggingface_hub import try_to_load_from_cache

        if all(isinstance(try_to_load_from_cache(r, f), str) for r, f in MODEL_FILES):
            os.environ.setdefault("HF_HUB_OFFLINE", "1")
    except Exception:
        pass


def _free_port(preferred: int) -> int:
    for port in [preferred] + list(range(preferred + 1, preferred + 40)):
        with socket.socket() as s:
            try:
                s.bind(("127.0.0.1", port))
                return port
            except OSError:
                continue
    return preferred


def _start_server(host: str, port: int):
    import uvicorn

    server = uvicorn.Server(uvicorn.Config("app.server:app", host=host, port=port, log_level="warning"))
    t = threading.Thread(target=server.run, daemon=True, name="swara-server")
    t.start()
    for _ in range(600):  # model libraries take a few seconds to import
        if server.started:
            break
        time.sleep(0.1)
    return server


class Bridge:
    """Functions the page can call when it runs inside the desktop window
    (web views can't save downloads on their own)."""

    def __init__(self, base: str):
        self.base = base
        self.window = None

    def save_file(self, path: str, suggested: str) -> str:
        import urllib.request

        import webview

        ext = suggested.rsplit(".", 1)[-1].upper() if "." in suggested else "File"
        target = self.window.create_file_dialog(
            webview.SAVE_DIALOG, save_filename=suggested, file_types=(f"{ext} file (*.{ext.lower()})", "All files (*.*)"),
        )
        if not target:
            return ""
        target = target if isinstance(target, str) else target[0]
        with urllib.request.urlopen(self.base + path, timeout=600) as r, open(target, "wb") as fh:
            fh.write(r.read())
        return target

    def open_in_browser(self) -> None:
        import webbrowser

        webbrowser.open(self.base)


def main() -> None:
    ap = argparse.ArgumentParser(description="Swara: offline voice studio")
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=int(os.environ.get("SWARA_PORT", 7860)))
    ap.add_argument("--browser", action="store_true", help="open in your web browser instead of an app window")
    ap.add_argument("--no-browser", action="store_true", help="only start the engine (no window, no browser)")
    ap.add_argument("--prefetch", action="store_true", help="download every model, then exit")
    ap.add_argument("--skip-multilingual", action="store_true", help="with --prefetch: skip the 23-language cloning model")
    args = ap.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(message)s", datefmt="%H:%M:%S")
    for noisy in ("httpx", "huggingface_hub", "urllib3", "faster_whisper"):
        logging.getLogger(noisy).setLevel(logging.WARNING)

    if args.prefetch:
        from app.engines import EngineManager

        em = EngineManager()
        print(f"Device: {em.device}")
        steps = ["kokoro", "clone_en"] + ([] if args.skip_multilingual else ["clone_multi"]) + ["changer", "whisper", "whisper_accurate"]
        for s in steps:
            print(f"  Downloading / loading: {s} ...", flush=True)
            em.warm([s])
        print("All models are downloaded. Swara now works offline.")
        return

    _offline_if_cached()
    port = _free_port(args.port) if args.host == "127.0.0.1" else args.port
    url = f"http://{'127.0.0.1' if args.host == '0.0.0.0' else args.host}:{port}"

    use_window = not (args.browser or args.no_browser)
    webview = None
    if use_window:
        try:
            import webview  # pywebview
        except Exception:
            print("App window unavailable (pywebview not installed); opening your browser instead.")
            use_window = False

    print(f"\n  Swara is starting at {url} ...", flush=True)
    server = _start_server(args.host, port)

    if use_window:
        bridge = Bridge(url)
        try:
            bridge.window = webview.create_window(
                "Swara", url, js_api=bridge, width=1380, height=900, min_size=(940, 620), background_color="#13161C",
            )
            webview.start(private_mode=False)
            server.should_exit = True
            return
        except Exception as e:  # no GUI toolkit available, e.g. a bare Linux server
            print(f"App window failed ({e}); opening your browser instead.")

    if not args.no_browser:
        import webbrowser

        webbrowser.open(url)
    print(f"  Swara is running at {url}\n  Keep this window open. Press Ctrl+C to stop.\n", flush=True)
    try:
        while not server.should_exit:
            time.sleep(0.5)
    except KeyboardInterrupt:
        server.should_exit = True


if __name__ == "__main__":
    main()
