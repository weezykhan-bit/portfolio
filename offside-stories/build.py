"""Generates index.html and compositions/*.html for Offside Stories Ep 001.
Narration timing comes from vo/script.json (one TTS clip per phrase)."""
import json, re, html

S = json.load(open("vo/script.json"))
W, H = 1080, 1920
Y, R, WH, BK, BLUE = "#FFE600", "#E10600", "#F5F5F0", "#0A0A0A", "#1D428A"

BASE = f"""
    #root{{position:absolute;inset:0;overflow:hidden;background:{BK};color:{WH};font-family:Inter,sans-serif}}
    #root *{{box-sizing:border-box;margin:0}}
    #root .a{{position:absolute}}
    #root .lg{{font-family:'League Gothic',sans-serif;font-weight:400;line-height:.86;letter-spacing:.005em;text-transform:uppercase;white-space:nowrap}}
    #root .kick{{font-weight:800;font-size:38px;letter-spacing:.14em;text-transform:uppercase}}
    #root .y{{color:{Y}}} #root .r{{color:{R}}}
    #root .grain{{position:absolute;inset:0;opacity:.06;background-image:radial-gradient(rgba(255,255,255,.9) 1px,transparent 1.4px);background-size:7px 7px}}
"""

def scene(cid, css, body, js):
    return f"""<template>
  <style>{BASE}{css}
  </style>
  <div id="root" data-composition-id="{cid}" data-width="{W}" data-height="{H}">
{body}
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
{js}
    window.__timelines["{cid}"] = tl;
  </script>
</template>
"""

# shared pyramid ladder (tiers top->bottom)
TIERS = ["PREMIER LEAGUE", "CHAMPIONSHIP", "LEAGUE ONE", "LEAGUE TWO", "NON-LEAGUE"]
def ladder(p, top=560, extra=""):
    rows = []
    for i, t in enumerate(TIERS):
        w = 360 + i * 100
        rows.append(f'<div class="a tier" id="{p}-t{i}" style="left:{540 - w//2}px;top:{top + i*104}px;width:{w}px"><span>{t}</span></div>')
    return "\n".join(rows) + f'\n    <div class="a dot" id="{p}-dot" style="left:{540-22}px;top:{top + 4*104 - 30}px"></div>'
LADDER_CSS = f"""
    #root .tier{{height:88px;border:3px solid rgba(245,245,240,.35);display:flex;align-items:center;justify-content:center;background:#0A0A0A;z-index:2}}
    #root .tier span{{font-weight:800;font-size:30px;letter-spacing:.16em;color:rgba(245,245,240,.6)}}
    #root .dot{{width:44px;height:44px;border-radius:50%;background:{Y};z-index:3}}
"""
def tier_y(i, top=560):  # dot top for tier i
    return top + i * 104 - 30

# ---------------------------------------------------------------- S1 HOOK
s1 = scene("hook", LADDER_CSS + f"""
    #h-pitch{{left:0;top:0}}
    #h-pitch *{{fill:none;stroke:{WH};stroke-width:4;opacity:.22}}
    #h-from{{left:120px;top:330px}}
    #h-big{{left:122px;top:396px;font-size:330px}}
    #h-to{{left:120px;top:400px}}
    #h-leg{{left:122px;top:466px;font-size:400px}}
    #h-sub{{left:120px;top:830px;font-weight:800;font-size:44px;letter-spacing:.06em;text-transform:uppercase}}
    #h-run{{left:518px;top:1460px;width:44px;height:44px;border-radius:50%;background:{Y}}}
    #h-trail{{left:534px;top:1482px;width:12px;height:0;background:{Y}}}
    #h-flash{{inset:0;background:{WH};opacity:0}}
""", f"""
    <div class="grain"></div>
    <svg id="h-pitch" class="a" width="1080" height="1920" viewBox="0 0 1080 1920">
      <g id="h-pg">
      <rect class="pl" x="150" y="230" width="780" height="1460"/>
      <line class="pl" x1="150" y1="960" x2="930" y2="960"/>
      <circle class="pl" cx="540" cy="960" r="130"/>
      <rect class="pl" x="330" y="230" width="420" height="250"/>
      <rect class="pl" x="330" y="1440" width="420" height="250"/>
      <rect class="pl" x="440" y="230" width="200" height="90"/>
      <rect class="pl" x="440" y="1600" width="200" height="90"/>
      </g>
    </svg>
    <div id="h-trail" class="a"></div>
    <div id="h-run" class="a"></div>
    <div id="h-txt1" class="a" style="inset:0">
      <div id="h-from" class="a kick">From</div>
      <div id="h-big" class="a lg">Non-<br>League</div>
    </div>
    <div id="h-txt2" class="a" style="inset:0">
      <div id="h-to" class="a kick">To</div>
      <div id="h-leg" class="a lg y">Legend.</div>
      <div id="h-sub" class="a">Premier League champion · 2016</div>
    </div>
    <div id="h-flash" class="a"></div>
""", f"""
    tl.fromTo("#h-pitch .pl", {{ strokeDasharray: 2400, strokeDashoffset: 1400 }}, {{ strokeDashoffset: 0, duration: 1.4, ease: "power2.out", stagger: 0.05 }}, 0);
    tl.fromTo("#h-big", {{ scale: 1.08, transformOrigin: "0 50%" }}, {{ scale: 1, duration: 0.6, ease: "expo.out" }}, 0);
    tl.fromTo("#h-txt1", {{ x: 0, filter: "blur(0px)" }}, {{ x: -1150, filter: "blur(18px)", duration: 0.28, ease: "power3.in" }}, 2.35); tl.set("#h-txt1", {{ opacity: 0 }}, 2.64);
    tl.fromTo("#h-pg", {{ scale: 1, transformOrigin: "540px 1480px" }}, {{ scale: 1.5, duration: 2.6, ease: "power2.inOut" }}, 2.45);
    tl.fromTo("#h-run", {{ y: 0 }}, {{ y: -980, duration: 2.5, ease: "power2.inOut" }}, 2.5);
    tl.fromTo("#h-trail", {{ height: 0, y: 0 }}, {{ height: 980, y: -980, duration: 2.5, ease: "power2.inOut" }}, 2.5);
    tl.fromTo("#h-flash", {{ opacity: 0 }}, {{ opacity: 0.95, duration: 0.05 }}, 5.38);
    tl.set("#h-pitch, #h-run, #h-trail", {{ opacity: 0 }}, 5.44);
    tl.to("#h-flash", {{ opacity: 0, duration: 0.18, ease: "power2.out" }}, 5.44);
    tl.fromTo("#h-txt2", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.01 }}, 5.43);
    tl.fromTo("#h-leg", {{ x: 900, filter: "blur(18px)" }}, {{ x: 0, filter: "blur(0px)", duration: 0.45, ease: "expo.out" }}, 5.43);
    tl.fromTo("#h-to", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.15 }}, 5.55);
    tl.fromTo("#h-sub", {{ opacity: 0, filter: "blur(6px)" }}, {{ opacity: 1, filter: "blur(0px)", duration: 0.2, ease: "power4.out" }}, 7.1);
""")

