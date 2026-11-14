import os
YT = os.environ.get('YT_ROOT', os.path.expanduser('~/yt_engine/yt'))
import sys, json, math
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1920, 1080, 30
IMG = YT + '/assets/img/'
LORA = YT + '/fonts/Lora.ttf'
INTER_B = YT + '/fonts/Inter-Bold.otf'
INTER_M = YT + '/fonts/Inter-Medium.otf'
TM = json.load(open('timing.json'))
CUES = TM['cues']; TOTAL = TM['total']
INTRO = 12.0

def ss(a, b, t):
    if b <= a: return 1.0 if t >= b else 0.0
    x = min(1.0, max(0.0, (t - a) / (b - a))); return x * x * (3 - 2 * x)
def eio(x):
    x = min(1.0, max(0.0, x)); return x * x * (3 - 2 * x)
def lora(size, weight='Bold'):
    f = ImageFont.truetype(LORA, size)
    try: f.set_variation_by_name(weight)
    except Exception: pass
    return f

yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
dd = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
VIG = (1 - 0.36 * np.clip((dd - 0.6) / 0.9, 0, 1) ** 1.5)[..., None]
BOT = (1 - np.clip((yy - 860) / 220, 0, 1) * 0.45)[..., None]
_IMG = {}
def img(name):
    if name not in _IMG:
        im = cv2.imread(IMG + name + '.jpg')[:, :, ::-1]
        im = cv2.resize(im, (W, H), interpolation=cv2.INTER_LANCZOS4).astype(np.float32)
        _IMG[name] = np.clip(im * VIG * BOT, 0, 255).astype(np.uint8)
    return _IMG[name]

def kb(src, u, z0, z1, c0, c1):
    e = eio(u); s = z0 + (z1 - z0) * e
    cx = (c0[0] + (c1[0] - c0[0]) * e) * W; cy = (c0[1] + (c1[1] - c0[1]) * e) * H
    cx = min(max(cx, W / 2 / s), W - W / 2 / s); cy = min(max(cy, H / 2 / s), H - H / 2 / s)
    M = np.float32([[s, 0, W / 2 - cx * s], [0, s, H / 2 - cy * s]])
    return cv2.warpAffine(src, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)

def overlay(f, rgba, x, y, a=1.0):
    h, w = rgba.shape[:2]
    xa, ya = max(0, x), max(0, y); xb, yb = min(W, x + w), min(H, y + h)
    if xb <= xa or yb <= ya or a <= 0.01: return
    s = rgba[ya - y:yb - y, xa - x:xb - x]
    al = s[..., 3:4].astype(np.float32) / 255.0 * a
    reg = f[ya:yb, xa:xb].astype(np.float32)
    f[ya:yb, xa:xb] = (reg * (1 - al) + s[..., :3] * al).astype(np.uint8)

def text_rgba(text, font, fill, pad=30):
    d = ImageDraw.Draw(Image.new('RGBA', (10, 10)))
    bb = d.textbbox((0, 0), text, font=font)
    w, h = bb[2] - bb[0] + 2 * pad, bb[3] - bb[1] + 2 * pad
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    sh = Image.new('RGBA', (w, h), (0, 0, 0, 0)); ImageDraw.Draw(sh).text((pad - bb[0], pad - bb[1] + 3), text, font=font, fill=(0, 0, 0, 230))
    sh = sh.filter(ImageFilter.GaussianBlur(9)); im = Image.alpha_composite(im, sh); im = Image.alpha_composite(im, sh)
    ImageDraw.Draw(im).text((pad - bb[0], pad - bb[1]), text, font=font, fill=fill)
    return np.array(im)

def stack(parts, gap=-28, center=True):
    w = max(p.shape[1] for p in parts); hh = sum(p.shape[0] for p in parts) + gap * (len(parts) - 1)
    out = np.zeros((hh, w, 4), np.uint8); y = 0
    for p in parts:
        x = (w - p.shape[1]) // 2 if center else 0
        reg = out[y:y + p.shape[0], x:x + p.shape[1]]; al = p[..., 3:4] / 255.0
        reg[..., :3] = (reg[..., :3] * (1 - al) + p[..., :3] * al).astype(np.uint8)
        reg[..., 3] = np.maximum(reg[..., 3], p[..., 3]); y += p.shape[0] + gap
    return out

