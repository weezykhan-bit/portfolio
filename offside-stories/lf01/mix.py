"""LF01 sound design: an original procedural underscore (no samples, no licensing) + extra SFX,
mixed under the existing VO and muxed onto the rendered picture (no re-render needed)."""
import json, re, subprocess, html
import numpy as np, soundfile as sf
from scipy.signal import butter, sosfilt

src = open("build.py").read().split("# =================================================================== COLD OPEN")[0]
exec(src)  # B, order, IDX, P, WD, LW, LP, I, TOTAL ...
SR = 48000
N = int((TOTAL + 1) * SR)
rng = np.random.default_rng(28)

def lp(x, f, o=4): return sosfilt(butter(o, f, "low", fs=SR, output="sos"), x)
def hp(x, f, o=2): return sosfilt(butter(o, f, "high", fs=SR, output="sos"), x)
def bp(x, a, b, o=2): return sosfilt(butter(o, [a, b], "band", fs=SR, output="sos"), x)
def t_(d): return np.arange(int(d * SR)) / SR
def add(buf, x, t, g=1.0):
    s = int(t * SR)
    if s < 0: x = x[-s:]; s = 0
    e = min(len(buf), s + len(x)); buf[s:e] += g * x[: e - s]
def load(f):
    out = subprocess.run(["ffmpeg", "-v", "error", "-i", f, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True).stdout
    return np.frombuffer(out, np.float32).astype(np.float64)
def norm(x, peak=1.0): return x / (np.abs(x).max() + 1e-9) * peak

# ------------------------------------------------------------------ synth voices
NOTE = {n: 440 * 2 ** ((i - 9) / 12) for i, n in enumerate(["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"])}
def hz(n):  # "A2"
    m = re.match(r"([A-G]#?)(\d)", n); return NOTE[m.group(1)] * 2 ** (int(m.group(2)) - 4)
CH = {"Am": ["A2", "E3", "A3", "C4", "E4"], "F": ["F2", "C3", "F3", "A3", "C4"], "C": ["C3", "G3", "C4", "E4", "G4"],
      "G": ["G2", "D3", "G3", "B3", "D4"], "E": ["E2", "B2", "E3", "G#3", "B3"], "Dm": ["D3", "A3", "D4", "F4"]}
def pad(chord, d, bright=1600, harm=9):
    tt = t_(d); out = np.zeros(len(tt))
    for n in CH[chord]:
        f0 = hz(n)
        for det in (-0.004, 0.0, 0.0045):
            f = f0 * (1 + det); ph = rng.uniform(0, 2 * np.pi)
            for h in range(1, harm + 1):
                if f * h > 9000: break
                out += np.sin(2 * np.pi * f * h * tt + ph * h) / h ** 1.7
    out = lp(out, bright)
    a = int(min(0.6, d / 3) * SR); env = np.ones(len(tt)); env[:a] = np.linspace(0, 1, a); env[-a:] = np.linspace(1, 0, a)
    return out * env
def sub(chord, d):
    tt = t_(d); f = hz(CH[chord][0]) / 2
    x = np.sin(2 * np.pi * f * tt); a = int(0.3 * SR); x[:a] *= np.linspace(0, 1, a); x[-a:] *= np.linspace(1, 0, a); return x
def kick(g=1.0, f0=95, f1=42, d=0.45):
    tt = t_(d); f = f1 + (f0 - f1) * np.exp(-tt * 28); ph = 2 * np.pi * np.cumsum(f) / SR
    return g * np.sin(ph) * np.exp(-tt * 7)
def hat(g=0.25):
    x = hp(rng.normal(0, 1, int(0.06 * SR)), 6000) * np.exp(-t_(0.06) * 70); return g * x
def boom(g=1.0):  # deep cinematic hit
    tt = t_(3.0); f = 30 + 60 * np.exp(-tt * 9); ph = 2 * np.pi * np.cumsum(f) / SR
    body = np.sin(ph) * np.exp(-tt * 1.6)
    noise = lp(rng.normal(0, 1, len(tt)), 400) * np.exp(-tt * 6) * 0.25
    return g * norm(body + noise)
def tick(g=0.5):
    tt = t_(0.03); return g * (np.sin(2 * np.pi * 3200 * tt) * np.exp(-tt * 260) + 0.4 * hp(rng.normal(0, 1, len(tt)), 3000) * np.exp(-tt * 400))
def whistle(blasts):  # pea-whistle: two partials + 30 Hz trill + breath
    out = []
    for d in blasts:
        tt = t_(d); trill = 0.6 + 0.4 * np.sin(2 * np.pi * 28 * tt) ** 2
        tone = (np.sin(2 * np.pi * 2950 * tt + 0.6 * np.sin(2 * np.pi * 28 * tt)) + 0.35 * np.sin(2 * np.pi * 3420 * tt)) * trill
        tone += 0.15 * bp(rng.normal(0, 1, len(tt)), 2500, 4500)
        env = np.ones(len(tt)); a = int(0.02 * SR); env[:a] = np.linspace(0, 1, a); env[-int(0.06 * SR):] = np.linspace(1, 0, int(0.06 * SR))
        out += [tone * env, np.zeros(int(0.16 * SR))]
    return norm(np.concatenate(out), 0.9)
def crowd(d, g=1.0):  # swell of filtered noise with slow chaotic modulation
    tt = t_(d); n = rng.normal(0, 1, len(tt))
    body = bp(n, 250, 2600) + 0.5 * bp(rng.normal(0, 1, len(tt)), 900, 3800)
    mod = lp(rng.normal(0, 1, len(tt)), 6) ; mod = 0.75 + 0.25 * mod / (np.abs(mod).max() + 1e-9)
    env = np.minimum(1, tt / 0.35) * np.exp(-np.maximum(0, tt - 0.6) * (3.0 / d))
    return g * norm(body * mod * env)
def heart(g=0.6):
    x = np.zeros(int(0.7 * SR)); add(x, kick(1, 70, 38, 0.25), 0); add(x, kick(0.7, 65, 36, 0.25), 0.22); return g * x

# ------------------------------------------------------------------ underscore by section
MOOD = {}
for b in order:
    if b in ("co_tv", "co_odds", "c5_wait", "c6_arsenal", "c7_chase", "c8_match"): MOOD[b] = "tense"
    elif b in ("c8_champs",) or b.startswith("c9"): MOOD[b] = "triumph"
    elif b in ("c10_vichai",): MOOD[b] = "somber"
    elif b in ("c10_after", "close", "close_q"): MOOD[b] = "reflect"
    elif b in ("brand",): MOOD[b] = "none"
    elif b == "co_title": MOOD[b] = "title"
    elif re.match(r"^c\d+$", b): MOOD[b] = "card"
    else: MOOD[b] = "story"
PROG = {"tense": ["Am", "Am", "F", "E"], "story": ["Am", "F", "C", "G"], "triumph": ["C", "G", "Am", "F"], "reflect": ["Am", "F", "C", "G"],
        "somber": ["Am", "F"], "title": ["Am", "F"], "card": ["Am"]}
BRIGHT = {"tense": 1100, "story": 1700, "triumph": 3400, "reflect": 1300, "somber": 700, "title": 2200, "card": 1500}
LVL = {"tense": 0.8, "story": 0.75, "triumph": 1.0, "reflect": 0.7, "somber": 0.35, "title": 0.95, "card": 0.8}
BPM = 72; beat = 60 / BPM; bar = 4 * beat
music = np.zeros(N); drums = np.zeros(N)
for b in order:
    m = MOOD[b]
    if m == "none": continue
    a, d = B[b]; a0 = max(0, a - 0.6); d0 = d + 1.2
    prog = PROG[m]; seg = 2 * bar if m != "tense" else bar
    k = 0; t = 0.0; x = np.zeros(int(d0 * SR) + SR)
    while t < d0:
        dd = min(seg + 0.6, d0 - t + 0.6); ch = prog[k % len(prog)]
        add(x, pad(ch, dd, BRIGHT[m]) * 0.5 + 0.35 * sub(ch, dd), t); t += seg; k += 1
    env = np.ones(len(x)); f = int(0.8 * SR); env[:f] = np.linspace(0, 1, f); env[-f:] = np.linspace(1, 0, f)
    add(music, norm(x) * env * LVL[m], a0)
    # rhythm
    if m in ("tense", "story", "triumph", "reflect"):
        nb = int(d / beat)
        for j in range(nb):
            tb = a + j * beat
            if m == "tense": add(drums, kick(0.55), tb); add(drums, hat(0.12), tb + beat / 2)
            elif m == "story" and j % 2 == 0: add(drums, kick(0.35), tb)
            elif m == "triumph": add(drums, kick(0.7), tb); (j % 4 == 2) and add(drums, hat(0.2), tb)
            elif m == "reflect" and j % 4 == 0: add(drums, kick(0.25), tb)
# silence before the champions hit, swell after it
gap = B["c8_champs"][0]
z0, z1 = int((gap - 0.9) * SR), int((gap + 0.05) * SR)
music[z0:z1] *= np.linspace(1, 0, z1 - z0) ** 2; drums[z0:z1] = 0
music = norm(music); drums = norm(drums) * 0.8

# ------------------------------------------------------------------ SFX
fx = np.zeros(N)
# keep the original clips from index.html
for mt in re.finditer(r'<audio id="x-[^"]+" class="clip" src="([^"]+)" data-start="([\d.]+)" data-duration="([\d.]+)" data-track-index="\d+" data-volume="([\d.]+)"', open("index.html").read()):
    f, s, d, v = mt.group(1), float(mt.group(2)), float(mt.group(3)), float(mt.group(4))
    add(fx, load(f)[: int(d * SR)], s, v * 1.4)
WHOOSH = load("assets/sfx/whoosh.mp3")
for b in order:
    if not re.match(r"^c\d+$", b) and B[b][0] > 1: add(fx, WHOOSH, B[b][0] - 0.12, 0.35)
def G(n, k, w): return WD(I(n, k), w)
# booms on the big numbers
for n, k, w in [("co_odds", 0, "5000"), ("co_title", 0, "unlikely"), ("c1_pearson", 0, "sacked"), ("c3_mahrez", 1, "400,000"), ("c3_kante", 1, "5.6"),
                ("c4_run", 5, "11th"), ("c5_xmas", 0, "top"), ("c6_city", 1, "won"), ("c8_champs", 0, "champions"), ("c9_table", 0, "ten"),
                ("c10_cup", 0, "2021"), ("close", 3, "5000"), ("close", 4, "happened")]:
    add(fx, boom(), G(n, k, w) - 0.02, 0.55)
for c in TITLES: add(fx, boom(), B[c][0] + 0.32, 0.35)
# ticks on counters
for k in range(7): add(fx, tick(), LW("c1_escape", 1, "seven") + k * 0.09 + B["c1_escape"][0], 0.5)
for k in range(10): add(fx, tick(), LW("c2_odds", 1, "40") + k * 0.08 + B["c2_odds"][0], 0.45)
lights = [LW("c4_run", 4, "One"), LW("c4_run", 4, "another"), LW("c4_run", 4, "Then", True) + 0.6] + [LW("c4_run", 5, "against") + k * 0.42 for k in range(7)] + [LW("c4_run", 5, "11th")]
for t in lights: add(fx, tick(0.8), t + B["c4_run"][0])
for k in range(9): add(fx, tick(0.6), LW("c8_match", 4, "nine") + k * 0.11 + B["c8_match"][0])
# whistles
add(fx, whistle([0.28, 0.28]), G("co_tv", 3, "half-time") - 0.05, 0.22)
add(fx, whistle([0.28, 0.28]), G("c8_match", 2, "half-time") - 0.05, 0.22)
add(fx, whistle([0.3, 0.3, 1.0]), P(I("c8_match", 6)) - 0.2, 0.25)
# crowd roars on the goals
for n, k, w, d, g in [("c4_run", 5, "11th", 2.5, 0.35), ("c6_arsenal", 2, "headed", 2.2, 0.3), ("c7_grind", 2, "Wes", 2.2, 0.3), ("c8_match", 3, "Cahill", 2.0, 0.28),
                      ("c8_match", 5, "equaliser", 3.0, 0.4), ("c9_everton", 2, "3–1", 2.5, 0.35)]:
    add(fx, crowd(d), G(n, k, w) - 0.1, g)
add(fx, crowd(6.0), B["c8_champs"][0] + 0.1, 0.55)
add(fx, crowd(4.0), G("c9_everton", 3, "lifted"), 0.4)
# heartbeat under the Stamford Bridge second half, speeding up
t = P(I("c8_match", 3)); end = G("c8_match", 5, "equaliser"); per = 1.0
while t < end - 0.3: add(fx, heart(0.5), t); t += per; per = max(0.62, per * 0.95)

# ------------------------------------------------------------------ mix
vo, vsr = sf.read("assets/audio/vo.wav"); vo = vo.mean(1) if vo.ndim > 1 else vo
assert vsr == SR; v = np.zeros(N); v[: min(N, len(vo))] = vo[:N]
envv = lp(np.abs(v), 4, 2); envv = envv / (np.percentile(envv[envv > 1e-4], 95) + 1e-9)
duck = 1 - 0.62 * np.clip(envv, 0, 1)        # music sits ~8 dB lower under speech
duck = lp(duck, 3, 1)
bed = (music * 0.34 + drums * 0.26) * duck
# hush the music for the Vichai tribute
a, d = B["c10_vichai"]; s0, s1 = int(a * SR), int((a + d) * SR); bed[s0:s1] *= 0.5
fxd = fx * (1 - 0.35 * np.clip(envv, 0, 1))
mix = v + bed + fxd * 0.75
# soft stereo: music slightly wider
L = mix + 0.02 * np.roll(bed, 240); Rr = mix + 0.02 * np.roll(bed, -240)
st = np.stack([L, Rr], 1)
st = st / max(1.0, np.abs(st).max() / 0.98)
sf.write("assets/audio/mix-raw.wav", st[: int(TOTAL * SR)], SR, subtype="FLOAT")
print("ok", TOTAL)
