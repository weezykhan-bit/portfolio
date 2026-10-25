---
name: Fowzan Khan
description: An Indian bazaar sponsor calendar, chromolithographed under one name and hung on a deep peacock wall.
colors:
  peacock-wall: "#0A3540"
  wall-line: "#1B5A68"
  on-wall: "#F4EFE4"
  on-wall-muted: "#B9D3D6"
  vermilion: "#C7301F"
  vermilion-deep: "#9A2115"
  marigold: "#F2A81D"
  marigold-deep: "#A06404"
  peacock: "#11606E"
  rose: "#A8344F"
  ink-violet: "#21142A"
  ink-violet-muted: "#55465A"
  newsprint: "#FBF8F1"
  newsprint-shade: "#EFE7D6"
  brass: "#C9A24B"
  process-cyan: "#1A8FB0"
  process-magenta: "#D33A6A"
  process-yellow: "#F5C318"
typography:
  display:
    fontFamily: "'Rozha One', 'Times New Roman', serif"
    fontSize: "clamp(3rem, 7.6vw, 6rem)"
    fontWeight: 400
    lineHeight: 1.02
    letterSpacing: "-0.01em"
  headline:
    fontFamily: "'Rozha One', 'Times New Roman', serif"
    fontSize: "clamp(2.4rem, 5.4vw, 4.5rem)"
    fontWeight: 400
    lineHeight: 1.02
    letterSpacing: "-0.01em"
  figure:
    fontFamily: "'Rozha One', 'Times New Roman', serif"
    fontSize: "clamp(3.25rem, 25cqi, 7rem)"
    fontWeight: 400
    lineHeight: 0.9
    letterSpacing: "-0.02em"
    fontFeature: "lnum"
  title:
    fontFamily: "'Rozha One', 'Times New Roman', serif"
    fontSize: "1.375rem"
    fontWeight: 400
    lineHeight: 1.1
  lede:
    fontFamily: "'Hind', 'Segoe UI', sans-serif"
    fontSize: "clamp(1.125rem, 1.6vw, 1.375rem)"
    fontWeight: 500
    lineHeight: 1.4
  body:
    fontFamily: "'Hind', 'Segoe UI', sans-serif"
    fontSize: "1.0625rem"
    fontWeight: 400
    lineHeight: 1.6
  label:
    fontFamily: "'Khand', 'Arial Narrow', sans-serif"
    fontSize: "0.875rem"
    fontWeight: 600
    lineHeight: 1.2
    letterSpacing: "0.08em"
  button:
    fontFamily: "'Khand', 'Arial Narrow', sans-serif"
    fontSize: "1rem"
    fontWeight: 600
    lineHeight: 1
    letterSpacing: "0.08em"
  stamp:
    fontFamily: "'Khand', 'Arial Narrow', sans-serif"
    fontSize: "1rem"
    fontWeight: 700
    lineHeight: 1
    letterSpacing: "0.12em"
rounded:
  print: "2px"
  stamp: "3px"
  eyelet: "50%"
spacing:
  gutter: "clamp(16px, 4vw, 40px)"
  container: "1240px"
  section: "clamp(72px, 10vw, 128px)"
  sheet-margin: "clamp(10px, 1.6vw, 18px)"
  panel: "clamp(16px, 2.4vw, 28px)"
  nav-height: "56px"
