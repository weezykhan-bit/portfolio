"""Offside Stories LF01: Leicester City 2015-16, 16:9 long-form. Graphics + CC BY / PD photos.
Cues come from vo/script.json (phrase timings). See FACTS.md for sources."""
import json, re, html

S = json.load(open("vo/script.json"))
PH = json.load(open("photos.json"))
W, H = 1920, 1080
Y, R, WH, BK, BL = "#FFE600", "#E10600", "#F5F5F0", "#0A0A0A", "#1D4E9E"
TOTAL = round(S[-1]["start"] + S[-1]["dur"] + 2.6, 2)

def weight(w):
    w = w.strip(".,!?…:")
    if re.match(r"^\d+–\d+$", w): return 12
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
    raise KeyError((i, needle, S[i]["show"]))

# ---- scenes = beats in order of appearance
order = []
for p in S:
    if p["beat"] not in order: order.append(p["beat"])
IDX = {b: [i for i, p in enumerate(S) if p["beat"] == b] for b in order}
def I(b, k): return IDX[b][k]
starts = {}
for b in order:
    i0 = IDX[b][0]
    lead = 0.55 if re.match(r"^c\d+$", b) else 0.3
    starts[b] = 0.0 if i0 == 0 else round(P(i0) - lead, 3)
B = {}
for k, n in enumerate(order):
    a = starts[n]; b = starts[order[k + 1]] if k + 1 < len(order) else TOTAL
    B[n] = (a, round(b - a, 3))
def L(n, t): return round(t - B[n][0], 3)
def LP(n, k): return L(n, P(I(n, k)))
def LW(n, k, needle, end=False): return L(n, WD(I(n, k), needle, end))

CH = {}  # beat -> chapter tag
cur = ""
TITLES = {"c1": "The great escape", "c2": "Claudio Ranieri? Really?", "c3": "The bargains", "c4": "The record", "c5": "Top at Christmas",
          "c6": "February", "c7": "Nerve", "c8": "Stamford Bridge", "c9": "The trophy", "c10": "After the fairy tale"}
for b in order:
    m = re.match(r"^(c\d+)", b)
    if m and m.group(1) in TITLES: cur = f"{int(m.group(1)[1:]):02d} · {TITLES[m.group(1)]}"
    if b.startswith("close") or b == "brand": cur = ""
    CH[b] = cur if not re.match(r"^c\d+$", b) and b != "c8_champs" else ""

BASE = f"""
    #root{{position:absolute;inset:0;overflow:hidden;background:{BK};color:{WH};font-family:Inter,sans-serif}}
    #root *{{box-sizing:border-box;margin:0}}
    #root .a{{position:absolute}}
    #root .lg{{font-family:'League Gothic',sans-serif;font-weight:400;line-height:.86;letter-spacing:.005em;text-transform:uppercase;white-space:nowrap}}
    #root .kick{{font-weight:800;font-size:30px;letter-spacing:.16em;text-transform:uppercase;white-space:nowrap}}
    #root .y{{color:{Y}}} #root .r{{color:{R}}} #root .g{{color:rgba(245,245,240,.5)}}
    #root .grain{{position:absolute;inset:0;opacity:.05;background-image:radial-gradient(rgba(255,255,255,.9) 1px,transparent 1.4px);background-size:6px 6px;z-index:8;pointer-events:none}}
    #root .tag{{position:absolute;left:96px;top:64px;font-weight:800;font-size:22px;letter-spacing:.2em;text-transform:uppercase;color:rgba(245,245,240,.6);z-index:9;white-space:nowrap}}
    #root .tag b{{display:inline-block;width:28px;height:4px;background:{Y};vertical-align:middle;margin-right:14px}}
    #root .cred{{position:absolute;right:40px;bottom:30px;font-size:16px;font-weight:600;letter-spacing:.04em;color:rgba(245,245,240,.55);z-index:9;white-space:nowrap;text-align:right}}
    #root .cam{{position:absolute;inset:0;transform-origin:50% 45%}}
    #root .ph{{position:absolute;overflow:hidden}}
    #root .ph img{{position:absolute;left:-5%;top:-5%;width:110%;height:110%;object-fit:cover}}
    #root .ph.fb{{background:#111}}
    #root .ph.fb .mv{{position:absolute;left:-5%;top:-5%;width:110%;height:110%;display:flex;align-items:center;justify-content:center;background:repeating-linear-gradient(135deg,rgba(245,245,240,.035) 0 2px,transparent 2px 22px),radial-gradient(ellipse at 60% 40%,#262626,#0d0d0d 75%)}}
    #root .ph.fb .mv span{{font-family:'League Gothic';font-size:420px;line-height:.85;text-transform:uppercase;color:transparent;-webkit-text-stroke:3px rgba(255,230,0,.22);white-space:nowrap}}
    #root .ph .ht{{position:absolute;inset:0;background-image:radial-gradient(rgba(10,10,10,.55) 1.1px,transparent 1.6px);background-size:5px 5px;opacity:.35;mix-blend-mode:multiply}}
    #root .shade{{position:absolute;inset:0}}
    #root .nc{{position:absolute;display:flex;align-items:stretch;height:70px}}
    #root .nc b{{width:10px;background:{Y};display:block}}
    #root .nc span{{background:{WH};color:{BK};font-weight:900;font-size:34px;letter-spacing:.02em;padding:14px 20px 0;text-transform:uppercase;white-space:nowrap}}
    #root .nc i{{background:{BK};color:{WH};font-style:normal;font-weight:700;font-size:22px;letter-spacing:.14em;padding:22px 18px 0;text-transform:uppercase;border:3px solid {WH};border-left:0;white-space:nowrap}}
    #root .chip{{display:inline-block;font-family:'League Gothic';font-size:58px;line-height:1;padding:8px 16px 0;color:{WH};text-transform:uppercase;white-space:nowrap}}
    #root .row{{position:absolute;display:flex;align-items:center;gap:22px;white-space:nowrap}}
    #root .res{{position:absolute;display:flex;align-items:center;white-space:nowrap;height:76px}}
    #root .res .d{{width:200px;font-weight:800;font-size:22px;letter-spacing:.14em;color:rgba(245,245,240,.6);text-transform:uppercase}}
    #root .res .t{{font-family:'League Gothic';font-size:64px;line-height:1;text-transform:uppercase}}
    #root .res .n{{margin-left:22px;font-weight:700;font-size:22px;letter-spacing:.1em;color:{Y};text-transform:uppercase}}
"""
def tag(b): return f'<div class="tag"><b></b>{html.escape(CH[b])}</div>' if CH.get(b) else ""
import os
HAVE = {k for k in PH if os.path.exists(f"assets/photos/{k}.jpg")}
FALLBACK = {"ranieri_appeal": "Ranieri", "ranieri_watch": "Ranieri", "schmeichel_morgan": "Defence", "clocktower": "Leicester",
            "mahrez_fk1": "2014–15", "mahrez_fk2": "14th", "mahrez": "Mahrez", "soton": "King Power", "vardy": "Vardy"}
def credit(key, extra=""):
    if key not in HAVE: return ""
    m = PH[key]; who = m["artist"].split(" from ")[0].replace("Unknown authorUnknown author", "Unknown author")
    lic = m["lic"]
    return f'<div class="cred">{extra}Photo: {html.escape(who)} · {html.escape(lic)} · Wikimedia Commons · tinted</div>'
def photo(id_, key, style, shade=None):
    sh = f'<div class="shade" style="background:{shade}"></div>' if shade else ""
    if key not in HAVE:
        return (f'<div class="ph fb" id="{id_}" style="{style}"><div class="mv"><span>{html.escape(FALLBACK[key])}</span></div>{sh}</div>')
    return f'<div class="ph" id="{id_}" style="{style}"><img class="mv" src="assets/photos/{key}.jpg"><div class="ht"></div>{sh}</div>'
def kb(id_, dur, x0=0, x1=-36, s0=1.0, s1=1.07, y0=0, y1=0, t=0):
    return f'tl.fromTo("#{id_} .mv", {{ scale: {s0}, x: {x0}, y: {y0} }}, {{ scale: {s1}, x: {x1}, y: {y1}, duration: {dur:.3f}, ease: "none" }}, {t});'
def namecard(id_, name, sub, left, top):
    return f'<div class="nc" id="{id_}" style="left:{left}px;top:{top}px"><b></b><span>{html.escape(name)}</span><i>{html.escape(sub)}</i></div>'
def nc_in(id_, t):
    return (f'tl.fromTo("#{id_} b", {{ scaleY: 0, transformOrigin: "50% 100%" }}, {{ scaleY: 1, duration: 0.18, ease: "expo.out" }}, {t:.3f});\n'
            f'    tl.fromTo("#{id_} span, #{id_} i", {{ clipPath: "inset(0 100% 0 0)" }}, {{ clipPath: "inset(0 0% 0 0)", duration: 0.32, ease: "expo.out", stagger: 0.08 }}, {t + 0.08:.3f});')
def nc_out(id_, t): return f'tl.to("#{id_}", {{ opacity: 0, x: -30, duration: 0.18, ease: "power2.in" }}, {t:.3f});'
def fade_in(sel, t, d=0.5): return f'tl.fromTo("{sel}", {{ opacity: 0 }}, {{ opacity: 1, duration: {d}, ease: "power2.out" }}, {t:.3f});'
def fade_out(sel, t, d=0.3): return f'tl.to("{sel}", {{ opacity: 0, duration: {d}, ease: "power2.in" }}, {t:.3f});'
def blur_in(sel, t, d=0.3, stagger=0): return f'tl.fromTo("{sel}", {{ opacity: 0, filter: "blur(12px)", y: 16 }}, {{ opacity: 1, filter: "blur(0px)", y: 0, duration: {d}, ease: "power4.out", stagger: {stagger} }}, {t:.3f});'
def blur_out(sel, t): return f'tl.to("{sel}", {{ opacity: 0, filter: "blur(10px)", duration: 0.2, ease: "power2.in" }}, {t:.3f});'
def rise(sel, t, d=0.45, stagger=0.08): return f'tl.fromTo("{sel}", {{ opacity: 0, y: 40 }}, {{ opacity: 1, y: 0, duration: {d}, ease: "expo.out", stagger: {stagger} }}, {t:.3f});'
def wipe(sel, t, d=0.45): return f'tl.fromTo("{sel}", {{ clipPath: "inset(0 100% 0 0)" }}, {{ clipPath: "inset(0 0% 0 0)", duration: {d}, ease: "expo.out" }}, {t:.3f});'
def pop(sel, t, s=1.18, origin="50% 50%"): return f'tl.fromTo("{sel}", {{ scale: {s}, transformOrigin: "{origin}" }}, {{ scale: 1, duration: 0.22, ease: "power4.out", immediateRender: false }}, {t:.3f});'
def stamp(sel, t, rot=-3):
    return (f'tl.fromTo("{sel}", {{ opacity: 0, scale: 1.5, rotation: {rot} }}, {{ opacity: 1, scale: 1, rotation: {rot}, duration: 0.16, ease: "power4.out" }}, {t:.3f});\n'
            f'    tl.fromTo("{sel}", {{ x: 0 }}, {{ x: 6, duration: 0.033, yoyo: true, repeat: 3, ease: "none" }}, {t + 0.16:.3f});')