# ---------------------------------------------------------------- S2 STRUGGLE
s2 = scene("struggle", LADDER_CSS + f"""
    #s-k{{left:120px;top:330px}}
    #s-j{{left:122px;top:390px;font-size:300px}}
    #s-v{{left:122px;top:640px;font-size:300px}}
    #s-club{{left:120px;top:912px;font-weight:800;font-size:40px;letter-spacing:.1em;text-transform:uppercase;color:rgba(245,245,240,.7)}}
    #s-rel{{left:120px;top:968px;font-family:'League Gothic';font-size:96px;line-height:1;color:{R};border:6px solid {R};padding:6px 22px 0;text-transform:uppercase}}
    #s-card{{left:170px;top:400px;width:740px;height:560px;background:{WH};color:{BK};padding:44px 48px}}
    #s-card h4{{font-family:'League Gothic';font-weight:400;font-size:120px;line-height:.9;text-transform:uppercase}}
    #s-card .row{{display:flex;justify-content:space-between;border-top:3px solid {BK};padding:16px 0 10px;font-weight:800;font-size:34px;letter-spacing:.06em;text-transform:uppercase}}
    #s-card .row b{{font-weight:600;letter-spacing:.02em}}
    #s-punch{{left:540px;top:770px;font-family:'League Gothic';font-size:110px;line-height:1;background:{Y};color:{BK};padding:8px 26px 0;text-transform:uppercase}}
    #s-l1,#s-l2,#s-l3{{left:124px;top:330px;font-size:170px}}
""", f"""
    <div class="grain"></div>
    <div id="s-name" class="a" style="inset:0">
      <div id="s-k" class="a kick y">Meet</div>
      <div id="s-j" class="a lg">Jamie</div>
      <div id="s-v" class="a lg y">Vardy</div>
      <div id="s-club" class="a">Sheffield Wednesday academy</div>
      <div id="s-rel" class="a">Released at 16</div>
    </div>
    <div id="s-card" class="a">
      <h4>Time card</h4>
      <div class="row"><span>Name</span><b>J. Vardy</b></div>
      <div class="row"><span>Job</span><b>Factory · medical splints</b></div>
      <div class="row"><span>Evenings</span><b>Non-league football</b></div>
    </div>
    <div id="s-punch" class="a">Shift over</div>
    <div id="s-lad" class="a" style="inset:0">
    {ladder("s", top=560)}
    </div>
    <div id="s-l1" class="a lg">No fame.</div>
    <div id="s-l2" class="a lg">No shortcuts.</div>
    <div id="s-l3" class="a lg y">Just a dream.</div>
""", f"""
    tl.fromTo("#s-k", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.1 }}, 0.02);
    tl.fromTo("#s-j", {{ opacity: 0, filter: "blur(10px)", x: -40 }}, {{ opacity: 1, filter: "blur(0px)", x: 0, duration: 0.3, ease: "expo.out" }}, 0.06);
    tl.fromTo("#s-v", {{ opacity: 0, filter: "blur(10px)", x: 40 }}, {{ opacity: 1, filter: "blur(0px)", x: 0, duration: 0.3, ease: "expo.out" }}, 0.5);
    tl.fromTo("#s-club", {{ opacity: 0, color: "#555" }}, {{ opacity: 1, color: "rgba(245,245,240,.7)", duration: 0.3 }}, 2.3);
    tl.fromTo("#s-rel", {{ opacity: 0, scale: 1.5, rotation: -4 }}, {{ opacity: 1, scale: 1, rotation: -4, duration: 0.16, ease: "power4.out" }}, 4.25);
    tl.fromTo("#s-rel", {{ x: 0 }}, {{ x: 7, duration: 0.033, yoyo: true, repeat: 3, ease: "none" }}, 4.41);
    // factory: name block whips up, time card drops in
    tl.to("#s-name", {{ y: -1300, filter: "blur(16px)", duration: 0.3, ease: "power3.in" }}, 5.1); tl.set("#s-name", {{ opacity: 0 }}, 5.41);
    tl.fromTo("#s-card", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.01 }}, 5.33); tl.fromTo("#s-punch", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.01 }}, 6.75); tl.fromTo("#s-card", {{ y: 1400, rotation: 4, filter: "blur(16px)" }}, {{ y: 0, rotation: -2, filter: "blur(0px)", duration: 0.55, ease: "expo.out" }}, 5.33);
    tl.fromTo("#s-punch", {{ scale: 1.6, rotation: 6 }}, {{ scale: 1, rotation: 6, duration: 0.16, ease: "power4.out" }}, 6.75);
    // card falls away, ladder rises: the dot starts at the bottom
    tl.to("#s-card, #s-punch", {{ y: 1500, rotation: 10, duration: 0.45, ease: "power3.in" }}, 7.35); tl.set("#s-card, #s-punch", {{ opacity: 0 }}, 7.81);
    tl.fromTo("#s-lad .tier", {{ opacity: 0, y: 60 }}, {{ opacity: 1, y: 0, duration: 0.4, ease: "expo.out", stagger: {{ each: 0.06, from: "end" }} }}, 7.6);
    tl.fromTo("#s-t4", {{ borderColor: "rgba(245,245,240,.35)" }}, {{ borderColor: "{Y}", duration: 0.2 }}, 8.0);
    tl.fromTo("#s-t4 span", {{ color: "rgba(245,245,240,.6)" }}, {{ color: "{Y}", duration: 0.2 }}, 8.0);
    tl.fromTo("#s-dot", {{ scale: 0 }}, {{ scale: 1, duration: 0.3, ease: "back.out(2)" }}, 8.05);
    // three hard-cut lines
    tl.fromTo("#s-l1", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.01 }}, 7.7);
    tl.set("#s-l1", {{ opacity: 0 }}, 8.75);
    tl.fromTo("#s-l2", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.01 }}, 8.75);
    tl.set("#s-l2", {{ opacity: 0 }}, 9.75);
    tl.fromTo("#s-l3", {{ opacity: 0, scale: 1.12, transformOrigin: "0 50%" }}, {{ opacity: 1, scale: 1, duration: 0.25, ease: "expo.out" }}, 9.75);
""")