components:
  button-marigold:
    backgroundColor: "{colors.marigold}"
    textColor: "{colors.ink-violet}"
    typography: "{typography.button}"
    rounded: "{rounded.print}"
    padding: "14px 20px 12px"
  button-marigold-hover:
    backgroundColor: "{colors.newsprint}"
    textColor: "{colors.ink-violet}"
  button-line:
    backgroundColor: "transparent"
    textColor: "{colors.newsprint}"
    typography: "{typography.button}"
    rounded: "{rounded.print}"
    padding: "14px 20px 12px"
  button-line-hover:
    backgroundColor: "{colors.newsprint}"
    textColor: "{colors.ink-violet}"
  button-ink:
    backgroundColor: "{colors.ink-violet}"
    textColor: "{colors.newsprint}"
    typography: "{typography.button}"
    rounded: "{rounded.print}"
    padding: "12px 16px 10px"
  button-ink-hover:
    backgroundColor: "{colors.vermilion}"
    textColor: "{colors.newsprint}"
  nav-rail:
    backgroundColor: "{colors.ink-violet}"
    textColor: "{colors.on-wall-muted}"
    typography: "{typography.label}"
    height: "{spacing.nav-height}"
  nav-cta:
    backgroundColor: "{colors.marigold}"
    textColor: "{colors.ink-violet}"
    rounded: "{rounded.print}"
    padding: "9px 14px 7px"
  year-tab:
    backgroundColor: "transparent"
    textColor: "{colors.on-wall-muted}"
    rounded: "{rounded.print}"
    padding: "9px 12px 7px"
  year-tab-current:
    backgroundColor: "{colors.marigold}"
    textColor: "{colors.ink-violet}"
  calendar-sheet:
    backgroundColor: "{colors.newsprint}"
    textColor: "{colors.ink-violet}"
    rounded: "{rounded.print}"
    padding: "{spacing.sheet-margin}"
  date-leaf:
    backgroundColor: "{colors.newsprint}"
    textColor: "{colors.ink-violet}"
    padding: "24px 26px 18px"
  status-stamp:
    backgroundColor: "transparent"
    textColor: "{colors.vermilion}"
    typography: "{typography.stamp}"
    rounded: "{rounded.stamp}"
    padding: "9px 12px 6px"
---

# Design System: Fowzan Khan

## Overview

**Creative North Star: "The Sponsor Calendar"**

Every surface is a printed object from an Indian bazaar merchant calendar: chromolithographed sheets in vermilion, marigold and peacock, keylined in ink-violet, hung on a deep peacock wall. The calendar was always commerce dressed in story, and the system takes that literally: content never floats on a generic page; it is printed on stock, framed in letterpress ornament, stamped, torn off, or flipped over a hanger.

Density is that of a well-filled print sheet: a 2px ink keyline inside a newsprint margin, panels divided by solid ink rules and dashed perforations, Khand labels set tight and uppercase like a printer's slug. The press is visible on purpose. Fields and photographs are screened in four-colour process halftone; the hero banner and picture panel are printed live by a WebGL press whose Y, M, C and K plates roll on in order and settle a hair out of register. Type never goes to the screens: it prints as solid line-work over the fields.

The wall is dark, the sheets are bright. Depth comes from paper hanging on a nail (a soft drop shadow, eyelets, a hook, a sway on arrival), never from glass, glow or gradients.

**Key Characteristics:**
- Deep peacock wall with a fine 7px dot texture; all content on hung sheets.
- Flat printed fields in vermilion, marigold, peacock, rose and ink-violet, rotated per sheet.
- Rozha One display, Khand condensed uppercase labels and figures, Hind body.
- Letterpress ornament bands and an authored rosette-and-quatrefoil frame (SVG border-image).
- CMYK halftone at 15°/75°/0°/45° on fields and stills; solid, unscreened type.
- Rubber-stamp status marks, a perforated tear-off date pad, sheets that flip over a hanger.
- Near-square 2px corners throughout.

## Colors

A chromolithograph palette: three saturated printed fields and an ink-violet keyline on warm newsprint, displayed against a dark peacock wall.

### Primary
- **Bazaar Vermilion** (vermilion): the sponsor banner, the closing sheet, the default career band, the default stamp and the hero figure on the date pad. The colour the visitor remembers.
- **Burnt Vermilion** (vermilion-deep): small Khand labels on paper (pad head, slate category lines, pitch headings, overleaf column heads) and the giant acreage numeral on marigold, where full vermilion would lose contrast.

### Secondary
- **Temple Marigold** (marigold): the primary action fill, the nav underline (3px) and CTA, the current year tab, the studio sheet field, list diamonds, the registration ghost behind display type, focus rings and selection.
- **Turmeric Ochre** (marigold-deep): marigold as text on paper; used only for the third date-leaf figure where marigold itself would be illegible.

