---
name: Swara
description: An offline voice studio laid out like a dubbing studio's script desk.
colors:
  booth: "#191c22"
  booth-2: "#22262e"
  booth-3: "#2c313b"
  booth-line: "#343a45"
  booth-text: "#ebe9e4"
  booth-muted: "#a4a9b4"
  desk: "#e9eaee"
  paper: "#ffffff"
  paper-2: "#f5f5f7"
  rule: "#e1e2e7"
  rule-strong: "#c9cbd3"
  ink: "#1b1d22"
  ink-2: "#4a4e58"
  ink-3: "#5f6470"
  highlighter: "#ffd83d"
  highlighter-deep: "#f2c200"
  highlighter-wash: "#fff3b8"
  cast-pink: "#ff9cc2"
  cast-green: "#7fe0a6"
  cast-blue: "#84c8ff"
  cast-orange: "#ffb661"
  cast-violet: "#c9adff"
  danger: "#c4312b"
  ok: "#1d7f55"
  warn: "#9a6400"
typography:
  title:
    fontFamily: "system-ui, -apple-system, Segoe UI, Roboto, Noto Sans, Noto Sans Devanagari, sans-serif"
    fontSize: "22px"
    fontWeight: 680
    lineHeight: 1.25
    letterSpacing: "-0.015em"
  heading:
    fontFamily: "system-ui, -apple-system, Segoe UI, Roboto, Noto Sans, Noto Sans Devanagari, sans-serif"
    fontSize: "15px"
    fontWeight: 650
    lineHeight: 1.4
  body:
    fontFamily: "system-ui, -apple-system, Segoe UI, Roboto, Noto Sans, Noto Sans Devanagari, sans-serif"
    fontSize: "14.5px"
    fontWeight: 400
    lineHeight: 1.5
  script:
    fontFamily: "system-ui, -apple-system, Segoe UI, Roboto, Noto Sans, Noto Sans Devanagari, sans-serif"
    fontSize: "17px"
    fontWeight: 400
    lineHeight: 1.75
  cue:
    fontFamily: "ui-monospace, SF Mono, Cascadia Mono, Menlo, Consolas, monospace"
    fontSize: "11.5px"
    fontWeight: 600
    lineHeight: 1
    letterSpacing: "0.06em"
  timecode:
    fontFamily: "ui-monospace, SF Mono, Cascadia Mono, Menlo, Consolas, monospace"
    fontSize: "12px"
    fontWeight: 400
    lineHeight: 1.5
rounded:
  cue: "3px 6px 4px 7px"
  sm: "7px"
  control: "9px"
  md: "10px"
  lg: "14px"
  pill: "99px"
spacing:
  xs: "4px"
  sm: "8px"
  md: "12px"
  lg: "18px"
  xl: "30px"
components:
  button-primary:
    backgroundColor: "{colors.highlighter}"
    textColor: "{colors.ink}"
    rounded: "{rounded.control}"
    height: "36px"
    padding: "0 14px"
  button-primary-hover:
    backgroundColor: "{colors.highlighter-deep}"
  button-dark:
    backgroundColor: "{colors.booth}"
    textColor: "{colors.booth-text}"
    rounded: "{rounded.control}"
    height: "36px"
  button-secondary:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.ink}"
    rounded: "{rounded.control}"
    height: "36px"
  input:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.ink}"
    rounded: "{rounded.control}"
    height: "38px"
    padding: "0 12px"
  cue:
    backgroundColor: "{colors.highlighter}"
    textColor: "{colors.ink}"
    typography: "{typography.cue}"
    rounded: "{rounded.cue}"
    padding: "5px 8px 4px"
  nav-item-active:
    backgroundColor: "{colors.booth-3}"
    textColor: "{colors.booth-text}"
    rounded: "{rounded.control}"
---

# Design System: Swara

## Overview

Swara is a dubbing studio's script desk. A dark booth (the left rail and the player) frames bright white script pages laid on a cool grey desk. The script is always the work surface, and every line visibly belongs to a speaker: its cue is swiped in that character's highlighter colour, the way voice actors mark their parts on a dubbing sheet, with mono timecodes in the margin.

It is a working tool (Operate mode): standard controls, dense where the task is dense, one signature move. Colour does jobs (the brand action, cast identity, line state), never decoration. Light and dark themes share the same structure; in dark, the desk and paper drop to slate while the booth stays darkest.

