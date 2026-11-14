import os
YT = os.environ.get('YT_ROOT', os.path.expanduser('~/yt_engine/yt'))
import sys, json, math
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1920, 1080, 30
OFF = 40.15; DUR = 31.2
IMG = YT + '/assets/img/'
CINZEL = YT + '/fonts/Cinzel.ttf'
INTER_B = YT + '/fonts/Inter-Bold.otf'
INTER_M = YT + '/fonts/Inter-Medium.otf'
LORA = YT + '/fonts/Lora.ttf'
GOLD = (232, 196, 120)
CUES = [[a - OFF, b - OFF, t] for a, b, t in json.load(open('timing.json'))['cues'] if OFF - 0.1 < a < OFF + DUR]

def ss(a, b, t):
    if b <= a: return 1.0 if t >= b else 0.0
    x = min(1.0, max(0.0, (t - a) / (b - a))); return x * x * (3 - 2 * x)
def eio(x):
    x = min(1.0, max(0.0, x)); return x * x * (3 - 2 * x)
def cinzel(size, w='Bold'):
    f = ImageFont.truetype(CINZEL, size)
    try: f.set_variation_by_name(w)
    except Exception: pass
    return f

yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
dd = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
VIG = (1 - 0.42 * np.clip((dd - 0.55) / 0.9, 0, 1) ** 1.4)[..., None]
# night grade: tint toward navy/violet so photos and graphics share one look
def grade(im, k=0.35):
    f = im.astype(np.float32)
    lum = f.mean(axis=2, keepdims=True)
    tint = lum * np.float32([0.62, 0.62, 1.0]) + np.float32([10, 6, 28])
    return np.clip((f * (1 - k) + tint * k) * VIG, 0, 255).astype(np.uint8)

_IMG = {}
def img(name):
    if name not in _IMG:
        im = cv2.imread(IMG + name + '.jpg')[:, :, ::-1]
        _IMG[name] = grade(cv2.resize(im, (W, H), interpolation=cv2.INTER_LANCZOS4))
    return _IMG[name]

def kb(src, u, z0, z1, c0, c1):
    e = eio(u); s = z0 + (z1 - z0) * e
    cx = (c0[0] + (c1[0] - c0[0]) * e) * W; cy = (c0[1] + (c1[1] - c0[1]) * e) * H
    cx = min(max(cx, W / 2 / s), W - W / 2 / s); cy = min(max(cy, H / 2 / s), H - H / 2 / s)
    M = np.float32([[s, 0, W / 2 - cx * s], [0, s, H / 2 - cy * s]])
    return cv2.warpAffine(src, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)

# starry navy background
rng = np.random.default_rng(5)
STARS = rng.uniform(0, 1, (420, 4))
def night_bg(t):
    g = (yy / H)[..., None]
    f = np.float32([14, 16, 44]) * (1 - g) + np.float32([46, 26, 70]) * g
    f = f.copy()
    for x, y, s, ph in STARS:
        a = (0.35 + 0.65 * s) * (0.6 + 0.4 * math.sin(t * (1 + 2 * s) + ph * 6))
        cv2.circle(f, (int(x * W), int(y * H * 0.85)), 1 if s < 0.8 else 2, (230 * a, 225 * a, 255 * a), -1, cv2.LINE_AA)
    return np.clip(f * VIG, 0, 255).astype(np.uint8)

def overlay(f, rgba, x, y, a=1.0):
    h, w = rgba.shape[:2]
    xa, ya = max(0, x), max(0, y); xb, yb = min(W, x + w), min(H, y + h)
    if xb <= xa or yb <= ya or a <= 0.01: return
    s = rgba[ya - y:yb - y, xa - x:xb - x]; al = s[..., 3:4].astype(np.float32) / 255.0 * a
    reg = f[ya:yb, xa:xb].astype(np.float32)
    f[ya:yb, xa:xb] = (reg * (1 - al) + s[..., :3] * al).astype(np.uint8)

def glow_text(text, font, fill=GOLD, glow=True, pad=40):
    d = ImageDraw.Draw(Image.new('RGBA', (10, 10))); bb = d.textbbox((0, 0), text, font=font)
    w, h = bb[2] - bb[0] + 2 * pad, bb[3] - bb[1] + 2 * pad
    base = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    if glow:
        g = Image.new('RGBA', (w, h), (0, 0, 0, 0)); ImageDraw.Draw(g).text((pad - bb[0], pad - bb[1]), text, font=font, fill=fill + (150,))
        base = Image.alpha_composite(base, g.filter(ImageFilter.GaussianBlur(10)))
    sh = Image.new('RGBA', (w, h), (0, 0, 0, 0)); ImageDraw.Draw(sh).text((pad - bb[0], pad - bb[1] + 3), text, font=font, fill=(0, 0, 0, 200))
    base = Image.alpha_composite(base, sh.filter(ImageFilter.GaussianBlur(5)))
    ImageDraw.Draw(base).text((pad - bb[0], pad - bb[1]), text, font=font, fill=fill + (255,))
    return np.array(base)

