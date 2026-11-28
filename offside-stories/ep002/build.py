"""Offside Stories Ep 002: The Miracle of Istanbul. Graphics only.
Every cue is derived from vo/script.json (one TTS clip per phrase), so a re-voice only needs a rebuild."""
import json, re, html

S = json.load(open("vo/script.json"))
W, H = 1080, 1920
Y, R, WH, BK = "#FFE600", "#E10600", "#F5F5F0", "#0A0A0A"
LIVRED = "#C8102E"
TOTAL = 100.0

def weight(w):
    w = w.strip(".,!?…:")
    if re.match(r"^\d+–\d+$", w): return 12
    if re.match(r"^\d{4}$", w): return 14
    if w.isdigit(): return 8
    return len(re.sub(r"[^\w]", "", w)) + 2

def word_times(i):
    p = S[i]; words = p["show"].split(); ws = [weight(w) for w in words]; tot = sum(ws); t = p["start"]; out = []
    for w, k in zip(words, ws):
        d = p["dur"] * k / tot; out.append((w, t, t + d)); t += d
    return out

def P(i): return S[i]["start"]
def E(i): return S[i]["start"] + S[i]["dur"]
def WD(i, needle, end=False):
    """absolute time of the first word in phrase i containing needle"""
    for w, a, b in word_times(i):
        if needle.lower() in w.lower(): return b if end else a
    raise KeyError((i, needle))

# scene boundaries: each scene starts a little before its first phrase
def first(beat): return next(k for k, p in enumerate(S) if p["beat"] == beat)
B = {}
order = ["hook", "night", "roomA", "roomB", "turn", "six", "hero", "legacy", "brand"]
starts = {"hook": 0.0, "night": P(4) - 0.15, "roomA": P(8) - 0.2, "roomB": P(13) - 0.15, "turn": P(18) - 0.2,
          "six": P(22) - 0.15, "hero": P(26) - 0.2, "legacy": P(29) - 0.2, "brand": P(31) - 0.25}
for k, n in enumerate(order):
    a = round(starts[n], 3); b = round(starts[order[k + 1]], 3) if k + 1 < len(order) else TOTAL
    B[n] = (a, round(b - a, 3))
def L(n, t): return round(t - B[n][0], 3)  # absolute -> scene-local

BASE = f"""
    #root{{position:absolute;inset:0;overflow:hidden;background:{BK};color:{WH};font-family:Inter,sans-serif}}
    #root *{{box-sizing:border-box;margin:0}}
    #root .a{{position:absolute}}
    #root .lg{{font-family:'League Gothic',sans-serif;font-weight:400;line-height:.86;letter-spacing:.005em;text-transform:uppercase;white-space:nowrap}}
    #root .kick{{font-weight:800;font-size:36px;letter-spacing:.14em;text-transform:uppercase}}
    #root .y{{color:{Y}}} #root .r{{color:{R}}} #root .g{{color:rgba(245,245,240,.45)}}
    #root .grain{{position:absolute;inset:0;opacity:.06;background-image:radial-gradient(rgba(255,255,255,.9) 1px,transparent 1.4px);background-size:7px 7px}}
    #root .nc{{position:absolute;left:120px;display:flex;align-items:stretch;height:84px}}
    #root .nc b{{width:12px;background:{Y};display:block}}
    #root .nc span{{background:{WH};color:{BK};font-weight:900;font-size:40px;letter-spacing:.02em;padding:16px 22px 0;text-transform:uppercase;white-space:nowrap}}
    #root .nc i{{background:{BK};color:{WH};font-style:normal;font-weight:700;font-size:28px;letter-spacing:.12em;padding:26px 20px 0;text-transform:uppercase;border:3px solid {WH};border-left:0;white-space:nowrap}}
"""
def namecard(id_, name, club, top):
    return f'<div class="nc" id="{id_}" style="top:{top}px"><b></b><span>{html.escape(name)}</span><i>{html.escape(club)}</i></div>'
def nc_in(id_, t):
    return (f'tl.fromTo("#{id_} b", {{ scaleY: 0, transformOrigin: "50% 100%" }}, {{ scaleY: 1, duration: 0.18, ease: "expo.out" }}, {t:.3f});\n'
            f'    tl.fromTo("#{id_} span, #{id_} i", {{ clipPath: "inset(0 100% 0 0)" }}, {{ clipPath: "inset(0 0% 0 0)", duration: 0.35, ease: "expo.out", stagger: 0.08 }}, {t + 0.08:.3f});')
def nc_out(id_, t):
    return f'tl.to("#{id_}", {{ opacity: 0, x: -30, duration: 0.15, ease: "power2.in" }}, {t:.3f});'
def cut_in(sel, t): return f'tl.fromTo("{sel}", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.01 }}, {t:.3f});'
def cut_out(sel, t): return f'tl.set("{sel}", {{ opacity: 0 }}, {t:.3f});'
def blur_in(sel, t, d=0.2): return f'tl.fromTo("{sel}", {{ opacity: 0, filter: "blur(10px)" }}, {{ opacity: 1, filter: "blur(0px)", duration: {d}, ease: "power4.out" }}, {t:.3f});'
def blur_out(sel, t): return f'tl.to("{sel}", {{ opacity: 0, filter: "blur(10px)", duration: 0.15, ease: "power2.in" }}, {t:.3f});'
def stamp(sel, t, rot=-4):
    return (f'tl.fromTo("{sel}", {{ opacity: 0, scale: 1.5, rotation: {rot} }}, {{ opacity: 1, scale: 1, rotation: {rot}, duration: 0.16, ease: "power4.out" }}, {t:.3f});\n'
            f'    tl.fromTo("{sel}", {{ x: 0 }}, {{ x: 7, duration: 0.033, yoyo: true, repeat: 3, ease: "none" }}, {t + 0.16:.3f});')

def scene(cid, css, body, js):
    return f"""<template>
  <style>{BASE}{css}
  </style>
  <div id="root" data-composition-id="{cid}" data-width="{W}" data-height="{H}">
    <div class="grain"></div>
{body}
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
{js}
    window.__timelines["{cid}"] = tl;
  </script>
</template>
"""

PITCH_SVG = """<svg class="a pitch" style="left:0;top:0" width="1080" height="1920" viewBox="0 0 1080 1920"><g class="pg">
  <rect class="pl" x="150" y="230" width="780" height="1460"/><line class="pl" x1="150" y1="960" x2="930" y2="960"/>
  <circle class="pl" cx="540" cy="960" r="130"/><rect class="pl" x="330" y="230" width="420" height="250"/>
  <rect class="pl" x="330" y="1440" width="420" height="250"/></g></svg>"""
PITCH_CSS = f"#root .pitch *{{fill:none;stroke:{WH};stroke-width:4;opacity:.18}}"