def textswap(el_id, states, dur):
    js = json.dumps(states, ensure_ascii=False); v = el_id.replace("-", "_")
    return (f'const _s{v} = {js}, _e{v} = document.getElementById("{el_id}"), _o{v} = {{ v: 0 }};\n'
            f'    tl.fromTo(_o{v}, {{ v: 0 }}, {{ v: 1, duration: {dur}, ease: "none", onUpdate: () => {{ const t = _o{v}.v * {dur}; let c = _s{v}[0][1]; for (const x of _s{v}) if (t >= x[0]) c = x[1]; _e{v}.textContent = c; }} }}, 0);')
def enter(n): return f'tl.fromTo(".tag", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.4 }}, 0.05);' if CH.get(n) else ""

SCENES = {}
def scene(n, css, body, js):
    SCENES[n] = f"""<template>
  <style>{BASE}{css}
  </style>
  <div id="root" data-composition-id="{n}" data-width="{W}" data-height="{H}">
    <div class="cam" id="cam-{n}">
{body}
    </div>
    {tag(n)}
    <div class="grain"></div>
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
    {enter(n)}
    tl.fromTo("#cam-{n}", {{ scale: 1 }}, {{ scale: 1.035, duration: {B[n][1]}, ease: "none" }}, 0);
{js}
    window.__timelines["{n}"] = tl;
  </script>
</template>
"""

def scoreboard(pref, home, away, hs, as_, hc="#034694", ac="#F5F5F0", act=BK, top=380, size=300):
    """centered scoreboard: [HOME] h–a [AWAY]"""
    return f"""
    <div id="{pref}-sb" class="a" style="left:0;width:{W}px;top:{top}px;display:flex;justify-content:center;align-items:center;gap:44px">
      <span class="chip" style="background:{hc};font-size:76px">{home}</span>
      <span class="lg" id="{pref}-sc" style="font-size:{size}px">{hs}–{as_}</span>
      <span class="chip" style="background:{ac};color:{act};font-size:76px">{away}</span>
    </div>"""

# =================================================================== COLD OPEN
n = "co_tv"; D = B[n][1]
scene(n, f"""
    #t-tv{{left:300px;top:150px;width:1320px;height:640px;border:3px solid rgba(245,245,240,.25);border-radius:28px;background:radial-gradient(ellipse at 50% 40%,#1b1b1b,#0d0d0d)}}
    #t-scan{{left:303px;top:153px;width:1314px;height:634px;border-radius:26px;background:repeating-linear-gradient(0deg,rgba(255,255,255,.035) 0 2px,transparent 2px 5px)}}
    #t-k{{left:0;width:{W}px;top:210px;text-align:center}}
    #t-clk{{left:0;width:{W}px;top:640px;text-align:center;font-family:'League Gothic';font-size:64px;color:rgba(245,245,240,.7)}}
    #t-a, #t-b{{left:0;width:{W}px;text-align:center;font-weight:800;font-size:34px;letter-spacing:.08em;text-transform:uppercase}}
    #t-a{{top:838px}} #t-b{{top:900px}}
""", f"""
    <div id="t-tv" class="a"></div><div id="t-scan" class="a"></div>
    <div id="t-k" class="a kick y">2 May 2016 · Stamford Bridge · Premier League</div>
    {scoreboard("t", "Chelsea", "Tottenham", 0, 0, top=330, size=270)}
    <div id="t-clk" class="a"><span id="t-c">LIVE</span></div>
    <div id="t-a" class="a g">Tottenham win → the title race goes on</div>
    <div id="t-b" class="a y">Tottenham don't win → Leicester are champions</div>
""", f"""
    tl.fromTo("#t-tv, #t-scan", {{ opacity: 1, scale: 0.96 }}, {{ opacity: 1, scale: 1, duration: 0.8, ease: "expo.out" }}, 0.1);
    tl.fromTo("#t-sb > *", {{ y: 20 }}, {{ y: 0, duration: 0.6, ease: "expo.out" }}, 0.05);
    {fade_in("#t-clk", 1.1)}
    {blur_in("#t-a", LP(n, 1))}
    {blur_in("#t-b", LP(n, 2))}
    {textswap("t-sc", [[0, "0–0"], [LW(n, 3, "winning"), "0–2"]], D)}
    {textswap("t-c", [[0, "LIVE"], [LW(n, 3, "half-time"), "HALF-TIME"]], D)}
    {pop("#t-sc", LW(n, 3, "winning"), 1.25)}
    tl.to("#t-tv, #t-scan, #t-sb, #t-clk, #t-k, #t-a, #t-b", {{ opacity: 0, duration: 0.5, ease: "power2.in" }}, {D - 0.6:.3f});
""")

n = "co_odds"; D = B[n][1]
scene(n, f"""
    #o-k{{left:0;width:{W}px;top:250px;text-align:center}}
    #o-big{{left:0;width:{W}px;top:310px;text-align:center;font-size:470px;color:{Y}}}
    #o-sub{{left:0;width:{W}px;top:760px;text-align:center;font-weight:800;font-size:34px;letter-spacing:.12em;text-transform:uppercase}}
""", f"""
    <div id="o-k" class="a kick g">Summer 2015 · bookmakers' odds</div>
    <div id="o-big" class="a lg">5000–1</div>
    <div id="o-sub" class="a">Leicester City to win the Premier League</div>
""", f"""
    {blur_in("#o-k", 0.3)}
    {blur_in("#o-sub", 0.5)}
    {stamp("#o-big", LW(n, 0, "5000"), 0)}
""")

n = "co_title"; D = B[n][1]
scene(n, f"""
    #ti-ph{{inset:0}}
    #ti-pre{{left:120px;top:330px}}
    #ti-big{{left:112px;top:380px;font-size:330px;color:{Y}}}
    #ti-name{{left:120px;top:690px;font-family:'League Gothic';font-size:120px;line-height:1;text-transform:uppercase}}
    #ti-sub{{left:124px;top:830px;font-weight:700;font-size:30px;letter-spacing:.1em;color:rgba(245,245,240,.8);text-transform:uppercase}}
""", f"""
    {photo("ti-ph", "soton", "inset:0", "linear-gradient(90deg,rgba(10,10,10,.92) 0%,rgba(10,10,10,.6) 55%,rgba(10,10,10,.25) 100%)")}
    <div id="ti-pre" class="a kick">Offside Stories presents</div>
    <div id="ti-big" class="a lg">5000–1</div>
    <div id="ti-name" class="a">Leicester City 2015–16</div>
    <div id="ti-sub" class="a">The most unlikely title in English football</div>
    {credit("soton", "King Power Stadium, April 2016 · ")}
""", f"""
    {fade_in("#ti-ph", 0, 1.0)}
    {kb("ti-ph", D, 0, -60, 1.04, 1.12)}
    {blur_in("#ti-pre", 0.4)}
    {wipe("#ti-big", LW(n, 0, "unlikely"), 0.6)}
    {rise("#ti-name", LW(n, 0, "title"))}
    {blur_in("#ti-sub", LW(n, 0, "English"))}
    {fade_in(".cred", 1.0)}
""")

# =================================================================== CHAPTER CARDS
for c, title in TITLES.items():
    n = c; D = B[n][1]; num = int(c[1:])
    scene(n, f"""
    #cc-num{{right:80px;top:80px;font-size:900px;color:rgba(245,245,240,.08)}}
    #cc-k{{left:160px;top:420px}}
    #cc-bar{{left:160px;top:470px;width:120px;height:8px;background:{Y}}}
    #cc-t{{left:154px;top:500px;font-size:170px}}
""", f"""
    <div id="cc-num" class="a lg">{num:02d}</div>
    <div id="cc-k" class="a kick y">Chapter {num:02d}</div>
    <div id="cc-bar" class="a"></div>
    <div id="cc-t" class="a lg">{html.escape(title)}</div>
""", f"""
    tl.fromTo("#cc-num", {{ opacity: 0, x: 120 }}, {{ opacity: 1, x: 0, duration: 1.4, ease: "expo.out" }}, 0.0);
    {blur_in("#cc-k", 0.15)}
    tl.fromTo("#cc-bar", {{ scaleX: 0, transformOrigin: "0 50%" }}, {{ scaleX: 1, duration: 0.5, ease: "expo.out" }}, 0.2);
    {wipe("#cc-t", 0.35, 0.7)}
    tl.to("#cc-k, #cc-bar, #cc-t, #cc-num", {{ opacity: 0, x: -40, duration: 0.35, ease: "power2.in" }}, {D - 0.4:.3f});
""")

# =================================================================== CH1
n = "c1_bottom"; D = B[n][1]
LADX, LADY, LH = 1180, 150, 38
lad = "".join(f'<div class="a" style="left:{LADX}px;top:{LADY + (p-1)*LH}px;width:560px;height:{LH-6}px;background:rgba(245,245,240,{0.08 if p<18 else 0.14})"></div><div class="a" style="left:{LADX-64}px;top:{LADY + (p-1)*LH + 2}px;width:50px;text-align:right;font-weight:800;font-size:22px;color:rgba(245,245,240,.5)">{p}</div>' for p in range(1, 21))
scene(n, f"""
    #b-ph{{left:0;top:0;width:1000px;height:{H}px}}
    #b-lad{{left:0;top:0;width:{W}px;height:{H}px}}
    #b-lei{{left:{LADX}px;top:{LADY + 19*LH}px;width:560px;height:{LH-6}px;background:{BL};display:flex;align-items:center;padding-left:18px;font-weight:900;font-size:22px;letter-spacing:.12em}}
    #b-line{{left:{LADX-20}px;top:{LADY + 17*LH - 4}px;width:600px;height:3px;background:{R}}}
    #b-safe{{left:{LADX+580}px;top:{LADY + 17*LH - 18}px;font-weight:800;font-size:20px;letter-spacing:.12em;color:{R}}}
    #b-lab{{left:{LADX}px;top:{LADY + 20*LH + 18}px;font-weight:800;font-size:28px;letter-spacing:.1em;text-transform:uppercase;color:{Y}}}
    #b-champ{{left:96px;top:820px}}
""", f"""
    {photo("b-ph", "mahrez_fk1", "left:0;top:0;width:1000px;height:1080px", "linear-gradient(90deg,rgba(10,10,10,0) 60%,rgba(10,10,10,1) 100%)")}
    <div id="b-champ" class="a"><span class="chip" style="background:{BL}">2013–14 · Championship winners</span></div>
    <div id="b-lad" class="a">{lad}</div>
    <div id="b-lei" class="a">LEICESTER CITY</div>
    <div id="b-line" class="a"></div><div id="b-safe" class="a">SAFETY</div>
    <div id="b-lab" class="a"><span id="b-l">Christmas 2014 · bottom</span></div>
    {credit("mahrez_fk1", "Leicester, February 2015 · ")}
""", f"""
    {fade_in("#b-ph, .cred", 0, 0.8)}
    {kb("b-ph", D, 0, -30, 1.02, 1.09)}
    {wipe("#b-champ", LP(n, 1))}
    {fade_out("#b-champ", LP(n, 2) - 0.2)}
    tl.fromTo("#b-lad > div", {{ opacity: 0, x: 30 }}, {{ opacity: 1, x: 0, duration: 0.3, stagger: 0.012, ease: "expo.out" }}, {LP(n, 2):.3f});
    {wipe("#b-lei", LW(n, 2, "bottom"))}
    {blur_in("#b-lab", LW(n, 2, "bottom") + 0.2)}
    {textswap("b-l", [[0, "Christmas 2014 · bottom"], [LP(n, 3), "April 2015 · still bottom · 7 points from safety"]], D)}
    {wipe("#b-line", LW(n, 3, "seven"))}
    {fade_in("#b-safe", LW(n, 3, "safety"), 0.3)}
""")