## Colors

### Primary
Highlighter yellow (`highlighter`) is the brand colour and the primary action: Generate, Save, Clone, the active nav icon, the player's play button and played waveform. Its deeper tone (`highlighter-deep`) is hover and the focus ring.

### Secondary
The cast set is a fixed highlighter palette assigned to characters in cast order: yellow, `cast-pink`, `cast-green`, `cast-blue`, `cast-orange`, `cast-violet`. A cast colour appears only on cues and as a faint wash on the hovered line.

### Neutral
Booth tones (`booth` to `booth-3`, `booth-line`, `booth-text`, `booth-muted`) belong to the shell only: rail, player, toasts. Desk (`desk`), paper (`paper`, `paper-2`), rules and ink tones carry the work area.

### Named Rules
- **The Highlighter Rule.** Yellow means "do this" or "this is yours". It is never a background for large areas and never decoration.
- **Cast colour is identity.** A character keeps one colour everywhere in a project. Voice avatars use their own small label colour and never a cast colour.
- **State colours sit on paper.** `ok` (ready), `warn` (edited, needs re-render), `danger` (errors, delete) appear as small washed labels, not filled bars.

## Typography

One system sans for everything people read and click; the system mono for cues, timecodes, durations and counts. No web fonts: the app runs offline and must render Devanagari with the system's own faces.

### Hierarchy
- **Title** (22px / 680): view titles.
- **Heading** (15px / 650): section and panel heads.
- **Body** (14.5px / 400): UI text.
- **Script** (17px / 1.75): the Text to Speech page; Studio lines use 15.5px.
- **Cue** (mono 11.5px / 600, uppercase, 0.06em): speaker cues and column heads.
- **Timecode** (mono 12px, tabular figures): times, durations, counters.

## Layout

A 228px booth rail on the left; the work area scrolls on the desk. Text to Speech is a script page (flexible) beside a 340px cast panel; Studio is a cue sheet (flexible) beside a 300px cast-and-project column. The player docks to the bottom of the work area. Below 1080px side panels stack under the page; below 760px the rail becomes a top icon bar and sheet rows reflow to cue above line.

## Elevation & Depth

Paper sits on the desk with a soft two-layer shadow (`shadow-1`); hover on project cards lifts to `shadow-2`; dialogs float on `shadow-3` over a dimmed booth scrim. No hard offset shadows, no glows.

## Shapes

Controls are 9px rounded; panels 14px; badges and chips pill-shaped. The cue is the one irregular shape (3/6/4/7px corners, -0.6° tilt) so it reads as a hand-drawn highlighter swipe rather than a tag.

## Components

### Buttons
Primary is highlighter yellow with ink text; dark buttons (booth) are for the main secondary action in a toolbar (Export, Send to Studio); secondary is paper with a strong rule. All are 36px high (30px small, 48px for the main Generate/Change/Transcribe action).

### Chips
Pill outlines on paper for sample scripts; badges are 20px pills on `paper-2`.

### Cards / Containers
White paper panels with a 1px rule and `shadow-1`. Lists (history, transcripts, pronunciations) are one paper sheet with ruled rows, not separate cards.

### Inputs / Fields
38px, 9px rounded, strong rule border; focus darkens the border and adds a highlighter-tinted 3px ring.

### Navigation
Booth rail: muted items, a `booth-3` fill and yellow icon for the active tool, a count for saved voices, the live job queue and device at the foot.

### Cue sheet (signature)
Studio rows: timecode | cue | line | take. The cue is a highlighter swipe in the character's colour holding a hidden native select; the take column shows a state label (Ready, Edited, New, Rendering), play, new take, and a menu. Timecodes appear once every earlier line is rendered.

### Voice disc
A dark disc with a small coloured label and centre hole identifies a voice; cloned voices carry a microphone badge.

## Do's and Don'ts

### Do:
- Show who speaks every line and whether it is rendered.
- Keep yellow for the primary action and the active state.
- Use mono only for cues, times, durations and counts.
- Offer upload and record side by side wherever audio comes in.

### Don't:
- Don't add coloured side stripes to rows; the cue carries the colour.
- Don't fake materials (vinyl grooves, paper texture, embossing).
- Don't load web fonts or CDN assets; the app must work offline.
- Don't put labels or kickers above headings.