# ------------------------------------------------------------------ HOOK
n = "hook"
hook = scene(n, PITCH_CSS + f"""
    #h-k{{left:120px;top:330px}}
    #h-30{{left:116px;top:390px;font-size:520px}}
    #h-dn{{left:120px;top:830px;font-size:200px}}
    #h-cl{{left:120px;top:390px;font-size:220px}}
    #h-board{{left:120px;top:420px;width:840px;height:520px;background:#111;border:4px solid #262626}}
    #h-bl{{left:36px;top:28px;font-weight:800;font-size:32px;letter-spacing:.14em;color:{Y}}}
    #h-bt{{left:36px;top:110px;width:768px;display:flex;justify-content:space-between;align-items:center}}
    #h-bt .t{{font-family:'League Gothic';font-size:120px;line-height:1}}
    #h-bt .s{{font-family:'League Gothic';font-size:300px;line-height:.9}}
    #h-bs{{left:36px;top:430px;font-weight:700;font-size:30px;letter-spacing:.1em;color:rgba(245,245,240,.6)}}
    #h-45{{left:116px;top:400px;font-size:300px}}
    #h-q{{left:120px;top:690px;font-size:150px}}
""", f"""
    {PITCH_SVG}
    <div id="h-a" class="a" style="inset:0">
      <div id="h-k" class="a kick y">Champions League final · half-time</div>
      <div id="h-30" class="a lg">3–0</div>
      <div id="h-dn" class="a lg y">Down.</div>
    </div>
    <div id="h-cl" class="a lg">Champions<br>League<br><span class="y">final.</span></div>
    <div id="h-board" class="a">
      <div id="h-bl" class="a">HALF-TIME</div>
      <div id="h-bt" class="a"><span class="t">LIV</span><span class="s">0–3</span><span class="t">MIL</span></div>
      <div id="h-bs" class="a">LIVERPOOL · AC MILAN</div>
    </div>
    <div id="h-45" class="a lg"><span class="y">45</span> minutes left.</div>
    <div id="h-q" class="a lg">Still believe?</div>
""", f"""
    tl.fromTo(".pitch .pl", {{ strokeDasharray: 2400, strokeDashoffset: 1200 }}, {{ strokeDashoffset: 0, duration: 1.4, ease: "power2.out", stagger: 0.05 }}, 0);
    tl.fromTo("#h-30", {{ scale: 1.06, transformOrigin: "0 50%" }}, {{ scale: 1, duration: 0.6, ease: "expo.out" }}, 0);
    tl.fromTo("#h-a", {{ x: 0, filter: "blur(0px)" }}, {{ x: -1150, filter: "blur(18px)", duration: 0.26, ease: "power3.in" }}, {L(n, P(1)) - 0.27});
    {cut_out("#h-a", L(n, P(1)))}
    tl.fromTo("#h-cl", {{ opacity: 0, x: 900, filter: "blur(18px)" }}, {{ opacity: 1, x: 0, filter: "blur(0px)", duration: 0.4, ease: "expo.out" }}, {L(n, P(1))});
    {cut_out("#h-cl, .pitch", L(n, WD(2, "3–0")) - 0.05)}
    tl.fromTo("#h-board", {{ opacity: 0, scale: 1.08 }}, {{ opacity: 1, scale: 1, duration: 0.25, ease: "expo.out" }}, {L(n, WD(2, "3–0")) - 0.05});
    {cut_out("#h-board", L(n, P(3)))}
    {cut_in("#h-45", L(n, P(3)))}
    {blur_in("#h-q", L(n, WD(3, "believe")))}
""")

# ------------------------------------------------------------------ NIGHT
n = "night"
GX0, GX1, GY = 140, 940, 900
def gx(m): return GX0 + (GX1 - GX0) * m / 45
night = scene(n, f"""
    #n-k{{left:120px;top:420px}}
    #n-vs{{left:120px;top:470px;font-size:130px}}
    #n-sc{{left:116px;top:400px;font-size:400px}}
    #n-bar{{left:{GX0}px;top:{GY}px;width:{GX1-GX0}px;height:6px;background:rgba(245,245,240,.25)}}
    #n-fill{{left:{GX0}px;top:{GY}px;width:{GX1-GX0}px;height:6px;background:{WH};transform-origin:0 50%}}
    #root .mk{{position:absolute;top:{GY-34}px;width:4px;height:74px;background:{WH}}}
    #root .ml{{position:absolute;top:{GY+52}px;font-weight:800;font-size:30px;letter-spacing:.06em;transform:translateX(-50%)}}
    #n-t0,#n-t45{{top:{GY+52}px;font-weight:700;font-size:28px;color:rgba(245,245,240,.5)}}
    #n-head{{left:120px;top:400px;font-size:220px}}
""", f"""
    <div id="n-intro" class="a" style="inset:0">
      <div id="n-k" class="a kick y">25 May 2005 · Istanbul</div>
      <div id="n-vs" class="a lg">Liverpool <span class="g">v</span> AC Milan</div>
    </div>
    <div id="n-sc" class="a lg"><span id="n-s">0–1</span></div>
    <div id="n-bar" class="a"></div><div id="n-fill" class="a"></div>
    <div id="n-t0" class="a" style="left:{GX0}px">0'</div><div id="n-t45" class="a" style="left:{GX1-40}px">45'</div>
    <div class="mk" id="n-m1" style="left:{gx(1)-2}px"></div><div class="mk" id="n-m2" style="left:{gx(39)-2}px"></div><div class="mk" id="n-m3" style="left:{gx(44)-2}px"></div>
    {namecard("n-c1", "Paolo Maldini", "AC Milan · 1'", 1000)}
    {namecard("n-c2", "Hernán Crespo", "AC Milan · 39', 44'", 1000)}
    <div id="n-head" class="a lg">The perfect<br>night for<br><span class="y">Milan.</span></div>
""", f"""
    {blur_in("#n-k", L(n, P(4)))}
    tl.fromTo("#n-vs", {{ opacity: 0, color: "#333" }}, {{ opacity: 1, color: "{WH}", duration: 0.3 }}, {L(n, WD(4, "Liverpool"))});
    tl.fromTo("#n-bar, #n-t0, #n-t45", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.2 }}, {L(n, WD(4, "Liverpool"))});
    tl.fromTo("#n-fill", {{ scaleX: 0 }}, {{ scaleX: 1, duration: {E(7) - P(5) + 0.2:.2f}, ease: "none" }}, {L(n, P(5)) - 0.1});
    {blur_out("#n-intro", L(n, P(5)) - 0.15)}
    tl.fromTo("#n-sc", {{ opacity: 0, scale: 1.3, transformOrigin: "0 50%" }}, {{ opacity: 1, scale: 1, duration: 0.18, ease: "power4.out" }}, {L(n, WD(5, "scored"))});
    const sc = document.getElementById("n-s"), st = {{ v: 0 }};
    tl.fromTo(st, {{ v: 0 }}, {{ v: 1, duration: {TOTAL}, ease: "none", onUpdate: () => {{ const t = st.v * {TOTAL};
      sc.textContent = t < {L(n, WD(6, "twice")) :.3f} ? (t < {L(n, WD(6, "struck")):.3f} ? "0–1" : "0–2") : "0–3"; }} }}, 0);
    tl.fromTo("#n-m1", {{ scaleY: 0 }}, {{ scaleY: 1, duration: 0.2, ease: "expo.out" }}, {L(n, WD(5, "scored"))});
    {nc_in("n-c1", L(n, WD(5, "Maldini")))}
    {nc_out("n-c1", L(n, P(6)) - 0.1)}
    tl.fromTo("#n-sc", {{ scale: 1.12 }}, {{ scale: 1, duration: 0.18, ease: "power4.out" }}, {L(n, WD(6, "struck"))});
    tl.fromTo("#n-m2", {{ scaleY: 0 }}, {{ scaleY: 1, duration: 0.2, ease: "expo.out" }}, {L(n, WD(6, "struck"))});
    {nc_in("n-c2", L(n, WD(6, "Crespo")))}

    tl.fromTo("#n-sc", {{ scale: 1.12 }}, {{ scale: 1, duration: 0.18, ease: "power4.out" }}, {L(n, WD(6, "twice"))});
    tl.fromTo("#n-m3", {{ scaleY: 0 }}, {{ scaleY: 1, duration: 0.2, ease: "expo.out" }}, {L(n, WD(6, "twice"))});
    {nc_out("n-c2", L(n, P(7)) - 0.1)}
    tl.to("#n-sc", {{ y: -1300, filter: "blur(16px)", duration: 0.28, ease: "power3.in" }}, {L(n, P(7)) - 0.3});
    {cut_out("#n-sc", L(n, P(7)) - 0.01)}
    tl.fromTo("#n-head", {{ opacity: 0, y: 1300, filter: "blur(16px)" }}, {{ opacity: 1, y: 0, filter: "blur(0px)", duration: 0.45, ease: "expo.out" }}, {L(n, P(7))});
    tl.to("#n-bar, #n-fill, #n-t0, #n-t45, .mk", {{ opacity: 0.25, duration: 0.3 }}, {L(n, P(7))});
""")