# ---------------------------------------------------------------- S3 BREAKTHROUGH
T = 560
s3 = scene("break", LADDER_CSS + f"""
    #b-dream{{left:120px;top:330px;font-size:170px}}
    #b-yr{{left:120px;top:290px;font-size:220px}}
    #b-lc{{left:120px;top:478px;font-weight:900;font-size:60px;letter-spacing:.02em;text-transform:uppercase}}
    #b-tr{{left:120px;top:1000px;font-weight:700;font-size:34px;letter-spacing:.08em;text-transform:uppercase;color:rgba(245,245,240,.65)}}
    #b-g1{{left:120px;top:430px;font-size:300px}}
    #b-g2{{left:120px;top:690px;font-size:300px}}
    #b-p1{{left:120px;top:420px;font-weight:800;font-size:56px;letter-spacing:.04em;text-transform:uppercase}}
    #b-p2{{left:120px;top:500px;font-size:330px}}
""", f"""
    <div class="grain"></div>
    <div id="b-lad" class="a" style="inset:0">
    {ladder("b", top=T)}
    </div>
    <div id="b-dream" class="a lg y">Just a dream.</div>
    <div id="b-yr" class="a lg">2012</div>
    <div id="b-lc" class="a">Leicester City</div>
    <div id="b-gam" class="a" style="inset:0">
      <div id="b-g1" class="a lg">Massive</div>
      <div id="b-g2" class="a lg">Gamble<span class="r">?</span></div>
    </div>
    <div id="b-pl" class="a" style="inset:0">
      <div id="b-p1" class="a">But Vardy had</div>
      <div id="b-p2" class="a lg y">Other<br>plans.</div>
    </div>
""", f"""
    tl.set("#b-t4", {{ borderColor: "{Y}" }}, 0).set("#b-t4 span", {{ color: "{Y}" }}, 0);
    tl.to("#b-dream", {{ opacity: 0, filter: "blur(10px)", duration: 0.15 }}, 0.05);
    tl.fromTo("#b-yr", {{ opacity: 0, y: -120, filter: "blur(12px)" }}, {{ opacity: 1, y: 0, filter: "blur(0px)", duration: 0.35, ease: "expo.out" }}, 0.12);
    // dot jumps non-league -> championship (Leicester were in the Championship in 2012)
    tl.fromTo("#b-dot", {{ y: 0 }}, {{ y: {tier_y(1,T) - tier_y(4,T)}, duration: 0.6, ease: "power3.inOut" }}, 1.35);
    tl.fromTo("#b-dot", {{ x: 0 }}, {{ x: 0, keyframes: {{ x: [0, 90, 0], ease: "sine.inOut" }}, duration: 0.6 }}, 1.35);
    tl.to("#b-t4", {{ borderColor: "rgba(245,245,240,.35)", duration: 0.2 }}, 1.4);
    tl.to("#b-t4 span", {{ color: "rgba(245,245,240,.6)", duration: 0.2 }}, 1.4);
    tl.fromTo("#b-t1", {{ backgroundColor: "rgba(29,66,138,0)", borderColor: "rgba(245,245,240,.35)" }}, {{ backgroundColor: "{BLUE}", borderColor: "{BLUE}", duration: 0.3 }}, 1.85);
    tl.fromTo("#b-t1 span", {{ color: "rgba(245,245,240,.6)" }}, {{ color: "{WH}", duration: 0.3 }}, 1.85);
    tl.fromTo("#b-lc", {{ opacity: 0, filter: "blur(8px)" }}, {{ opacity: 1, filter: "blur(0px)", duration: 0.2, ease: "power4.out" }}, 1.4);
    
    // gamble
    tl.to("#b-yr, #b-lc, #b-lad", {{ opacity: 0, filter: "blur(10px)", duration: 0.18, ease: "power2.in" }}, 3.3);
    tl.fromTo("#b-g1", {{ opacity: 0, color: "#3a3a3a" }}, {{ opacity: 1, color: "{WH}", duration: 0.25 }}, 5.2);
    tl.fromTo("#b-g2", {{ opacity: 0, color: "#3a3a3a" }}, {{ opacity: 1, color: "{WH}", duration: 0.25 }}, 5.55);
    tl.fromTo("#b-gam", {{ x: 0 }}, {{ x: 0 }}, 0);
    // other plans: gamble wipes up, plans rise from below
    tl.to("#b-gam", {{ y: -1300, filter: "blur(16px)", duration: 0.28, ease: "power3.in" }}, 6.2);
    tl.fromTo("#b-pl", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.01 }}, 6.45); tl.fromTo("#b-pl", {{ y: 1300, filter: "blur(16px)" }}, {{ y: 0, filter: "blur(0px)", duration: 0.5, ease: "expo.out" }}, 6.45); tl.set("#b-gam", {{ opacity: 0 }}, 6.49);
""")