_T = {}
def title(txt, sub=None, big=False):
    k = (txt, sub, big)
    if k not in _T:
        parts = [text_rgba(txt, lora(110 if big else 64), (240, 205, 135, 255))]
        if sub: parts.append(text_rgba(sub, ImageFont.truetype(INTER_M, 40 if big else 34), (245, 240, 230, 255)))
        _T[k] = stack(parts)
    return _T[k]

_S = {}
def src_tag(txt):
    if txt not in _S:
        f = ImageFont.truetype(INTER_M, 26)
        d = ImageDraw.Draw(Image.new('RGBA', (10, 10))); bb = d.textbbox((0, 0), txt, font=f)
        tw, th = bb[2] - bb[0], bb[3] - bb[1]
        pw, ph = tw + 44, 50
        im = Image.new('RGBA', (pw, ph), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        d.rounded_rectangle((0, 0, pw - 1, ph - 1), ph // 2, fill=(14, 10, 24, 175), outline=(200, 165, 95, 200), width=2)
        d.text(((pw - tw) // 2 - bb[0], (ph - th) // 2 - bb[1]), txt, font=f, fill=(240, 220, 175, 255))
        _S[txt] = np.array(im)
    return _S[txt]

_SUB = {}
def sub_img(i):
    if i in _SUB: return _SUB[i]
    text = CUES[i][2]; size = 46
    while True:
        font = ImageFont.truetype(INTER_B, size)
        d = ImageDraw.Draw(Image.new('RGBA', (10, 10))); bb = d.textbbox((0, 0), text, font=font)
        tw = bb[2] - bb[0]
        if tw <= 1640 or size <= 34: break
        size -= 2
    th = bb[3] - bb[1]; pw, ph = tw + 64, 74
    im = Image.new('RGBA', (pw, ph), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, pw - 1, ph - 1), ph // 2, fill=(14, 10, 24, 200))
    d.text(((pw - tw) // 2 - bb[0], (ph - th) // 2 - bb[1] - 1), text, font=font, fill=(250, 248, 242, 255))
    _SUB[i] = np.array(im); return _SUB[i]

def draw_sub(f, t):
    for i, (a, b, _) in enumerate(CUES):
        if a <= t < b:
            al = min(ss(a, a + 0.08, t), 1 - ss(b - 0.08, b, t)); im = sub_img(i)
            overlay(f, im, (W - im.shape[1]) // 2, 1010 - im.shape[0] // 2, al); return

# ---------- effects ----------
RNG = np.random.default_rng(3)
DROPS = RNG.uniform(0, 1, (700, 3))
def rain(f, t):
    lay = np.zeros((H, W), np.float32)
    for x0, y0, s in DROPS:
        sp = 1500 + 900 * s
        y = (y0 * (H + 200) + t * sp) % (H + 200) - 100
        x = (x0 * (W + 300) - (t * sp * 0.18)) % (W + 300) - 150
        l = 18 + 26 * s
        cv2.line(lay, (int(x), int(y)), (int(x - l * 0.18), int(y - l)), 0.35 + 0.4 * s, 1, cv2.LINE_AA)
    lay = cv2.GaussianBlur(lay, (3, 3), 0)[..., None]
    return np.clip(f.astype(np.float32) + lay * np.float32([170, 185, 210]) * 0.55, 0, 255).astype(np.uint8)

def flicker(f, t, cx, cy, r):
    k = 0.5 + 0.25 * math.sin(t * 7.3) + 0.15 * math.sin(t * 13.1 + 1) + 0.1 * math.sin(t * 23.7)
    g = np.exp(-(((xx - cx) / r) ** 2 + ((yy - cy) / r) ** 2))[..., None]
    return np.clip(f.astype(np.float32) * (1 + g * 0.25 * k) + g * np.float32([60, 35, 10]) * k, 0, 255).astype(np.uint8)

DUST = RNG.uniform(0, 1, (160, 4))
def motes(f, t, col=(255, 225, 170), amt=0.5):
    lay = np.zeros((H // 2, W // 2), np.float32)
    for x0, y0, s, ph in DUST:
        x = (x0 * W / 2 + t * (12 + 25 * s)) % (W / 2); y = (y0 * H / 2 + math.sin(t * 0.5 + ph * 6) * 10) % (H / 2)
        cv2.circle(lay, (int(x), int(y)), 1 + int(2 * s), 0.4 + 0.6 * s, -1, cv2.LINE_AA)
    lay = cv2.resize(cv2.GaussianBlur(lay, (0, 0), 1.2), (W, H))[..., None]
    return np.clip(f.astype(np.float32) + lay * np.float32(col) * amt, 0, 255).astype(np.uint8)

# ---------- scenes ----------
def S(t0, t1, im, z0=1.0, z1=1.08, c0=(0.5, 0.5), c1=(0.5, 0.5), **kw):
    return dict(t0=t0, t1=t1, im=im, z0=z0, z1=z1, c0=c0, c1=c1, **kw)
SC = [
    S(12.0, 23.8, 'medina', 1.0, 1.10, (0.5, 0.5), (0.45, 0.48), titles=[(12.6, 20.0, 'Die Schlacht von Badr', 'Der Tag der Unterscheidung', True)], fx='motes'),
    S(23.8, 40.3, 'caravan', 1.0, 1.10, (0.4, 0.55), (0.5, 0.52), titles=[(24.0, 29.5, 'Die Karawane der Quraisch', None, False)]),
    S(40.3, 54.4, 'march', 1.02, 1.12, (0.5, 0.55), (0.48, 0.58), titles=[(40.5, 46.0, 'Etwas über 300 Mann', '2 Pferde, 70 Kamele', False)], srcs=[(43.0, 54.2, 'Quelle: Sahih al Bukhari 3957')]),
    S(54.4, 63.6, 'caravan', 1.12, 1.2, (0.75, 0.5), (0.85, 0.48)),
    S(63.6, 85.2, 'quraish', 1.0, 1.10, (0.5, 0.5), (0.55, 0.55), titles=[(63.8, 69.5, 'Rund 1000 Kämpfer', 'mit Pferden und Rüstungen', False)]),
    S(85.2, 105.3, 'march', 1.15, 1.25, (0.45, 0.6), (0.4, 0.6), srcs=[(87.4, 105.0, 'Quelle: Sahih al Bukhari 3952')]),
    S(105.3, 115.9, 'caravan', 1.0, 1.06, (0.5, 0.5), (0.45, 0.5), srcs=[(105.4, 115.6, 'Koran, Sure Al Anfal 8:7')]),
    S(115.9, 133.6, 'rain', 1.0, 1.10, (0.4, 0.55), (0.45, 0.55), titles=[(116.2, 121.5, 'Die Nacht vor Badr', None, False)], srcs=[(122.3, 133.4, 'Koran, Sure Al Anfal 8:11')], fx='rain'),
    S(133.6, 162.7, 'hut', 1.0, 1.12, (0.3, 0.55), (0.24, 0.58), srcs=[(145.5, 162.5, 'Quelle: Sahih Muslim 1763')], fx='lamp'),
    S(162.7, 169.3, 'dust', 1.0, 1.06, (0.6, 0.4), (0.62, 0.38), srcs=[(164.3, 169.1, 'Koran, Sure Al Anfal 8:9')]),
    S(169.3, 206.8, 'armies', 1.0, 1.14, (0.5, 0.5), (0.5, 0.55), titles=[(174.3, 180.3, '17. Ramadan', 'im 2. Jahr nach der Hidschra', False)], srcs=[(180.8, 204.0, 'Quelle: Sahih al Bukhari 3965 bis 3969')], fx='motes'),
    S(206.8, 230.8, 'dust', 1.0, 1.14, (0.45, 0.5), (0.55, 0.45), srcs=[(211.3, 218.5, 'Koran, Sure Al Anfal 8:17'), (221.7, 230.5, 'Koran, Sure Al Anfal 8:48')], fx='motes'),
    S(230.8, 257.7, 'quraish', 1.25, 1.35, (0.7, 0.65), (0.66, 0.62), srcs=[(231.0, 257.3, 'Quelle: Sahih al Bukhari 3141')]),
    S(257.7, 271.2, 'after', 1.0, 1.08, (0.6, 0.5), (0.55, 0.5), titles=[(260.7, 270.4, '70 gefallen, 70 gefangen', 'bei den Quraisch', False)]),
    S(271.2, 295.8, 'after', 1.2, 1.32, (0.25, 0.62), (0.22, 0.64), srcs=[(271.3, 295.5, 'Quelle: Sahih al Bukhari 3976')]),
    S(295.8, 316.7, 'medina', 1.15, 1.25, (0.5, 0.55), (0.55, 0.6), srcs=[(296.0, 307.5, 'Quelle: Sahih Muslim 1763')], fx='motes'),
    S(316.7, 326.4, 'dust', 1.12, 1.2, (0.62, 0.3), (0.62, 0.35), titles=[(316.9, 326.0, 'Yaum al Furqan', 'Der Tag der Unterscheidung', False)], srcs=[(317.0, 326.0, 'Koran, Sure Al Anfal 8:41')]),
    S(326.4, TOTAL + 0.1, 'after', 1.0, 1.1, (0.5, 0.45), (0.55, 0.4), titles=[(336.8, 343.5, 'Der Sieg kommt von Allah', None, False)], srcs=[(328.5, 335.0, 'Koran, Sure Al Imran 3:123')], fx='motes'),
]

def base(sc, t):
    u = (t - sc['t0']) / max(0.01, sc['t1'] - sc['t0'])
    f = kb(img(sc['im']), u, sc['z0'], sc['z1'], sc['c0'], sc['c1'])
    fx = sc.get('fx')
    if fx == 'rain': f = rain(f, t)
    elif fx == 'lamp':
        e = eio(u); s = sc['z0'] + (sc['z1'] - sc['z0']) * e
        cx = (sc['c0'][0] + (sc['c1'][0] - sc['c0'][0]) * e) * W; cy = (sc['c0'][1] + (sc['c1'][1] - sc['c0'][1]) * e) * H
        cx = min(max(cx, W / 2 / s), W - W / 2 / s); cy = min(max(cy, H / 2 / s), H - H / 2 / s)
        lx, ly = 0.188 * W, 0.53 * H
        f = flicker(f, t, W / 2 + (lx - cx) * s, H / 2 + (ly - cy) * s, 260)
    elif fx == 'motes': f = motes(f, t)
    return f

def decorate(f, sc, t):
    for a, b, txt, sub, big in sc.get('titles', []):
        if a <= t < b:
            al = min(ss(a, a + 0.5, t), 1 - ss(b - 0.5, b, t)); im = title(txt, sub, big)
            y = (H // 2 - im.shape[0] // 2 - 60) if big else 40
            overlay(f, im, (W - im.shape[1]) // 2, y + int((1 - al) * 10), al)
    for a, b, txt in sc.get('srcs', []):
        if a <= t < b:
            al = min(ss(a, a + 0.4, t), 1 - ss(b - 0.4, b, t)); im = src_tag(txt)
            overlay(f, im, W - im.shape[1] - 36, 40 if not any(x[0] <= t < x[1] for x in sc.get('titles', [])) else 40, al)

_IC = {'cap': None, 'idx': -1, 'cur': None}
def intro_frame(t):
    if _IC['cap'] is None:
        _IC['cap'] = cv2.VideoCapture(YT + '/assets/intro.mp4')
    target = int(t * 30)
    while _IC['idx'] < target:
        ok, fr = _IC['cap'].read()
        if not ok: break
        _IC['cur'] = fr[:, :, ::-1]; _IC['idx'] += 1
    return _IC['cur'].copy()

TR = 0.6
def frame(t):
    if t < INTRO:
        return intro_frame(t)
    i = max(k for k, s in enumerate(SC) if s['t0'] <= t) if t >= SC[0]['t0'] else 0
    sc = SC[i]; f = base(sc, t)
    if i == 0 and t < sc['t0'] + 0.8:
        k = ss(sc['t0'], sc['t0'] + 0.8, t)
        f = (f.astype(np.float32) * k).astype(np.uint8)
    elif i > 0 and t < sc['t0'] + TR:
        k = ss(sc['t0'], sc['t0'] + TR, t); p = base(SC[i - 1], t)
        f = cv2.addWeighted(p, 1 - k, f, k, 0)
    decorate(f, sc, t)
    if i > 0 and t < sc['t0'] + 0.6: decorate(f, SC[i - 1], t)
    if t > TOTAL - 1.5:
        f = (f.astype(np.float32) * (1 - ss(TOTAL - 1.5, TOTAL, t))).astype(np.uint8)
    draw_sub(f, t)
    return f

if __name__ == '__main__':
    if sys.argv[1] == 'still':
        out = sys.argv[2]; ts = [float(x) for x in sys.argv[3:]]
        tiles = [cv2.resize(frame(t), (640, 360)) for t in ts]
        while len(tiles) % 3: tiles.append(np.zeros_like(tiles[0]))
        cv2.imwrite(out, np.vstack([np.hstack(tiles[i:i + 3]) for i in range(0, len(tiles), 3)])[:, :, ::-1])
    else:
        f0, f1 = int(sys.argv[2]), int(sys.argv[3]); wr = sys.stdout.buffer
        for n in range(f0, f1):
            wr.write(np.ascontiguousarray(frame(n / FPS)).tobytes())