# ------------------------------------------------------------------ ROOM A
n = "roomA"
roomA = scene(n, f"""
    #ra-1{{left:120px;top:400px;font-size:200px}}
    #ra-2{{left:116px;top:390px;font-size:420px}}
    #ra-2l{{left:120px;top:760px;font-weight:900;font-size:56px;letter-spacing:.02em;text-transform:uppercase}}
    #ra-3{{left:120px;top:400px;font-size:190px}}
    #ra-bn{{left:120px;top:380px;font-size:250px}}
    #ra-bnk{{left:120px;top:830px;font-weight:800;font-size:36px;letter-spacing:.12em;color:{Y};text-transform:uppercase}}
    #ra-clk{{left:116px;top:390px;font-size:330px}}
    #ra-cl{{left:120px;top:700px;font-size:140px}}
""", f"""
    <div id="ra-1" class="a lg">Half-time.<br><span class="g">3–0 down.</span></div>
    <div id="ra-2" class="a lg">45</div>
    <div id="ra-2l" class="a">Minutes from defeat</div>
    <div id="ra-3" class="a lg">The dream<br>was slipping<br><span class="g">away.</span></div>
    <div id="ra-bn" class="a lg">Rafael<br><span class="y">Benítez</span></div>
    <div id="ra-bnk" class="a">Liverpool manager</div>
    <div id="ra-clk" class="a lg"><span id="ra-c">15:00</span></div>
    <div id="ra-cl" class="a lg">Minutes to change<br><span class="y">everything.</span></div>
""", f"""
    tl.fromTo("#ra-1", {{ opacity: 0, color: "#2a2a2a" }}, {{ opacity: 1, color: "{WH}", duration: 0.6, ease: "power2.out" }}, {L(n, P(8))});
    {blur_out("#ra-1", L(n, P(9)) - 0.15)}
    tl.fromTo("#ra-2", {{ opacity: 0, scale: 1.2, transformOrigin: "0 50%" }}, {{ opacity: 1, scale: 1, duration: 0.25, ease: "expo.out" }}, {L(n, WD(9, "Forty-five"))});
    {blur_in("#ra-2l", L(n, WD(9, "Forty-five")) + 0.2)}
    {blur_out("#ra-2, #ra-2l", L(n, P(10)) - 0.15)}
    tl.fromTo("#ra-3", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.3 }}, {L(n, P(10))});
    tl.to("#ra-3", {{ opacity: 0.0, filter: "blur(12px)", duration: 0.6, ease: "power2.in" }}, {L(n, P(11)) - 0.6});
    tl.fromTo("#ra-bn", {{ opacity: 0, x: -40, filter: "blur(10px)" }}, {{ opacity: 1, x: 0, filter: "blur(0px)", duration: 0.35, ease: "expo.out" }}, {L(n, WD(11, "Rafael"))});
    {blur_in("#ra-bnk", L(n, WD(11, "manager")))}
    tl.to("#ra-bn, #ra-bnk", {{ y: -1300, filter: "blur(16px)", duration: 0.26, ease: "power3.in" }}, {L(n, P(12)) - 0.28});
    {cut_out("#ra-bn, #ra-bnk", L(n, P(12)))}
    {cut_in("#ra-clk", L(n, P(12)))}
    const ck = document.getElementById("ra-c"), cs = {{ v: 900 }};
    tl.fromTo(cs, {{ v: 900 }}, {{ v: 0, duration: {B[n][1] - L(n, P(12)) - 0.3:.2f}, ease: "power1.in", onUpdate: () => {{ const s = Math.max(0, Math.round(cs.v)); ck.textContent = String(Math.floor(s / 60)).padStart(2, "0") + ":" + String(s % 60).padStart(2, "0"); }} }}, {L(n, P(12))});
    {blur_in("#ra-cl", L(n, P(12)) + 0.35)}
""")

# ------------------------------------------------------------------ ROOM B
n = "roomB"
roomB = scene(n, f"""
    #rb-1{{left:120px;top:400px;font-size:200px}}
    #rb-2{{left:120px;top:400px;font-size:200px}}
    #rb-3{{left:120px;top:400px;font-size:220px}}
    #rb-tun{{left:0;top:0;width:1080px;height:1920px;background:{WH};clip-path:inset(0 0 0 0)}}
    #rb-cor{{left:0;top:0}}
    #rb-cor line{{stroke:rgba(245,245,240,.35);stroke-width:3}}
    #rb-dark{{inset:0;background:{BK}}}
    #rb-4{{left:120px;top:960px;font-size:100px;z-index:3}}
    #rb-5{{left:120px;top:420px;font-size:230px;color:{BK};z-index:3}}
    #rb-6{{left:120px;top:900px;width:780px;font-weight:900;font-size:46px;line-height:1.15;color:{BK};text-transform:uppercase;z-index:3}}
""", f"""
    <div id="rb-1" class="a lg">No guarantee.</div>
    <div id="rb-2" class="a lg">No easy<br>answers.</div>
    <div id="rb-3" class="a lg">The game<br>wasn't<br><span class="y">over.</span></div>
    <svg id="rb-cor" class="a" width="1080" height="1920"><line id="rb-l1"/><line id="rb-l2"/><line id="rb-l3"/><line id="rb-l4"/></svg>
    <div id="rb-tun" class="a"></div>
    <div id="rb-4" class="a lg g">Not to save a final.</div>
    <div id="rb-5" class="a lg">To make<br>history.</div>
    <div id="rb-6" class="a">The second half was about to change football history.</div>
""", f"""
    {cut_in("#rb-1", L(n, P(13)))}
    {cut_out("#rb-1", L(n, WD(13, "No")))}
    {cut_in("#rb-2", L(n, WD(13, "No")))}
    {cut_out("#rb-2", L(n, P(14)))}
    tl.fromTo("#rb-3", {{ opacity: 0, color: "#2a2a2a" }}, {{ opacity: 1, color: "{WH}", duration: 0.5 }}, {L(n, P(14))});
    {blur_out("#rb-3", L(n, P(15)) - 0.1)}
    // the tunnel mouth: light at the end, growing as they walk out
    // corridor: lines from the frame corners to a lit doorway that grows as they walk out
    const CX = 540, CY = 700, DW = 220, DH = 330, tun = document.getElementById("rb-tun");
    const ls = ["rb-l1", "rb-l2", "rb-l3", "rb-l4"].map(id => document.getElementById(id));
    const FC = [[0, 300], [1080, 300], [0, 1920], [1080, 1920]];
    const dr = {{ s: 0.25 }};
    const drawT = () => {{ const w = DW * dr.s, h = DH * dr.s, x0 = CX - w, x1 = CX + w, y0 = CY - h, y1 = CY + h;
      const ins = [Math.max(0, y0), Math.max(0, 1080 - x1), Math.max(0, 1920 - y1), Math.max(0, x0)];
      tun.style.clipPath = `inset(${{ins[0]}}px ${{ins[1]}}px ${{ins[2]}}px ${{ins[3]}}px)`;
      const DC = [[x0, y0], [x1, y0], [x0, y1], [x1, y1]];
      ls.forEach((l, k) => {{ l.setAttribute("x1", FC[k][0]); l.setAttribute("y1", FC[k][1]); l.setAttribute("x2", DC[k][0]); l.setAttribute("y2", DC[k][1]); }}); }};
    tl.fromTo("#rb-tun, #rb-cor", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.4 }}, {L(n, P(15))});
    tl.fromTo(dr, {{ s: 0.25 }}, {{ s: 0.7, duration: {P(17) - P(15) - 0.6:.2f}, ease: "power1.in", onUpdate: drawT }}, {L(n, P(15))});
    tl.fromTo(dr, {{ s: 0.7 }}, {{ s: 6, duration: 0.45, ease: "power3.in", onUpdate: drawT, immediateRender: false }}, {L(n, P(17)) - 0.3});
    tl.to("#rb-cor", {{ opacity: 0, duration: 0.2 }}, {L(n, P(17)) - 0.1});
    tl.fromTo("#rb-4", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.3 }}, {L(n, P(16))});
    {cut_out("#rb-4", L(n, P(17)))}
    tl.fromTo("#rb-5", {{ opacity: 0, filter: "blur(12px)" }}, {{ opacity: 1, filter: "blur(0px)", duration: 0.3, ease: "power4.out" }}, {L(n, WD(17, "make"))});
    {blur_in("#rb-6", L(n, E(17)) + 0.1)}
""")