_C = {}
def C(key, fn):
    if key not in _C: _C[key] = fn()
    return _C[key]

def medallion(big, small, r=150):
    S = 2 * r + 80; im = Image.new('RGBA', (S, S), (0, 0, 0, 0)); c = S // 2
    g = Image.new('RGBA', (S, S), (0, 0, 0, 0)); ImageDraw.Draw(g).ellipse((c - r - 6, c - r - 6, c + r + 6, c + r + 6), outline=GOLD + (170,), width=10)
    im = Image.alpha_composite(im, g.filter(ImageFilter.GaussianBlur(12)))
    d = ImageDraw.Draw(im)
    d.ellipse((c - r, c - r, c + r, c + r), fill=(22, 18, 48, 235), outline=GOLD + (255,), width=5)
    d.ellipse((c - r + 14, c - r + 14, c + r - 14, c + r - 14), outline=GOLD + (110,), width=2)
    # 8-point star pattern
    pts = []
    for k in range(16):
        ang = k * math.pi / 8 - math.pi / 2; rr = (r - 30) if k % 2 == 0 else (r - 52)
        pts.append((c + rr * math.cos(ang), c + rr * math.sin(ang)))
    d.polygon(pts, outline=GOLD + (60,))
    fb = cinzel(int(r * 0.62)); bb = d.textbbox((0, 0), big, font=fb)
    d.text((c - (bb[2] + bb[0]) / 2, c - (bb[3] + bb[1]) / 2 - (14 if small else 0)), big, font=fb, fill=GOLD + (255,))
    if small:
        fs = cinzel(int(r * 0.23)); bb = d.textbbox((0, 0), small, font=fs)
        d.text((c - (bb[2] + bb[0]) / 2, c + r * 0.30), small, font=fs, fill=(235, 225, 205, 255))
    return np.array(im)

def quote_card(text, src, w=1180):
    f = ImageFont.truetype(LORA, 40)
    try: f.set_variation_by_name('Italic')
    except Exception: pass
    d = ImageDraw.Draw(Image.new('RGBA', (10, 10))); words = text.split(); lines = []; cur = ''
    for x in words:
        tst = (cur + ' ' + x).strip()
        if d.textlength(tst, font=f) < w - 120: cur = tst
        else: lines.append(cur); cur = x
    lines.append(cur)
    h = 70 + len(lines) * 56 + 60
    im = Image.new('RGBA', (w + 40, h + 40), (0, 0, 0, 0))
    sh = Image.new('RGBA', im.size, (0, 0, 0, 0)); ImageDraw.Draw(sh).rounded_rectangle((26, 30, w + 26, h + 30), 16, fill=(0, 0, 0, 170))
    im = Image.alpha_composite(im, sh.filter(ImageFilter.GaussianBlur(12))); d = ImageDraw.Draw(im)
    d.rounded_rectangle((20, 20, w + 20, h + 20), 16, fill=(18, 14, 38, 225), outline=GOLD + (230,), width=3)
    y = 60
    for l in lines:
        tw = d.textlength(l, font=f); d.text((20 + (w - tw) / 2, y), l, font=f, fill=(245, 238, 222, 255)); y += 56
    fs = ImageFont.truetype(INTER_M, 24); tw = d.textlength(src, font=fs)
    d.text((20 + (w - tw) / 2, y + 12), src, font=fs, fill=GOLD + (255,))
    return np.array(im)