### Tertiary
- **Peacock Plate** (peacock): the second career band, peacock stamps, the leaf provenance line, links inside newsprint copy, the studio mandate figure, and the empty photo frame before the press runs.
- **Faded Rose** (rose): the fourth career band and planning-stage stamps. The shipped value is the deeper rose that keeps newsprint text legible on it.

### Neutral
- **Peacock Wall** (peacock-wall): the page ground and the eyelet holes punched through sheets; also `theme-color`.
- **Wall Seam** (wall-line): hairlines and idle tab borders drawn directly on the wall.
- **Lamp-lit Paper** (on-wall): body text set directly on the wall.
- **Verdigris Mist** (on-wall-muted): secondary text on the wall and on ink (section intros, nav links, press strip, crop and registration marks).
- **Ink Violet** (ink-violet): every keyline, rule and body text on paper; the nav rail, the press strip, the photo frame field, the dark button and the K plate.
- **Faded Ink** (ink-violet-muted): secondary text on paper (counters, cell captions, imprint).
- **Newsprint** (newsprint): sheet stock, date leaves, paper text on printed fields.
- **Aged Newsprint** (newsprint-shade): the date-pad panel, blank calendar cells, the pitch strip.
- **Hook Brass** (brass): calendar hardware only, the hanger wire and eyelet rims.

### Process inks
- **Process Cyan / Magenta / Yellow** (process-cyan, process-magenta, process-yellow) with Ink Violet as K: the four press plates, and the colour bar printed outside the trim. They exist only inside the halftone and the colour bar; never use them as UI fills.

### Named Rules
**The Wall And Sheet Rule.** The peacock wall is ground, never a content surface for more than a section head. Anything that carries substance is printed on a sheet: newsprint, vermilion or marigold stock.

**The Band Rotation Rule.** Career sheets cycle vermilion, peacock, marigold, rose, ink as their band colour. On the marigold band, text flips to ink-violet; on every other band, text is newsprint.

**The Process-Inks-Stay-In-The-Press Rule.** Cyan, magenta and yellow appear only as halftone dots and colour-bar chips. UI colour comes from the printed-field palette.

## Typography

**Display Font:** Rozha One (with Times New Roman, serif)
**Body Font:** Hind (with Segoe UI, sans-serif)
**Label/Figure Font:** Khand (with Arial Narrow, sans-serif)

**Character:** Rozha One is the high-contrast Devanagari-family display face of Indian commercial print; Khand is the condensed slug of the printer's furniture; Hind is the quiet reading voice. All three are self-hosted with Latin and Latin-extended subsets.

### Hierarchy
- **Display** (Rozha One 400, clamp(3rem, 7.6vw, 6rem), 1.02): the name on the sponsor banner and the closing headline (clamp(2.8rem, 7.4vw, 6rem)). The only type that carries the registration ghost.
- **Headline** (Rozha One 400, clamp(2.4rem, 5.4vw, 4.5rem), 1.02, max 16ch): section heads on the wall; bill and studio headings step down to clamp(1.6rem, 2.4vw, 2.1rem) through clamp(2.2rem, 4.4vw, 3.75rem).
- **Figure** (Rozha One 400, clamp(3.25rem, 25cqi, 7rem), 0.9, lining numerals): date-leaf figures, sized by the leaf's container. Units drop to 0.42em in ink. The studio acreage numeral scales to clamp(6rem, 17vw, 13.5rem) at 0.8.
- **Title** (Rozha One 400, 1.375rem, 1.1): promo captions, frame caption, the wordmark, calendar cell titles (1.0625rem).
- **Lede** (Hind 500, clamp(1.125rem, 1.6vw, 1.375rem), 1.4, max 44ch): the opening statement on the hero sheet.
- **Body** (Hind 400, 1.0625rem, 1.6, 46-62ch): all running copy.
- **Label** (Khand 600, 0.875rem, 0.08em, uppercase): role lines, counters, captions, nav links, mastheads, imprint. Small variant 0.75-0.8125rem at 0.06-0.12em. Counters use tabular numerals.
- **Stamp** (Khand 700, 1rem, 0.12em, uppercase): status stamps only.

