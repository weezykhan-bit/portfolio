# Review: Offside Stories Ep 001 (Jamie Vardy)

Output: offside-stories-ep001-jamie-vardy.mp4, 1080×1920, 30 fps, 60.0 s, H.264/AAC, 13 MB. Cover: offside-stories-ep001-cover.png.
Rebuild: `python3 build.py` (scenes + captions are generated from vo/script.json), then render.

## Calls made
- Motion graphics only (no credits for AI footage). Carrier: a yellow dot (the player) climbing the English pyramid.
- Narration is now English (v2, `-en.mp4`); the Hinglish script is kept in vo/script-hinglish.json.
- Script fix: "No fancy academy" → "16 saal ki umar mein Sheffield Wednesday ne release kar diya" (he was in Wednesday's academy).
- Voice: local Kokoro `bm_george` (British male), English, mostly at natural speed (1.0–1.12×, two short lines at 1.25×). Each English line starts where its Hinglish line did, so the graphics stay in sync.
- Subtitle word timing is estimated by word length inside each phrase clip (no transcriber reachable), so a word can light up up to ~0.2 s early or late; phrase starts are exact.

## Measured vs not
- check: passes with the Reels safe zone. Kept: "SEASON 2015–16" holds 1.0 s (scene ends on the flood).
- Mix: −12.3 LUFS, −1.0 dBTP, no clipping. Not heard by anyone: pronunciation of the Hinglish lines is unverified.
- No music bed yet: HeyGen sign-in, huggingface (MusicGen) and every free music site are blocked by this environment's network.

## Weakest parts
- The voice: Kokoro is clear but light, not a deep baritone.
- Scenes 2 and 3 are type-heavy; real reenactment footage would lift them most.