# ------------------------------------------------------------------ TURN (Gerrard header, 54')
n = "turn"
# pitch: attacking upward; goal at top (y 230..). Riise crosses from the left.
turn = scene(n, PITCH_CSS + f"""
    #t-wh{{inset:0;background:{WH}}}
    #t-goal{{left:440px;top:196px;width:200px;height:36px;border:5px solid {WH};border-bottom:0}}
    #t-ball{{left:0;top:0;width:30px;height:30px;border-radius:50%;background:{WH}}}
    #t-ger{{left:0;top:0;width:60px;height:60px;border-radius:50%;background:{LIVRED};border:4px solid {WH};font-weight:900;font-size:30px;display:flex;align-items:center;justify-content:center}}
    #t-cross{{left:0;top:0}}
    #t-cross path{{fill:none;stroke:{Y};stroke-width:6;stroke-dasharray:14 12}}
    #t-min{{left:120px;top:300px;font-size:120px;z-index:3}}
    #t-sc{{left:116px;top:560px;font-size:330px;z-index:3}}
    #t-head{{left:120px;top:420px;font-size:250px;z-index:3}}
""", f"""
    {PITCH_SVG}
    <div id="t-goal" class="a"></div>
    <svg id="t-cross" class="a" width="1080" height="1920"><path id="t-cp" d="M 170 640 Q 420 320 650 380"/><path id="t-hp" d="M 650 380 L 590 214"/></svg>
    <div id="t-ger" class="a">8</div>
    <div id="t-ball" class="a"></div>
    {namecard("t-nc", "Steven Gerrard", "Liverpool FC · 54'", 1000)}
    <div id="t-sc" class="a lg"><span class="y">1</span>–3</div>
    <div id="t-head" class="a lg">The<br>comeback<br><span class="y">begins.</span></div>
    <div id="t-wh" class="a"></div>
""", f"""
    tl.fromTo("#t-wh", {{ opacity: 1 }}, {{ opacity: 0, duration: 0.45, ease: "power2.out" }}, 0);
    tl.fromTo(".pitch .pl", {{ strokeDasharray: 2400, strokeDashoffset: 1600 }}, {{ strokeDashoffset: 0, duration: 1.0, ease: "power2.out", stagger: 0.04 }}, 0.2);
    tl.fromTo(".pg", {{ scale: 1, transformOrigin: "540px 300px" }}, {{ scale: 1.35, duration: {L(n, E(19)):.2f}, ease: "power1.inOut" }}, 0.2);
    tl.fromTo("#t-goal", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.3 }}, 0.6);
    // the cross from the left, Gerrard arrives, header
    const cp = document.getElementById("t-cp"), hp = document.getElementById("t-hp");
    const cl = cp.getTotalLength(), hl = hp.getTotalLength();
    gsap.set(cp, {{ strokeDasharray: cl, strokeDashoffset: cl }}); gsap.set(hp, {{ strokeDasharray: hl, strokeDashoffset: hl }});
    const tc0 = {L(n, P(19)):.3f}, tc1 = {L(n, WD(19, "headed")):.3f}, th1 = {L(n, WD(19, "home", True)):.3f};
    tl.fromTo(cp, {{ strokeDashoffset: cl }}, {{ strokeDashoffset: 0, duration: tc1 - tc0, ease: "none" }}, tc0);
    tl.fromTo(hp, {{ strokeDashoffset: hl }}, {{ strokeDashoffset: 0, duration: th1 - tc1, ease: "power2.in" }}, tc1);
    const bl = {{ t: 0 }}, ball = document.getElementById("t-ball");
    const place = () => {{ const t = bl.t; let pt;
      if (t <= 1) pt = cp.getPointAtLength(cl * t); else pt = hp.getPointAtLength(hl * Math.min(1, t - 1));
      ball.style.transform = `translate(${{pt.x - 15}}px, ${{pt.y - 15}}px)`; }};
    tl.fromTo(bl, {{ t: 0 }}, {{ t: 1, duration: tc1 - tc0, ease: "none", onUpdate: place }}, tc0);
    tl.fromTo(bl, {{ t: 1 }}, {{ t: 2, duration: th1 - tc1, ease: "power2.in", onUpdate: place, immediateRender: false }}, tc1);
    tl.fromTo("#t-ball", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.1 }}, tc0);
    tl.fromTo("#t-ger", {{ x: 600, y: 760, opacity: 0 }}, {{ x: 623, y: 353, opacity: 1, duration: tc1 - tc0 + 0.1, ease: "power2.out" }}, tc0 - 0.1);
    tl.fromTo("#t-goal", {{ borderColor: "{WH}" }}, {{ borderColor: "{Y}", duration: 0.1 }}, th1);
    {nc_in("t-nc", L(n, WD(19, "Gerrard")))}
    // score lands
    tl.to(".pitch, #t-goal, #t-cross, #t-ball, #t-ger", {{ opacity: 0, duration: 0.3 }}, th1 + 0.2);
    {nc_out("t-nc", L(n, P(21)) - 0.2)}
    tl.fromTo("#t-sc", {{ opacity: 0, scale: 1.3, transformOrigin: "0 50%" }}, {{ opacity: 1, scale: 1, duration: 0.2, ease: "power4.out" }}, th1 + 0.25);
    {cut_out("#t-sc", L(n, P(21)))}
    tl.to(".pitch, #t-goal, #t-cross, #t-ball, #t-ger", {{ opacity: 0, duration: 0.2 }}, {L(n, P(21))});
    tl.fromTo("#t-head", {{ opacity: 0, x: 900, filter: "blur(16px)" }}, {{ opacity: 1, x: 0, filter: "blur(0px)", duration: 0.4, ease: "expo.out" }}, {L(n, P(21))});
""")

