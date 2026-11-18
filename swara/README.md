# Swara

**Swara** (स्वर, "voice") is an offline voice studio for Windows and Mac. It does the everyday jobs people pay ElevenLabs for, on your own computer: no subscription, no per-character cost, and your scripts and recordings never leave the machine.

| Tool | What it does |
|---|---|
| **Text to Speech** | Paste up to 20,000 characters, pick a voice, generate. Long text is split at sentences and paragraphs and joined back with natural pauses. |
| **Studio** | Long-form projects with a cast: audiobooks, ads, promos, dialogue. Each line has a speaker; each speaker is cast to a voice. Edit one line and only that line re-renders. Export the whole project as MP3 or WAV. |
| **Voice Changer** | Record or upload yourself speaking; Swara keeps your words, timing and emotion and changes the voice. |
| **Speech to Text** | Transcribe audio or video (MP3, WAV, M4A, MP4, MOV) into text and SRT/VTT subtitles. The language is detected automatically (Hindi and English included), or you can set it. Send a transcript straight to Text to Speech or Studio. |
| **Voices** | Clone a voice from 10–30 seconds of speech (upload or record), or use 28 built-in voices in US English, UK English and Hindi. Cloned voices speak 23 languages. |
| **History** | Everything you generate is kept locally, with playback and WAV/MP3 download. |
| **Pronunciations** | Teach every voice how to say brand names, people's names and abbreviations ("OTT" → "O T T"). |

Light and dark themes. Opens in its own app window.

## Install

You need **Python 3.10, 3.11 or 3.12** and about **12 GB free disk** (libraries plus about 6 GB of models). The installer downloads everything once; after that Swara works with no internet.

### Windows

1. Install Python 3.12 from [python.org](https://www.python.org/downloads/windows/). During setup, tick **"Add python.exe to PATH"**.
2. Double-click **`install-windows.bat`**. It detects an NVIDIA graphics card and installs the matching build, downloads the models, and adds a **Swara** shortcut to your desktop and Start menu.
3. Open **Swara** from the shortcut. It opens in its own window with no console.

### Mac

1. Install Python 3.12 from [python.org](https://www.python.org/downloads/macos/) or with `brew install python@3.12`.
2. Double-click **`install-mac.command`**. If macOS blocks it, right-click it and choose **Open**, or run `bash install-mac.command` in Terminal.
3. The installer creates **`Swara.app`** next to it. Double-click it, or drag it to your Dock.

Linux uses the same `install-mac.command`, and you start it with `start-mac.command`.

If the app window can't open on your system, Swara opens in your web browser instead. Run `start-windows.bat --browser` or `./start-mac.command --browser` to choose that yourself.

## Writing scripts for Studio

Paste a script when you create a project. Start a line with a name and a colon and that character joins the cast:

```
NARRATOR: The train pulled into Mumbai Central just after midnight.
RIYA: Did you bring the tickets?
ARJUN: They're in my bag. Relax.
The platform slowly emptied around them.
```

Untagged lines go to the narrator. In the project, cast a voice for each character, then **Render**. Edited lines show **Edited** and only those re-render. In the sheet, press Enter at the end of a line to add the next one for the same speaker.

## Hardware and speed

| Machine | Built-in voices | Cloned voices / Voice Changer | Transcription (Fast) |
|---|---|---|---|
| NVIDIA GPU (6 GB+) | Instant | About real time | Many times faster than real time |
| Apple Silicon (M1–M4) | Faster than real time | Roughly 1–2× real time | Faster than real time |
| CPU only (4 cores, measured) | 15 s of audio in ~11 s | 4 s of audio in ~39 s; 11 s converted in ~28 s | 14 s transcribed in ~6 s |

The sidebar shows which hardware Swara is using.

## Getting a good clone

- 10–30 seconds of **one person** speaking naturally. Longer than 40 seconds is trimmed.
- No music, background noise or room echo. A quiet room and a phone held 20 cm away beats a laptop microphone across the room.
- Record in the style you want out: a calm narration sample gives calm narration.

Only clone your own voice or voices you have permission to use; Swara asks you to confirm this. Audio from the cloning and voice-changing models carries Resemble AI's inaudible watermark identifying it as AI-generated.

## Settings

| Setting | Applies to | What it does |
|---|---|---|
| Speed | Built-in voices | 0.6× to 1.6× speaking rate |
| Expressiveness | Cloned voices | Higher is more emotional; above ~0.8 can sound exaggerated |
| Pacing | Cloned voices | Lower is slower and more deliberate; lower it when raising expressiveness |
| Variation | Cloned voices | Lower is more consistent between takes |
| Seed | Text to Speech | Same text, voice, settings and seed give the same audio |
| Accuracy | Speech to Text | Fast (Whisper small) or Accurate (Whisper large-v3-turbo; better for accents, Hindi, noise) |

## How it's built

| Part | What it is | License |
|---|---|---|
| Built-in voices | [Kokoro-82M](https://huggingface.co/hexgrad/Kokoro-82M) | Apache 2.0 |
| Cloning and Voice Changer | [Chatterbox](https://github.com/resemble-ai/chatterbox) (English, multilingual and voice-conversion models), Resemble AI | MIT |
| Speech to Text | [faster-whisper](https://github.com/SYSTRAN/faster-whisper) with OpenAI Whisper weights | MIT |
| Engine | Python, FastAPI, on `127.0.0.1` only | |
| App window | pywebview (Edge WebView2 on Windows, WebKit on Mac) | BSD |
| Interface | Plain HTML/CSS/JS in `web/`; no build step, web fonts or CDNs | |

All model licenses allow commercial use.

```
swara/
  run.py              launcher: app window, --browser, --prefetch
  app/engines.py      model loading, speech, voice changer, transcription
  app/server.py       local API and job queue
  app/store.py        voices, history, Studio projects, transcripts
  app/lexicon.py      pronunciation dictionary
  web/                the interface (js/ holds one file per tool)
  data/               your voices, projects and audio (created on first run)
```

Back up `data/` to keep your voices and projects. Set `SWARA_DATA` to store them elsewhere.

### Local API

Other tools on your computer can use the same API as the interface:

```bash
curl -X POST http://127.0.0.1:7860/api/generate -H "Content-Type: application/json" \
  -d '{"text": "Hello from the API.", "voice_id": "preset:af_heart"}'
curl http://127.0.0.1:7860/api/jobs/<id>                      # poll until "done"
curl -o out.mp3 "http://127.0.0.1:7860/api/history/<result.id>/audio?format=mp3"
```

Other endpoints: `/api/voices`, `/api/changer`, `/api/transcribe`, `/api/transcripts/<id>/export?format=srt`, `/api/projects`, `/api/projects/<id>/render`, `/api/projects/<id>/export?format=mp3`, `/api/pronunciations`.

## Not included yet

- Dubbing (translate and re-voice a video), sound effects, and designing a voice from a text description.
- Built-in voices cover English and Hindi only; other languages need a cloned voice.
- Very expressive delivery (whispering, shouting) is weaker than ElevenLabs.

## Troubleshooting

- **"Python was not found"**: install Python 3.12; on Windows make sure "Add to PATH" was ticked.
- **The first generation is slow**: each model loads into memory on first use (10–60 s).
- **Recording doesn't work in the app window**: Swara offers to open in your browser, where recording works. Uploading a file always works.
- **Port in use**: Swara picks the next free port automatically.
