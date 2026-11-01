---
name: Fowzan Khan
description: A commercial leader's career published as an annual report.
colors:
  report-stock: "#F3F3EF"
  report-stock-shade: "#E7E7E1"
  hairline: "#C8CAD0"
  cover-navy: "#0D1B2E"
  cover-navy-rule: "#2A3D5B"
  ink-muted: "#475266"
  on-navy-muted: "#A7B2C4"
  vermilion: "#C9381C"
  vermilion-deep: "#A82C14"
  vermilion-on-navy: "#FF7A5C"
typography:
  display:
    fontFamily: "Schibsted Grotesk, Helvetica Neue, Arial, sans-serif"
    fontSize: "clamp(3.4rem, 8.6vw, 6rem)"
    fontWeight: 800
    lineHeight: 0.92
    letterSpacing: "-0.04em"
  headline:
    fontFamily: "Schibsted Grotesk, Helvetica Neue, Arial, sans-serif"
    fontSize: "clamp(2.2rem, 4.6vw, 3.75rem)"
    fontWeight: 800
    lineHeight: 1.04
    letterSpacing: "-0.025em"
  figure:
    fontFamily: "Schibsted Grotesk, Helvetica Neue, Arial, sans-serif"
    fontSize: "clamp(2rem, 3.3vw, 3rem)"
    fontWeight: 700
    lineHeight: 1
    letterSpacing: "-0.035em"
    fontFeature: "lnum"
  lead:
    fontFamily: "Schibsted Grotesk, Helvetica Neue, Arial, sans-serif"
    fontSize: "clamp(1.3rem, 2.1vw, 1.75rem)"
    fontWeight: 500
    lineHeight: 1.4
    letterSpacing: "-0.012em"
  title:
    fontFamily: "Schibsted Grotesk, Helvetica Neue, Arial, sans-serif"
    fontSize: "1.0625rem"
    fontWeight: 700
    lineHeight: 1.35
    letterSpacing: "-0.01em"
  dek:
    fontFamily: "Schibsted Grotesk, Helvetica Neue, Arial, sans-serif"
    fontSize: "1rem"
    fontWeight: 500
    lineHeight: 1.45
  body:
    fontFamily: "Source Serif 4, Georgia, serif"
    fontSize: "1.125rem"
    fontWeight: 400
    lineHeight: 1.62
  label:
    fontFamily: "Schibsted Grotesk, Helvetica Neue, Arial, sans-serif"
    fontSize: "0.8125rem"
    fontWeight: 600
    lineHeight: 1.3
    letterSpacing: "0.06em"
rounded:
  none: "0px"
  sm: "2px"
spacing:
  gutter: "clamp(16px, 4vw, 48px)"
  row: "14px"
  block: "44px"
  section: "clamp(72px, 10vw, 136px)"
components:
  button-solid:
    backgroundColor: "{colors.vermilion}"
    textColor: "{colors.report-stock}"
    typography: "{typography.title}"
    rounded: "{rounded.sm}"
    padding: "15px 20px"
  button-solid-hover:
    backgroundColor: "{colors.vermilion-deep}"
  button-solid-on-navy:
    backgroundColor: "{colors.report-stock}"
    textColor: "{colors.cover-navy}"
    rounded: "{rounded.sm}"
    padding: "15px 20px"
  button-solid-on-navy-hover:
    backgroundColor: "{colors.vermilion-on-navy}"
  button-line:
    backgroundColor: "transparent"
    textColor: "{colors.cover-navy}"
    rounded: "{rounded.sm}"
    padding: "15px 20px"
  button-line-hover:
    backgroundColor: "{colors.cover-navy}"
    textColor: "{colors.report-stock}"
  masthead:
    backgroundColor: "{colors.cover-navy}"
    textColor: "{colors.on-navy-muted}"
    height: "60px"
  section-tab:
    textColor: "{colors.vermilion}"
    typography: "{typography.label}"
---

# Design System: Fowzan Khan

## Overview

**Creative North Star: "The Annual Report"**

The site is a career published the way a board reads performance: figures first, every number footnoted, narrative set as the commentary that explains the figures. Two materials carry the whole world. Report stock (the uncoated off-white page) holds the reading sections; ink-navy cover boards open and close the document and mark the career chapter. Structure comes from typography and rules, never from boxes: hairlines separate rows, a 2px ink rule heads every table and list, and section numbers sit in a side column like the tabs of a printed report.

Density is that of a well-set financial statement: generous section spacing (72–136px), tight ruled rows inside. One vermilion accent behaves like a reviewer's highlighter; it marks the section number, the note reference, the live status, the current role on the timeline, and the primary action, and nothing else. Motion is mechanical and documentary: cover figures roll in on odometer reels, Fig. 1 is printed live as a two-colour halftone, and charts draw themselves when they scroll into view. Every motion device has a complete static state; nothing depends on JavaScript to be read.

The world explicitly replaces a playful print-ephemera presentation the owner rejected as too casual, and refuses the dark executive template of hero, stat counters and card grid.