# ---------------------------------------------------------------- S4 RECORD
s4 = scene("record", f"""
    #r-board{{left:120px;top:330px;width:840px;height:620px;background:#111;border:4px solid #262626}}
    #r-lab{{left:40px;top:30px;font-weight:800;font-size:32px;letter-spacing:.14em;color:rgba(245,245,240,.7)}}
    #r-cv{{left:40px;top:90px}}
    #r-cap{{left:40px;top:480px;width:760px;font-weight:900;font-size:44px;line-height:1.1;text-transform:uppercase}}
    #r-strip{{left:120px;top:990px;width:840px;display:flex;gap:10px}}
    #r-strip i{{flex:1;height:60px;border:3px solid #333;display:block;position:relative}}
    #r-strip i b{{position:absolute;inset:14px;border-radius:50%;background:{WH};display:block}}
    #r-cmp{{left:120px;top:330px;width:840px}}
    #r-cmp .lb{{font-weight:800;font-size:36px;letter-spacing:.08em;text-transform:uppercase;margin-top:34px}}
    #r-cmp .bar{{height:120px;display:flex;align-items:center;justify-content:flex-end;padding-right:24px;font-family:'League Gothic';font-size:110px;margin-top:10px;transform-origin:0 50%}}
    #r-rb{{left:300px;top:850px;font-family:'League Gothic';font-size:120px;line-height:1;color:{R};border:7px solid {R};padding:6px 26px 0;text-transform:uppercase}}
    #r-w1,#r-w2,#r-w3{{left:122px;top:520px;font-size:280px}}
""", f"""
    <div class="grain"></div>
    <div id="r-sb" class="a" style="inset:0">
      <div id="r-board" class="a">
        <div id="r-lab" class="a">PREMIER LEAGUE · 2015</div>
        <canvas id="r-cv" class="a" width="760" height="380"></canvas>
        <div id="r-cap" class="a">Consecutive Premier League matches <span class="y">scored in</span></div>
      </div>
      <div id="r-strip" class="a">{"".join(f'<i id="r-m{k}"><b></b></i>' for k in range(11))}</div>
    </div>
    <div id="r-cmp" class="a">
      <div class="lb">Previous record · Van Nistelrooy</div>
      <div class="bar" id="r-b1" style="width:{int(840*10/11)}px;background:#3a3a3a">10</div>
      <div class="lb y">Jamie Vardy · 2015</div>
      <div class="bar" id="r-b2" style="width:840px;background:{Y};color:{BK}">11</div>
    </div>
    <div id="r-rb" class="a">Record broken</div>
    <div id="r-w1" class="a lg">The whole</div>
    <div id="r-w2" class="a lg y">World</div>
    <div id="r-w3" class="a lg">Was<br>watching.</div>
""", f"""
    // dot-matrix digits
    const F = {{ "0":["01110","10001","10011","10101","11001","10001","01110"], "1":["00100","01100","00100","00100","00100","00100","01110"],
      "2":["01110","10001","00001","00010","00100","01000","11111"], "3":["11110","00001","00001","01110","00001","00001","11110"],
      "4":["00010","00110","01010","10010","11111","00010","00010"], "5":["11111","10000","11110","00001","00001","10001","01110"],
      "6":["00110","01000","10000","11110","10001","10001","01110"], "7":["11111","00001","00010","00100","01000","01000","01000"],
      "8":["01110","10001","10001","01110","10001","10001","01110"], "9":["01110","10001","10001","01111","00001","00010","01100"] }};
    const cv = document.getElementById("r-cv"), cx = cv.getContext("2d");
    const P = 50, RAD = 20;
    const drawN = (n) => {{
      cx.clearRect(0, 0, 760, 380);
      const s = String(n).padStart(2, " ");
      for (let d = 0; d < 2; d++) for (let r = 0; r < 7; r++) for (let c = 0; c < 5; c++) {{
        const on = s[d] !== " " && F[s[d]][r][c] === "1";
        cx.fillStyle = on ? "{Y}" : "#222";
        cx.beginPath(); cx.arc(40 + d * 340 + c * P + P / 2, 14 + r * P + P / 2 - 10, on ? RAD : RAD * 0.7, 0, 6.2832); cx.fill();
      }}
    }};
    const g = {{ v: 0 }};
    tl.fromTo(g, {{ v: 0 }}, {{ v: 11, duration: 1.3, ease: "power1.in", onUpdate: () => drawN(Math.max(0, Math.floor(g.v + 1e-6))) }}, 0.95);
    for (let k = 0; k < 11; k++) {{
      const t = 0.95 + 1.3 * Math.sqrt((k + 1) / 11) - 0.01;
      tl.fromTo(`#r-m${{k}} b`, {{ scale: 0 }}, {{ scale: 1, duration: 0.12, ease: "back.out(3)" }}, t);
      tl.fromTo(`#r-m${{k}}`, {{ borderColor: "#333" }}, {{ borderColor: "{Y}", duration: 0.1 }}, t);
    }}
    tl.fromTo("#r-sb", {{ opacity: 0, scale: 1.06, transformOrigin: "50% 30%" }}, {{ opacity: 1, scale: 1, duration: 0.35, ease: "expo.out" }}, 0);
    tl.fromTo("#r-cap", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.2 }}, 2.4);
    // compare bars
    tl.to("#r-sb", {{ y: -1400, filter: "blur(16px)", duration: 0.3, ease: "power3.in" }}, 5.55); tl.set("#r-sb", {{ opacity: 0 }}, 5.86);
    tl.fromTo("#r-cmp .lb", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.15, stagger: 0.5 }}, 5.85);
    tl.fromTo("#r-b1", {{ scaleX: 0 }}, {{ scaleX: 1, duration: 0.6, ease: "expo.out" }}, 5.95);
    tl.fromTo("#r-b2", {{ scaleX: 0 }}, {{ scaleX: 1, duration: 0.7, ease: "expo.out" }}, 6.45);
    tl.fromTo("#r-rb", {{ opacity: 0, scale: 1.6, rotation: -5 }}, {{ opacity: 1, scale: 1, rotation: -5, duration: 0.16, ease: "power4.out" }}, 7.55);
    tl.fromTo("#r-rb", {{ x: 0 }}, {{ x: 8, duration: 0.033, yoyo: true, repeat: 3, ease: "none" }}, 7.71);
    // whole world was watching: hard cuts
    tl.set("#r-cmp, #r-rb", {{ opacity: 0 }}, 8.35);
    tl.fromTo("#r-w1", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.01 }}, 8.35);
    tl.set("#r-w1", {{ opacity: 0 }}, 9.05);
    tl.fromTo("#r-w2", {{ opacity: 0, scale: 1.25, transformOrigin: "0 50%" }}, {{ opacity: 1, scale: 1, duration: 0.2, ease: "expo.out" }}, 9.05);
    tl.set("#r-w2", {{ opacity: 0 }}, 9.65);
    tl.fromTo("#r-w3", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.01 }}, 9.65);
""")