# ------------------------------------------------------------------ SIX MINUTES
n = "six"
six = scene(n, f"""
    #x-box{{left:150px;top:420px;width:780px;height:520px}}
    #x-box *{{fill:none;stroke:{WH};stroke-width:4;opacity:.25}}
    #x-box .gl{{opacity:1;stroke-width:6}}
    #x-shot{{left:0;top:0}}
    #x-shot path{{fill:none;stroke:{Y};stroke-width:7}}
    #root .ball{{left:0;top:0;width:28px;height:28px;border-radius:50%;background:{WH}}}
    #x-kp{{left:0;top:0;width:44px;height:44px;border-radius:50%;background:{WH};border:4px solid {BK}}}
    #x-saved{{left:620px;top:470px;font-family:'League Gothic';font-size:80px;line-height:1;color:{R};border:5px solid {R};padding:4px 16px 0;text-transform:uppercase;z-index:3}}
    #x-sc{{left:116px;top:400px;font-size:330px;z-index:3}}
    #x-3g{{left:116px;top:400px;font-size:330px}}
    #x-6m{{left:116px;top:400px;font-size:330px}}
    #x-fl{{inset:0;background:{Y}}}
    #x-33{{left:0;top:330px;width:1080px;text-align:center;font-size:640px;color:{BK}}}
    #x-33k{{left:0;top:900px;width:1080px;text-align:center;font-weight:900;font-size:48px;letter-spacing:.1em;color:{BK}}}
""", f"""
    <svg id="x-box" class="a" width="780" height="520" viewBox="0 0 780 520">
      <line class="gl" x1="290" y1="6" x2="490" y2="6"/>
      <rect x="10" y="6" width="760" height="300"/><rect x="200" y="6" width="380" height="110"/><circle cx="390" cy="220" r="5"/>
    </svg>
    <svg id="x-shot" class="a" width="1080" height="1920"><path id="x-p1" d="M 700 900 Q 620 600 615 432"/><path id="x-p2" d="M 540 640 L 560 470"/><path id="x-p3" d="M 560 470 L 520 430"/></svg>
    <div id="x-b1" class="a ball"></div><div id="x-b2" class="a ball"></div>
    <div id="x-kp" class="a"></div>
    <div id="x-saved" class="a">Saved</div>
    {namecard("x-n1", "Vladimír Šmicer", "Liverpool FC · 56'", 1000)}
    {namecard("x-n2", "Xabi Alonso", "Liverpool FC · 60'", 1000)}
    <div id="x-sc" class="a lg"><span id="x-s">2–3</span></div>
    <div id="x-3g" class="a lg"><span class="y">3</span> goals.</div>
    <div id="x-6m" class="a lg"><span class="y">6</span> minutes.</div>
    <div id="x-fl" class="a"></div>
    <div id="x-33" class="a lg">3–3</div>
    <div id="x-33k" class="a">LIVERPOOL 3–3 AC MILAN · 60'</div>
""", f"""
    const p1 = document.getElementById("x-p1"), p2 = document.getElementById("x-p2"), p3 = document.getElementById("x-p3");
    [p1, p2, p3].forEach(p => {{ const l = p.getTotalLength(); gsap.set(p, {{ strokeDasharray: l, strokeDashoffset: l }}); }});
    const along = (path, el, o) => {{ const l = path.getTotalLength(); return () => {{ const pt = path.getPointAtLength(l * Math.min(1, Math.max(0, o.t))); el.style.transform = `translate(${{pt.x - 14}}px, ${{pt.y - 14}}px)`; }}; }};
    tl.fromTo("#x-box", {{ opacity: 0, y: 40 }}, {{ opacity: 1, y: 0, duration: 0.35, ease: "expo.out" }}, 0);
    // Smicer from distance
    const s1 = {L(n, P(22)) + 0.2:.3f}, s1e = {L(n, WD(22, "3–2")):.3f};
    tl.fromTo(p1, {{ strokeDashoffset: p1.getTotalLength() }}, {{ strokeDashoffset: 0, duration: s1e - s1, ease: "power2.in" }}, s1);
    const o1 = {{ t: 0 }}, b1 = document.getElementById("x-b1");
    tl.fromTo(o1, {{ t: 0 }}, {{ t: 1, duration: s1e - s1, ease: "power2.in", onUpdate: along(p1, b1, o1) }}, s1);
    tl.fromTo("#x-b1", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.05 }}, s1);
    {nc_in("x-n1", L(n, WD(22, "made")) - 0.4)}
    tl.fromTo("#x-sc", {{ opacity: 0, scale: 1.3, transformOrigin: "0 50%" }}, {{ opacity: 1, scale: 1, duration: 0.2, ease: "power4.out" }}, s1e);
    tl.to("#x-box", {{ opacity: 0.15, duration: 0.2 }}, s1e);
    tl.to("#x-shot path, #x-b1", {{ opacity: 0.15, duration: 0.2 }}, s1e);
    {nc_out("x-n1", L(n, P(23)) - 0.1)}
    {cut_out("#x-sc", L(n, P(23)))}
    // Alonso: penalty saved, rebound in
    tl.to("#x-box, #x-shot path", {{ opacity: 1, duration: 0.15 }}, {L(n, P(23))});
    tl.set("#x-p1, #x-b1", {{ opacity: 0 }}, {L(n, P(23))});
    {nc_in("x-n2", L(n, WD(23, "Alonso")))}
    const k1 = {L(n, WD(24, "penalty")):.3f}, k2 = {L(n, WD(24, "saved")) + 0.1:.3f}, k3 = {L(n, WD(24, "buried")):.3f}, k4 = {L(n, WD(24, "rebound", True)):.3f};
    tl.set("#x-kp", {{ x: 516, y: 418 }}, 0); tl.fromTo("#x-kp", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.1 }}, k1);
    tl.to("#x-kp", {{ x: 538, y: 448, duration: k2 - k1, ease: "power3.in" }}, k1);
    tl.fromTo(p2, {{ strokeDashoffset: p2.getTotalLength() }}, {{ strokeDashoffset: 0, duration: k2 - k1, ease: "power2.in" }}, k1);
    const o2 = {{ t: 0 }}, b2 = document.getElementById("x-b2");
    tl.fromTo("#x-b2", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.05 }}, k1);
    tl.fromTo(o2, {{ t: 0 }}, {{ t: 1, duration: k2 - k1, ease: "power2.in", onUpdate: along(p2, b2, o2) }}, k1);
    tl.fromTo("#x-saved", {{ opacity: 0, scale: 1.5, rotation: -5 }}, {{ opacity: 1, scale: 1, rotation: -5, duration: 0.16, ease: "power4.out" }}, k2);
    {cut_out("#x-saved", L(n, WD(24, "buried")))}
    const o3 = {{ t: 0 }};
    tl.fromTo(p3, {{ strokeDashoffset: p3.getTotalLength() }}, {{ strokeDashoffset: 0, duration: k4 - k3, ease: "power3.in" }}, k3);
    tl.fromTo(o3, {{ t: 0 }}, {{ t: 1, duration: k4 - k3, ease: "power3.in", onUpdate: along(p3, b2, o3), immediateRender: false }}, k3);
    {nc_out("x-n2", L(n, P(25)) - 0.1)}
    tl.to("#x-box, #x-shot, #x-kp, #x-b2", {{ opacity: 0, duration: 0.15 }}, {L(n, P(25)) - 0.1});
    {cut_in("#x-3g", L(n, P(25)))}
    {cut_out("#x-3g", L(n, WD(25, "six")))}
    tl.fromTo("#x-6m", {{ opacity: 0, scale: 1.15, transformOrigin: "0 50%" }}, {{ opacity: 1, scale: 1, duration: 0.2, ease: "expo.out" }}, {L(n, WD(25, "six"))});
    {cut_out("#x-6m", L(n, WD(25, "score")) - 0.2)}
    // payoff: yellow flood, 3-3
    tl.fromTo("#x-fl", {{ clipPath: "inset(48% 48% 48% 48%)", opacity: 0 }}, {{ clipPath: "inset(0% 0% 0% 0%)", opacity: 1, duration: 0.4, ease: "power3.inOut" }}, {L(n, WD(25, "score")) - 0.2});
    tl.fromTo("#x-33", {{ opacity: 0, scale: 1.4, filter: "blur(14px)" }}, {{ opacity: 1, scale: 1, filter: "blur(0px)", duration: 0.35, ease: "expo.out" }}, {L(n, WD(25, "3–3")) - 0.1});
    {blur_in("#x-33k", L(n, WD(25, "3–3")) + 0.3)}
""")

