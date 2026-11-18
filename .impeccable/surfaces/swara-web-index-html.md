---
version: 1
slug: "swara-web-index-html"
primary_target: "swara/web/index.html"
related_targets: []
---

# Swara app shell

Scope: the whole Swara desktop app UI (Text to Speech, Studio, Voice Changer, Speech to Text, Voices, History, Pronunciations). Mode: Operate.
Audience: content and production teams in Indian media (promos, ad reads, micro-drama, narration, dubbing) working at a desk, often late, in an edit suite. Job: turn scripts into voice, cast voices to characters, re-voice and transcribe recordings, offline.
Constraints: offline (no CDNs, no web fonts fetched), runs in a pywebview window and in browsers, light and dark, phone width usable. Must not imitate ElevenLabs' look.

## Direction contract

THESIS: Swara is a dubbing studio's script desk: the script is the work surface and every line is visibly cast to a voice. It refuses the category default of a white SaaS dashboard with one accent and a text box.
OWN-WORLD: A dark booth shell (deep ink slate rail and player) around bright white script pages on a cool grey desk. Highlighter yellow is the brand accent and primary action; a fixed highlighter cast set (yellow, pink, green, blue, orange, violet) marks speakers. System sans for UI, system mono for timecodes and cue labels.
STORY: The user sees their script, sees who speaks each line, renders it, hears it, fixes one line, exports. Trust comes from status on every line.
FIRST VIEWPORT: Left dark rail with the six tools. Main: a white script page (editor) taking two thirds, a cast panel on the right with the voice, its settings and a highlighter-yellow Generate button at the bottom. Player docked at the bottom in the booth colour.
FORM: Dubbing script sheet, candidate 1 of my ordered list (user chose it over assigned candidate 7). seed:3a5eb9fd4a4685a7. Signature move: each script line's speaker cue is swiped in that character's highlighter colour, with mono timecodes in the margin, as on a dubbing cue sheet. (Built as cue swipes rather than left-edge bands because the craft floor refuses coloured side stripes on list rows.)
FINISH: unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, DESIGN.md, and every shipping raster carrying its provenance