# ---------------------------------------------------------------- S5 MIRACLE
CELLS = 9
s5 = scene("miracle", f"""
    #m-k{{left:120px;top:330px}}
    #m-sea{{left:122px;top:390px;font-size:320px}}
    #m-panel{{left:84px;top:430px;width:912px;height:560px;background:{Y};padding:34px 30px}}
    #m-pk{{width:fit-content;font-weight:900;font-size:36px;letter-spacing:.1em;color:{BK};text-transform:uppercase}}
    #m-pn{{width:fit-content;font-family:'League Gothic';font-size:96px;line-height:1;color:{BK};text-transform:uppercase;margin-top:6px}}
    #m-cells{{display:flex;gap:8px;margin-top:40px}}
    #root .fc{{width:88px;height:150px;background:{BK};position:relative;overflow:hidden}}
    #root .fc i{{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;font-family:'League Gothic';font-style:normal;font-size:132px;color:{WH};line-height:1}}
    #root .fc:after{{content:"";position:absolute;left:0;right:0;top:74px;height:3px;background:{Y}}}
    #m-imp{{left:120px;top:1006px;font-size:96px}}
    #m-flood{{left:0;top:0;width:1080px;height:1920px;background:{Y};clip-path:inset(430px 84px 930px 84px)}}
    #m-ch{{left:96px;top:620px;font-size:250px;color:{BK}}}
    #m-chk{{left:120px;top:560px;font-weight:900;font-size:44px;letter-spacing:.12em;color:{BK};text-transform:uppercase}}
    #m-chs{{left:120px;top:880px;font-weight:900;font-size:44px;letter-spacing:.06em;color:{BK};text-transform:uppercase}}
    #m-conf{{left:0;top:0;width:1080px;height:1920px}}
    #m-conf b{{position:absolute;left:0;top:0;width:18px;height:30px;display:block}}
""", f"""
    <div class="grain"></div>
    <div id="m-s" class="a" style="inset:0">
      <div id="m-k" class="a kick y">Then came the</div>
      <div id="m-sea" class="a lg">2015–16</div>
    </div>
    <div id="m-panel" class="a">
      <div id="m-pk">Odds to win the league · Aug 2015</div>
      <div id="m-pn">Leicester City</div>
      <div id="m-cells">{"".join(f'<div class="fc" id="m-c{k}"><i></i></div>' for k in range(CELLS))}</div>
    </div>
    <div id="m-imp" class="a lg">The impossible <span class="y">dream.</span></div>
    <div id="m-flood" class="a"></div>
    <div id="m-chk" class="a">Premier League</div>
    <div id="m-ch" class="a lg">Champions</div>
    <div id="m-chs" class="a">Season 2015–16</div>
    <div id="m-conf" class="a"></div>
""", f"""
    const DRUM = " 0123456789-ACHIMNOPS";
    const A = "  5000-1 ", B = "CHAMPIONS";
    const cells = Array.from(document.querySelectorAll("#m-cells .fc i"));
    const steps = (a, b) => {{ const i = DRUM.indexOf(a), j = DRUM.indexOf(b); return (j - i + DRUM.length) % DRUM.length; }};
    const flap = (from, to, t0, dur, stagger) => {{
      cells.forEach((el, k) => {{
        const a = from[k], n = steps(a, to[k]), st = {{ v: 0 }};
        const ch = (v) => DRUM[(DRUM.indexOf(a) + Math.floor(v)) % DRUM.length];
        tl.fromTo(st, {{ v: 0 }}, {{ v: n, duration: Math.max(0.05, dur * n / DRUM.length + 0.25), ease: "power1.inOut",
          onUpdate: () => {{ el.textContent = ch(st.v); const f = st.v % 1; el.style.transform = n ? `scaleY(${{1 - 0.45 * Math.sin(f * Math.PI)}})` : ""; }} }}, t0 + k * stagger);
      }});
    }};
    cells.forEach(el => el.textContent = " ");
    tl.fromTo("#m-sea", {{ opacity: 0, scale: 1.15, transformOrigin: "0 50%", filter: "blur(10px)" }}, {{ opacity: 1, scale: 1, filter: "blur(0px)", duration: 0.35, ease: "expo.out" }}, 0.75);
    tl.fromTo("#m-k", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.1 }}, 0.05);
    tl.to("#m-s", {{ x: -1150, filter: "blur(16px)", duration: 0.26, ease: "power3.in" }}, 2.5); tl.set("#m-s", {{ opacity: 0 }}, 2.77);
    tl.fromTo("#m-panel", {{ x: 1150, filter: "blur(16px)" }}, {{ x: 0, filter: "blur(0px)", duration: 0.45, ease: "expo.out" }}, 2.7);
    flap(" ".repeat({CELLS}), A, 3.0, 1.4, 0.05);
    tl.fromTo("#m-imp", {{ opacity: 0, filter: "blur(8px)" }}, {{ opacity: 1, filter: "blur(0px)", duration: 0.2, ease: "power4.out" }}, 5.7);
    flap(A, B, 6.85, 1.1, 0.03);
    
    // payoff: the yellow panel floods the frame
    tl.fromTo("#m-flood", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.01 }}, 7.5);
    tl.fromTo("#m-flood", {{ clipPath: "inset(430px 84px 930px 84px)" }}, {{ clipPath: "inset(0px 0px 0px 0px)", duration: 0.45, ease: "power3.inOut" }}, 7.51);
    tl.set("#m-panel", {{ opacity: 0 }}, 7.75);
    tl.fromTo("#m-ch", {{ opacity: 0, scale: 1.35, transformOrigin: "0 50%", filter: "blur(12px)" }}, {{ opacity: 1, scale: 1, filter: "blur(0px)", duration: 0.35, ease: "expo.out" }}, 7.8);
    tl.fromTo("#m-chk, #m-chs", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.2, stagger: 0.06 }}, 7.82);
    // seeded confetti
    let s = 2016; const rnd = () => (s = (s * 16807) % 2147483647) / 2147483647;
    const box = document.getElementById("m-conf"), parts = [];
    const COLS = ["{BK}", "{WH}", "{BK}", "{R}"];
    for (let i = 0; i < 90; i++) {{
      const b = document.createElement("b"); b.style.background = COLS[i % 4]; box.appendChild(b);
      parts.push({{ el: b, x: 540 + (rnd() - 0.5) * 300, y: 700, vx: (rnd() - 0.5) * 1500, vy: -900 - rnd() * 1100, r: rnd() * 360, vr: (rnd() - 0.5) * 900, d: rnd() * 0.25 }});
    }}
    const cf = {{ t: 0 }};
    const drawC = () => parts.forEach(p => {{
      const t = Math.max(0, cf.t - p.d), x = p.x + p.vx * t * Math.exp(-0.6 * t), y = p.y + p.vy * t + 900 * t * t;
      p.el.style.transform = `translate(${{x}}px, ${{y}}px) rotate(${{p.r + p.vr * t}}deg) scaleX(${{Math.cos(t * 9 + p.r)}})`;
      p.el.style.opacity = cf.t > p.d ? 1 : 0;
    }});
    tl.fromTo(cf, {{ t: 0 }}, {{ t: 1.55, duration: 1.55, ease: "none", onUpdate: drawC }}, 7.7);
""")