# ------------------------------------------------------------------ HERO (extra time, Dudek, shootout)
n = "hero"
KICKS = [("MIL", "Serginho", 0), ("LIV", "Hamann", 1), ("MIL", "Pirlo", 0), ("LIV", "Cissé", 1), ("MIL", "Tomasson", 1),
         ("LIV", "Riise", 0), ("MIL", "Kaká", 1), ("LIV", "Šmicer", 1), ("MIL", "Shevchenko", 0)]
k_t0 = P(28) + 0.2; k_t1 = E(28) + 0.55
def krow(team):
    cells = []; c = 0
    for k, (tm, nm, ok) in enumerate(KICKS):
        if tm != team: continue
        cells.append(f'<div class="kc" id="k{k}"><b class="{"ok" if ok else "no"}">{"●" if ok else "✕"}</b></div>'); c += 1
    while c < 5: cells.append('<div class="kc empty"><b></b></div>'); c += 1
    return "".join(cells)
hero = scene(n, f"""
    #e-et{{left:116px;top:400px;font-size:300px}}
    #e-clk{{left:120px;top:930px;font-size:120px}}
    #e-goal{{left:190px;top:470px;width:700px;height:260px;border:8px solid {WH};border-bottom:0}}
    #e-net{{left:198px;top:478px;width:684px;height:252px;background-image:linear-gradient(rgba(245,245,240,.12) 2px,transparent 2px),linear-gradient(90deg,rgba(245,245,240,.12) 2px,transparent 2px);background-size:34px 34px}}
    #e-line{{left:120px;top:730px;width:840px;height:6px;background:{WH}}}
    #root .sx{{position:absolute;font-family:'League Gothic';font-size:120px;line-height:1;color:{Y}}}
    #e-117{{left:120px;top:790px;font-weight:900;font-size:40px;letter-spacing:.06em;text-transform:uppercase}}
    #e-117 span{{color:{Y}}}
    #e-so{{left:120px;top:400px;width:840px}}
    #e-so h5{{font-weight:900;font-size:36px;letter-spacing:.14em;color:{Y};margin-bottom:26px}}
    #root .krow{{display:flex;align-items:center;gap:14px;margin-bottom:34px}}
    #root .krow > span{{width:120px;font-family:'League Gothic';font-size:80px;line-height:1}}
    #root .kc{{width:126px;text-align:center}}
    #root .kc b{{display:flex;align-items:center;justify-content:center;width:96px;height:96px;margin:0 auto;border:4px solid rgba(245,245,240,.35);border-radius:50%;font-size:54px;font-weight:900}}
    #root .kc b.ok{{background:{WH};color:{BK};border-color:{WH}}}
    #root .kc b.no{{color:{R};border-color:{R}}}
    #root .kc i{{display:block;font-style:normal;font-weight:700;font-size:22px;margin-top:8px;color:rgba(245,245,240,.7);white-space:nowrap}}
    #e-win{{left:116px;top:780px;font-size:200px}}
""", f"""
    <div id="e-et" class="a lg">Extra<br>time</div>
    <div id="e-clk" class="a lg g"><span id="e-c">90'</span></div>
    <div id="e-dd" class="a" style="inset:0">
      <div id="e-net" class="a"></div><div id="e-goal" class="a"></div><div id="e-line" class="a"></div>
      <div class="sx" id="e-x1" style="left:430px;top:560px">✕</div>
      <div class="sx" id="e-x2" style="left:560px;top:600px">✕</div>
      <div id="e-117" class="a"><span>117'</span> · Double save from Shevchenko</div>
    </div>
    {namecard("e-nc", "Jerzy Dudek", "Liverpool FC", 1000)}
    <div id="e-so" class="a">
      <h5>PENALTY SHOOTOUT</h5>
      <div class="krow"><span>MIL</span>{krow("MIL")}</div>
      <div class="krow"><span class="y">LIV</span>{krow("LIV")}</div>
    </div>
    <div id="e-win" class="a lg">Liverpool<br>win <span class="y">3–2</span></div>
""", f"""
    tl.fromTo("#e-et", {{ opacity: 0, scale: 1.15, transformOrigin: "0 50%" }}, {{ opacity: 1, scale: 1, duration: 0.25, ease: "expo.out" }}, {L(n, P(26))});
    tl.fromTo("#e-clk", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.2 }}, {L(n, P(26)) + 0.2});
    const ec = document.getElementById("e-c"), eo = {{ v: 90 }};
    tl.fromTo(eo, {{ v: 90 }}, {{ v: 120, duration: {E(26) - P(26) + 0.3:.2f}, ease: "power1.in", onUpdate: () => {{ ec.textContent = Math.round(eo.v) + "'"; }} }}, {L(n, P(26)) + 0.2});
    tl.to("#e-et, #e-clk", {{ y: -1300, filter: "blur(16px)", duration: 0.26, ease: "power3.in" }}, {L(n, P(27)) - 0.27});
    {cut_out("#e-et, #e-clk", L(n, P(27)))}
    tl.fromTo("#e-dd", {{ opacity: 0, y: 200 }}, {{ opacity: 1, y: 0, duration: 0.4, ease: "expo.out" }}, {L(n, P(27))});
    {nc_in("e-nc", L(n, WD(27, "Dudek")) - 0.2)}
    {stamp("#e-x1", L(n, WD(27, "unbelievable")), 0)}
    {stamp("#e-x2", L(n, WD(27, "saves")), 0)}
    {blur_in("#e-117", L(n, WD(27, "produced")))}
    {nc_out("e-nc", L(n, P(28)) - 0.1)}
    {blur_out("#e-dd", L(n, P(28)) - 0.1)}
    tl.fromTo("#e-so", {{ opacity: 0, x: 900, filter: "blur(16px)" }}, {{ opacity: 1, x: 0, filter: "blur(0px)", duration: 0.35, ease: "expo.out" }}, {L(n, P(28))});
    {"".join(f'tl.fromTo("#k{k} b", {{ opacity: 0, scale: 1.4 }}, {{ opacity: 1, scale: 1, duration: 0.14, ease: "power4.out" }}, {L(n, k_t0 + (k_t1 - k_t0) * k / 8):.3f});' + chr(10) + "    " for k in range(9))}
    
    tl.fromTo("#e-win", {{ opacity: 0, filter: "blur(12px)" }}, {{ opacity: 1, filter: "blur(0px)", duration: 0.3, ease: "power4.out" }}, {L(n, k_t1) + 0.25});
""")

