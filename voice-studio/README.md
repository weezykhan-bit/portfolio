# Voice Studio

A local alternative to ElevenLabs. Type text, pick a voice or clone your own from a short recording, and get lifelike speech. Everything runs on your computer: no subscription, no per-character cost, and your scripts and voice samples never leave the machine.

- **Text to Speech**: up to 20,000 characters per generation. Long text is split at sentence and paragraph boundaries automatically and stitched back together with natural pauses.
- **Voice cloning**: upload or record 10–30 seconds of someone speaking and save it as a reusable voice. Cloned voices speak 23 languages, including Hindi.
- **28 built-in voices**: US English, UK English and Hindi, fast even without a GPU.
- **Voice library**: preview, rename and delete voices.
- **History**: every generation is saved locally, with playback, "reuse settings", and WAV/MP3 download.
- **Controls**: speed for built-in voices; expressiveness, pacing and variability for cloned voices; a seed to reproduce a take exactly.
- Light and dark mode. Works in any browser, including on a phone on the same network if you start it with `--host 0.0.0.0`.

## Install

You need **Python 3.10, 3.11 or 3.12** and about **10 GB of free disk** (libraries plus about 4 GB of models). The installer downloads everything once; after that the app works with no internet.

### Windows

1. Install Python 3.12 from [python.org](https://www.python.org/downloads/windows/). During setup, tick **"Add python.exe to PATH"**.
2. Double-click **`install-windows.bat`**. It detects an NVIDIA GPU and installs the right build, downloads the models, and puts a "Voice Studio" shortcut on your desktop.
3. Double-click **`start-windows.bat`** (or the shortcut). Your browser opens at `http://127.0.0.1:7860`.

### Mac

1. Install Python 3.12 from [python.org](https://www.python.org/downloads/macos/) or with `brew install python@3.12`.
2. Double-click **`install-mac.command`**. If macOS blocks it ("unidentified developer"), right-click it and choose **Open**, or run `bash install-mac.command` in Terminal.
3. Double-click **`start-mac.command`**. Your browser opens at `http://127.0.0.1:7860`.

Linux works with the same `install-mac.command` / `start-mac.command` scripts.

Keep the window that opens while you use the app; closing it stops Voice Studio.

## Hardware and speed

| Machine | Built-in voices | Cloned voices |
|---|---|---|
| NVIDIA GPU (6 GB+ VRAM) | Instant | About real time |
| Apple Silicon (M1–M4), 16 GB | ~2× faster than real time | Roughly 1–2× real time |
| CPU only (4 cores, measured) | 15 s of audio in ~11 s | 4 s of audio in ~39 s |

The app detects your hardware automatically and shows it in the sidebar.

## Getting a good clone

The clone copies everything in the sample, including noise, echo and microphone quality.

- 10–30 seconds of **one person** speaking naturally. Longer than 40 seconds is trimmed.
- No music, no background noise, no room echo. A quiet room and a phone held 20 cm away beats a laptop mic across the room.
- Record in the language and style you want out: a calm narration sample gives calm narration.
- Set **Language spoken** when saving, and pick the output language in the Text to Speech panel.

Only clone your own voice or voices you have explicit permission to use. Audio from the cloning model carries an inaudible watermark (Resemble AI's Perth) that identifies it as AI-generated.

## Settings explained

| Setting | Applies to | What it does |
|---|---|---|
| Speed | Built-in voices | 0.6× to 1.6× speaking rate |
| Expressiveness | Cloned voices | Higher is more emotional and dramatic; above ~0.8 can sound exaggerated |
| Pacing | Cloned voices | Lower gives slower, more deliberate delivery. Lower it when raising expressiveness |
| Variability | Cloned voices | Lower is more consistent between takes; higher is livelier but less predictable |
| Seed | All | Same text, voice, settings and seed produce the same audio |

## How it works

| Part | What it is |
|---|---|
| Built-in voices | [Kokoro-82M](https://huggingface.co/hexgrad/Kokoro-82M), Apache 2.0 |
| Voice cloning | [Chatterbox](https://github.com/resemble-ai/chatterbox) English and multilingual models by Resemble AI, MIT |
| Server | Python, FastAPI, listening on `127.0.0.1` only |
| Interface | Plain HTML/CSS/JS in `web/`, no build step, no external fonts or CDNs |

Both model licenses allow commercial use.

```
voice-studio/
  run.py                 launcher (python run.py --help)
  app/engines.py         model loading and generation
  app/textproc.py        sentence/paragraph chunking
  app/server.py          HTTP API and job queue
  app/store.py           saved voices and history
  web/                   the interface
  data/                  your voices and generated audio (created on first run)
```

Your data lives in `data/` next to the app. Back up that folder to keep your voices. Set `VOICE_STUDIO_DATA` to store it elsewhere.

### Local API

Other tools on your computer can use the same API the interface uses:

```bash
curl -X POST http://127.0.0.1:7860/api/generate \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello from the API.", "voice_id": "preset:af_heart"}'
# -> {"id": "<job>", "status": "queued", ...}
curl http://127.0.0.1:7860/api/jobs/<job>          # poll until "done"
curl -o out.mp3 "http://127.0.0.1:7860/api/history/<result.id>/audio?format=mp3"
```

`GET /api/voices` lists voice IDs. Cloned voices look like `clone:20261118-165513-763df1` and accept `"language": "hi"` and the other cloning settings.

## Limits

- Not a full ElevenLabs replacement: there's no speech-to-speech, dubbing or sound effects yet. Very expressive delivery (whispering, shouting) and strong accents are weaker than ElevenLabs.
- Cloning on a CPU-only machine is slow (roughly 8–10× slower than real time).
- Built-in voices cover English and Hindi. Other languages need a cloned voice.

## Troubleshooting

- **"Python was not found"**: install Python 3.12 and, on Windows, make sure "Add to PATH" was ticked.
- **First generation is slow**: the model loads into memory on first use (10–60 s). Later generations are faster.
- **Microphone recording doesn't start**: allow microphone access for `127.0.0.1` in your browser, or upload a file instead.
- **Port in use**: `start-windows.bat --port 7861` or `./start-mac.command --port 7861`.
