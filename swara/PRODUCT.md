# Product

<!-- impeccable:product-schema 1 -->

## Platform

desktop app (Windows, macOS, Linux) built as a local web UI shown in a native window (pywebview), with a browser fallback.

## Stack

Python engine (FastAPI on 127.0.0.1) running open models: Kokoro (built-in voices), Chatterbox (cloning, voice conversion), faster-whisper (speech to text). Front end is plain HTML/CSS/JS in `web/`, no build step, no CDNs or web fonts.

## Users

Content and production teams in Indian media (promo producers, ad and narration teams, micro-drama and dubbing crews) and independent creators who currently pay for ElevenLabs-style subscriptions. They work at a desk, often late, with scripts in English and Hindi.

## Product Purpose

Turn scripts into natural speech, cast voices to characters, clone a voice from a short sample, re-voice a recording and transcribe audio, all offline on the user's own computer. Success: the user stops paying for a cloud voice subscription for day-to-day work.

## Positioning

A local, private, subscription-free voice studio. Not a copy of ElevenLabs: comparable features, its own identity (a dubbing studio's script desk).

## Capabilities and Constraints

- Everything runs offline after a one-time model download (about 6 GB).
- Speed depends on hardware; CPU-only cloning is roughly 8–10× slower than real time.
- Not included yet: dubbing/translation, sound effects, voice design from a text description.
- Cloning requires the user to confirm they have the speaker's permission; cloned audio carries Resemble AI's inaudible watermark.

## Brand Commitments

Name: Swara (स्वर, "voice / note"). Must not imitate ElevenLabs' visual identity.

## Accessibility & Inclusion

Keyboard reachable, visible focus, WCAG AA text contrast in light and dark, respects prefers-reduced-motion, Devanagari renders with system fonts.