**Key Characteristics:**
- Two surfaces only: report stock and navy cover board, in full-bleed bands.
- Hairline rules and 2px ink rule heads instead of cards, borders or shadows.
- Tabular, lining figures everywhere a number appears; figures carry superscript note references to "Notes to the figures".
- Section number tabs in a 3/9 side column, hidden on phones; a dek line under every h2.
- Single vermilion accent, swapped to a lighter vermilion on navy.
- Mechanical motion (odometer, halftone press, self-drawing charts) that is always optional.

## Colors

A two-material palette (paper and navy board) with a single vermilion highlighter.

### Primary
- **Highlighter Vermilion** (vermilion): the only accent on report stock. Section number tabs and their trailing rule, footnote numerals in the notes list, the solid button, the "live" status dot, focus rings, text selection, and the highlighted fragment in a pull quote.
- **Pressed Vermilion** (vermilion-deep): hover state of the solid vermilion button only.
- **Lit Vermilion** (vermilion-on-navy): the accent's navy-board form, used wherever vermilion appears on navy: note superscripts in the figures strip, section tabs, the current-role bar and its marker on the timeline, the reading-progress line, the email underline, focus rings and button hovers on navy.

### Neutral
- **Report Stock** (report-stock): page background for every reading section, and text colour on navy (the same value, so the two materials stay one pair).
- **Stock Shade** (report-stock-shade): the unfilled state of the 25-acre grid before it draws in.
- **Hairline Grey** (hairline): 1px row rules, section top rules, notes rule.
- **Cover Navy** (cover-navy): masthead, cover, career chapter, contact close and footer backgrounds; also the ink colour for headings, body emphasis and 2px rule heads on paper.
- **Cover Rule** (cover-navy-rule): hairlines and column rules on navy; the timeline year grid.
- **Commentary Grey** (ink-muted): body copy, deks, meta labels and table headers on paper.
- **Board Grey** (on-navy-muted): secondary text, deks, captions and nav links on navy.

### Named Rules
**The Highlighter Rule.** Vermilion marks a reference, a status or an action; it is never a fill for a surface, a heading colour, or decoration. If it does not point at something, it is not vermilion.

**The Material Swap Rule.** On navy, every paper-side colour has a fixed counterpart: vermilion becomes lit vermilion, ink-muted becomes board grey, hairline becomes cover rule. Never place the paper-side vermilion on navy.

## Typography

**Display Font:** Schibsted Grotesk (with Helvetica Neue, Arial)
**Body Font:** Source Serif 4 (with Georgia)

**Character:** A dense, newsroom grotesk carries headings, figures, labels and every table cell head; a quiet text serif carries the narrative, like the commentary pages of a report. Both are self-hosted.

### Hierarchy
- **Display** (800, clamp(3.4rem, 8.6vw, 6rem), 0.92): the name on the cover only; lines rise in from a mask on load. The contact close uses the same weight at clamp(2.8rem, 7vw, 6rem).
- **Headline** (800, clamp(2.2rem, 4.6vw, 3.75rem), 1.04, max 18ch): section h2s.
- **Figure** (700, clamp(2rem, 3.3vw, 3rem), 1, lining figures): cover key figures; unit set in a 0.48em small, note reference as a 0.75rem superscript. Studio KPIs use 800 at 2.25rem; the acre count 800 at clamp(3.4rem, 6vw, 5rem).
- **Lead** (500, clamp(1.3rem, 2.1vw, 1.75rem), 1.4, max 40ch): the opening statement of a section, in the grotesk.
- **Pull figure** (700, clamp(1.4rem, 2.4vw, 2rem), 1.25, max 34ch): a pull statement under a 3px ink rule, with one vermilion fragment.
- **Title** (700, 1.0625rem, 1.35): row heads in ruled lists and the first column of tables.
- **Dek** (500, 1rem, 1.45, max 60ch): the line directly under every h2: entity, role, date range or scope.
- **Body** (400, 1.125rem, 1.62, max 68ch): narrative in Source Serif 4, in ink-muted with ink-coloured strong.
- **Label** (600, 0.8125rem, 0.06em, uppercase): table headers, role meta lines, figure captions' "Fig. n" lead.

### Named Rules
**The Tabular Figures Rule.** Every number that can sit in a column uses tabular, lining numerals (tables, axis years, tabs, stream numbers); display figures use lining numerals.

**The Serif Is Commentary Rule.** Source Serif 4 is for running narrative, captions and the cover lede. Headings, figures, labels, list rows and table text stay in the grotesk.

## Layout

A single 1280px measure (`min(1280px, 100% - 2 × gutter)`, gutter clamp(16px, 4vw, 48px)) holds everything. Reading sections use a 3/9 split: the left column carries only the section number tab with a hairline running to the edge; the right column carries h2, dek and content. Below 860px the side column is hidden and content runs single-column. Sections are separated by a 1px hairline and clamp(72px, 10vw, 136px) vertical padding; navy sections drop the hairline because the material change is the separator.

