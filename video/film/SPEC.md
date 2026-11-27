# SPEC: The ledger behind the shot

GOAL:    A recruiter scrolling LinkedIn, sound off, understands in 34 s that Fowzan runs the
         business side of production (P&L, studio revenue, deals) and came up from the floor,
         and knows how to reach him.
OUTPUT:  HyperFrames, 1080 x 1350 (4:5, LinkedIn feed), 30 fps
TIME:    34 s x 30 = 1020 frames. No music bed (no catalog sign-in); SFX only, picture carries it muted.
LOOK:    Medium = a printed production ledger / call sheet.
         ground report-stock #F3F3EF flat; ruled hairlines #C8CAD0 1.5 px; ink navy #0D1B2E;
         muted ink #475266; accent vermilion #C9381C: one figure per shot, nothing else.
         End card ground = cover-navy #0D1B2E with report-stock ink, accent #FF7A5C.
         Display: Schibsted Grotesk 800, figures 300-420 px, tracking -0.05em, tabular nums.
         Labels: Schibsted 600, 30-34 px, tracking 0.06em caps. Body/line: Schibsted 600 44-56 px.
         Margins 84 px left/right, 120 px top/bottom (inside LinkedIn UI).
         No shadows, no grain, no gradients. Stamps are flat ink with 2 px off-register edge.
OBJECTS: call sheet (navy header bar, ruled rows: show | network | status stamp),
         ledger total line (double rule under, total figure), 5x5 acre grid (one square per acre),
         a sheet of 3,000 tally dots (one dot per contact), a 2014-2026 year rule with role ticks.
MOTION:  enter expo.out 0.5-0.7 s; stamps scale 1.35 -> 1 in 0.16 s power4.out + 1 frame shake;
         camera/sheet moves power2.inOut 0.6-0.8 s; exits power3.in, 40% shorter than entrances.
         Count-ups 1.4 s power2.out, tabular. Row stagger 0.18 s. Landed titles dead still.
SHOTS:
  S1 0-5.4   Call sheet. Frame 0: header "CALL SHEET · ON AIR" + first row already printed.
             Rows print 0.18 s apart, each gets an ON AIR stamp. 3.4 s: rows compress up,
             vermilion "6+" stamps huge; line "prime-time & digital shows at once". key-press per row (3), impact on 6+.
  S2 5.4-10.6 Ledger. 6+ slides to the left margin label; six cost lines draw in, a double rule
             draws under them, total counts to "₹120 Cr+"; line "annual production P&L, owned". pop on rule, impact on total.
  S3 10.6-17.4 Studio. Sheet whips up (whoosh); "LOCATION: Swastik Bhoomi, Umargaon" row; the row
             unfolds into a 5x5 grid, squares fill navy in a snake order; "25 acres" + "studio business built from zero";
             then the grid flood-fills vermilion-on-its-edge and "₹10 Cr+ revenue mandate" stamps.
  S4 17.4-22.6 Outreach. Grid squares shrink into dots; dots multiply to 3,000 across the sheet;
             count "3,000+" ; line "industry decision-makers reached". riser-light? no: soft key ticks off, one pop on landing.
  S5 22.6-27.8 Career rule 2014 -> 2026: playhead runs along, role ticks print
             (Production Coordinator 2014, Executive Producer 2020, Commercial roles 2021, Head of Commercial 2024).
             "12+ years. Floor to P&L." whoosh on start, impact on 2024.
  S6 27.8-34 End card: navy colour flood from the 2026 tick (0.4 s). Name per letter, title, email, LinkedIn.
             riser into the flood, holds 3.5 s.
BANNED:  dark void with floating bits; glow/particles; cream-paper + serif display + italic accents;
         numbered 01/02 labels; pills; three cards in a row; KPI grid; everything fading up;
         titles drifting after landing; logo docked in corner; any figure not in index.html.
QA:      t=0 (thumbnail reads: call sheet + show), 4.2 (6+), 9.6 (₹120 Cr+), 14 (grid), 16.8 (₹10 Cr+),
         21.8 (3,000+), 27 (12+ years), 33.5 (end card fully legible at 360 px).