# ---------------------------------------------------------------- S6 LEGACY
T6 = 560
s6 = scene("legacy", LADDER_CSS + f"""
    #l-bg{{inset:0;background:{Y}}}
    #l-trail{{left:{540-5}px;width:10px;background:{Y};z-index:1}}
    #root .yr{{position:absolute;font-weight:900;font-size:34px;letter-spacing:.08em;color:{Y}}}
    #l-txt{{left:122px;top:330px}}
    #l-txt div{{font-size:220px}}
""", f"""
    <div class="grain"></div>
    <div id="l-lad" class="a" style="inset:0">
    {ladder("l", top=T6)}
    <div id="l-trail" class="a" style="top:{tier_y(4,T6)+22}px;height:0"></div>
    <div class="yr" id="l-y1" style="left:{540+460//2+18}px;top:{T6+1*104+26}px">2012</div>
    <div class="yr" id="l-y2" style="left:{540+360//2+18}px;top:{T6+26}px">2016</div>
    </div>
    <div id="l-bg" class="a"></div>
    <div id="l-txt" class="a">
      <div class="lg" id="l-w1">It's never</div>
      <div class="lg" id="l-w2">too late</div>
      <div class="lg" id="l-w3">to make</div>
      <div class="lg y" id="l-w4">history.</div>
    </div>
""", f"""
    tl.fromTo("#l-bg", {{ opacity: 1 }}, {{ opacity: 0, duration: 0.6, ease: "power2.inOut" }}, 0.0);
    tl.fromTo("#l-lad .tier", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.3, stagger: 0.05 }}, 0.3);
    tl.fromTo("#l-dot", {{ y: 0 }}, {{ y: {tier_y(0,T6) - tier_y(4,T6)}, duration: 2.9, ease: "power2.inOut" }}, 0.45);
    tl.fromTo("#l-trail", {{ height: 0, y: 0 }}, {{ height: {tier_y(4,T6) - tier_y(0,T6)}, y: {tier_y(0,T6) - tier_y(4,T6)}, duration: 2.9, ease: "power2.inOut" }}, 0.45);
        tl.fromTo("#l-y1", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.2 }}, 1.9);
    tl.fromTo("#l-y2", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.2 }}, 3.3);
    tl.fromTo("#l-t0", {{ backgroundColor: "rgba(255,230,0,0)" }}, {{ backgroundColor: "{Y}", duration: 0.3 }}, 3.3);
    tl.fromTo("#l-t0 span", {{ color: "rgba(245,245,240,.6)" }}, {{ color: "{BK}", duration: 0.3 }}, 3.3);
    // the line, slowly
    tl.to("#l-lad", {{ opacity: 0, duration: 0.6, ease: "power2.inOut" }}, 3.7);
    ["#l-w1", "#l-w2", "#l-w3", "#l-w4"].forEach((id, k) => {{
      const t = [5.95, 6.45, 6.95, 7.45][k];
      tl.fromTo(id, {{ opacity: 0, color: "#2a2a2a" }}, {{ opacity: 1, color: k === 3 ? "{Y}" : "{WH}", duration: 0.45, ease: "power2.out" }}, t);
    }});
""")