n = "c1_escape"; D = B[n][1]
scene(n, f"""
    #e-ph{{left:920px;top:0;width:1000px;height:{H}px}}
    #e-k{{left:120px;top:250px}}
    #e-big{{left:112px;top:300px;font-size:420px}}
    #e-sub{{left:120px;top:690px;font-weight:800;font-size:32px;letter-spacing:.1em;text-transform:uppercase}}
    #e-fin{{left:120px;top:780px;display:flex;align-items:baseline;gap:24px}}
    #e-fin .lg{{font-size:170px;color:{Y}}}
    #e-fin span.l{{font-weight:800;font-size:30px;letter-spacing:.1em;text-transform:uppercase}}
""", f"""
    {photo("e-ph", "mahrez_fk2", "left:920px;top:0;width:1000px;height:1080px", "linear-gradient(90deg,rgba(10,10,10,1) 0%,rgba(10,10,10,.1) 45%)")}
    <div id="e-k" class="a kick y">Spring 2015 · the last nine games</div>
    <div id="e-big" class="a lg"><span id="e-n">0</span><span class="g">/9</span></div>
    <div id="e-sub" class="a">Wins</div>
    <div id="e-fin" class="a"><span class="lg">14th</span><span class="l">Final position, 2014–15</span></div>
    {credit("mahrez_fk2", "Leicester, February 2015 · ")}
""", f"""
    {fade_in("#e-ph, .cred", 0, 0.8)}
    {kb("e-ph", D, 0, 40, 1.08, 1.02)}
    {blur_in("#e-k", 0.3)}
    {blur_in("#e-big, #e-sub", LW(n, 0, "nine"))}
    {textswap("e-n", [[0, "0"]] + [[round(LW(n, 1, "seven") + k * 0.09, 3), str(k + 1)] for k in range(7)], D)}
    {pop("#e-big", LW(n, 1, "seven") + 0.63, 1.1, "0 60%")}
    {rise("#e-fin", LW(n, 2, "14th"))}
""")

n = "c1_pearson"; D = B[n][1]
scene(n, f"""
    #pe-n{{left:120px;top:420px}}
    #pe-s{{left:126px;top:530px;font-family:'League Gothic';font-size:140px;line-height:1;color:{R};border:8px solid {R};padding:10px 30px 0;text-transform:uppercase}}
    #pe-k{{left:120px;top:360px}}
""", f"""
    <div id="pe-k" class="a kick g">Summer 2015</div>
    {namecard("pe-n", "Nigel Pearson", "Manager · 2011–15", 120, 420)}
    <div id="pe-s" class="a">Sacked</div>
""", f"""
    {blur_in("#pe-k", 0.2)}
    {nc_in("pe-n", LW(n, 0, "Nigel"))}
    {stamp("#pe-s", LW(n, 0, "sacked"))}
""")

# =================================================================== CH2
n = "c2_cv"; D = B[n][1]
clubs = ["Chelsea", "Valencia", "Juventus", "Roma", "Inter"]
scene(n, f"""
    #cv-ph{{left:760px;top:0;width:1160px;height:{H}px}}
    #cv-cl{{left:120px;top:300px;display:flex;flex-direction:column;gap:6px}}
    #cv-cl span{{font-family:'League Gothic';font-size:86px;line-height:1;text-transform:uppercase}}
    #cv-zero{{left:120px;top:300px;display:flex;align-items:baseline;gap:26px}}
    #cv-zero .lg{{font-size:300px;color:{Y}}}
    #cv-zero span.l{{font-weight:800;font-size:30px;letter-spacing:.1em;text-transform:uppercase;width:340px;white-space:normal;line-height:1.3}}
    #cv-gf{{left:120px;top:690px}}
    #cv-gf .res .t{{font-size:72px}}
""", f"""
    {photo("cv-ph", "ranieri_watch", "left:760px;top:0;width:1160px;height:1080px", "linear-gradient(90deg,rgba(10,10,10,1) 0%,rgba(10,10,10,0) 40%)")}
    {namecard("cv-n", "Claudio Ranieri", "Age 63 · appointed July 2015", 120, 180)}
    <div id="cv-cl" class="a">{"".join(f'<span id="cv-c{k}">{c}</span>' for k, c in enumerate(clubs))}</div>
    <div id="cv-zero" class="a"><span class="lg">0</span><span class="l">Top-flight league titles as a manager</span></div>
    <div id="cv-gf" class="a"><div class="res" style="position:relative"><span class="d">Nov 2014</span><span class="t">Greece 0–1 Faroe Islands</span><span class="n">Last job: sacked</span></div></div>
    {credit("ranieri_watch", "Ranieri at Arsenal, February 2016 · ")}
""", f"""
    {fade_in("#cv-ph, .cred", 0, 0.8)}
    {kb("cv-ph", D, 0, -50, 1.03, 1.1)}
    {nc_in("cv-n", LW(n, 0, "Claudio"))}
    {"".join(rise(f"#cv-c{k}", LW(n, 1, c), 0.35) + chr(10) + "    " for k, c in enumerate(clubs))}
    {fade_out("#cv-cl", LP(n, 2) - 0.25)}
    {blur_in("#cv-zero", LW(n, 2, "never"))}
    {wipe("#cv-gf", LW(n, 3, "Greece"))}
""")

n = "c2_tweet"; D = B[n][1]
scene(n, f"""
    #q-m{{left:150px;top:180px;font-family:'League Gothic';font-size:420px;line-height:.7;color:{Y}}}
    #q-t{{left:150px;top:420px;font-size:200px}}
    #q-a{{left:156px;top:640px;font-weight:800;font-size:30px;letter-spacing:.14em;color:rgba(245,245,240,.75);text-transform:uppercase}}
""", f"""
    <div id="q-m" class="a">“</div>
    <div id="q-t" class="a lg">Claudio Ranieri? <span class="y">Really?</span></div>
    <div id="q-a" class="a">Gary Lineker · on Twitter, July 2015</div>
""", f"""
    {blur_in("#q-m", 0.2)}
    {blur_in("#q-a", LW(n, 0, "Gary"))}
    tl.fromTo("#q-t", {{ opacity: 0, color: "#2a2a2a" }}, {{ opacity: 1, color: "{WH}", duration: 0.5 }}, {LP(n, 1):.3f});
    {pop("#q-t .y", LW(n, 1, "Really"), 1.2, "0 50%")}
""")

n = "c2_odds"; D = B[n][1]
scene(n, f"""
    #od-big{{left:112px;top:280px;font-size:380px;color:{Y}}}
    #od-k{{left:120px;top:230px}}
    #od-t{{left:1080px;top:300px}}
    #od-tn{{left:1072px;top:350px;font-size:300px}}
    #od-bar{{left:1080px;top:660px;width:700px;height:16px;background:rgba(245,245,240,.15)}}
    #od-fill{{left:1080px;top:660px;width:700px;height:16px;background:{WH};transform-origin:0 50%}}
    #od-l{{left:1080px;top:700px;font-weight:800;font-size:26px;letter-spacing:.12em;text-transform:uppercase;color:rgba(245,245,240,.7)}}
""", f"""
    <div id="od-k" class="a kick g">Odds to win the league</div>
    <div id="od-big" class="a lg">5000–1</div>
    <div id="od-t" class="a kick y">Ranieri's target</div>
    <div id="od-tn" class="a lg"><span id="od-n">0</span> pts</div>
    <div id="od-bar" class="a"></div><div id="od-fill" class="a"></div>
    <div id="od-l" class="a">The usual mark for safety</div>
""", f"""
    {blur_in("#od-k", 0.2)}
    {stamp("#od-big", LW(n, 0, "5000"), 0)}
    {blur_in("#od-t, #od-tn, #od-bar", LP(n, 1))}
    tl.fromTo("#od-fill", {{ scaleX: 0 }}, {{ scaleX: 1, duration: 0.8, ease: "power2.out" }}, {LW(n, 1, "40"):.3f});
    {textswap("od-n", [[0, "0"]] + [[round(LW(n, 1, "40") + k * 0.08, 3), str((k + 1) * 4)] for k in range(10)], D)}
    {blur_in("#od-l", LW(n, 1, "safety"))}
""")

# =================================================================== CH3
n = "c3_def"; D = B[n][1]
scene(n, f"""
    #d-ph{{inset:0}}
    #d-k{{left:96px;top:140px;font-family:'League Gothic';font-size:96px;line-height:1;text-transform:uppercase;width:900px;white-space:normal}}
""", f"""
    {photo("d-ph", "schmeichel_morgan", "inset:0", "linear-gradient(0deg,rgba(10,10,10,.85) 0%,rgba(10,10,10,.1) 50%,rgba(10,10,10,.6) 100%)")}
    <div id="d-k" class="a">Players other clubs had <span class="y">overlooked</span></div>
    {namecard("d-n1", "Kasper Schmeichel", "Goalkeeper", 96, 760)}
    {namecard("d-n2", "Wes Morgan", "Centre-back · captain", 96, 760)}
    {namecard("d-n3", "Robert Huth", "Centre-back", 96, 860)}
    {credit("schmeichel_morgan", "Schmeichel and Morgan, 2014 · ")}
""", f"""
    {fade_in("#d-ph, .cred", 0, 0.8)}
    {kb("d-ph", D, 0, -50, 1.02, 1.1)}
    {blur_in("#d-k", LW(n, 0, "squad"))}
    {fade_out("#d-k", LP(n, 1) - 0.1)}
    {nc_in("d-n1", LW(n, 1, "Kasper"))}
    {nc_out("d-n1", LW(n, 1, "Wes") - 0.2)}
    {nc_in("d-n2", LW(n, 1, "Wes"))}
    {nc_in("d-n3", LW(n, 1, "Huth"))}
""")

