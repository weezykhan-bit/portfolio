---
name: Fowzan Khan
description: A senior commercial leader's portfolio, built with tasteskill 2.5.1 as a one-page service site.
colors:
  stone: "#ebe5e3"
  stone-surface: "#e1dad7"
  ink: "#2b2622"
  ink-muted: "#655c58"
  go-green: "#0f7d45"
  on-green: "#ffffff"
  inverse-ground: "#2b2622"
  inverse-surface: "#36312d"
  inverse-ink: "#ebe5e3"
  inverse-muted: "#a29c99"
typography:
  display:
    fontFamily: "Instrument Sans, system-ui, sans-serif"
    fontWeight: 400
    letterSpacing: "-0.028em (hero -0.036em)"
    fontStretch: "96%"
  text:
    fontFamily: "Instrument Sans, system-ui, sans-serif"
    fontWeight: "400 text, 500 labels and buttons"
rounded:
  scheme: "soft (8 / 12 / 20)"
components:
  button-primary:
    backgroundColor: "{colors.go-green}"
    textColor: "{colors.on-green}"
    note: "on the inverse ground (hero box, footer) the kit swaps it to stone on ink"
  nav:
    type: "nav-split: four words left, the name centred, Email Fowzan right"
---

# Design System: Fowzan Khan

## Overview

The site was rebuilt in November 2026 with the tasteskill 2.5.1 frontend skill, which replaced the earlier "annual report" design (navy cover boards, vermilion highlighter, Schibsted Grotesk and Source Serif). Everything structural comes from the skill's kit in `assets/` (system.css, layout.css, motion.css and their scripts). Do not edit those files; change the page in `index.html`.

The page is treated as a **service** page (a person being hired). Its one main action is **Email Fowzan**, worded the same in the nav, the hero and the close.

## The deal

The skill deals each of these at random so pages don't repeat. They are recorded here so a later edit keeps them:

| Part | Dealt | Note |
|---|---|---|
| Hero | `film` | The first deal was `photo`. No licensed photograph of the trade could stand in without showing strangers as the owner's crew, so the hero became the official Shiv Shakti promo still in a cinema frame, linking to the promo on YouTube |
| Palette | `rose-grey-green` | Warm stone ground, one green accent; the interface stays about 95% neutral |
| Type | `instrument` | Instrument Sans, one family, headlines at 400 |
| Nav | `nav-split` | The Work word opens a panel with the three promo stills |
| Close | `close-type` | `close-photo` was dealt again: no unused photograph was left |
| Footer | `footer-dark` | `footer-visit` was dealt again: there is no street address to publish |
| Rhythm | `surface-pairs` | `#work` and `#pipeline` sit on the surface tone |
| Buttons | `solid` | |
| Mark | `stack` | Also `favicon.svg` |
| Moment | `word-highlight` | The Swastik Bhoomi statement in `#studio` turns to ink word by word as it scrolls past |

## Layout rules the page keeps

- One section per screen at 1440x900 and 390x844; the hero alone on the first screen.
- Equal left and right edges on the kit's `.wrap` (1280px, x 80 to 1360 at 1440).
- Phones hide the explanatory lines in `#record`, `#pipeline` and `#career` so each section fits one screen; names, figures, statuses and years stay.
- No captions under pictures; the promo stills credit their rights holders in the footer line.

## Content rules (from PRODUCT.md)

- Every figure is from the 2026 résumé; in-development work is labelled with its real status.
- No headshot, testimonials, press or stock people. The three promo stills are the only pictures until the owner supplies photographs of his own.
- No phone number. Email and LinkedIn only.

## Checks

The skill's finish gate passed (`GATE: PASS`) with five waivers in `.taste-skill/waivers.json`: three sections without a picture (no permitted imagery exists), the film hero's phone gap, and a 1px overflow of the kit's own menu button at 320px.