# ---------------------------------------------------------------- S7 BRAND
s7 = scene("brand", f"""
    #o-line{{left:0;top:590px;width:6px;height:250px;background:{Y}}}
    #o-word{{left:0;top:620px;width:1080px;text-align:center;font-size:250px}}
    #o-word span{{display:inline-block}}
    #o-st{{left:0;top:850px;width:1080px;text-align:center;font-weight:900;font-size:62px;letter-spacing:.42em;padding-left:.42em}}
    #o-tag{{left:0;top:990px;width:1080px;text-align:center;font-weight:800;font-size:44px;letter-spacing:.12em;color:{Y}}}
    #o-fol{{left:0;top:1070px;width:1080px;text-align:center;font-weight:700;font-size:32px;letter-spacing:.12em;color:rgba(245,245,240,.75)}}
""", f"""
    <div class="grain"></div>
    <div id="o-line" class="a"></div>
    <div id="o-word" class="a lg"><span>O</span><span>F</span><span>F</span><span>S</span><span>I</span><span>D</span><span id="o-e">E</span></div>
    <div id="o-st" class="a">STORIES</div>
    <div id="o-tag" class="a">BEYOND THE 90 MINUTES.</div>
    <div id="o-fol" class="a">FOLLOW FOR MORE FOOTBALL STORIES</div>
""", f"""
    // the offside line sits just behind the E; the E steps past it
    const e = document.getElementById("o-e").getBoundingClientRect(), root = document.querySelector('[data-composition-id="brand"]').getBoundingClientRect();
    const lx = e.left - root.left - 8;
    gsap.set("#o-line", {{ x: lx }});
    tl.fromTo("#o-line", {{ scaleY: 0, transformOrigin: "50% 0" }}, {{ scaleY: 1, duration: 0.4, ease: "expo.out" }}, 0.0);
    tl.fromTo("#o-word span", {{ opacity: 0, filter: "blur(8px)" }}, {{ opacity: 1, filter: "blur(0px)", duration: 0.18, stagger: 0.05, ease: "power4.out" }}, 0.15);
    tl.fromTo("#o-e", {{ x: -30 }}, {{ x: 22, duration: 0.28, ease: "back.out(2.2)" }}, 0.62);
    tl.fromTo("#o-st", {{ opacity: 0, scaleX: 1.35 }}, {{ opacity: 1, scaleX: 1, duration: 0.5, ease: "expo.out" }}, 0.75);
    tl.fromTo("#o-tag", {{ opacity: 0, filter: "blur(6px)" }}, {{ opacity: 1, filter: "blur(0px)", duration: 0.2, ease: "power4.out" }}, 2.2);
    tl.fromTo("#o-fol", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.25 }}, 2.3);
""")