def src_tag(txt):
    f = ImageFont.truetype(INTER_M, 26); d = ImageDraw.Draw(Image.new('RGBA', (10, 10))); bb = d.textbbox((0, 0), txt, font=f)
    tw, th = bb[2] - bb[0], bb[3] - bb[1]; pw, ph = tw + 44, 50
    im = Image.new('RGBA', (pw, ph), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, pw - 1, ph - 1), 8, fill=(14, 10, 30, 190), outline=GOLD + (220,), width=2)
    d.text(((pw - tw) // 2 - bb[0], (ph - th) // 2 - bb[1]), txt, font=f, fill=(240, 222, 180, 255))
    return np.array(im)

# word-highlight subtitles
FS = ImageFont.truetype(INTER_B, 44)
def sub_layout(i):
    text = CUES[i][2]; words = text.split()
    d = ImageDraw.Draw(Image.new('RGBA', (10, 10)))
    sp = d.textlength(' ', font=FS); ws = [d.textlength(w_, font=FS) for w_ in words]
    tw = sum(ws) + sp * (len(words) - 1)
    L = np.array([len(w_) + 1 for w_ in words], float); cum = np.concatenate([[0], np.cumsum(L) / L.sum()])
    return words, ws, sp, tw, cum
def draw_sub(f, t):
    for i, (a, b, txt) in enumerate(CUES):
        if a <= t < b:
            words, ws, sp, tw, cum = C(('L', i), lambda: sub_layout(i))
            u = (t - a) / (b - a); cur = int(np.searchsorted(cum, u, side='right') - 1)
            pw, ph = int(tw + 64), 72
            im = Image.new('RGBA', (pw, ph), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
            d.rounded_rectangle((0, 0, pw - 1, ph - 1), ph // 2, fill=(14, 10, 28, 200))
            x = 32
            for k, (w_, wd) in enumerate(zip(words, ws)):
                d.text((x, 12), w_, font=FS, fill=(GOLD + (255,)) if k == cur else (250, 248, 242, 255)); x += wd + sp
            al = min(ss(a, a + 0.08, t), 1 - ss(b - 0.08, b, t))
            overlay(f, np.array(im), (W - pw) // 2, 1010 - ph // 2, al); return

# map scene (stylized, Rechtsschulen look)
COAST = [(560, 0), (600, 120), (640, 240), (700, 360), (760, 470), (830, 580), (900, 690), (960, 790), (1010, 900), (1050, 1080)]
def map_scene(t, u):
    f = night_bg(t).astype(np.float32)
    land = np.zeros((H, W), np.uint8)
    cv2.fillPoly(land, [np.array(COAST + [(W, 1080), (W, 0)], np.int32)], 1)
    lf = cv2.GaussianBlur(land.astype(np.float32), (0, 0), 3)[..., None]
    f = f * (1 - lf * 0.55) + np.float32([70, 52, 40]) * lf * 0.55
    f = f.astype(np.uint8)
    cv2.polylines(f, [np.array(COAST, np.int32)], False, GOLD, 2, cv2.LINE_AA)
    P = dict(Medina=(1120, 330), Badr=(930, 470), Mekka=(1180, 760))
    syr = (720, 60)
    # caravan route along the coast (from north to Mecca)
    route = [syr, (760, 200), (820, 330), (860, 440), (920, 560), (1000, 650), P['Mekka']]
    k = ss(0.05, 0.85, u)
    pts = np.array(route, np.float32); seg = np.linalg.norm(np.diff(pts, axis=0), axis=1); tot = seg.sum() * k
    acc = 0; drawn = [route[0]]
    for i, sl in enumerate(seg):
        if acc + sl <= tot: drawn.append(route[i + 1]); acc += sl
        else:
            r = (tot - acc) / sl; drawn.append(tuple(pts[i] + (pts[i + 1] - pts[i]) * r)); break
    for i in range(len(drawn) - 1):
        a, b = np.array(drawn[i]), np.array(drawn[i + 1]); n = int(np.linalg.norm(b - a) / 18)
        for j in range(0, n, 2):
            p0 = a + (b - a) * j / max(1, n); p1 = a + (b - a) * min(1, (j + 1) / max(1, n))
            cv2.line(f, tuple(map(int, p0)), tuple(map(int, p1)), GOLD, 4, cv2.LINE_AA)
    if len(drawn) > 1:
        hx, hy = map(int, drawn[-1]); cv2.circle(f, (hx, hy), 11, (255, 230, 170), -1, cv2.LINE_AA)
    # Muslim march Medina -> Badr
    m = ss(0.0, 0.4, u)
    a, b = np.array(P['Medina']), np.array(P['Badr']); e = a + (b - a) * m
    cv2.line(f, tuple(a), tuple(map(int, e)), (140, 210, 160), 4, cv2.LINE_AA)
    for name, (x, y) in P.items():
        glow = (1 + 0.15 * math.sin(t * 3))
        cv2.circle(f, (x, y), int(16 * glow), GOLD, 2, cv2.LINE_AA); cv2.circle(f, (x, y), 7, GOLD, -1, cv2.LINE_AA)
        lab = C(('lab', name), lambda: glow_text(name, cinzel(40), glow=False, pad=20))
        overlay(f, lab, x + 26, y - lab.shape[0] // 2)
    sea = C('sea', lambda: glow_text('Rotes Meer', cinzel(30, 'Regular'), fill=(150, 170, 220), glow=False, pad=10))
    overlay(f, sea, 330, 560, 0.8)
    return f

def scene(t):
    # returns base frame and decorations per time
    if t < 9.55:
        f = kb(img('march'), t / 9.55, 1.0, 1.1, (0.5, 0.55), (0.46, 0.58))
        m = C('m313', lambda: medallion('313', 'Mann'))
        a = min(ss(0.15, 0.7, t), 1 - ss(2.6, 3.0, t))
        overlay(f, m, W // 2 - m.shape[1] // 2, 300 - int((1 - a) * 20), a)
        q = C('q1', lambda: quote_card('„Wir sprachen davon, dass die Leute von Badr so viele waren wie die Gefährten Taluts, die mit ihm den Fluss überquerten.“', 'Sahih al Bukhari 3957'))
        a2 = min(ss(3.1, 3.6, t), 1 - ss(9.2, 9.55, t))
        overlay(f, q, W // 2 - q.shape[1] // 2, 330, a2)
        return f, ('Sahih al Bukhari 3957', ss(3.1, 3.6, t))
    if t < 14.05:
        u = (t - 9.55) / 4.5
        f = kb(img('march'), u, 1.12, 1.18, (0.3, 0.6), (0.27, 0.6))
        m1 = C('m2', lambda: medallion('2', 'Pferde', 125)); m2 = C('m70', lambda: medallion('70', 'Kamele', 125))
        a1 = ss(9.65, 10.2, t); a2 = ss(10.6, 11.1, t)
        overlay(f, m1, W // 2 - 260 - m1.shape[1] // 2, 280 + int((1 - a1) * 20), a1)
        overlay(f, m2, W // 2 + 260 - m2.shape[1] // 2, 280 + int((1 - a2) * 20), a2)
        return f, None
    if t < 23.3:
        u = (t - 14.05) / 9.25
        f = map_scene(t, u)
        ti = C('tmap', lambda: glow_text('Der Weg der Karawane', cinzel(64)))
        overlay(f, ti, W // 2 - ti.shape[1] // 2 + 260, 40, ss(14.1, 14.6, t))
        return f, None
    u = (t - 23.3) / (DUR - 23.3)
    f = kb(img('quraish'), u, 1.0, 1.1, (0.5, 0.5), (0.56, 0.55))
    ma = C('mA', lambda: medallion('313', 'Muslime', 135)); mb = C('mB', lambda: medallion('1000', 'Quraisch', 135))
    a1 = ss(25.6, 26.1, t); a2 = ss(25.9, 26.4, t); ag = ss(26.3, 26.7, t)
    overlay(f, ma, W // 2 - 330 - ma.shape[1] // 2, 230 - int((1 - a1) * 20), a1)
    overlay(f, mb, W // 2 + 330 - mb.shape[1] // 2, 230 - int((1 - a2) * 20), a2)
    g = C('geg', lambda: glow_text('gegen', cinzel(54)))
    overlay(f, g, W // 2 - g.shape[1] // 2, 365, ag)
    return f, None

TRS = [9.55, 14.05, 23.3]
def frame(t):
    f, src = scene(t)
    for tr in TRS:
        if tr <= t < tr + 0.5:
            p, _ = scene(tr - 0.001); k = ss(tr, tr + 0.5, t)
            f = cv2.addWeighted(p, 1 - k, f, k, 0)
    if t < 0.6: f = (f.astype(np.float32) * ss(0, 0.6, t)).astype(np.uint8)
    if t > DUR - 0.8: f = (f.astype(np.float32) * (1 - ss(DUR - 0.8, DUR, t))).astype(np.uint8)
    if src:
        tag = C(('src', src[0]), lambda: src_tag(src[0])); overlay(f, tag, W - tag.shape[1] - 36, 36, src[1])
    draw_sub(f, t)
    return f

if __name__ == '__main__':
    if sys.argv[1] == 'still':
        ts = [float(x) for x in sys.argv[3:]]
        tiles = [cv2.resize(frame(t), (640, 360)) for t in ts]
        while len(tiles) % 3: tiles.append(np.zeros_like(tiles[0]))
        cv2.imwrite(sys.argv[2], np.vstack([np.hstack(tiles[i:i + 3]) for i in range(0, len(tiles), 3)])[:, :, ::-1])
    else:
        wr = sys.stdout.buffer
        for n in range(int(DUR * FPS)): wr.write(np.ascontiguousarray(frame(n / FPS)).tobytes())