The cover is a 7/5 grid (name and lede left, Fig. 1 right) above a full-width figures strip: six columns separated by navy hairlines under a 2px paper rule, reflowing to three (≤1100px) and two (≤560px). Inside sections, content blocks start about 44px below the dek; ruled rows run 10–22px tall padding. Tables collapse to stacked two-column rows under 700px with the status in the right column. Breakpoints in use: 1100, 1060, 860, 760, 700, 560, 480px.

## Elevation & Depth

The system is flat. Depth comes from the change of material (paper to navy board) and from rule weight, not from shadow. The single exception is the Fig. 1 plate on the navy cover, which carries a soft drop so the printed sheet reads as laid on the board.

### Shadow Vocabulary
- **Plate on board** (`box-shadow: 0 30px 60px -30px rgba(0,0,0,.6)`): the cover photograph plate only.

### Named Rules
**The Rules Not Boxes Rule.** Group content with a heavy rule above and hairlines between, never with a filled card, an outline box or a shadow.

## Shapes

Square by default. Buttons, the masthead call to action and the promo play tab take a 2px corner, enough to read as cut card stock rather than pills. Status markers are 8px dots (filled for live and development, outlined for planned). Rule weights form the real shape vocabulary: 1px hairline for rows, 2px ink for table and list heads and the figures strip, 3px ink for the pull statement and the email underline.

## Components

### Buttons
- **Shape:** gently squared (2px), 1.5px border slot, 15px 20px padding, grotesk 600 1rem, optional 1.05em stroke icon.
- **Solid:** vermilion on paper; on navy it inverts to a report-stock button with navy text.
- **Line:** transparent with a currentColor border; on hover it fills with ink (paper) or report stock (navy).
- **Hover / Focus:** 0.15s colour transitions; solid hovers to pressed vermilion on paper and lit vermilion on navy. Focus is a 2px vermilion outline at 3px offset (lit vermilion on navy).

### Navigation (masthead)
- 60px sticky navy bar with a 1px cover-rule bottom. Wordmark in grotesk 800 with an uppercase report title that hides under 1060px. Links in board grey brighten to report stock on hover and when current. The email action is a small report-stock button; LinkedIn is an underlined text link. A 2px lit-vermilion reading-progress line runs along the bottom edge. Under 860px only the email and LinkedIn actions remain.

### Figures strip
- The cover's ledger: a caption row ("Key figures" and the source line linking to the notes), then six figures each with a unit, a superscript note number linking to its note, and a one-line grotesk description. Separated by vertical navy hairlines.

### Notes to the figures
- A numbered two-column list (one column under 700px) under a hairline; numerals in vermilion grotesk. A targeted note gets a vermilion highlighter band across the lower 40% of its line.

### Ruled tables and lists
- A 2px ink rule heads the block; rows are divided by hairlines. Table headers are uppercase labels; the first column is a grotesk title with an uppercase sub-label. All figures are tabular.

### Status marker
- 8px dot plus grotesk 600 label in the last column: vermilion for live, a filled dot for in development, an outlined dot for planned.

### Section tab and dek
- Side-column number ("01"…"08") in vermilion grotesk 700 with a half-opacity rule running out to the column edge; decorative and hidden from assistive tech. Under every h2, a dek line naming entity, role, dates or scope.

### Halftone press (signature)
- Fig. 1 is drawn by WebGL as a two-colour halftone (navy and vermilion screens on report stock) that prints in after load; a ring loupe under the pointer (or touch) clears the screen to show the photograph. Without WebGL, or if the image fails within 6s, the photo shows grayscale at contrast 1.15 under a navy multiply dot screen (5px pitch). A small caption ("Fig. 1" label plus serif line) sits beneath.

### Odometer figures (signature)
- Each digit in a cover figure becomes a two-turn reel that rolls to its value (1.5s, expo-out ease), staggered right-to-left and by figure. The number is plain text in the HTML and keeps its aria-label; reduced motion leaves it static.

### Self-drawing charts (signature)
- The career timeline (13-year grid, white role bars, lit-vermilion current bar with a marker) and the 25-acre 5×5 grid render complete in HTML. With motion allowed and IntersectionObserver present they reset to empty and draw in on scroll (bars scale from the left over 1.1s; acres fill one by one at 40ms steps).

## Do's and Don'ts

### Do:
- **Do** put every number in Schibsted Grotesk with tabular or lining figures, and give cover figures a note reference that links to "Notes to the figures".
- **Do** head every table and ruled list with a 2px ink rule and separate rows with 1px hairlines.
- **Do** follow every h2 with a dek line, and give every reading section a side-column number tab.
- **Do** swap to lit vermilion (vermilion-on-navy) and board grey on navy surfaces.
- **Do** render every chart and figure complete without JavaScript; motion only resets and replays it.
- **Do** remove draw-ins, the odometer and the name rise under prefers-reduced-motion.

### Don't:
- **Don't** use vermilion as a surface fill, heading colour or ornament; it marks references, status and actions only.
- **Don't** introduce cards, outlined boxes or shadows to group content; the plate on the cover is the only shadow.
- **Don't** add a third surface colour or a second accent hue.
- **Don't** set headings, figures or table text in the serif.
- **Don't** let any motion hide content that has no static state.