n = "c3_vardy"; D = B[n][1]
steps = [("Sheffield Wednesday", "Released as a teenager"), ("Stocksbridge Park Steels", "Non-league · factory job"), ("FC Halifax Town", "2010"), ("Fleetwood Town", "2011"), ("Leicester City", "2012 · ~£1m (reported)")]
scene(n, f"""
    #v-ph{{left:1180px;top:0;width:740px;height:{H}px}}
    #v-path{{left:150px;top:200px;width:900px;height:760px}}
    #v-line{{left:170px;top:236px;width:4px;height:600px;background:rgba(245,245,240,.25);transform-origin:50% 0}}
    #root .st{{position:absolute;left:150px;display:flex;align-items:center;gap:34px}}
    #root .st i{{width:44px;height:44px;border-radius:50%;background:{BK};border:4px solid {WH};display:block;flex:none}}
    #root .st b{{font-family:'League Gothic';font-weight:400;font-size:74px;line-height:1;text-transform:uppercase;white-space:nowrap}}
    #root .st em{{font-style:normal;font-weight:800;font-size:22px;letter-spacing:.12em;color:rgba(245,245,240,.6);text-transform:uppercase;white-space:nowrap;margin-left:6px}}
    #root .st.last i{{background:{Y};border-color:{Y}}}
    #root .st.last b{{color:{Y}}}
    #v-split{{left:150px;top:900px}}
""", f"""
    {photo("v-ph", "vardy", "left:1180px;top:0;width:740px;height:1080px", "linear-gradient(90deg,rgba(10,10,10,1) 0%,rgba(10,10,10,0) 35%)")}
    {namecard("v-n", "Jamie Vardy", "Striker", 150, 110)}
    <div id="v-line" class="a"></div>
    {"".join(f'<div class="st{" last" if k == len(steps)-1 else ""}" id="v-s{k}" style="top:{214 + k*150}px"><i></i><div><b>{html.escape(a)}</b><em>{html.escape(b)}</em></div></div>' for k, (a, b) in enumerate(steps))}
    {credit("vardy", "Vardy pictured in 2019 · ")}
""", f"""
    {fade_in("#v-ph, .cred", 0, 0.8)}
    {kb("v-ph", D, 0, 0, 1.02, 1.1, 0, -30)}
    {nc_in("v-n", LW(n, 0, "Jamie"))}
    tl.fromTo("#v-line", {{ scaleY: 0 }}, {{ scaleY: 1, duration: {LW(n, 2, "Leicester") - LP(n, 1) + 0.3:.2f}, ease: "power1.inOut" }}, {LP(n, 1):.3f});
    {rise("#v-s0", LW(n, 1, "Sheffield"))}
    {rise("#v-s1", LW(n, 1, "Stocksbridge"))}
    {rise("#v-s2", LW(n, 1, "Stocksbridge") + 0.9)}
    {rise("#v-s3", LW(n, 2, "Fleetwood"))}
    {rise("#v-s4", LW(n, 2, "reported"))}
    {pop("#v-s4 b", LW(n, 2, "million"), 1.2, "0 50%")}
""")

n = "c3_mahrez"; D = B[n][1]
scene(n, f"""
    #m-ph{{left:1180px;top:0;width:740px;height:{H}px}}
    #m-r{{left:150px;top:330px;font-family:'League Gothic';font-size:96px;line-height:1;text-transform:uppercase;white-space:nowrap}}
    #m-r2{{left:156px;top:440px;font-weight:800;font-size:26px;letter-spacing:.12em;color:rgba(245,245,240,.65);text-transform:uppercase}}
    #m-big{{left:142px;top:540px;font-size:300px;color:{Y}}}
    #m-l{{left:150px;top:820px;font-weight:800;font-size:28px;letter-spacing:.12em;text-transform:uppercase}}
""", f"""
    {photo("m-ph", "mahrez", "left:1180px;top:0;width:740px;height:1080px", "linear-gradient(90deg,rgba(10,10,10,1) 0%,rgba(10,10,10,0) 35%)")}
    {namecard("m-n", "Riyad Mahrez", "Winger · Algeria", 150, 200)}
    <div id="m-r" class="a">Le Havre <span class="g">→</span> Leicester</div>
    <div id="m-r2" class="a">Ligue 2 (French second division) · January 2014</div>
    <div id="m-big" class="a lg">~£400k</div>
    <div id="m-l" class="a">Reported fee</div>
    {credit("mahrez", "Mahrez pictured in 2014 · ")}
""", f"""
    {fade_in("#m-ph, .cred", 0, 0.8)}
    {kb("m-ph", D, 0, 0, 1.02, 1.1, 0, -30)}
    {nc_in("m-n", LW(n, 0, "Riyad"))}
    {wipe("#m-r", LW(n, 0, "French"))}
    {blur_in("#m-r2", LW(n, 0, "division"))}
    {stamp("#m-big", LW(n, 1, "400,000"), 0)}
    {blur_in("#m-l", LW(n, 1, "400,000") + 0.3)}
""")

n = "c3_kante"; D = B[n][1]
scene(n, f"""
    #k-d{{left:150px;top:200px}}
    #k-r{{left:150px;top:420px;font-family:'League Gothic';font-size:110px;line-height:1;text-transform:uppercase;white-space:nowrap}}
    #k-big{{left:1040px;top:300px;font-size:330px;color:{Y}}}
    #k-l{{left:1050px;top:600px;font-weight:800;font-size:28px;letter-spacing:.12em;text-transform:uppercase}}
    #k-q{{left:150px;top:760px;font-family:'League Gothic';font-size:100px;line-height:1;text-transform:uppercase;white-space:nowrap}}
""", f"""
    <div id="k-d" class="a kick y">3 August 2015</div>
    {namecard("k-n", "N'Golo Kanté", "Midfielder · France", 150, 290)}
    <div id="k-r" class="a">Caen <span class="g">→</span> Leicester</div>
    <div id="k-big" class="a lg">£5.6m</div>
    <div id="k-l" class="a">Reported fee</div>
    <div id="k-q" class="a"><span class="g" id="k-q1">Nobody had heard of him.</span> <span id="k-q2">By May, <span class="y">everybody had.</span></span></div>
""", f"""
    {blur_in("#k-d", LW(n, 0, "third"))}
    {nc_in("k-n", LW(n, 1, "N'Golo"))}
    {wipe("#k-r", LW(n, 1, "Caen"))}
    {stamp("#k-big", LW(n, 1, "5.6"), 0)}
    {blur_in("#k-l", LW(n, 1, "5.6") + 0.3)}
    {blur_in("#k-q1", LP(n, 2))}
    {blur_in("#k-q2", LW(n, 2, "By"))}
""")

n = "c3_plan"; D = B[n][1]
PX, PY, PW, PHh = 560, 130, 1180, 820
def pos(x, y): return PX + x * PW, PY + y * PHh
dots = {"gk": (0.06, 0.5, "Schmeichel"), "rb": (0.24, 0.14, "Simpson"), "cb1": (0.2, 0.38, "Morgan"), "cb2": (0.2, 0.62, "Huth"), "lb": (0.24, 0.86, "Fuchs"),
        "rm": (0.5, 0.12, "Mahrez"), "cm1": (0.46, 0.4, "Kanté"), "cm2": (0.46, 0.6, "Drinkwater"), "lm": (0.5, 0.88, "Albrighton"),
        "st1": (0.76, 0.4, "Okazaki"), "st2": (0.8, 0.6, "Vardy")}
dhtml = "".join(f'<div class="dt" id="pl-{k}" style="left:{pos(x,y)[0]-22}px;top:{pos(x,y)[1]-22}px"><i></i><span>{html.escape(lab)}</span></div>' for k, (x, y, lab) in dots.items())
scene(n, f"""
    #pl-k{{left:96px;top:200px;font-family:'League Gothic';font-size:120px;line-height:1;text-transform:uppercase;white-space:normal;width:420px}}
    #pl-p{{left:{PX}px;top:{PY}px;width:{PW}px;height:{PHh}px;border:3px solid rgba(245,245,240,.35)}}
    #pl-p .hw{{position:absolute;left:50%;top:0;width:3px;height:100%;background:rgba(245,245,240,.35)}}
    #pl-p .cc{{position:absolute;left:50%;top:50%;width:200px;height:200px;margin:-100px 0 0 -100px;border:3px solid rgba(245,245,240,.35);border-radius:50%}}
    #pl-p .bx1{{position:absolute;left:0;top:25%;width:14%;height:50%;border:3px solid rgba(245,245,240,.35);border-left:0}}
    #pl-p .bx2{{position:absolute;right:0;top:25%;width:14%;height:50%;border:3px solid rgba(245,245,240,.35);border-right:0}}
    #root .dt{{position:absolute;width:44px;height:44px}}
    #root .dt i{{position:absolute;inset:0;border-radius:50%;background:{BL};border:4px solid {WH}}}
    #root .dt span{{position:absolute;left:50%;top:52px;transform:translateX(-50%);font-weight:800;font-size:20px;letter-spacing:.08em;text-transform:uppercase;white-space:nowrap}}
    #pl-l1, #pl-l2{{position:absolute;height:3px;background:{Y};transform-origin:0 50%}}
    #pl-sub{{left:96px;top:600px;font-weight:800;font-size:28px;letter-spacing:.1em;text-transform:uppercase;color:{Y};width:420px;line-height:1.4}}
""", f"""
    <div id="pl-k" class="a">Two banks of four</div>
    <div id="pl-p" class="a"><div class="hw"></div><div class="cc"></div><div class="bx1"></div><div class="bx2"></div></div>
    {dhtml}
    <div id="pl-sub" class="a">Win it. Give it to Vardy and Mahrez. Fast.</div>
""", f"""
    {fade_in("#pl-p", 0.1, 0.6)}
    tl.fromTo(".dt", {{ opacity: 0, scale: 0.4 }}, {{ opacity: 1, scale: 1, duration: 0.3, stagger: 0.05, ease: "back.out(2)" }}, {LW(n, 0, "Two"):.3f});
    {blur_in("#pl-k", LW(n, 0, "Two"))}
    tl.to("#pl-cm1 i", {{ background: "{Y}", borderColor: "{Y}", duration: 0.15 }}, {LW(n, 1, "Win"):.3f});
    tl.to("#pl-rm i, #pl-st2 i", {{ background: "{Y}", borderColor: "{Y}", duration: 0.15 }}, {LW(n, 1, "Vardy"):.3f});
    tl.fromTo("#pl-cm1", {{ x: 0 }}, {{ x: 0, duration: 0.01 }}, 0);
    tl.fromTo("#pl-rm, #pl-st2", {{ x: 0 }}, {{ x: 140, duration: {LW(n, 1, "fast") - LW(n, 1, "Vardy") + 0.6:.2f}, ease: "power2.inOut" }}, {LW(n, 1, "Vardy"):.3f});
    {blur_in("#pl-sub", LW(n, 1, "fast"))}
""")

