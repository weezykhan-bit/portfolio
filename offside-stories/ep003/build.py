"""Offside Stories Ep 003: Barcelona 6-1 PSG (La Remontada). Graphics only.
Cues derive from vo/script.json. Facts checked against ESPN match report and the match record:
1st leg 14 Feb 2017 PSG 4-0 (Di Maria 18', 55'; Draxler 40'; Cavani 72').
2nd leg 8 Mar 2017 Camp Nou: Suarez 3', Kurzawa og 40', Messi pen 50', Cavani 62', Neymar 88' and 90+1' pen, Sergi Roberto 90+5'. Agg 6-5."""
import json, re, html

S = json.load(open("vo/script.json"))
W, H = 1080, 1920
Y, R, WH, BK = "#FFE600", "#E10600", "#F5F5F0", "#0A0A0A"
BAR, PSG = "#A50044", "#004170"
TOTAL = 48.0

def weight(w):
    w = w.strip(".,!?…:")
    if re.match(r"^\d+–\d+$", w): return 12
    if re.match(r"^\d+(th|st)$", w): return 13
    if w.isdigit(): return 9
    return len(re.sub(r"[^\w]", "", w)) + 2

def word_times(i):
    p = S[i]; words = p["show"].split(); ws = [weight(w) for w in words]; tot = sum(ws); t = p["start"]; out = []
    for w, k in zip(words, ws):
        d = p["dur"] * k / tot; out.append((w, t, t + d)); t += d
    return out

def P(i): return S[i]["start"]
def E(i): return S[i]["start"] + S[i]["dur"]
def WD(i, needle, end=False):
    for w, a, b in word_times(i):
        if needle.lower() in w.lower(): return b if end else a
    raise KeyError((i, needle))

order = ["hook", "rewind", "first", "seven", "payoff", "brand"]
starts = {"hook": 0.0, "rewind": P(1) - 0.15, "first": P(3) - 0.15, "seven": P(5) - 0.2, "payoff": P(10) - 0.15, "brand": P(11) - 0.25}
B = {}
for k, n in enumerate(order):
    a = round(starts[n], 3); b = round(starts[order[k + 1]], 3) if k + 1 < len(order) else TOTAL
    B[n] = (a, round(b - a, 3))
def L(n, t): return round(t - B[n][0], 3)

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
    #root .chip{{display:inline-block;font-family:'League Gothic';font-size:70px;line-height:1;padding:8px 18px 0;color:{WH}}}
    #root .agg{{font-weight:800;font-size:36px;letter-spacing:.12em;text-transform:uppercase}}
