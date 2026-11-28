"""Download CC BY / PD Commons photos and bake the Offside Stories print look:
greyscale, contrast curve, duotone (black #0A0A0A -> off-white #F5F5F0), grain, vignette.
Usage: python treat.py  (reads photos.json: key -> {title,url,...})"""
import json, os, time, urllib.request, io
from PIL import Image, ImageOps, ImageFilter, ImageChops
import numpy as np
UA = "OffsideStoriesDoc/1.0 (football documentary research; low volume)"
P = json.load(open("photos.json"))
os.makedirs("assets/photos/raw", exist_ok=True)
for key, m in P.items():
    raw = f"assets/photos/raw/{key}.jpg"; out = f"assets/photos/{key}.jpg"
    if not os.path.exists(raw):
        url = m.get("thumb", m["url"])
        # use a 2560px thumbnail where the original is bigger
        if False:
            parts = url.split("/commons/")[1]; fn = parts.split("/")[-1]
            url = f"https://upload.wikimedia.org/wikipedia/commons/thumb/{parts}/1920px-{fn}"
        data = None
        for a in range(5):
            try:
                data = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=60).read(); break
            except Exception as e:
                print("retry", key, e); time.sleep(300)
        if data is None: print("FAILED", key); continue
        open(raw, "wb").write(data); time.sleep(60)
    im = Image.open(raw); im = ImageOps.exif_transpose(im).convert("L")
    if "crop" in m:  # [l,t,r,b] fractions
        l, t, r, b = m["crop"]; W0, H0 = im.size; im = im.crop((int(l * W0), int(t * H0), int(r * W0), int(b * H0)))
    # fit to cover 2112x1188 (10% headroom for camera moves)
    TW, TH = 2112, 1188
    s = max(TW / im.width, TH / im.height); im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    fx, fy = m.get("focus", (0.5, 0.5))
    x0 = int(min(max(fx * im.width - TW / 2, 0), im.width - TW)); y0 = int(min(max(fy * im.height - TH / 2, 0), im.height - TH))
    im = im.crop((x0, y0, x0 + TW, y0 + TH))
    a = np.asarray(ImageOps.autocontrast(im, cutoff=1), dtype=np.float32) / 255
    a = 0.5 + (a - 0.5) * 1.25  # contrast
    a = np.clip(a, 0, 1) ** 1.1
    rng = np.random.default_rng(7); a = np.clip(a + rng.normal(0, 0.035, a.shape), 0, 1)
    yy, xx = np.mgrid[0:TH, 0:TW]; d = np.sqrt(((xx - TW / 2) / (TW / 2)) ** 2 + ((yy - TH / 2) / (TH / 2)) ** 2)
    a = a * np.clip(1.15 - 0.45 * d ** 2, 0.35, 1)
    lo = np.array([10, 10, 10], np.float32); hi = np.array([245, 245, 240], np.float32)
    rgb = lo + a[..., None] * (hi - lo)
    Image.fromarray(rgb.astype(np.uint8)).save(out, quality=88)
    print("ok", key, im.size)
