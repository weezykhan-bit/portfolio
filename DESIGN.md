---
name: Fowzan Khan
description: A senior commercial leader's portfolio; the work in a cinema frame, the record on quiet stone.
colors:
  go-light-green: "#0f7d45"
  on-green: "#ffffff"
  studio-stone: "#ebe5e3"
  stone-surface: "#e1dad7"
  greasepaint-ink: "#2b2622"
  ink-muted: "#655c58"
  projection-booth: "#2b2622"
  booth-surface: "#36312d"
  booth-ink: "#ebe5e3"
  booth-muted: "#a29c99"
typography:
  display:
    fontFamily: "Instrument Sans, system-ui, sans-serif"
    fontSize: "clamp(38px, 3.24vw + 25.4px, 72px)"
    fontWeight: 400
    lineHeight: 1.02
    letterSpacing: "-0.036em"
    fontVariation: "'wdth' 96"
  headline:
    fontFamily: "Instrument Sans, system-ui, sans-serif"
    fontSize: "clamp(30px, 1.72vw + 23.3px, 48px)"
    fontWeight: 400
    letterSpacing: "-0.028em"
  title:
    fontFamily: "Instrument Sans, system-ui, sans-serif"
    fontSize: "20px"
    fontWeight: 400
  body:
    fontFamily: "Instrument Sans, system-ui, sans-serif"
    fontSize: "16px"
    fontWeight: 400
    lineHeight: 1.625
  label:
    fontFamily: "Instrument Sans, system-ui, sans-serif"
    fontSize: "13px"
    fontWeight: 500
rounded:
  sm: "8px"
  md: "12px"
  lg: "20px"
  btn: "8px"
spacing:
  s-1: "4px"
  s-2: "8px"
  s-3: "12px"
  s-4: "16px"
  s-5: "24px"
  s-6: "32px"
  s-7: "48px"
  s-8: "64px"
  s-9: "96px"
  s-10: "128px"
components:
  button-primary:
    backgroundColor: "{colors.go-light-green}"
    textColor: "{colors.on-green}"
    rounded: "{rounded.btn}"
    height: "44px"
    padding: "0 24px"
  button-primary-on-booth:
    backgroundColor: "{colors.booth-ink}"
    textColor: "{colors.projection-booth}"
    rounded: "{rounded.btn}"
    height: "44px"
  nav:
    backgroundColor: "{colors.studio-stone}"
    textColor: "{colors.greasepaint-ink}"
    height: "72px"
  hero-box:
    backgroundColor: "{colors.projection-booth}"
    textColor: "{colors.booth-ink}"
    rounded: "{rounded.md}"
    padding: "48px"
  promo-tile:
    rounded: "{rounded.lg}"
    typography: "{typography.title}"
  list-row:
    textColor: "{colors.greasepaint-ink}"
    typography: "{typography.body}"
---

# Design System: Fowzan Khan

## Overview

**Creative North Star: "The Screening Room"**

The work is shown the way a screening room shows it: one picture, large, in a dark rounded frame, and everything around it kept quiet so the picture carries. The first screen is a cinema frame holding an official promo still, with the name and title set in a solid booth-dark box at its lower left and a play control that goes to the real promo. After that the lights come up: the record, the slate and the career are plain rows on a warm stone ground, read like the papers handed round after a screening.

Density is low and even: every section is exactly one screen tall at 1440x900 and 390x844, with one idea and one heading per screen. Colour comes from the promos, not the interface; the interface stays about 95% neutral, with one green used only where the visitor can act or where one figure must land. Motion is small and earned: the hero enters once on load, linked tiles lift 2px and their stills zoom 3% inside the frame, and one statement turns to ink word by word as it crosses the screen.

The system is built on the tasteskill 2.5.1 kit (`assets/`). It replaced, in November 2026, an "annual report" world of navy cover boards, a vermilion highlighter and Schibsted Grotesk with Source Serif; do not bring those back piecemeal.

The kit dealt these parts at random so pages don't repeat; a later edit keeps them:

| Part | Dealt | Note |
|---|---|---|
| Hero | film | Redealt from `photo`: no licensed photograph of the trade could stand in without showing strangers as the owner's crew |
| Palette | rose-grey-green | Warm stone ground, one green accent |
| Type | instrument | Instrument Sans alone, headlines at 400 |
| Nav | nav-split | The Work word opens a panel of the three promo stills |
| Close | close-type | `close-photo` redealt: no unused photograph left |
| Footer | footer-dark | `footer-visit` redealt: no street address to publish |
| Rhythm | surface-pairs | `#work` and `#pipeline` sit on the stone surface |
| Buttons | solid | |
| Mark | stack | Also `favicon.svg` |
| Moment | word-highlight | The Swastik Bhoomi statement in `#studio` |

**Key Characteristics:**
- One picture leads: an official promo still in a dark rounded cinema frame; no captions under any picture.
- Warm stone ground, near-black warm ink, one green go-light.
- One type family at regular weight; size and tight tracking carry the hierarchy, never bold.
- One section per screen, equal left and right edges on a 1280px wrap.
- Lists are plain rows closed by hairlines, never cards, icons or stat counters.

## Colors

A warm, almost colourless room with one green signal; the promo stills bring all the colour.

### Primary
- **Go-Light Green** (#0f7d45): the primary button (Email Fowzan in the nav, hero and close), the focus ring, links, and the one strong word (₹10 Cr+) in the Swastik Bhoomi statement. Nothing decorative.

### Neutral
- **Studio Stone** (#ebe5e3): the page ground and the nav bar.
- **Stone Surface** (#e1dad7): the alternate ground for `#work` and `#pipeline`, so neighbouring sections part by a full-width change of ground.
- **Greasepaint Ink** (#2b2622): all text people read, at 7:1 or more on stone.
- **Ink Muted** (#655c58): labels, tile meta lines and a heading's grey run-on only; never body text (5.2:1 on stone, 4.7:1 on the surface).
- **Projection Booth** (#2b2622): the inverse ground of the hero's text box and the closing footer. The same value as the ink, so the dark is the ink itself, not a new colour.
- **Booth Surface** (#36312d), **Booth Ink** (#ebe5e3), **Booth Muted** (#a29c99): surface, text and labels on the booth ground. On the booth, the primary button turns Booth Ink with booth-dark text.

### Named Rules
**The One Go-Light Rule.** Green marks what the visitor can do and nothing else, plus at most one word a page. Under 3% of any screen.

**The Colour Comes From the Work Rule.** No tints, gradients or coloured panels in the interface; the promo stills are the only saturated colour on the page.

## Typography

**Display Font:** Instrument Sans (with system-ui, sans-serif)
**Body Font:** Instrument Sans (with system-ui, sans-serif)

**Character:** A precise, slightly condensed neo-grotesk (width axis at 96%) used at regular weight throughout; it reads as calm and senior, closer to a film's end credits than to a pitch deck.

### Hierarchy
- **Display** (400, 72px at 1440 / 40px at 390, line-height 1.02, -3.6%): the hero h1 only, at most three lines, never hyphenated.
- **Headline** (400, 48px / 30px, -2.8%): one h2 per section, first in the section; the closing h2 too. Each names a thing or carries a digit.
- **Title** (400–500, 20px / 18px): the hero lead, row names, tile titles.
- **Body** (400, 16px, line-height 1.6): row descriptions and section leads, at most 62 characters a line.
- **Label** (500, 13px, sentence case): the statement's eyebrow, footer column heads, tile meta. Never tracked capitals.

### Named Rules
**The Regular Weight Rule.** Headlines are set at 400; 500 only for labels and buttons. No 600, 700 or 800 anywhere on the page.

**The Statement Is Body-Sized Thought Rule.** The word-highlight statement is set at headline scale as running prose with one strong word, never as a slogan.

## Layout

One section per screen: every `main > section` and the closing footer is exactly 1 or 2 screen heights (`100svh`; `100lvh` on phones), with 120px above the h2 and 72px below the content at 1440 (96 and 48 on phones). The fixed nav is 72px (56 on phones). Content sits on one 1280px wrap with 80px gutters (24px on phones), 12 columns with a 24px gap (12 on phones). Text always starts on the left line; nothing is centred wider than half the wrap, nothing staggers, nothing bleeds to one side only.

Breakpoints: under 640px (phone: one column, full-width buttons, menu sheet), 640–1023px (tablet: splits stack text first), 1024px and up (desktop). On phones the explanatory lines under the figures, projects and roles are hidden so each section stays one screen; names, values, statuses and years always remain.

Spacing follows the 4, 8, 12, 16, 24, 32, 48, 64, 96, 128px scale; heading to content is 48px (32 on phones), tiles sit 24px apart.

## Elevation & Depth

Flat by default. Depth comes from two things: the change of ground between stone, stone surface and booth dark, and the cinema frame's dark rounded box around the hero still. The only shadow is a response to the pointer.

### Shadow Vocabulary
- **Hover lift** (`box-shadow: 0 14px 32px -18px` in a ground-derived ink, with `translateY(-2px)`, 180ms): a linked card or tile under the pointer.

### Named Rules
**The Flat-At-Rest Rule.** Nothing casts a shadow at rest; no glows, no blurred panels, no scrims or gradients over a photograph.

## Shapes

Gently rounded throughout on the kit's soft scheme: controls and buttons 8px, the hero's text box 12px, the cinema frame and promo tiles 20px. Lists have no corners at all: rows run on the wrap's lines, each closed by a 1px hairline at about 11% of the ink. The mark is three stacked rounded bars of shrinking length.

## Components

### Buttons
- **Shape:** gently rounded (8px), 44px tall, 24px side padding, 16px label at 500. One filled button per view.
- **Primary:** Go-Light Green with white text on stone; on the booth ground (hero box, footer) it turns Booth Ink with booth-dark text. The label is always "Email Fowzan" and opens a mailto.
- **Hover / Focus:** steps on hover, presses on click (the kit's motion layer); a 2px green focus ring that never animates. The primary carries a small drawn arrow.
- **Extra-large:** once, in the close, across the full wrap.

### Cards / Containers
- **Promo tile:** a 16:9 still in a 20px-rounded mask, the title and one meta line under it on the ground, no box. The whole tile links to the promo; on hover it lifts 2px and the still zooms 3% inside its mask.
- **Hero box:** a solid booth-dark box (12px radius, 48px padding) at the cinema frame's lower left; never a scrim.

### Lists (rows)
- **Style:** name in title size on the left, a one-line description under it, the value or status right-aligned; a 1px hairline closes each row. Used for the figures, the development slate and the career.

### Navigation
- **Style:** a fixed, opaque stone bar with a 1px hairline: four words on the left (Record, Work, Studio, Career, 15px at 500), the mark and name centred, Email Fowzan on the right. Work opens a flat panel of the three promo stills after 150ms of hover.
- **Mobile:** the name moves left, a 44px menu button opens a full-screen sheet; the nav's button keeps its place on tablet.

### Cinema frame (signature)
The hero: one rounded frame on the wrap's lines from 16px under the nav to 16px above the fold, holding an official promo still with `object-fit: cover`. The play control (a 64px white disc and a booth-dark label pill) sits at the frame's lower right and opens the real promo on YouTube; it is never a dead button.

### Word-highlight statement (signature)
One statement of 12 to 40 words in its own one-screen section, resting at half ink and turning to full ink word by word as it crosses the middle of the screen, its one strong word in green. Under reduced motion it rests in full ink.

## Do's and Don'ts

### Do:
- **Do** keep the main action worded "Email Fowzan" in the nav, the hero and the close, and nowhere else as a filled button.
- **Do** keep every section exactly one or two screens tall, with its h2 first and top-aligned.
- **Do** credit the promo stills to their rights holders in the one footer line.
- **Do** change the page in `index.html` only; the kit's files in `assets/` stay as shipped.
- **Do** record any check you judge false in `.taste-skill/waivers.json` with its reason (five are there now: three sections without a picture, the film hero's phone gap, the kit menu button's 1px overflow at 320px).

### Don't:
- **Don't** put a caption, label or description under any picture.
- **Don't** use stock photographs of crews, studios or people; they read as the owner's own work. No headshot until the owner supplies one.
- **Don't** bring back the navy, vermilion, Schibsted Grotesk or Source Serif of the replaced design.
- **Don't** use bold or tracked-capital type, coloured panels, gradients, scrims, glows or a row of big stat counters.
- **Don't** add a phone number, a form, or a second filled button style.