"""
def namecard(id_, name, club, top):
    return f'<div class="nc" id="{id_}" style="top:{top}px"><b></b><span>{html.escape(name)}</span><i>{html.escape(club)}</i></div>'
def nc_in(id_, t):
    return (f'tl.fromTo("#{id_} b", {{ scaleY: 0, transformOrigin: "50% 100%" }}, {{ scaleY: 1, duration: 0.18, ease: "expo.out" }}, {t:.3f});\n'
            f'    tl.fromTo("#{id_} span, #{id_} i", {{ clipPath: "inset(0 100% 0 0)" }}, {{ clipPath: "inset(0 0% 0 0)", duration: 0.3, ease: "expo.out", stagger: 0.08 }}, {t + 0.08:.3f});')
def nc_out(id_, t): return f'tl.to("#{id_}", {{ opacity: 0, x: -30, duration: 0.15, ease: "power2.in" }}, {t:.3f});'
def cut_in(sel, t): return f'tl.fromTo("{sel}", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.01 }}, {t:.3f});'
def cut_out(sel, t): return f'tl.set("{sel}", {{ opacity: 0 }}, {t:.3f});'
def blur_in(sel, t, d=0.2): return f'tl.fromTo("{sel}", {{ opacity: 0, filter: "blur(10px)" }}, {{ opacity: 1, filter: "blur(0px)", duration: {d}, ease: "power4.out" }}, {t:.3f});'
def blur_out(sel, t): return f'tl.to("{sel}", {{ opacity: 0, filter: "blur(10px)", duration: 0.15, ease: "power2.in" }}, {t:.3f});'
def stamp(sel, t, rot=-4):
    return (f'tl.fromTo("{sel}", {{ opacity: 0, scale: 1.5, rotation: {rot} }}, {{ opacity: 1, scale: 1, rotation: {rot}, duration: 0.16, ease: "power4.out" }}, {t:.3f});\n'
            f'    tl.fromTo("{sel}", {{ x: 0 }}, {{ x: 7, duration: 0.033, yoyo: true, repeat: 3, ease: "none" }}, {t + 0.16:.3f});')
def textswap(el_id, states, dur):
    """states: [(local_t, text)] — text set by timeline time (seek-safe)"""
    js = json.dumps(states); v = el_id.replace("-", "_")
    return (f'const _s{v} = {js}, _e{v} = document.getElementById("{el_id}"), _o{v} = {{ v: 0 }};\n'
            f'    tl.fromTo(_o{v}, {{ v: 0 }}, {{ v: 1, duration: {dur}, ease: "none", onUpdate: () => {{ const t = _o{v}.v * {dur}; let c = _s{v}[0][1]; for (const x of _s{v}) if (t >= x[0]) c = x[1]; _e{v}.textContent = c; }} }}, 0);')

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

# ------------------------------------------------------------------ HOOK: 88', need three
n = "hook"
hook = scene(n, f"""
    #h-k{{left:120px;top:330px}}
    #h-clk{{left:120px;top:390px;font-size:150px}}
    #h-teams{{left:120px;top:560px;display:flex;gap:20px;align-items:center}}
    #h-sc{{left:116px;top:640px;font-size:440px}}
    #h-agg{{left:120px;top:1030px}}
    #h-need{{left:540px;top:990px;font-family:'League Gothic';font-size:96px;line-height:1;background:{Y};color:{BK};padding:8px 22px 0;text-transform:uppercase}}
""", f"""
    <div id="h-k" class="a kick y">Champions League · Last 16</div>
    <div id="h-clk" class="a lg"><span id="h-c">88:00</span></div>
    <div id="h-teams" class="a"><span class="chip" style="background:{BAR}">BARCELONA</span><span class="chip" style="background:{PSG}">PSG</span></div>
    <div id="h-sc" class="a lg">3–1</div>
    <div id="h-agg" class="a agg">Aggregate <span class="r">3–5</span></div>
    <div id="h-need" class="a">Need 3 goals</div>
""", f"""
    const hc = document.getElementById("h-c"), ho = {{ v: 0 }};
    tl.fromTo(ho, {{ v: 0 }}, {{ v: 1, duration: {B[n][1]}, ease: "none", onUpdate: () => {{ const s = Math.floor(ho.v * {B[n][1]}); hc.textContent = "88:" + String(s).padStart(2, "0"); }} }}, 0);
    tl.set("#h-need", {{ rotation: -4 }}, 0);
    tl.fromTo("#h-need", {{ scale: 1 }}, {{ scale: 1.12, duration: 0.12, yoyo: true, repeat: 1, ease: "power2.out" }}, {L(n, WD(0, "three")):.3f});
    tl.to("#h-clk, #h-teams, #h-sc, #h-agg, #h-need, #h-k", {{ x: -1150, filter: "blur(18px)", duration: 0.26, ease: "power3.in" }}, {B[n][1] - 0.27});
""")

# ------------------------------------------------------------------ REWIND: Paris 4-0, Luis Enrique quote
n = "rewind"
rewind = scene(n, f"""
    #r-k{{left:120px;top:330px}}
    #r-teams{{left:120px;top:400px;display:flex;gap:20px}}
    #r-sc{{left:116px;top:500px;font-size:460px}}
    #r-sub{{left:120px;top:920px;font-weight:700;font-size:34px;letter-spacing:.06em;color:rgba(245,245,240,.7)}}
    #r-q{{left:120px;top:360px;width:840px}}
    #r-q .qm{{font-family:'League Gothic';font-size:260px;line-height:.7;color:{Y};display:block;height:150px}}
    #r-q .qt{{font-family:'League Gothic';font-size:150px;line-height:.92;text-transform:uppercase}}
    #r-q .qa{{display:block;margin-top:40px;font-weight:800;font-size:34px;letter-spacing:.12em;color:rgba(245,245,240,.75);text-transform:uppercase}}