# =================================================================== CH4
n = "c4_run"; D = B[n][1]
res = [("8 Aug 2015", "Leicester 4–2 Sunderland", "Opening day"), ("13 Sep 2015", "Leicester 3–2 Aston Villa", "From 2–0 down"), ("26 Sep 2015", "Leicester 2–5 Arsenal", "Defeat 1")]
boxes = "".join(f'<div class="bx" id="g{k}"><span>{k+1}</span></div>' for k in range(11))
scene(n, f"""
    #r-list{{left:150px;top:260px}}
    #root .bx{{width:120px;height:120px;border:4px solid rgba(245,245,240,.25);display:flex;align-items:center;justify-content:center;font-family:'League Gothic';font-size:70px;color:rgba(245,245,240,.3)}}
    #r-boxes{{left:150px;top:420px;display:flex;gap:28px}}
    #r-k{{left:150px;top:300px}}
    #r-big{{left:150px;top:620px;display:flex;align-items:baseline;gap:30px}}
    #r-big .lg{{font-size:200px;color:{Y}}}
    #r-big span.l{{font-weight:800;font-size:30px;letter-spacing:.1em;text-transform:uppercase;line-height:1.35}}
    #r-old{{left:150px;top:860px;font-weight:800;font-size:28px;letter-spacing:.1em;text-transform:uppercase;color:rgba(245,245,240,.7)}}
""", f"""
    <div id="r-list" class="a">{"".join(f'<div class="res" id="r-r{k}" style="position:relative;margin-bottom:34px"><span class="d">{d}</span><span class="t">{t}</span><span class="n" style="{"color:"+R if "Defeat" in nn else ""}">{nn}</span></div>' for k, (d, t, nn) in enumerate(res))}</div>
    {namecard("r-n", "Jamie Vardy", "Premier League games in a row with a goal", 150, 170)}
    <div id="r-boxes" class="a">{boxes}</div>
    <div id="r-big" class="a"><span class="lg">11</span><span class="l">games in a row · new record<br><span class="g">28 Nov 2015 · Leicester 1–1 Man Utd</span></span></div>
    <div id="r-old" class="a">Old record: 10 · Ruud van Nistelrooy</div>
""", f"""
    {wipe("#r-r0", LW(n, 0, "Sunderland"))}
    {wipe("#r-r1", LW(n, 1, "Villa"))}
    {wipe("#r-r2", LW(n, 2, "Arsenal"))}
    {fade_out("#r-list", LP(n, 3) - 0.3)}
    {nc_in("r-n", LW(n, 3, "Vardy"))}
    tl.fromTo(".bx", {{ opacity: 0, y: 20 }}, {{ opacity: 1, y: 0, duration: 0.3, stagger: 0.03, ease: "expo.out" }}, {LW(n, 3, "scoring"):.3f});
    {"".join(f'tl.to("#g{k}", {{ background: "{Y}", borderColor: "{Y}", color: "{BK}", duration: 0.12 }}, {t:.3f});' + chr(10) + "    " for k, t in enumerate([LW(n, 4, "One"), LW(n, 4, "another"), LW(n, 4, "Then", True) + 0.6] + [LW(n, 5, "against") + k * 0.42 for k in range(7)] + [LW(n, 5, "11th")]))}
    {pop("#g10", LW(n, 5, "11th"), 1.35)}
    {rise("#r-big", LW(n, 5, "11th") + 0.15)}
    {blur_in("#r-old", LW(n, 6, "record"))}
""")

n = "c4_pizza"; D = B[n][1]
scene(n, f"""
    #pz{{left:1180px;top:240px;width:520px;height:520px;border-radius:50%;background:radial-gradient(circle,#e8b04a 0 58%,#c98a2c 59% 66%,#b4742a 67%)}}
    #pz i{{position:absolute;width:62px;height:62px;border-radius:50%;background:#b8341f}}
    #pz .cut{{position:absolute;left:50%;top:0;width:4px;height:100%;background:rgba(10,10,10,.35);transform-origin:50% 50%}}
    #pz-k{{left:150px;top:300px}}
    #pz-t{{left:144px;top:350px;font-size:190px}}
    #pz-d{{left:150px;top:720px}}
    #pz-s{{left:150px;top:780px;font-weight:800;font-size:32px;letter-spacing:.08em;text-transform:uppercase}}
""", f"""
    <div id="pz-k" class="a kick y">Ranieri's deal</div>
    <div id="pz-t" class="a lg">Clean sheet<br>= <span class="y">pizza</span></div>
    <div id="pz" class="a">{"".join(f'<div class="cut" style="transform:rotate({a}deg)"></div>' for a in (0, 45, 90, 135))}{"".join(f'<i style="left:{x}px;top:{y}px"></i>' for x, y in ((120, 130), (300, 110), (380, 260), (240, 330), (110, 300), (300, 400), (200, 200)))}</div>
    <div id="pz-d" class="a kick g">Late October 2015</div>
    <div id="pz-s" class="a">First clean sheet. The players made the pizzas themselves.</div>
""", f"""
    {blur_in("#pz-k", LW(n, 0, "promise"))}
    {wipe("#pz-t", LW(n, 0, "clean"), 0.6)}
    tl.fromTo("#pz", {{ opacity: 0, scale: 0.6, rotation: -40 }}, {{ opacity: 1, scale: 1, rotation: 0, duration: 0.7, ease: "back.out(1.6)" }}, {LW(n, 0, "pizza"):.3f});
    tl.fromTo("#pz", {{ rotation: 0 }}, {{ rotation: 25, duration: {D:.2f}, ease: "none", immediateRender: false }}, {LW(n, 0, "pizza") + 0.7:.3f});
    {blur_in("#pz-d", LW(n, 1, "October"))}
    {blur_in("#pz-s", LW(n, 1, "players"))}
""")

n = "c4_bell"; D = B[n][1]
scene(n, f"""
    #bl-k{{left:0;width:{W}px;top:260px;text-align:center}}
    #bl-a, #bl-b{{left:0;width:{W}px;text-align:center;font-size:230px}}
    #bl-a{{top:330px}} #bl-b{{top:560px;color:{Y}}}
    #bl-c{{left:0;width:{W}px;top:820px;text-align:center;font-weight:800;font-size:32px;letter-spacing:.16em;text-transform:uppercase;color:rgba(245,245,240,.75)}}
""", f"""
    <div id="bl-k" class="a kick g">Ranieri in training</div>
    <div id="bl-a" class="a lg">Dilly ding,</div>
    <div id="bl-b" class="a lg">dilly dong.</div>
    <div id="bl-c" class="a">Wake up.</div>
""", f"""
    {blur_in("#bl-k", LW(n, 0, "catchphrase"))}
    {stamp("#bl-a", LW(n, 1, "ding"), -2)}
    {stamp("#bl-b", LW(n, 1, "dong"), 2)}
    {blur_in("#bl-c", LW(n, 1, "Wake"))}
""")

# =================================================================== CH5
n = "c5_xmas"; D = B[n][1]
scene(n, f"""
    #x-l, #x-r{{top:250px;width:760px;text-align:center}}
    #x-l{{left:160px}} #x-r{{left:1000px}}
    #x-l .lg, #x-r .lg{{font-size:400px;display:block}}
    #x-l .k, #x-r .k{{font-weight:800;font-size:32px;letter-spacing:.14em;text-transform:uppercase;display:block;margin-bottom:24px}}
    #x-div{{left:958px;top:280px;width:4px;height:520px;background:rgba(245,245,240,.2)}}
""", f"""
    <div id="x-l" class="a"><span class="k g">Christmas 2014</span><span class="lg g">20th</span></div>
    <div id="x-div" class="a"></div>
    <div id="x-r" class="a"><span class="k y">Christmas 2015</span><span class="lg y">1st</span></div>
""", f"""
    {stamp("#x-r", LW(n, 0, "top"), 0)}
    {fade_in("#x-div", LP(n, 1), 0.4)}
    {blur_in("#x-l", LW(n, 1, "bottom") - 0.2)}
""")

n = "c5_wait"; D = B[n][1]
scene(n, f"""
    #w-t{{left:150px;top:300px;font-family:'League Gothic';font-size:120px;line-height:1;text-transform:uppercase;white-space:nowrap}}
    #w-r{{left:150px;top:470px}}
    #w-c{{left:150px;top:640px;font-family:'League Gothic';font-size:120px;line-height:1;text-transform:uppercase;color:{R};white-space:nowrap}}
""", f"""
    <div id="w-t" class="a">This is where stories like this end.</div>
    <div id="w-r" class="a"><div class="res" style="position:relative"><span class="d">26 Dec 2015</span><span class="t">Liverpool 1–0 Leicester</span><span class="n" style="color:{R}">Defeat 2</span></div></div>
    <div id="w-c" class="a">Waiting for the collapse…</div>
""", f"""
    {blur_in("#w-t", 0.25)}
    tl.to("#w-t", {{ opacity: 0.35, duration: 0.3 }}, {LP(n, 1) - 0.2:.3f});
    {wipe("#w-r", LW(n, 1, "Liverpool"))}
    {blur_in("#w-c", LW(n, 2, "collapse") - 0.3)}
    tl.to("#w-c", {{ y: 60, opacity: 0.6, duration: {D - LW(n, 2, "collapse"):.2f}, ease: "power1.in" }}, {LW(n, 2, "collapse") + 0.2:.3f});
""")

# =================================================================== CH6
n = "c6_city"; D = B[n][1]
scene(n, f"""
    #ci-t{{left:0;width:{W}px;top:180px;text-align:center;font-family:'League Gothic';font-size:110px;line-height:1;text-transform:uppercase}}
    #ci-k{{left:0;width:{W}px;top:330px;text-align:center}}
    #ci-sc2{{left:0;width:{W}px;top:720px;text-align:center;font-weight:800;font-size:34px;letter-spacing:.12em;text-transform:uppercase}}
""", f"""
    <div id="ci-t" class="a">The collapse never came.</div>
    <div id="ci-k" class="a kick y">6 Feb 2016 · Etihad Stadium · against the favourites</div>
    {scoreboard("ci", "Man City", "Leicester", 1, 3, hc="#6CABDD", ac=BL, act=WH, top=390, size=280)}
    <div id="ci-sc2" class="a">Huth 2 · Mahrez <span class="g">— Agüero</span></div>
""", f"""
    {blur_in("#ci-t", 0.2)}
    {fade_out("#ci-t", LP(n, 1) - 0.2)}
    {blur_in("#ci-k", LW(n, 1, "Manchester"))}
    {rise("#ci-sb > *", LW(n, 1, "Manchester"), 0.5, 0.1)}
    {textswap("ci-sc", [[0, "–"], [LW(n, 1, "won"), "1–3"]], D)}
    {pop("#ci-sc", LW(n, 1, "won"), 1.25)}
    {blur_in("#ci-sc2", LW(n, 2, "Huth"))}
""")

n = "c6_arsenal"; D = B[n][1]
scene(n, f"""
    #ar-ph{{inset:0}}
    #ar-k{{left:96px;top:150px}}
    #ar-sb{{left:96px;top:200px;display:flex;align-items:center;gap:30px}}
    #ar-sb .lg{{font-size:200px}}
    #ar-clk{{left:96px;top:420px;font-family:'League Gothic';font-size:80px;color:{Y}}}
    #ar-ev{{left:96px;top:540px;display:flex;flex-direction:column;gap:14px}}
    #ar-ev div{{font-weight:800;font-size:30px;letter-spacing:.08em;text-transform:uppercase;white-space:nowrap}}
    #ar-ev .rc{{display:inline-block;width:22px;height:30px;background:{R};vertical-align:-4px;margin-right:12px}}
    #ar-last{{left:96px;top:840px;font-family:'League Gothic';font-size:96px;line-height:1;text-transform:uppercase;color:{Y};white-space:nowrap}}
""", f"""
    {photo("ar-ph", "ranieri_appeal", "inset:0", "linear-gradient(90deg,rgba(10,10,10,.95) 0%,rgba(10,10,10,.75) 45%,rgba(10,10,10,.2) 100%)")}
    <div id="ar-k" class="a kick y">14 Feb 2016 · Emirates Stadium</div>
    <div id="ar-sb" class="a"><span class="chip" style="background:#EF0107">Arsenal</span><span class="lg" id="ar-s">0–0</span><span class="chip" style="background:{BL}">Leicester</span></div>
    <div id="ar-clk" class="a"><span id="ar-c"></span></div>
    <div id="ar-ev" class="a"><div id="ar-e1">Vardy (pen) · 0–1</div><div id="ar-e2"><span class="rc"></span>Simpson sent off</div><div id="ar-e3">Walcott · 1–1</div><div id="ar-e4" class="y">Welbeck · 90+5' · 2–1</div></div>
    <div id="ar-last" class="a">Their last league defeat of the season</div>
    {credit("ranieri_appeal", "Ranieri at Arsenal, 14 Feb 2016 · ")}
""", f"""
    {fade_in("#ar-ph, .cred", 0, 0.8)}
    {kb("ar-ph", D, 0, -60, 1.02, 1.1)}
    {blur_in("#ar-k", 0.3)}
    {rise("#ar-sb > *", LW(n, 0, "Arsenal"), 0.45, 0.08)}
    {textswap("ar-s", [[0, "0–0"], [LW(n, 1, "Vardy"), "0–1"], [LW(n, 2, "Walcott"), "1–1"], [LW(n, 2, "headed"), "2–1"]], D)}
    {textswap("ar-c", [[0, ""], [LW(n, 2, "95th"), "90+5'"]], D)}
    {wipe("#ar-e1", LW(n, 1, "penalty"))}
    {wipe("#ar-e2", LW(n, 1, "sent"))}
    {wipe("#ar-e3", LW(n, 2, "Walcott"))}
    {wipe("#ar-e4", LW(n, 2, "Welbeck"))}
    {pop("#ar-s", LW(n, 2, "headed"), 1.25, "50% 50%")}
    {rise("#ar-last", LW(n, 3, "last"))}
""")