# ------------------------------------------------------------------ LEGACY
n = "legacy"
legacy = scene(n, f"""
    #g-1{{left:116px;top:400px;font-size:200px}}
    #g-2{{left:116px;top:400px;font-size:200px}}
    #g-3{{left:116px;top:400px;font-size:230px}}
    #g-k{{left:120px;top:900px;font-weight:800;font-size:32px;letter-spacing:.1em;color:rgba(245,245,240,.7)}}
""", f"""
    <div id="g-1" class="a lg">From<br><span class="r">3–0</span> down</div>
    <div id="g-2" class="a lg">To European<br><span class="y">champions.</span></div>
    <div id="g-3" class="a lg">The miracle<br>of <span class="y">Istanbul.</span></div>
    <div id="g-k" class="a">25 MAY 2005 · ATATÜRK OLYMPIC STADIUM</div>
""", f"""
    tl.fromTo("#g-1", {{ opacity: 0, color: "#2a2a2a" }}, {{ opacity: 1, color: "{WH}", duration: 0.4 }}, {L(n, P(29))});
    {cut_out("#g-1", L(n, WD(29, "European")) - 0.1)}
    tl.fromTo("#g-2", {{ opacity: 0, scale: 1.12, transformOrigin: "0 50%" }}, {{ opacity: 1, scale: 1, duration: 0.25, ease: "expo.out" }}, {L(n, WD(29, "European")) - 0.1});
    {blur_out("#g-2", L(n, P(30)) - 0.1)}
    tl.fromTo("#g-3", {{ opacity: 0, color: "#2a2a2a" }}, {{ opacity: 1, color: "{WH}", duration: 0.8, ease: "power2.out" }}, {L(n, P(30)) + 0.1});
    {blur_in("#g-k", L(n, P(30)) + 1.2, 0.3)}
""")

# ------------------------------------------------------------------ BRAND (same treatment as Ep 001)
brand = scene("brand", f"""
    #o-line{{left:0;top:590px;width:6px;height:250px;background:{Y}}}
    #o-word{{left:0;top:620px;width:1080px;text-align:center;font-size:250px}}
    #o-word span{{display:inline-block}}
    #o-st{{left:0;top:850px;width:1080px;text-align:center;font-weight:900;font-size:62px;letter-spacing:.42em;padding-left:.42em}}
    #o-tag{{left:0;top:990px;width:1080px;text-align:center;font-weight:800;font-size:44px;letter-spacing:.12em;color:{Y}}}
    #o-fol{{left:0;top:1070px;width:1080px;text-align:center;font-weight:700;font-size:32px;letter-spacing:.12em;color:rgba(245,245,240,.75)}}
""", """
    <div id="o-line" class="a"></div>
    <div id="o-word" class="a lg"><span>O</span><span>F</span><span>F</span><span>S</span><span>I</span><span>D</span><span id="o-e">E</span></div>
    <div id="o-st" class="a">STORIES</div>
    <div id="o-tag" class="a">BEYOND THE 90 MINUTES.</div>
    <div id="o-fol" class="a">FOLLOW FOR MORE FOOTBALL STORIES</div>
""", f"""
    const e = document.getElementById("o-e").getBoundingClientRect(), root = document.querySelector('[data-composition-id="brand"]').getBoundingClientRect();
    gsap.set("#o-line", {{ x: e.left - root.left - 8 }});
    tl.fromTo("#o-line", {{ scaleY: 0, transformOrigin: "50% 0" }}, {{ scaleY: 1, duration: 0.4, ease: "expo.out" }}, 0.0);
    tl.fromTo("#o-word span", {{ opacity: 0, filter: "blur(8px)" }}, {{ opacity: 1, filter: "blur(0px)", duration: 0.18, stagger: 0.05, ease: "power4.out" }}, 0.15);
    tl.fromTo("#o-e", {{ x: -30 }}, {{ x: 22, duration: 0.28, ease: "back.out(2.2)" }}, 0.62);
    tl.fromTo("#o-st", {{ opacity: 0, scaleX: 1.35 }}, {{ opacity: 1, scaleX: 1, duration: 0.5, ease: "expo.out" }}, 0.75);
    {blur_in("#o-tag", L("brand", P(32)) - 0.1)}
    tl.fromTo("#o-fol", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.25 }}, {L("brand", P(32)) + 0.15});
""")

# ------------------------------------------------------------------ SCORE BUG (overlay, night -> legacy)
bug_a, bug_b = B["night"][0], B["brand"][0]
def ab(t): return round(t - bug_a, 3)
STATES = [  # (absolute time, LIV, MIL, clock)
    (0, "0", "0", "1'"), (WD(5, "scored"), "0", "1", "1'"), (WD(6, "struck"), "0", "2", "39'"), (WD(6, "twice"), "0", "3", "44'"),
    (E(7) - 0.3, "0", "3", "HT"), (B["turn"][0], "0", "3", "54'"), (WD(19, "home", True), "1", "3", "54'"),
    (B["six"][0], "1", "3", "56'"), (WD(22, "3–2"), "2", "3", "56'"), (P(23), "2", "3", "60'"), (WD(24, "rebound", True), "3", "3", "60'"),
    (B["hero"][0], "3", "3", "ET"), (P(28), "3", "3", "PENS"), (B["legacy"][0], "3", "3", "FT")]
bug = scene("bug", f"""
    #root{{background:transparent}}
    #root .grain{{display:none}}
    #bg{{left:120px;top:300px;height:76px;display:flex;align-items:stretch;font-family:'League Gothic';font-size:62px;line-height:1}}
    #bg .tm{{padding:10px 16px 0;letter-spacing:.04em}}
    #bg .l{{background:{LIVRED};color:{WH}}}
    #bg .m{{background:{WH};color:{BK}}}
    #bg .sc{{background:{BK};color:{WH};padding:10px 18px 0;min-width:128px;text-align:center;border-top:3px solid {WH};border-bottom:3px solid {WH}}}
    #bg .ck{{background:{Y};color:{BK};padding:10px 16px 0;min-width:110px;text-align:center}}
""", """
    <div id="bg" class="a"><span class="tm l">LIV</span><span class="sc" id="bg-s">0–0</span><span class="tm m">MIL</span><span class="ck" id="bg-c">1'</span></div>
""", f"""
    const ST = {json.dumps([[ab(t), l, m, c] for t, l, m, c in STATES])};
    const s = document.getElementById("bg-s"), c = document.getElementById("bg-c"), o = {{ v: 0 }};
    tl.fromTo(o, {{ v: 0 }}, {{ v: 1, duration: {round(bug_b - bug_a, 3)}, ease: "none", onUpdate: () => {{
      const t = o.v * {round(bug_b - bug_a, 3)}; let cur = ST[0]; for (const x of ST) if (t >= x[0]) cur = x;
      s.textContent = cur[1] + "–" + cur[2]; c.textContent = cur[3]; }} }}, 0);
    tl.fromTo("#bg", {{ opacity: 0, x: -40 }}, {{ opacity: 1, x: 0, duration: 0.3, ease: "expo.out" }}, {ab(WD(4, "Liverpool"))});
    tl.fromTo("#bg-s", {{ scale: 1.25 }}, {{ scale: 1, duration: 0.2, ease: "power4.out" }}, {ab(WD(19, "home", True))});
    tl.fromTo("#bg-s", {{ scale: 1.25 }}, {{ scale: 1, duration: 0.2, ease: "power4.out" }}, {ab(WD(22, "3–2"))});
    tl.fromTo("#bg-s", {{ scale: 1.25 }}, {{ scale: 1, duration: 0.2, ease: "power4.out" }}, {ab(WD(24, "rebound", True))});
""")

# ------------------------------------------------------------------ CAPTIONS
HL = {"3–0", "3–0.", "maldini", "crespo", "silence.", "benítez.", "15", "history.", "gerrard", "belief", "possible.", "šmicer", "3–2.", "alonso.",
      "rebound.", "six", "3–3.", "dudek", "shootout,", "champions.", "over.", "offside", "stories.", "90", "istanbul.", "defeat.", "over"}