### Named Rules
**The Solid Type Rule.** Type is always solid line-work, never screened. Halftone layers sit beneath the text layer (text at z-index 1 over the dot overlay); in the WebGL press the field is a flat tint sent to the screens and the type prints over the canvas.

**The Khand Slug Rule.** Every uppercase label is Khand with positive tracking (0.06-0.12em). Hind is never set in uppercase; Rozha One is never tracked open.

## Layout

A single centred column, `min(1240px, 100% - 2 × gutter)` with a fluid gutter, carrying one sheet per section. Sections breathe at clamp(72px, 10vw, 128px) vertically; consecutive sections drop their top padding so sheets read as one hanging run.

Inside sheets, structure is a print grid ruled in ink: the hero sheet is a two-column grid (1.45fr / 1fr) under a full-width banner with a full-width press strip at the foot; career sheets split band and calendar (1fr / 1.05fr) with a 4-column cell grid; the slate is a 6-column newsprint page (lead bill spans 6, column bills span 2).

The hero sheet fills the first viewport (`100svh - nav - 132px`). Printer's furniture (crop marks, registration targets, colour bar) sits outside the trim on wide screens and drops below 1100px. At 900px the hero stacks banner, pad, picture, press; at 860px career and slate collapse to one column, the 4-up calendar becomes 2-up, and year tabs hide. At 480px ornament bands shrink to 10px and press buttons go full-width. The scroll-driven flip only runs at ≥861px wide, ≥680px tall, with motion allowed; otherwise sheets stack and swing in individually.

## Elevation & Depth

Depth is physical paper, not interface layering. The wall is flat; sheets hang on it with one consistent soft drop shadow; nothing else lifts. Hardware sells the hang: a brass hook wire, punched eyelets that show the wall through the sheet, a centre nail hole on career sheets, and a damped sway when the hero sheet arrives.

### Shadow Vocabulary
- **Hang** (`box-shadow: 0 2px 3px rgba(0,0,0,.25), 0 24px 48px -18px rgba(0,0,0,.55)`): every sheet on the wall (hero, career, studio, slate, overleaf, close).
- **Punched hole** (`box-shadow: inset 0 1px 2px rgba(0,0,0,.6)`): eyelets and nail holes.
- **Registration ghost** (`text-shadow: 3px 2px 0 #F2A81D, -2px -1px 0 #21142A`): display type on vermilion fields, the marigold and ink plates printing slightly out of register. Arrives from a wide offset and settles.

### Named Rules
**The Paper Only Lifts Once Rule.** A sheet carries the Hang shadow; nothing printed on a sheet carries its own shadow. Inner structure is ruled, not raised.

## Shapes

Near-square everywhere (2px): sheets, buttons, tabs, the press caption. Stamps get 3px and an inner 1px rule. Circles are reserved for hardware (eyelets, nail holes). Recurring forms: rotated-square diamonds as bullets and separators; the letterpress ornament band (diamond and dot, 28×14 repeat, 14px wide) around the hero trim; the rosette-and-quatrefoil frame (26px border-image, eight-petal rosettes at corners, four-dot quatrefoils at edge midpoints) around the picture; perforated leaf tops (4px circles every 16px, via mask) with a dashed tear line; 4px double rules for mastheads and comp strips; dashed 1px perforation rules between list items.

## Components

### Buttons
Tactile and blunt, like a printed coupon.
- **Shape:** near-square (2px), 2px border slot, Khand uppercase at 0.08em with an inline SVG icon.
- **Marigold (primary):** marigold fill, ink text; hover flips to newsprint.
- **Line (secondary):** transparent with a currentColor 2px border in newsprint; hover fills newsprint with ink text. Only on dark or printed fields.
- **Ink (on paper):** ink fill, newsprint text; hover goes vermilion. Used for pad controls and the play badge.
- **Hover / Focus / Active:** 0.15s colour swaps; active nudges 1px down; focus is a 3px marigold outline at 3px offset.