# =================================================================== CH7
n = "c7_grind"; D = B[n][1]
scene(n, f"""
    #gr-ph{{inset:0}}
    #gr-t{{left:0;width:{W}px;top:300px;text-align:center;font-family:'League Gothic';font-size:130px;line-height:1;text-transform:uppercase}}
    #gr-ones{{left:0;width:{W}px;top:470px;display:flex;justify-content:center;gap:50px}}
    #gr-ones span{{font-family:'League Gothic';font-size:220px;line-height:1;color:{Y}}}
    #gr-list{{left:96px;top:560px}}
""", f"""
    {photo("gr-ph", "soton", "inset:0", "linear-gradient(0deg,rgba(10,10,10,.97) 0%,rgba(10,10,10,.9) 45%,rgba(10,10,10,.45) 75%,rgba(10,10,10,.35) 100%)")}
    <div id="gr-t" class="a">The pressure was supposed to break them.</div>
    <div id="gr-ones" class="a"><span>1–0</span><span>1–0</span><span>1–0</span><span>1–0</span></div>
    <div id="gr-list" class="a">
      <div class="res" id="gr-r1" style="position:relative;margin-bottom:28px"><span class="d">3 Apr 2016</span><span class="t">Leicester 1–0 Southampton</span><span class="n">Morgan header</span></div>
      <div class="res" id="gr-r2" style="position:relative;margin-bottom:28px"><span class="d">17 Apr 2016</span><span class="t">Leicester 2–2 West Ham</span><span class="n" style="color:{R}">Vardy sent off · Ulloa pen, stoppage time</span></div>
      <div class="res" id="gr-r3" style="position:relative"><span class="d">24 Apr 2016</span><span class="t">Leicester 4–0 Swansea</span><span class="n">Without Vardy</span></div>
    </div>
    {credit("soton", "Leicester v Southampton, 3 Apr 2016 · ")}
""", f"""
    {blur_in("#gr-t", 0.25)}
    tl.fromTo("#gr-ones span", {{ opacity: 0, scale: 1.4 }}, {{ opacity: 1, scale: 1, duration: 0.2, stagger: 0.28, ease: "power4.out" }}, {LW(n, 1, "run"):.3f});
    tl.to("#gr-t, #gr-ones", {{ opacity: 0, duration: 0.3 }}, {LP(n, 2) - 0.3:.3f});
    {fade_in("#gr-ph, .cred", LP(n, 2) - 0.3, 0.8)}
    {kb("gr-ph", D - LP(n, 2), 0, -50, 1.02, 1.1, t=LP(n, 2))}
    {wipe("#gr-r1", LW(n, 2, "Wes"))}
    {wipe("#gr-r2", LW(n, 3, "West"))}
    {wipe("#gr-r3", LW(n, 4, "Swansea"))}
""")

n = "c7_chase"; D = B[n][1]
scene(n, f"""
    #ch-k{{left:150px;top:220px}}
    #root .tr{{position:absolute;left:150px;width:1000px;height:110px;display:flex;align-items:center;gap:30px;padding-left:30px;font-family:'League Gothic';font-size:80px;text-transform:uppercase}}
    #ch-1{{top:280px;background:{BL}}} #ch-2{{top:410px;background:rgba(245,245,240,.1)}}
    #ch-r{{left:150px;top:600px}}
    #ch-t{{left:150px;top:740px;font-family:'League Gothic';font-size:110px;line-height:1;text-transform:uppercase;white-space:nowrap}}
""", f"""
    <div id="ch-k" class="a kick y">The title race, May 2016</div>
    <div class="tr" id="ch-1"><span>1</span><span>Leicester City</span></div>
    <div class="tr" id="ch-2"><span class="g">2</span><span>Tottenham</span></div>
    <div id="ch-r" class="a"><div class="res" style="position:relative"><span class="d">1 May 2016</span><span class="t">Man Utd 1–1 Leicester</span></div></div>
    <div id="ch-t" class="a">One more win. <span class="y" id="ch-t2">Or one Spurs slip.</span></div>
""", f"""
    {blur_in("#ch-k", 0.2)}
    {wipe("#ch-1", LW(n, 0, "Tottenham") - 0.4)}
    {wipe("#ch-2", LW(n, 0, "chasing"))}
    {wipe("#ch-r", LW(n, 1, "Old"))}
    {blur_in("#ch-t", LW(n, 1, "One"))}
    {blur_in("#ch-t2", LP(n, 2))}
""")

# =================================================================== CH8
n = "c8_match"; D = B[n][1]
scene(n, f"""
    #m8-tv{{left:300px;top:150px;width:1320px;height:640px;border:3px solid rgba(245,245,240,.25);border-radius:28px;background:radial-gradient(ellipse at 50% 40%,#1b1b1b,#0d0d0d)}}
    #m8-scan{{left:303px;top:153px;width:1314px;height:634px;border-radius:26px;background:repeating-linear-gradient(0deg,rgba(255,255,255,.035) 0 2px,transparent 2px 5px)}}
    #m8-k{{left:0;width:{W}px;top:210px;text-align:center}}
    #m8-clk{{left:0;width:{W}px;top:640px;text-align:center;font-family:'League Gothic';font-size:64px;color:rgba(245,245,240,.7)}}
    #m8-yc{{left:1360px;top:200px;display:flex;align-items:center;gap:12px;font-family:'League Gothic';font-size:70px}}
    #m8-yc i{{width:34px;height:48px;background:{Y};display:block}}
    #m8-ev{{left:0;width:{W}px;top:840px;text-align:center;font-weight:800;font-size:34px;letter-spacing:.08em;text-transform:uppercase}}
    #m8-house{{left:0;width:{W}px;top:900px;text-align:center}}
""", f"""
    <div id="m8-tv" class="a"></div><div id="m8-scan" class="a"></div>
    <div id="m8-k" class="a kick y">2 May 2016 · Stamford Bridge</div>
    {scoreboard("m8", "Chelsea", "Tottenham", 0, 0, top=330, size=270)}
    <div id="m8-clk" class="a"><span id="m8-c">LIVE</span></div>
    <div id="m8-yc" class="a"><i></i><span id="m8-y">0</span></div>
    <div id="m8-ev" class="a"><span id="m8-e"></span></div>
    <div id="m8-house" class="a kick g">Watching at Jamie Vardy's house</div>
""", f"""
    tl.fromTo("#m8-tv, #m8-scan", {{ opacity: 0, scale: 0.96 }}, {{ opacity: 1, scale: 1, duration: 0.8, ease: "expo.out" }}, 0.1);
    {blur_in("#m8-k", 0.4)}
    {rise("#m8-sb > *", 0.5, 0.5, 0.1)}
    {fade_in("#m8-clk", 0.9)}
    {blur_in("#m8-house", LW(n, 1, "Vardy's"))}
    {fade_out("#m8-house", LP(n, 2) - 0.1)}
    {textswap("m8-sc", [[0, "0–0"], [LW(n, 2, "led"), "0–2"], [LW(n, 3, "Cahill"), "1–2"], [LW(n, 5, "equaliser") - 0.2, "2–2"]], D)}
    {textswap("m8-c", [[0, "LIVE"], [LW(n, 2, "half-time"), "HALF-TIME"], [LP(n, 3), "SECOND HALF"], [LP(n, 6), "FULL TIME"]], D)}
    {textswap("m8-e", [[0, ""], [LW(n, 2, "led"), "Spurs lead at the break"], [LW(n, 3, "Cahill"), "Cahill · Chelsea pull one back"], [LP(n, 4), "Tottenham: nine yellow cards"], [LW(n, 5, "Hazard"), "Hazard · the equaliser"], [LP(n, 6), "Tottenham can't catch Leicester"]], D)}
    {"".join(pop("#m8-sc", t, 1.25) + chr(10) + "    " for t in (LW(n, 2, "led"), LW(n, 3, "Cahill"), LW(n, 5, "equaliser") - 0.2))}
    {fade_in("#m8-yc", LP(n, 4), 0.2)}
    {textswap("m8-y", [[0, "0"]] + [[round(LW(n, 4, "nine") + k * 0.11, 3), str(k + 1)] for k in range(9)], D)}
    tl.to("#m8-ev", {{ color: "{Y}", duration: 0.2 }}, {LP(n, 6):.3f});
""")

n = "c8_champs"; D = B[n][1]
scene(n, f"""
    #cp-bg{{inset:0;background:{Y}}}
    #cp-k{{left:0;width:{W}px;top:240px;text-align:center;font-weight:900;font-size:36px;letter-spacing:.2em;color:{BK}}}
    #cp-t{{left:0;width:{W}px;top:290px;text-align:center;font-size:380px;color:{BK}}}
    #cp-s{{left:0;width:{W}px;top:680px;text-align:center;font-family:'League Gothic';font-size:110px;line-height:1;color:{BK};text-transform:uppercase}}
""", f"""
    <div id="cp-bg" class="a"></div>
    <div id="cp-k" class="a">LEICESTER CITY · 2 MAY 2016</div>
    <div id="cp-t" class="a lg">Champions</div>
    <div id="cp-s" class="a">From 5000–1</div>
""", f"""
    tl.fromTo("#cp-bg", {{ clipPath: "inset(50% 50% 50% 50%)" }}, {{ clipPath: "inset(0% 0% 0% 0%)", duration: 0.5, ease: "power3.inOut" }}, 0.1);
    {blur_in("#cp-k", 0.45)}
    {stamp("#cp-t", LW(n, 0, "champions"), 0)}
    {rise("#cp-s", LW(n, 0, "5000") )}
""")