""", f"""
    <div id="r-p" class="a" style="inset:0">
      <div id="r-k" class="a kick y">14 Feb 2017 · Paris · first leg</div>
      <div id="r-teams" class="a"><span class="chip" style="background:{PSG}">PSG</span><span class="chip" style="background:{BAR}">BARCELONA</span></div>
      <div id="r-sc" class="a lg">4–0</div>
      <div id="r-sub" class="a">DI MARÍA 2 · DRAXLER · CAVANI</div>
    </div>
    <div id="r-q" class="a"><span class="qm">“</span><span class="qt">If they can score <span class="y">four</span>, we can score <span class="y">six.</span></span><span class="qa">Luis Enrique · before the second leg</span></div>
""", f"""
    tl.fromTo("#r-p", {{ opacity: 0, x: 900, filter: "blur(18px)" }}, {{ opacity: 1, x: 0, filter: "blur(0px)", duration: 0.4, ease: "expo.out" }}, 0.0);
    tl.fromTo("#r-sc", {{ scale: 1.25, transformOrigin: "0 50%" }}, {{ scale: 1, duration: 0.25, ease: "power4.out" }}, {L(n, WD(1, "4–0")) - 0.05});
    {blur_in("#r-sub", 0.45)}
    {blur_out("#r-p", L(n, P(2)) - 0.15)}
    tl.fromTo("#r-q .qm", {{ opacity: 0, scale: 1.4 }}, {{ opacity: 1, scale: 1, duration: 0.2, ease: "power4.out" }}, {L(n, P(2))});
    tl.fromTo("#r-q .qt", {{ opacity: 0, color: "#2a2a2a" }}, {{ opacity: 1, color: "{WH}", duration: 0.45 }}, {L(n, WD(2, "if"))});
    {blur_in("#r-q .qa", L(n, WD(2, "if")) + 0.5)}
""")

# ------------------------------------------------------------------ FIRST HOUR: 3-0, then Cavani
n = "first"
GX0, GX1, GY = 140, 940, 820
def gx(m): return GX0 + (GX1 - GX0) * m / 90
first = scene(n, f"""
    #f-k{{left:120px;top:330px}}
    #f-sc{{left:116px;top:390px;font-size:330px}}
    #f-agg{{left:120px;top:700px}}
    #f-bar{{left:{GX0}px;top:{GY}px;width:{GX1-GX0}px;height:6px;background:rgba(245,245,240,.25)}}
    #f-fill{{left:{GX0}px;top:{GY}px;width:{GX1-GX0}px;height:6px;background:{WH};transform-origin:0 50%}}
    #root .mk{{position:absolute;top:{GY-34}px;width:4px;height:74px;background:{WH}}}
    #root .mk.red{{background:{R}}}
    #root .ml{{position:absolute;top:{GY+52}px;font-weight:800;font-size:28px;letter-spacing:.04em;white-space:nowrap}}
    #f-need{{left:120px;top:960px;font-family:'League Gothic';font-size:96px;line-height:1;color:{R};border:6px solid {R};padding:6px 22px 0;text-transform:uppercase}}