groups = []
for i in range(len(S)):
    cur = []; wt = word_times(i)
    for k, x in enumerate(wt):
        cur.append(x)
        if len(cur) == 3 or re.search(r"[.,!?…:]$", x[0]) or k == len(wt) - 1:
            groups.append(cur); cur = []
cap_html, cap_js = [], []
for gi, g in enumerate(groups):
    spans = "".join(f'<span id="c{gi}w{k}" class="cw{" hl" if w.lower().strip(".,!?:") in {h.strip(".,!?:") for h in HL} else ""}">{html.escape(w)}</span> ' for k, (w, a, b) in enumerate(g))
    cap_html.append(f'<div class="cg" id="c{gi}"><span class="bx">{spans.strip()}</span></div>')
    a, b = g[0][1], g[-1][2]
    nxt = groups[gi + 1][0][1] if gi + 1 < len(groups) else TOTAL
    end = min(b + 0.35, nxt)
    cap_js.append(f'tl.fromTo("#c{gi}", {{ opacity: 0, y: 14 }}, {{ opacity: 1, y: 0, duration: 0.1, ease: "power3.out" }}, {a - 0.04:.3f});')
    for k, (w, ws_, we) in enumerate(g):
        cap_js.append(f'tl.fromTo("#c{gi}w{k}", {{ color: "rgba(245,245,240,.55)" }}, {{ color: "var(--on)", duration: 0.06 }}, {ws_:.3f});')
    cap_js.append(f'tl.to("#c{gi}", {{ opacity: 0, duration: 0.08 }}, {end - 0.08:.3f}); tl.set("#c{gi}", {{ visibility: "hidden" }}, {end:.3f});')
caps = f"""<template>
  <style>
    #root{{position:absolute;inset:0;pointer-events:none}}
    #root .cg{{position:absolute;left:120px;width:780px;top:1110px;text-align:center;font-family:Inter,sans-serif;font-weight:900;font-size:56px;line-height:1.3;letter-spacing:-.01em;opacity:0}}
    #root .cg .bx{{background:rgba(10,10,10,.86);padding:4px 18px 8px;-webkit-box-decoration-break:clone;box-decoration-break:clone}}
    #root .cw{{--on:{WH}}}
    #root .cw.hl{{--on:{Y}}}
  </style>
  <div id="root" data-composition-id="captions" data-width="{W}" data-height="{H}">
    {chr(10).join(cap_html)}
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
    {chr(10).join(cap_js)}
    window.__timelines["captions"] = tl;
  </script>
</template>
"""

# ------------------------------------------------------------------ ROOT
files = {"hook": hook, "night": night, "roomA": roomA, "roomB": roomB, "turn": turn, "six": six, "hero": hero, "legacy": legacy, "brand": brand,
         "bug": bug, "captions": caps}
for k, v in files.items(): open(f"compositions/{k}.html", "w").write(v)
hosts = "\n".join(f'      <div id="{k}" data-composition-id="{k}" data-composition-src="compositions/{k}.html" data-start="{B[k][0]}" data-duration="{B[k][1]}" data-track-index="0" data-track-kind="graphics" data-width="{W}" data-height="{H}" style="z-index:1"></div>' for k in order)
DUR = {"impact-bass-1": 2.1, "impact-bass-2": 2.5, "whoosh": 0.57, "whoosh-cinematic": 1.0, "riser": 4.0, "pop": 0.7, "key-press": 0.43, "click-soft": 0.36, "typing": 1.5, "sparkle": 1.5}
def at(t, peak=0.07): return round(t + 0.033 - peak, 3)
SFX = [("x-open", "impact-bass-2", 0.0, 0.35), ("x-w1", "whoosh", at(P(1) - 0.15, 0.16), 0.6), ("x-board", "impact-bass-1", at(WD(2, "3–0")), 0.3),
       ("x-g1", "pop", at(WD(5, "scored"), 0.12), 1.2), ("x-g2", "pop", at(WD(6, "struck"), 0.12), 1.2), ("x-g3", "pop", at(WD(6, "twice"), 0.12), 1.2),
       ("x-perf", "whoosh-cinematic", at(E(7) - 0.4, 0.2), 0.45), ("x-45", "impact-bass-2", at(WD(9, "Forty-five"), 0.03), 0.22),
       ("x-bn", "whoosh", at(WD(11, "Rafael"), 0.16), 0.4), ("x-clock", "typing", P(12) + 0.3, 0.25),
       ("x-tun", "riser", round(P(17) + 0.15 - 3.47, 3), 0.45), ("x-hist", "impact-bass-1", at(P(17) + 0.15), 0.35),
       ("x-head", "impact-bass-1", at(WD(19, "home", True)), 0.35), ("x-begins", "whoosh", at(P(21), 0.16), 0.5),
       ("x-smi", "impact-bass-2", at(WD(22, "3–2"), 0.03), 0.3), ("x-saved", "key-press", at(WD(24, "saved") + 0.1), 2.5),
       ("x-alo", "pop", at(WD(24, "rebound", True), 0.12), 1.3), ("x-33r", "riser", round(WD(25, "3–3") - 3.47, 3), 0.4),
       ("x-33", "impact-bass-1", at(WD(25, "3–3") - 0.1), 0.45), ("x-et", "whoosh-cinematic", at(P(26), 0.2), 0.4),
       ("x-sv1", "pop", at(WD(27, "unbelievable"), 0.12), 1.0), ("x-sv2", "pop", at(WD(27, "saves"), 0.12), 1.0),
       ("x-win", "impact-bass-1", at(k_t1 + 0.25), 0.4), ("x-mir", "impact-bass-2", at(P(30) + 0.1, 0.03), 0.25),
       ("x-logo", "impact-bass-1", at(B["brand"][0] + 0.62), 0.4)]
ends, lanes = [], []
for sid, f, a, v in sorted(SFX, key=lambda x: x[2]):
    e = a + DUR[f]
    for li, le in enumerate(ends):
        if le <= a: ends[li] = e; break
    else: ends.append(e); li = len(ends) - 1
    fade = ' data-fade-out="0.4"' if f == "riser" else ""
    lanes.append(f'      <audio id="{sid}" class="clip" src="assets/sfx/{f}.mp3" data-start="{max(0,a)}" data-duration="{DUR[f]}" data-track-index="{20+li}" data-volume="{v}"{fade}></audio>')
idx = f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width={W}, height={H}" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ width: {W}px; height: {H}px; overflow: hidden; background: {BK}; }}
      #root {{ position: relative; width: {W}px; height: {H}px; background: {BK}; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{TOTAL}" data-width="{W}" data-height="{H}">
{hosts}
      <div id="bug" data-composition-id="bug" data-composition-src="compositions/bug.html" data-start="{bug_a}" data-duration="{round(bug_b-bug_a,3)}" data-track-index="1" data-track-kind="graphics" data-width="{W}" data-height="{H}" style="z-index:4"></div>
      <div id="captions" data-composition-id="captions" data-composition-src="compositions/captions.html" data-start="0" data-duration="{TOTAL}" data-track-index="2" data-track-kind="captions" data-width="{W}" data-height="{H}" style="z-index:5"></div>
      <audio id="vo" class="clip" src="assets/audio/vo.wav" data-start="0" data-duration="{TOTAL}" data-track-index="10" data-volume="1"></audio>
{chr(10).join(lanes)}
    </div>
    <script>
      window.__timelines["main"] = gsap.timeline({{ paused: true }});
    </script>
  </body>
</html>
"""
open("index.html", "w").write(idx)
print({k: B[k] for k in order}); print("groups", len(groups))