# =================================================================== CH9
n = "c9_everton"; D = B[n][1]
scene(n, f"""
    #ev-k{{left:0;width:{W}px;top:200px;text-align:center}}
    #ev-nd{{left:0;width:{W}px;top:560px;text-align:center}}
    #ev-nd .q{{font-family:'League Gothic';font-size:120px;line-height:1;text-transform:uppercase}}
    #ev-nd .a2{{display:block;font-weight:800;font-size:26px;letter-spacing:.14em;color:rgba(245,245,240,.7);text-transform:uppercase;margin-top:12px}}
    #ev-sc2{{left:0;width:{W}px;top:580px;text-align:center;font-weight:800;font-size:34px;letter-spacing:.12em;text-transform:uppercase}}
    #ev-tr{{left:0;width:{W}px;top:760px;text-align:center;font-family:'League Gothic';font-size:96px;line-height:1;text-transform:uppercase;color:{Y}}}
""", f"""
    <div id="ev-k" class="a kick y">7 May 2016 · King Power Stadium</div>
    {scoreboard("ev", "Leicester", "Everton", "", "", hc=BL, ac="#003399", act=WH, top=270, size=260)}
    <div id="ev-nd" class="a"><span class="q">“Nessun Dorma”</span><span class="a2">Andrea Bocelli · before kick-off</span></div>
    <div id="ev-sc2" class="a">Vardy 2 · King <span class="g">— Mirallas</span></div>
    <div id="ev-tr" class="a">Morgan and Ranieri lift the trophy</div>
""", f"""
    {blur_in("#ev-k", LW(n, 0, "Five"))}
    {rise("#ev-sb > *", LW(n, 0, "Everton"), 0.5, 0.1)}
    {textswap("ev-sc", [[0, "v"], [LW(n, 2, "3–1"), "3–1"]], D)}
    {blur_in("#ev-nd", LW(n, 1, "Andrea"))}
    {fade_out("#ev-nd", LP(n, 2) - 0.2)}
    {pop("#ev-sc", LW(n, 2, "3–1"), 1.25)}
    {blur_in("#ev-sc2", LW(n, 2, "Vardy"))}
    {wipe("#ev-tr", LW(n, 3, "lifted"), 0.7)}
""")

n = "c9_table"; D = B[n][1]
tab = [("Leicester City", 81, BL), ("Arsenal", 71, "#2a2a2a"), ("Tottenham", 70, "#2a2a2a"), ("Man City", 66, "#2a2a2a")]
scene(n, f"""
    #tb-k{{left:150px;top:180px}}
    #root .tr2{{position:absolute;left:150px;height:120px;display:flex;align-items:center;font-family:'League Gothic';font-size:74px;text-transform:uppercase}}
    #root .tr2 .bar{{position:absolute;left:0;top:0;height:100%;transform-origin:0 50%}}
    #root .tr2 span{{position:relative;padding-left:28px;white-space:nowrap}}
    #root .tr2 .pt{{position:absolute;right:24px;top:22px}}
    #tb-gap{{left:1500px;top:230px;font-family:'League Gothic';font-size:150px;color:{Y}}}
    #tb-gl{{left:1500px;top:380px;font-weight:800;font-size:24px;letter-spacing:.12em;text-transform:uppercase}}
    #tb-def{{left:150px;top:860px;display:flex;align-items:baseline;gap:24px}}
    #tb-def .lg{{font-size:150px}}
    #tb-def span.l{{font-weight:800;font-size:28px;letter-spacing:.12em;text-transform:uppercase}}
""", f"""
    <div id="tb-k" class="a kick y">Premier League 2015–16 · final table</div>
    {"".join(f'<div class="tr2" id="tb-{k}" style="top:{240 + k*140}px;width:{int(1200*pts/81)}px"><div class="bar" style="width:100%;background:{col}"></div><span>{k+1}  {html.escape(nm)}</span><span class="pt">{pts}</span></div>' for k, (nm, pts, col) in enumerate(tab))}
    <div id="tb-gap" class="a lg">+10</div><div id="tb-gl" class="a">points clear</div>
    <div id="tb-def" class="a"><span class="lg y">3</span><span class="l">league defeats all season</span></div>
""", f"""
    {blur_in("#tb-k", 0.2)}
    tl.fromTo(".tr2 .bar", {{ scaleX: 0 }}, {{ scaleX: 1, duration: 0.8, stagger: 0.12, ease: "expo.out" }}, {LW(n, 0, "81") - 0.3:.3f});
    tl.fromTo(".tr2 span", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.3, stagger: 0.12 }}, {LW(n, 0, "81"):.3f});
    {stamp("#tb-gap", LW(n, 0, "ten"), 0)}
    {blur_in("#tb-gl", LW(n, 0, "clear"))}
    {rise("#tb-def", LW(n, 1, "three"))}
""")

n = "c9_awards"; D = B[n][1]
scene(n, f"""
    #aw-1, #aw-2{{top:120px;width:780px;height:840px;background:#141414;overflow:hidden}}
    #aw-1{{left:150px}} #aw-2{{left:990px}}
    #root .awp{{position:absolute;left:0;top:0;width:780px;height:440px}}
    #root .awt{{position:absolute;left:40px;top:470px;width:700px}}
    #root .awt .lg{{font-size:170px;color:{Y};display:block}}
    #root .awt b{{display:block;font-family:'League Gothic';font-weight:400;font-size:64px;line-height:1;text-transform:uppercase;margin-top:6px}}
    #root .awt em{{display:block;font-style:normal;font-weight:800;font-size:22px;letter-spacing:.12em;text-transform:uppercase;color:rgba(245,245,240,.7);margin-top:12px;line-height:1.4}}
""", f"""
    <div id="aw-1" class="a">{photo("aw-p1", "vardy", "left:0;top:0;width:780px;height:440px")}<div class="awt"><span class="lg">24</span><b>Jamie Vardy · league goals</b><em>Football Writers' Footballer of the Year</em></div></div>
    <div id="aw-2" class="a">{photo("aw-p2", "mahrez", "left:0;top:0;width:780px;height:440px")}<div class="awt"><span class="lg">1st</span><b>Riyad Mahrez · PFA award</b><em>First African winner of the PFA Players' Player of the Year</em></div></div>
    {credit("vardy", "Vardy pictured in 2019 · ")}
""", f"""
    {rise("#aw-1", LW(n, 0, "Vardy"), 0.6)}
    {kb("aw-p1", D, 0, 0, 1.0, 1.08, 0, -20)}
    {kb("aw-p2", D, 0, 0, 1.0, 1.08, 0, -20)}
    {pop("#aw-1 .lg", LW(n, 0, "24"), 1.2, "0 50%")}
    {rise("#aw-2", LW(n, 1, "Mahrez"), 0.6)}
    {fade_in(".cred", LW(n, 0, "Vardy"), 0.5)}
""")

# =================================================================== CH10
n = "c10_after"; D = B[n][1]
TLX0, TLX1, TLY = 200, 1720, 560
def tx(yr): return {2016.5: 300, 2017.15: 720, 2017.3: 1140, 2020.5: 1560}[yr]
pts = [("Jul 2016", 2016.5, "Kanté → Chelsea", "Champions again 2016–17", 1, "Kanté"), ("Feb 2017", 2017.15, "Ranieri sacked", "Nine months after the trophy", 3, "sacked"),
       ("Apr 2017", 2017.3, "Champions League", "Quarter-finals", 2, "quarter-finals"), ("2020", 2020.5, "Vardy · Golden Boot", "At 33", 4, "Golden")]
ptsh = ""
for k, (d, yr, a, b, ph, nd) in enumerate(pts):
    up = k % 2 == 0
    ptsh += f'<div class="tp" id="tp{k}" style="left:{tx(yr)-12}px;top:{TLY-12}px"><i></i></div><div class="tl{" up" if up else ""}" id="tl{k}" style="left:{tx(yr)-12}px;top:{TLY-250 if up else TLY+50}px"><span class="d">{d}</span><b>{html.escape(a)}</b><em>{html.escape(b)}</em></div>'
scene(n, f"""
    #af-t{{left:150px;top:180px;font-family:'League Gothic';font-size:96px;line-height:1;text-transform:uppercase;white-space:nowrap}}
    #af-line{{left:{TLX0}px;top:{TLY-2}px;width:{TLX1-TLX0}px;height:4px;background:rgba(245,245,240,.35);transform-origin:0 50%}}
    #root .tp{{position:absolute;width:24px;height:24px}}
    #root .tp i{{position:absolute;inset:0;border-radius:50%;background:{Y}}}
    #root .tl{{position:absolute;width:400px}}
    #root .tl .d{{display:block;font-weight:800;font-size:22px;letter-spacing:.14em;color:{Y};text-transform:uppercase}}
    #root .tl b{{display:block;font-family:'League Gothic';font-weight:400;font-size:62px;line-height:1;text-transform:uppercase;margin-top:6px;white-space:nowrap}}
    #root .tl em{{display:block;font-style:normal;font-weight:700;font-size:22px;letter-spacing:.1em;color:rgba(245,245,240,.65);text-transform:uppercase;margin-top:6px}}
""", f"""
    <div id="af-t" class="a">Fairy tales don't have a second chapter.</div>
    <div id="af-line" class="a"></div>
    {ptsh}
""", f"""
    {blur_in("#af-t", 0.25)}
    tl.fromTo("#af-line", {{ scaleX: 0 }}, {{ scaleX: 1, duration: 1.2, ease: "power2.inOut" }}, {LW(n, 0, "This"):.3f});
    {"".join(f'tl.fromTo("#tp{k}", {{ scale: 0 }}, {{ scale: 1, duration: 0.25, ease: "back.out(3)" }}, {LW(n, ph, nd) - 0.1:.3f});' + chr(10) + "    " + rise(f"#tl{k}", LW(n, ph, nd) - 0.05) + chr(10) + "    " for k, (d, yr, a, b, ph, nd) in enumerate(pts))}
""")

n = "c10_vichai"; D = B[n][1]
scene(n, f"""
    #vi-n{{left:0;width:{W}px;top:430px;text-align:center;font-family:'League Gothic';font-size:120px;line-height:1;text-transform:uppercase}}
    #vi-d{{left:0;width:{W}px;top:570px;text-align:center;font-weight:700;font-size:32px;letter-spacing:.3em;color:rgba(245,245,240,.7)}}
    #vi-r{{left:0;width:{W}px;top:640px;text-align:center;font-weight:600;font-size:24px;letter-spacing:.12em;color:rgba(245,245,240,.5);text-transform:uppercase}}
""", f"""
    <div id="vi-n" class="a">Vichai Srivaddhanaprabha</div>
    <div id="vi-d" class="a">1958 – 2018</div>
    <div id="vi-r" class="a">Leicester City chairman, 2010–2018</div>
""", f"""
    {fade_in("#vi-n", LW(n, 0, "owner"), 1.2)}
    {fade_in("#vi-d", LW(n, 0, "died"), 1.0)}
    {fade_in("#vi-r", LW(n, 0, "stadium"), 1.0)}
""")

n = "c10_cup"; D = B[n][1]
scene(n, f"""
    #cu-y{{left:0;width:{W}px;top:220px;text-align:center;font-size:420px;color:{Y}}}
    #cu-t{{left:0;width:{W}px;top:640px;text-align:center;font-family:'League Gothic';font-size:120px;line-height:1;text-transform:uppercase}}
    #cu-s{{left:0;width:{W}px;top:780px;text-align:center;font-weight:800;font-size:30px;letter-spacing:.14em;text-transform:uppercase;color:rgba(245,245,240,.7)}}
""", f"""
    <div id="cu-y" class="a lg">2021</div>
    <div id="cu-t" class="a">FA Cup winners</div>
    <div id="cu-s" class="a">The first in the club's history</div>
""", f"""
    {stamp("#cu-y", LW(n, 0, "2021"), 0)}
    {rise("#cu-t", LW(n, 0, "FA"))}
    {blur_in("#cu-s", LW(n, 0, "first"))}
""")