### Navigation
The hanger rail: a sticky 56px ink-violet bar with a 3px marigold underline. Wordmark in Rozha One with the surname in marigold. Links in Khand uppercase, muted verdigris, brightening to newsprint on hover; the Contact link is a marigold CTA chip. Below 760px only the wordmark and CTA remain.

### Year tabs
Khand tabular figures in a 1.5px wall-seam outline; hover brightens the border; the current year is a solid marigold chip with ink text.

### Calendar sheets (cards)
- **Corner Style:** 2px.
- **Background:** newsprint, or a full printed field (vermilion, marigold) for studio and close.
- **Shadow Strategy:** the Hang shadow only.
- **Border:** a 2px ink keyline inset from the sheet edge by the sheet margin.
- **Internal Padding:** panel scale, clamp(16px, 2.4vw, 28px) to clamp(22px, 3.4vw, 44px).

### Tear-off date pad (signature)
A stack of perforated newsprint leaves on an aged-newsprint panel. Each leaf: a Khand slug row over a 2px ink rule, a giant Rozha figure (vermilion, peacock, turmeric in rotation), a Hind line of what it means, and a dashed-rule provenance line in peacock. Leaves tear off every 3.4s, with a Tear button and a Pause toggle.

### Status stamp (signature)
A rubber stamp: Khand 700 uppercase in a 3px border with an inner 1px rule, rotated -7deg, distressed by a dot mask. Vermilion, peacock and rose variants map to status. It thumps in from 1.7× scale on a slight overshoot.

### Career sheets (signature)
On wide screens the career sections pin under the nav and each sheet flips up over the hanger on scroll (rotateX to 104deg with an ink shade and a slight stack offset behind). Elsewhere sheets swing in from -70deg as they enter.

### The press (signature)
A WebGL four-colour press on the hero banner field and picture panel. Plates print in press order Y, M, C, K at 0°, 75°, 15° and 45°, each sweeping left to right (0.9s, staggered 0.42s) and settling over 1.3s into sub-pixel misregistration. A printer's loupe (3.4× magnification, ink ring with tick marks) follows the pointer or a touch. CSS fallback: the flat field or photo with a multiply dot-screen overlay (4-5px cells) and a vermilion-to-peacock multiply tint on stills. If WebGL fails or the image is tainted, the fallback stays.

### Promo frames
Newsprint, marigold or vermilion mounts (10px) around a 16:9 screen with a 2px ink outline, a halftone overlay that lifts on hover while the still scales up slightly, and an ink Play badge that turns vermilion on hover.

## Do's and Don'ts

### Do:
- **Do** hang every substantive block on a sheet with the Hang shadow, a 2px ink keyline and 2px corners.
- **Do** keep type solid over screens: dot overlays and press canvases sit beneath the text layer.
- **Do** screen photographs and printed fields at 15°/75°/0°/45° with dots of 4-6.5px, and let plates settle slightly out of register.
- **Do** set every uppercase label in Khand at 0.06-0.12em tracking, with tabular numerals for counters.
- **Do** rotate band colours across a series of sheets and flip text to ink-violet on marigold.
- **Do** use diamonds, ornament bands, perforations and double rules as the dividers and bullets.
- **Do** give status only as a rubber stamp that states the real stage.
- **Do** provide the CSS dot-screen fallback for anything the press prints, and honour reduced motion (no sway, no flip, stamps static).

### Don't:
- **Don't** screen, halftone or misregister body copy, labels or buttons; the registration ghost belongs to display type on printed fields only.
- **Don't** use process cyan, magenta or yellow as UI fills.
- **Don't** round corners past 3px or use pill shapes; circles are for hardware only.
- **Don't** stack shadows on elements inside a sheet; depth belongs to the hanging sheet alone.
- **Don't** place long-form content directly on the peacock wall; the wall carries section heads and fine print only.
- **Don't** set Hind in uppercase or track Rozha One open.
- **Don't** use icon fonts or emoji; icons are inline 2px-stroke SVG.