""", f"""
    <div id="f-k" class="a kick y">8 Mar 2017 · Camp Nou · second leg</div>
    <div id="f-sc" class="a lg"><span id="f-s">0–0</span></div>
    <div id="f-agg" class="a agg">Aggregate <span id="f-a" class="r">0–4</span></div>
    <div id="f-bar" class="a"></div><div id="f-fill" class="a"></div>
    <div class="mk" id="f-m1" style="left:{gx(3)-2}px"></div>
    <div class="mk" id="f-m2" style="left:{gx(40)-2}px"></div>
    <div class="mk" id="f-m3" style="left:{gx(50)-2}px"></div>
    <div class="mk red" id="f-m4" style="left:{gx(62)-2}px"></div>
    <div class="ml" id="f-l1" style="left:{gx(3)-4}px">3' SUÁREZ</div>
    <div class="ml" id="f-l2" style="left:{gx(40)-150}px;top:{GY+92}px">40' OWN GOAL</div>
    <div class="ml" id="f-l3" style="left:{gx(50)-6}px">50' MESSI (PEN)</div>
    <div class="ml r" id="f-l4" style="left:{gx(62)-6}px;top:{GY+92}px">62' CAVANI</div>
    <div id="f-need" class="a">Need 3 more</div>
""", f"""
    tl.fromTo("#f-k, #f-sc, #f-agg, #f-bar", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.25 }}, 0);
    tl.fromTo("#f-fill", {{ scaleX: 0 }}, {{ scaleX: 62 / 90, duration: {E(4) - B[n][0] - 0.3:.2f}, ease: "none" }}, 0.1);
    {textswap("f-s", [[0, "0–0"], [L(n, WD(3, "Suárez")), "1–0"], [L(n, WD(3, "own")), "2–0"], [L(n, WD(3, "Messi")), "3–0"], [L(n, WD(4, "Cavani")), "3–1"]], B[n][1])}
    {textswap("f-a", [[0, "0–4"], [L(n, WD(3, "Suárez")), "1–4"], [L(n, WD(3, "own")), "2–4"], [L(n, WD(3, "Messi")), "3–4"], [L(n, WD(4, "Cavani")), "3–5"]], B[n][1])}
    {"".join(f'tl.fromTo("#f-m{k}, #f-l{k}", {{ opacity: 0, scaleY: 0.2 }}, {{ opacity: 1, scaleY: 1, duration: 0.2, ease: "expo.out" }}, {L(n, t):.3f});' + chr(10) + "    " + f'tl.fromTo("#f-sc", {{ scale: 1.12, transformOrigin: "0 50%" }}, {{ scale: 1, duration: 0.18, ease: "power4.out", immediateRender: false }}, {L(n, t):.3f});' + chr(10) + "    " for k, t in [(1, WD(3, "Suárez")), (2, WD(3, "own")), (3, WD(3, "Messi")), (4, WD(4, "Cavani"))])}
    {stamp("#f-need", L(n, WD(4, "three")), -3)}
""")

# ------------------------------------------------------------------ THE SEVEN MINUTES
n = "seven"
seven = scene(n, f"""
    #s-k{{left:120px;top:330px}}
    #s-clk{{left:116px;top:390px;font-size:300px}}
    #s-agg{{left:120px;top:680px;display:flex;align-items:baseline;gap:26px}}
    #s-agg .lab{{font-weight:800;font-size:36px;letter-spacing:.12em;text-transform:uppercase;color:rgba(245,245,240,.7)}}
    #s-a{{font-family:'League Gothic';font-size:200px;line-height:.9}}
    #s-out{{left:120px;top:880px;font-weight:800;font-size:34px;letter-spacing:.08em;color:{R};text-transform:uppercase}}
    #s-boom{{inset:0;background:{Y}}}
""", f"""
    <div id="s-k" class="a kick y">Barcelona v PSG · second leg</div>
    <div id="s-clk" class="a lg"><span id="s-c">88'</span></div>
    <div id="s-agg" class="a"><span class="lab">Aggregate</span><span id="s-a">3–5</span></div>
    <div id="s-out" class="a">5–5: PSG still through on the away goal</div>
    {namecard("s-n1", "Neymar", "Free kick · 88'", 1000)}
    {namecard("s-n2", "Neymar", "Penalty · 90+1'", 1000)}
    {namecard("s-n3", "Sergi Roberto", "90+5'", 1000)}
    <div id="s-boom" class="a"></div>