# =================================================================== CLOSE
n = "close"; D = B[n][1]
scene(n, f"""
    #cl-ph{{inset:0}}
    #cl-q{{left:150px;top:400px;font-family:'League Gothic';font-size:150px;line-height:1;text-transform:uppercase;white-space:nowrap}}
    #cl-g{{left:150px;top:400px;font-family:'League Gothic';font-size:110px;line-height:1.02;text-transform:uppercase;width:1400px;white-space:normal}}
    #cl-yr{{left:142px;top:300px;font-size:330px;color:{Y}}}
    #cl-3{{left:150px;top:260px;display:flex;flex-direction:column;gap:6px}}
    #cl-3 span{{font-family:'League Gothic';font-size:140px;line-height:1;text-transform:uppercase;white-space:nowrap}}
    #cl-once{{left:150px;top:760px;font-family:'League Gothic';font-size:150px;line-height:1;text-transform:uppercase;color:{Y};white-space:nowrap}}
""", f"""
    {photo("cl-ph", "clocktower", "inset:0", "linear-gradient(90deg,rgba(10,10,10,.95) 0%,rgba(10,10,10,.7) 55%,rgba(10,10,10,.45) 100%)")}
    <div id="cl-q" class="a">Could it happen again?</div>
    <div id="cl-g" class="a">The gap between the richest clubs and everyone else is <span class="y">wider than ever.</span></div>
    <div id="cl-yr" class="a lg">2015–16</div>
    <div id="cl-3" class="a"><span id="cl-a">A manager nobody wanted.</span><span id="cl-b">Players nobody rated.</span><span id="cl-c" class="y">5000–1.</span></div>
    <div id="cl-once" class="a">It happened once.</div>
    {credit("clocktower", "Leicester Clock Tower, c.1909 · ")}
""", f"""
    {fade_in("#cl-ph, .cred", 0, 1.2)}
    {kb("cl-ph", D, 0, 0, 1.02, 1.12, 0, -40)}
    {blur_in("#cl-q", LW(n, 0, "Could"))}
    {blur_out("#cl-q", LP(n, 1) - 0.2)}
    {blur_in("#cl-g", LW(n, 1, "gap"))}
    {blur_out("#cl-g", LP(n, 2) - 0.2)}
    {stamp("#cl-yr", LW(n, 2, "2015–16"), 0)}
    {blur_out("#cl-yr", LP(n, 3) - 0.2)}
    {rise("#cl-a", LW(n, 3, "manager"))}
    {rise("#cl-b", LW(n, 3, "Players"))}
    {stamp("#cl-c", LW(n, 3, "5000"), 0)}
    {wipe("#cl-once", LP(n, 4), 0.6)}
""")

n = "close_q"; D = B[n][1]
scene(n, f"""
    #cq-t{{left:0;width:{W}px;top:330px;text-align:center;font-size:190px;line-height:.95;white-space:normal}}
    #cq-s{{left:0;width:{W}px;top:760px;text-align:center;font-weight:800;font-size:32px;letter-spacing:.16em;text-transform:uppercase;color:{Y}}}
""", f"""
    <div id="cq-t" class="a lg">Will we ever see<br>another Leicester?</div>
    <div id="cq-s" class="a">Tell us in the comments</div>
""", f"""
    {blur_in("#cq-t", 0.2, 0.5)}
    {blur_in("#cq-s", LW(n, 0, "Tell"))}
""")

n = "brand"; D = B[n][1]
scene(n, f"""
    #o-line{{left:0;top:330px;width:6px;height:260px;background:{Y}}}
    #o-word{{left:0;top:360px;width:{W}px;text-align:center;font-size:260px}}
    #o-word span{{display:inline-block}}
    #o-st{{left:0;top:600px;width:{W}px;text-align:center;font-weight:900;font-size:62px;letter-spacing:.42em;padding-left:.42em}}
    #o-tag{{left:0;top:720px;width:{W}px;text-align:center;font-weight:800;font-size:40px;letter-spacing:.12em;color:{Y}}}
    #o-fol{{left:0;top:800px;width:{W}px;text-align:center;font-weight:700;font-size:28px;letter-spacing:.14em;color:rgba(245,245,240,.75)}}
""", """
    <div id="o-line" class="a"></div>
    <div id="o-word" class="a lg"><span>O</span><span>F</span><span>F</span><span>S</span><span>I</span><span>D</span><span id="o-e">E</span></div>
    <div id="o-st" class="a">STORIES</div>
    <div id="o-tag" class="a">BEYOND THE 90 MINUTES.</div>
    <div id="o-fol" class="a">SUBSCRIBE FOR MORE FOOTBALL STORIES</div>
""", f"""
    const e = document.getElementById("o-e").getBoundingClientRect(), root = document.querySelector('[data-composition-id="brand"]').getBoundingClientRect();
    gsap.set("#o-line", {{ x: e.left - root.left - 8 }});
    tl.fromTo("#o-line", {{ scaleY: 0, transformOrigin: "50% 0" }}, {{ scaleY: 1, duration: 0.4, ease: "expo.out" }}, 0.0);
    tl.fromTo("#o-word span", {{ opacity: 0, filter: "blur(8px)" }}, {{ opacity: 1, filter: "blur(0px)", duration: 0.18, stagger: 0.05, ease: "power4.out" }}, 0.15);
    tl.fromTo("#o-e", {{ x: -30 }}, {{ x: 22, duration: 0.28, ease: "back.out(2.2)" }}, 0.62);
    tl.fromTo("#o-st", {{ opacity: 0, scaleX: 1.35 }}, {{ opacity: 1, scaleX: 1, duration: 0.5, ease: "expo.out" }}, 0.75);
    {blur_in("#o-tag", LP(n, 1) - 0.1)}
    tl.fromTo("#o-fol", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.25 }}, {LP(n, 1) + 0.15:.3f});
""")

missing = [b for b in order if b not in SCENES]
assert not missing, missing

# =================================================================== WRITE
for k, v in SCENES.items(): open(f"compositions/{k}.html", "w").write(v)
hosts = "\n".join(f'      <div id="{k}" data-composition-id="{k}" data-composition-src="compositions/{k}.html" data-start="{B[k][0]}" data-duration="{B[k][1]}" data-track-index="0" data-track-kind="graphics" data-width="{W}" data-height="{H}" style="z-index:1"></div>' for k in order)
DUR = {"impact-bass-1": 2.1, "impact-bass-2": 2.5, "whoosh": 0.57, "whoosh-cinematic": 1.0, "riser": 4.0, "pop": 0.7, "key-press": 0.43, "click-soft": 0.36, "typing": 1.5, "sparkle": 1.5}
def at(t, peak=0.07): return round(t + 0.033 - peak, 3)
def G(n, k, needle): return WD(I(n, k), needle)
SFX = [("open", "impact-bass-2", 0.1, 0.25), ("ht", "impact-bass-1", at(G("co_tv", 3, "winning")), 0.3), ("odds", "impact-bass-2", at(G("co_odds", 0, "5000"), 0.03), 0.3),
       ("title", "whoosh-cinematic", at(B["co_title"][0] + 0.2, 0.2), 0.4)]
for c in TITLES: SFX.append((f"ch{c}", "whoosh-cinematic", at(B[c][0] + 0.3, 0.2), 0.35))
SFX += [("sack", "impact-bass-1", at(G("c1_pearson", 0, "sacked")), 0.3), ("400k", "impact-bass-2", at(G("c3_mahrez", 1, "400,000"), 0.03), 0.22),
        ("56", "impact-bass-2", at(G("c3_kante", 1, "5.6"), 0.03), 0.22), ("rec", "impact-bass-1", at(G("c4_run", 5, "11th")), 0.35),
        ("ding", "pop", at(G("c4_bell", 1, "ding"), 0.12), 0.8), ("dong", "pop", at(G("c4_bell", 1, "dong"), 0.12), 0.8),
        ("top", "impact-bass-1", at(G("c5_xmas", 0, "top")), 0.3), ("city", "pop", at(G("c6_city", 1, "won"), 0.12), 0.9),
        ("welb", "impact-bass-2", at(G("c6_arsenal", 2, "headed"), 0.03), 0.25),
        ("m8a", "pop", at(G("c8_match", 2, "led"), 0.12), 0.8), ("m8b", "pop", at(G("c8_match", 3, "Cahill"), 0.12), 0.8), ("m8c", "pop", at(G("c8_match", 5, "equaliser") - 0.2, 0.12), 0.9),
        ("rise", "riser", round(B["c8_champs"][0] + 0.2 - 3.5, 3), 0.4), ("champ", "impact-bass-1", at(G("c8_champs", 0, "champions")), 0.5), ("champs2", "sparkle", at(B["c8_champs"][0] + 0.15), 0.4),
        ("ev", "pop", at(G("c9_everton", 2, "3–1"), 0.12), 0.9), ("gap", "impact-bass-2", at(G("c9_table", 0, "ten"), 0.03), 0.22),
        ("2021", "impact-bass-2", at(G("c10_cup", 0, "2021"), 0.03), 0.25), ("5k", "impact-bass-1", at(G("close", 3, "5000")), 0.3),
        ("logo", "impact-bass-1", at(B["brand"][0] + 0.62), 0.4)]
ends, lanes = [], []
for sid, f, a, v in sorted(SFX, key=lambda x: x[2]):
    e = a + DUR[f]
    for li, le in enumerate(ends):
        if le <= a: ends[li] = e; break
    else: ends.append(e); li = len(ends) - 1
    fade = ' data-fade-out="0.4"' if f == "riser" else ""
    lanes.append(f'      <audio id="x-{sid}" class="clip" src="assets/sfx/{f}.mp3" data-start="{max(0, a)}" data-duration="{DUR[f]}" data-track-index="{20+li}" data-volume="{v}"{fade}></audio>')
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

# ---- SRT + chapters
def ts(t, sep=","):
    h = int(t // 3600); m = int(t % 3600 // 60); s = t % 60
    return f"{h:02d}:{m:02d}:{int(s):02d}{sep}{int(round((s - int(s)) * 1000)):03d}"
cues = []
for i in range(len(S)):
    wt = word_times(i); chunk = []
    for j, x in enumerate(wt):
        chunk.append(x)
        txt = " ".join(w for w, _, _ in chunk)
        if len(txt) > 38 or re.search(r"[.?!]$", x[0]) or j == len(wt) - 1:
            cues.append([chunk[0][1], chunk[-1][2] + 0.25, txt]); chunk = []
for a_, b_ in zip(cues, cues[1:]): a_[1] = min(a_[1], b_[0] - 0.02)
srt = [f"{k}\n{ts(a_)} --> {ts(b_)}\n{t_}\n" for k, (a_, b_, t_) in enumerate(cues, 1)]; k = len(cues) + 1
open("offside-stories-lf01-leicester.srt", "w").write("\n".join(srt))
chap = [("Cold open: 2 May 2016", 0)] + [(f"Chapter {int(c[1:])}: {t}", B[c][0]) for c, t in TITLES.items()] + [("Could it happen again?", B["close"][0])]
open("chapters.txt", "w").write("\n".join(f"{int(t//60)}:{int(t%60):02d} {nm}" for nm, t in chap))
print("TOTAL", TOTAL, "scenes", len(order), "srt", k - 1)