# ---------------------------------------------------------------- CAPTIONS
HL = {"non-league", "champion", "vardy", "vardy.", "factory,", "dream", "2012,", "leicester", "gamble.", "plans.", "11", "record.", "watching.", "5000", "champions!", "history.", "offside", "stories.", "90", "released", "16."}
def weight(w):
    w = w.strip(".,!?…")
    if re.match(r"^\d{4}–\d{2}$", w): return 20
    if w == "5000": return 14
    if re.match(r"^\d{4}$", w): return 12
    if w.isdigit(): return 6
    return len(re.sub(r"[^\w]", "", w)) + 2
groups = []
for p in S:
    words = p["show"].split()
    ws = [weight(w) for w in words]; tot = sum(ws); t = p["start"]
    timed = []
    for w, k in zip(words, ws):
        d = p["dur"] * k / tot; timed.append((w, t, t + d)); t += d
    cur = []
    for i, x in enumerate(timed):
        cur.append(x)
        if len(cur) == 3 or re.search(r"[.,!?…]$", x[0]) or i == len(timed) - 1:
            groups.append(cur); cur = []
cap_html, cap_js = [], []
for gi, g in enumerate(groups):
    spans = "".join(f'<span id="c{gi}w{k}" class="cw{" hl" if w.lower().strip(".,!?") in {h.strip(".,!?") for h in HL} else ""}">{html.escape(w)}</span> ' for k, (w, a, b) in enumerate(g))
    cap_html.append(f'<div class="cg" id="c{gi}"><span class="bx">{spans.strip()}</span></div>')
    a, b = g[0][1], g[-1][2]
    nxt = groups[gi + 1][0][1] if gi + 1 < len(groups) else 60
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

# ---------------------------------------------------------------- ROOT
beats = {}
for p in S: beats.setdefault(p["beat"], p["start"])
SC = [("hook", 0, 8.4), ("struggle", 8.4, 10.9), ("break", 19.3, 8.2), ("record", 27.5, 10.5), ("miracle", 38.0, 9.0), ("legacy", 47.0, 8.5), ("brand", 55.5, 4.5)]
for name, src in [("hook", s1), ("struggle", s2), ("break", s3), ("record", s4), ("miracle", s5), ("legacy", s6), ("brand", s7), ("captions", caps)]:
    open(f"compositions/{name}.html", "w").write(src)
hosts = "\n".join(f'      <div id="{n}" data-composition-id="{n}" data-composition-src="compositions/{n}.html" data-start="{a}" data-duration="{d}" data-track-index="0" data-track-kind="graphics" data-width="{W}" data-height="{H}" style="z-index:1"></div>' for n, a, d in SC)
DUR = {"impact-bass-1": 2.1, "impact-bass-2": 2.5, "whoosh": 0.57, "whoosh-cinematic": 1.0, "riser": 4.0, "pop": 0.7, "key-press": 0.43, "click-soft": 0.36, "typing": 1.5, "sparkle": 1.5}
SFX = [("x-open", "impact-bass-2", 0.0, 0.35), ("x-whip1", "whoosh", 2.3, 0.7), ("x-flash", "impact-bass-1", 5.37, 0.35),
       ("x-cut2", "whoosh-cinematic", 8.25, 0.5), ("x-rel", "impact-bass-1", 12.6, 0.22), ("x-card", "whoosh", 13.6, 0.5),
       ("x-punch", "key-press", 15.1, 2.5), ("x-l1", "click-soft", 16.08, 1.2), ("x-l2", "key-press", 17.1, 2.5), ("x-l3", "pop", 18.04, 1.2),
       ("x-2012", "impact-bass-2", 19.4, 0.25), ("x-jump", "whoosh", 20.55, 0.5), ("x-plans", "whoosh", 25.6, 0.6),
       ("x-eleven", "impact-bass-1", 29.67, 0.3), ("x-rb", "impact-bass-2", 35.05, 0.3), ("x-world", "whoosh-cinematic", 35.75, 0.45),
       ("x-whip5", "whoosh", 40.45, 0.6), ("x-flaps", "typing", 40.95, 0.35), ("x-rise", "riser", 42.05, 0.5),
       ("x-champ", "impact-bass-1", 45.47, 0.4), ("x-conf", "sparkle", 45.75, 0.45), ("x-logo", "impact-bass-1", 56.1, 0.4)]
ends, lanes = [], []
for sid, f, a, v in SFX:
    e = a + DUR[f]
    for li, le in enumerate(ends):
        if le <= a: ends[li] = e; break
    else: ends.append(e); li = len(ends) - 1
    lanes.append(f'      <audio id="{sid}" class="clip" src="assets/sfx/{f}.mp3" data-start="{a}" data-duration="{DUR[f]}" data-track-index="{20+li}" data-volume="{v}"{" data-fade-out=\"0.5\"" if f=="riser" else ""}></audio>')
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
    <div id="root" data-composition-id="main" data-start="0" data-duration="60" data-width="{W}" data-height="{H}">
{hosts}
      <div id="captions" data-composition-id="captions" data-composition-src="compositions/captions.html" data-start="0" data-duration="60" data-track-index="1" data-track-kind="captions" data-width="{W}" data-height="{H}" style="z-index:5"></div>
      <audio id="vo" class="clip" src="assets/audio/vo.wav" data-start="0" data-duration="60" data-track-index="10" data-volume="1"></audio>
{chr(10).join(lanes)}
    </div>
    <script>
      window.__timelines["main"] = gsap.timeline({{ paused: true }});
    </script>
  </body>
</html>
"""
open("index.html", "w").write(idx)
print("groups", len(groups))