""", f"""
    tl.fromTo("#s-k, #s-clk, #s-agg", {{ opacity: 0, filter: "blur(10px)" }}, {{ opacity: 1, filter: "blur(0px)", duration: 0.25, ease: "power4.out" }}, 0.05);
    {textswap("s-c", [[0, "88'"], [L(n, WD(7, "Neymar")), "90+1'"], [L(n, WD(8, "95th")), "90+5'"]], B[n][1])}
    {textswap("s-a", [[0, "3–5"], [L(n, WD(6, "free")), "4–5"], [L(n, WD(7, "penalty")), "5–5"], [L(n, WD(9, "Sergi")), "6–5"]], B[n][1])}
    {"".join(f'tl.fromTo("#s-a", {{ scale: 1.3, transformOrigin: "0 70%" }}, {{ scale: 1, duration: 0.2, ease: "power4.out", immediateRender: false }}, {L(n, t):.3f});' + chr(10) + "    " for t in [WD(6, "free"), WD(7, "penalty"), WD(9, "Sergi")])}
    tl.fromTo("#s-clk", {{ scale: 1.08, transformOrigin: "0 50%" }}, {{ scale: 1, duration: 0.2, ease: "power4.out", immediateRender: false }}, {L(n, WD(7, "Neymar")):.3f});
    tl.fromTo("#s-clk", {{ scale: 1.08, transformOrigin: "0 50%" }}, {{ scale: 1, duration: 0.2, ease: "power4.out", immediateRender: false }}, {L(n, WD(8, "95th")):.3f});
    {nc_in("s-n1", L(n, P(6)))}
    {nc_out("s-n1", L(n, P(7)) - 0.1)}
    {nc_in("s-n2", L(n, P(7)))}
    {nc_out("s-n2", L(n, P(8)) - 0.1)}
    {blur_in("#s-out", L(n, WD(7, "penalty")) + 0.35)}
    tl.to("#s-out", {{ opacity: 0, duration: 0.15 }}, {L(n, P(9)) - 0.1});
    tl.to("#s-a", {{ color: "{Y}", duration: 0.1 }}, {L(n, WD(9, "Sergi")):.3f});
    {nc_in("s-n3", L(n, P(9)))}
    tl.fromTo("#s-boom", {{ clipPath: "inset(50% 50% 50% 50%)", opacity: 0 }}, {{ clipPath: "inset(0% 0% 0% 0%)", opacity: 1, duration: 0.4, ease: "power3.inOut" }}, {B[n][1] - 0.42});
""")

# ------------------------------------------------------------------ PAYOFF
n = "payoff"
payoff = scene(n, f"""
    #root{{background:{Y};color:{BK}}}
    #root .grain{{display:none}}
    #p-k{{left:0;top:340px;width:1080px;text-align:center;font-weight:900;font-size:40px;letter-spacing:.16em;color:{BK}}}
    #p-sc{{left:0;top:420px;width:1080px;text-align:center;font-size:520px;color:{BK}}}
    #p-agg{{left:0;top:880px;width:1080px;text-align:center;font-weight:900;font-size:52px;letter-spacing:.06em;color:{BK}}}
    #p-line{{left:150px;top:980px;width:780px;text-align:center;font-weight:800;font-size:36px;line-height:1.2;color:{BK}}}
""", f"""
    <div id="p-k" class="a">LA REMONTADA · 8 MARCH 2017</div>
    <div id="p-sc" class="a lg">6–1</div>
    <div id="p-agg" class="a">6–5 ON AGGREGATE</div>
    <div id="p-line" class="a">The biggest comeback in Champions League history</div>
""", f"""
    tl.fromTo("#p-sc", {{ opacity: 0, scale: 1.4, filter: "blur(14px)" }}, {{ opacity: 1, scale: 1, filter: "blur(0px)", duration: 0.35, ease: "expo.out" }}, {L(n, P(10)):.3f});
    {blur_in("#p-k", L(n, P(10)) + 0.25)}
    {blur_in("#p-agg", L(n, WD(10, "aggregate")) - 0.1)}
    {blur_in("#p-line", L(n, WD(10, "biggest")))}
""")

# ------------------------------------------------------------------ BRAND (series sign-off)
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
    {blur_in("#o-tag", L("brand", P(12)) - 0.1)}
    tl.fromTo("#o-fol", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.25 }}, {L("brand", P(12)) + 0.15});
""")

# ------------------------------------------------------------------ CAPTIONS
HL = {"88th", "three", "4–0", "six", "3–0", "suárez", "messi", "cavani", "3–1", "neymar", "penalty", "95th", "sergi", "roberto", "6–1", "6–5", "comeback", "offside", "stories", "90"}
groups = []
for i in range(len(S)):
    cur = []; wt = word_times(i)
    for k, x in enumerate(wt):
        cur.append(x)
        if len(cur) == 3 or re.search(r"[.,!?…:]$", x[0]) or k == len(wt) - 1:
            groups.append(cur); cur = []
cap_html, cap_js = [], []
for gi, g in enumerate(groups):
    spans = "".join(f'<span id="c{gi}w{k}" class="cw{" hl" if w.lower().strip(".,!?:") in HL else ""}">{html.escape(w)}</span> ' for k, (w, a, b) in enumerate(g))
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
files = {"hook": hook, "rewind": rewind, "first": first, "seven": seven, "payoff": payoff, "brand": brand, "captions": caps}
for k, v in files.items(): open(f"compositions/{k}.html", "w").write(v)
hosts = "\n".join(f'      <div id="{k}" data-composition-id="{k}" data-composition-src="compositions/{k}.html" data-start="{B[k][0]}" data-duration="{B[k][1]}" data-track-index="0" data-track-kind="graphics" data-width="{W}" data-height="{H}" style="z-index:1"></div>' for k in order)
DUR = {"impact-bass-1": 2.1, "impact-bass-2": 2.5, "whoosh": 0.57, "whoosh-cinematic": 1.0, "riser": 4.0, "pop": 0.7, "key-press": 0.43, "click-soft": 0.36, "typing": 1.5, "sparkle": 1.5}
def at(t, peak=0.07): return round(t + 0.033 - peak, 3)
SFX = [("x-open", "impact-bass-2", 0.0, 0.3), ("x-need", "impact-bass-1", at(WD(0, "three")), 0.3),
       ("x-rew", "whoosh-cinematic", at(B["rewind"][0], 0.2), 0.5), ("x-40", "impact-bass-2", at(WD(1, "4–0"), 0.03), 0.25),
       ("x-g1", "pop", at(WD(3, "Suárez"), 0.12), 1.1), ("x-g2", "pop", at(WD(3, "own"), 0.12), 1.1), ("x-g3", "pop", at(WD(3, "Messi"), 0.12), 1.1),
       ("x-cav", "impact-bass-2", at(WD(4, "Cavani"), 0.03), 0.25), ("x-cut", "whoosh", at(B["seven"][0], 0.16), 0.5),
       ("x-ney1", "impact-bass-1", at(WD(6, "free")), 0.3), ("x-ney2", "impact-bass-1", at(WD(7, "penalty")), 0.3),
       ("x-rise", "riser", round(WD(9, "Sergi") - 3.47, 3), 0.5), ("x-sr", "impact-bass-1", at(WD(9, "Sergi")), 0.45),
       ("x-boom", "sparkle", at(P(10)), 0.4), ("x-logo", "impact-bass-1", at(B["brand"][0] + 0.62), 0.4)]
ends, lanes = [], []
for sid, f, a, v in sorted(SFX, key=lambda x: x[2]):
    e = a + DUR[f]
    for li, le in enumerate(ends):
        if le <= a: ends[li] = e; break
    else: ends.append(e); li = len(ends) - 1
    fade = ' data-fade-out="0.4"' if f == "riser" else ""
    lanes.append(f'      <audio id="{sid}" class="clip" src="assets/sfx/{f}.mp3" data-start="{max(0, a)}" data-duration="{DUR[f]}" data-track-index="{20+li}" data-volume="{v}"{fade}></audio>')
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
