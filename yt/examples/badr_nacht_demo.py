import os, sys, math, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, cv2
import badr_base as R
from badr_base import *
from badr_mix import person, sprite, camel as camel_icon

OFF = 115.6; DUR = 53.4
R.CUES = [[a - OFF, b - OFF, t] for a, b, t in json.load(open('timing.json'))['cues'] if OFF - 0.1 < a < OFF + DUR]

# ---------- palettes / grading ----------
def grade_to(im, tint, k=0.35, gain=1.0):
    f = im.astype(np.float32); lum = f.mean(axis=2, keepdims=True)
    t = lum * np.float32(tint) / 255.0 * 1.6
    return np.clip((f * (1 - k) + t * k) * gain * R.VIG, 0, 255).astype(np.uint8)

_G = {}
def gimg(name, tint, k=0.35, gain=1.0):
    key = (name, tint, k, gain)
    if key not in _G:
        im = cv2.imread(R.YT + '/assets/img/' + name + '.jpg')[:, :, ::-1]
        im = cv2.resize(im, (W, H), interpolation=cv2.INTER_LANCZOS4)
        _G[key] = grade_to(im, tint, k, gain)
    return _G[key]

NIGHT = (90, 100, 200)
WARM = (255, 190, 120)
DAWN = (240, 150, 150)

yyf = (np.arange(H, dtype=np.float32) / H)[:, None, None]
def sky(top, bottom, horizon=0.62):
    g = np.clip(yyf / horizon, 0, 1)
    return np.float32(top) * (1 - g) + np.float32(bottom) * g

DUNES = [(0.66, 40, 0.004, 0.0, (150, 105, 70)), (0.74, 50, 0.003, 1.3, (175, 125, 82)), (0.84, 60, 0.0025, 2.1, (200, 148, 98))]
def dunes(f, t, cam=0.0, tint=1.0):
    for k, (y0, amp, fr, ph, col) in enumerate(DUNES):
        xs = np.arange(0, W + 20, 20)
        ys = H * y0 + amp * np.sin(xs * fr + ph + cam * (k + 1) * 0.3) + 0.4 * amp * np.sin(xs * fr * 2.7 + ph * 2)
        pts = np.array([(0, H)] + list(zip(xs, ys.astype(int))) + [(W, H)], np.int32)
        cv2.fillPoly(f, [pts], tuple(int(c * tint) for c in col), cv2.LINE_AA)

def day_scene(t, u):
    f = sky((110, 150, 205), (245, 205, 150)).copy()
    sx, sy = int(W * 0.78), int(H * 0.36)
    sun = np.exp(-(((np.arange(W)[None, :] - sx) / 140.0) ** 2 + ((np.arange(H)[:, None] - sy) / 140.0) ** 2))[..., None]
    f = f + sun * np.float32([255, 220, 160]) * 0.9
    f = np.clip(f, 0, 255).astype(np.uint8)
    cv2.circle(f, (sx, sy), 46, (255, 244, 215), -1, cv2.LINE_AA)
    dunes(f, t, u)
    # wells
    for wx in (1320, 1500):
        cv2.ellipse(f, (wx, 790), (60, 18), 0, 0, 360, (95, 75, 60), -1, cv2.LINE_AA)
        cv2.ellipse(f, (wx, 784), (52, 13), 0, 0, 360, (40, 45, 70), -1, cv2.LINE_AA)
    # column of men + camels arriving
    items = []
    for i in range(40):
        x = -200 + i * 32 + u * 900 + 6 * math.sin(i * 1.7)
        y = 820 + (i % 3) * 14
        if x > 1250: continue
        items.append((y, 'p', x, i))
    for i in range(6):
        x = -420 + i * 150 + u * 900
        if x > 1150: continue
        items.append((812, 'c', x, i))
    for y, kind, x, i in sorted(items):
        if kind == 'p':
            person(f, x, y + 2 * math.sin(t * 8 + i), 2.3, (60, 45, 40))
        else:
            sp = sprite('camel', 88)
            overlay(f, sp, int(x), int(y - 80 + 2 * math.sin(t * 6 + i)))
    return R.np.ascontiguousarray(f)

def rain(f, t, amt=0.55):
    rng = np.random.default_rng(3); D = rng.uniform(0, 1, (650, 3))
    lay = np.zeros((H, W), np.float32)
    for x0, y0, s in D:
        sp = 1500 + 900 * s
        y = (y0 * (H + 200) + t * sp) % (H + 200) - 100
        x = (x0 * (W + 300) - t * sp * 0.18) % (W + 300) - 150
        l = 18 + 26 * s
        cv2.line(lay, (int(x), int(y)), (int(x - l * 0.18), int(y - l)), 0.35 + 0.4 * s, 1, cv2.LINE_AA)
    lay = cv2.GaussianBlur(lay, (3, 3), 0)[..., None]
    return np.clip(f.astype(np.float32) + lay * np.float32([170, 185, 225]) * amt, 0, 255).astype(np.uint8)

xx_, yy_ = np.meshgrid(np.arange(W, dtype=np.float32), np.arange(H, dtype=np.float32))
def lamp(f, t, cx, cy, r=260):
    k = 0.55 + 0.25 * math.sin(t * 7.3) + 0.12 * math.sin(t * 13.1 + 1) + 0.08 * math.sin(t * 23.7)
    g = np.exp(-(((xx_ - cx) / r) ** 2 + ((yy_ - cy) / r) ** 2))[..., None]
    return np.clip(f.astype(np.float32) * (1 + g * 0.3 * k) + g * np.float32([70, 40, 10]) * k, 0, 255).astype(np.uint8)

def predawn(t, k):
    # night -> dawn over the camp: sky blends, horizon glows, tents as silhouettes
    top = np.float32([14, 16, 44]) * (1 - k) + np.float32([40, 50, 110]) * k
    bot = np.float32([46, 26, 70]) * (1 - k) + np.float32([235, 140, 110]) * k
    f = sky(top, bot, 0.68).copy()
    st = night_bg(t).astype(np.float32)
    f = f * 0.85 + st * 0.15 * (1 - k)
    f = np.clip(f, 0, 255).astype(np.uint8)
    hz = int(H * 0.68)
    cv2.rectangle(f, (0, hz), (W, H), (18, 14, 24), -1)
    for i, x in enumerate(range(80, W, 170)):
        h = 70 + 25 * math.sin(i * 1.9)
        pts = np.array([(x - 70, hz + 4), (x, hz - h), (x + 70, hz + 4)], np.int32)
        cv2.fillPoly(f, [pts], (12, 10, 18), cv2.LINE_AA)
    return f

def beams(f, t, a):
    lay = np.zeros((H // 2, W // 2), np.float32)
    for i in range(7):
        x = (W // 2) * (0.15 + i * 0.12) + 20 * math.sin(t * 0.6 + i)
        w = 18 + 10 * math.sin(i * 2.3)
        pts = np.array([(x - w, 0), (x + w, 0), (x + w * 2.5, H // 2), (x - w * 2.5, H // 2)], np.int32)
        cv2.fillPoly(lay, [pts], 0.35 + 0.25 * math.sin(t * 1.3 + i))
    lay = cv2.resize(cv2.GaussianBlur(lay, (0, 0), 14), (W, H))[..., None] * a
    return np.clip(f.astype(np.float32) + lay * np.float32([255, 238, 200]) * 0.9, 0, 255).astype(np.uint8)


def night_ground(f, y0=760, col=(34, 28, 40)):
    xs = np.arange(0, W + 20, 20)
    ys = y0 + 18 * np.sin(xs * 0.004 + 1.2) + 8 * np.sin(xs * 0.011)
    pts = np.array([(0, H)] + list(zip(xs, ys.astype(int))) + [(W, H)], np.int32)
    cv2.fillPoly(f, [pts], col, cv2.LINE_AA)

def moon(f, x, y, r=46):
    g = np.exp(-(((xx_ - x) / (r * 3.2)) ** 2 + ((yy_ - y) / (r * 3.2)) ** 2))[..., None]
    f[:] = np.clip(f.astype(np.float32) + g * np.float32([150, 160, 210]) * 0.35, 0, 255).astype(np.uint8)
    cv2.circle(f, (x, y), r, (236, 236, 250), -1, cv2.LINE_AA)

def tent(f, x, y, s, col=(70, 58, 72)):
    pts = np.array([(x - 90 * s, y), (x, y - 85 * s), (x + 90 * s, y)], np.int32)
    cv2.fillPoly(f, [pts], col, cv2.LINE_AA)
    cv2.fillPoly(f, [np.array([(x - 14 * s, y), (x, y - 40 * s), (x + 14 * s, y)], np.int32)], (20, 16, 26), cv2.LINE_AA)

def sleeper(f, x, y, s, t, i):
    b = 1 + 0.05 * math.sin(t * 1.4 + i)
    cv2.circle(f, (int(x - 40 * s), int(y - 6 * s)), int(10 * s), (120, 110, 125), -1, cv2.LINE_AA)       # Kopf mit Turban
    cv2.ellipse(f, (int(x - 40 * s), int(y - 11 * s)), (int(11 * s), int(6 * s)), 0, 180, 360, (215, 210, 220), -1, cv2.LINE_AA)
    cv2.ellipse(f, (int(x), int(y - 2 * s)), (int(36 * s), int(13 * s * b)), 0, 180, 360, (175, 160, 150), -1, cv2.LINE_AA)  # Decke
    cv2.line(f, (int(x - 30 * s), int(y)), (int(x + 36 * s), int(y)), (175, 160, 150), max(1, int(3 * s)), cv2.LINE_AA)
    cv2.line(f, (int(x - 10 * s), int(y - 10 * s * b)), (int(x + 20 * s), int(y - 6 * s * b)), (140, 125, 120), 2, cv2.LINE_AA)

def camp_night(t):
    f = night_bg(t).copy()
    moon(f, 1720, 140, 40)
    night_ground(f)
    for i, (x, s) in enumerate([(220, 1.6), (560, 1.2), (1300, 1.3), (1660, 1.7)]):
        tent(f, x, 785, s)
    for i in range(14):
        x = 380 + (i % 7) * 170 + (i // 7) * 60
        y = 860 + (i // 7) * 70
        sleeper(f, x, y, 1.3 + (i // 7) * 0.2, t, i)
    return f

MOTES = np.random.default_rng(9).uniform(0, 1, (90, 3))
def prayer_night(t):
    f = night_bg(t).copy()
    night_ground(f, 800, (24, 20, 30))
    hx, hy = 520, 790
    cv2.fillPoly(f, [np.array([(hx - 110, hy), (hx - 95, hy - 120), (hx + 95, hy - 120), (hx + 110, hy)], np.int32)], (14, 12, 18), cv2.LINE_AA)
    k = 0.75 + 0.15 * math.sin(t * 7) + 0.1 * math.sin(t * 13)
    g = np.exp(-(((xx_ - hx) / 180) ** 2 + ((yy_ - (hy - 50)) / 140) ** 2))[..., None]
    f = np.clip(f.astype(np.float32) + g * np.float32([255, 170, 80]) * 0.55 * k, 0, 255).astype(np.uint8)
    cv2.rectangle(f, (hx - 40, hy - 80), (hx + 40, hy), (255, 190, 110), -1)
    for x0, y0, s in MOTES:
        y = hy - 60 - ((t * (25 + 40 * s) + y0 * 700) % 700)
        x = hx + (x0 - 0.5) * 220 + 25 * math.sin(t * 0.8 + y0 * 9)
        a = max(0.0, 1 - (hy - 60 - y) / 700)
        cv2.circle(f, (int(x), int(y)), 2 + int(2 * s), (int(255 * a), int(220 * a), int(150 * a)), -1, cv2.LINE_AA)
    return f

LIGHTS = np.random.default_rng(4).uniform(0, 1, (1000, 3))
def angels_dawn(t, t0):
    f = sky((60, 70, 140), (250, 170, 130), 0.66).copy()
    f = np.clip(f, 0, 255).astype(np.uint8)
    night_ground(f, 760, (95, 70, 70))
    f = beams(f, t, ss(t0, t0 + 1.5, t) * 0.45)
    u = t - t0
    for i, (x0, y0, s) in enumerate(LIGHTS):
        st = (i / 1000.0) * 3.0
        if u < st: continue
        p = min(1.0, (u - st) / 2.5)
        x = 200 + x0 * 1520; y = -20 + (300 + y0 * 380) * eio(p)
        cv2.circle(f, (int(x), int(y)), 2, (255, 250, 230), -1, cv2.LINE_AA)
    return cv2.addWeighted(f, 1.0, cv2.GaussianBlur(f, (0, 0), 5), 0.4, 0)

Q811 = '„Als Er Schläfrigkeit über euch kommen liess als Sicherheit von Ihm und Wasser vom Himmel auf euch herabsandte, um euch damit zu reinigen und eure Füsse damit zu festigen.“ (sinngemäss)'
QM = '„O Allah, erfülle mir, was Du mir versprochen hast. O Allah, wenn diese kleine Schar untergeht, wirst Du auf der Erde nicht mehr angebetet.“'
QPOS = {'qm': ('center', 220, 170), 'q89': ('center', 0, 520)}   # (anchor, dx, y); overridable

def qx(q, key):
    anc, dx, _ = QPOS[key]
    return (W - q.shape[1] - 60) if anc == 'right' else (W // 2 - q.shape[1] // 2 + dx)

Q89 = '„Ich werde euch mit tausend Engeln unterstützen, die einander folgen.“'

def scene(t):
    if t < 3.3:                                   # Tag, Wüste: warme Farbwelt, animiert
        f = day_scene(t, t / 3.3)
        ti = C('t_br', lambda: glow_text('Die Brunnen von Badr', cinzel(66), fill=(120, 70, 30), glow=False))
        overlay(f, ti, W // 2 - ti.shape[1] // 2, 60, ss(0.3, 0.8, t))
        return f, None
    if t < 10.0:                                  # BILD: Nacht, Regen
        u = (t - 3.3) / 6.7
        f = kb(gimg('rain', NIGHT, 0.4), u, 1.0, 1.06, (0.4, 0.55), (0.43, 0.55))
        return rain(f, t), None
    if t < 17.8:                                  # ANIMATION: ruhiges Lager, Schlaf
        f = rain(camp_night(t), t, 0.25 * (1 - ss(10.0, 13.0, t)))
        q = C('q811', lambda: quote_card(Q811, 'Sure Al Anfal 8:11'))
        a = min(ss(10.4, 10.9, t), 1 - ss(17.3, 17.8, t))
        overlay(f, q, W // 2 - q.shape[1] // 2, 150, a)
        return f, ('Sure Al Anfal 8:11', a)
    if t < 29.9:                                  # BILD: Hütte, Lampenlicht
        u = (t - 17.8) / 12.1
        z0, z1, c0, c1 = 1.0, 1.1, (0.3, 0.55), (0.25, 0.57)
        f = kb(gimg('hut', NIGHT, 0.25), u, z0, z1, c0, c1)
        e = eio(u); s_ = z0 + (z1 - z0) * e
        cx = (c0[0] + (c1[0] - c0[0]) * e) * W; cy = (c0[1] + (c1[1] - c0[1]) * e) * H
        cx = min(max(cx, W / 2 / s_), W - W / 2 / s_); cy = min(max(cy, H / 2 / s_), H - H / 2 / s_)
        return lamp(f, t, W / 2 + (0.188 * W - cx) * s_, H / 2 + (0.53 * H - cy) * s_), None
    if t < 39.0:                                  # ANIMATION: Bittgebet, Licht steigt auf
        f = prayer_night(t)
        q = C('qm', lambda: quote_card(QM, 'Sahih Muslim 1763'))
        a = min(ss(30.0, 30.5, t), 1 - ss(38.5, 39.0, t))
        overlay(f, q, qx(q, 'qm'), QPOS['qm'][2], a)
        return f, ('Sahih Muslim 1763', a)
    if t < 46.9:                                  # Nacht geht in Morgengrauen über: Bild wird wärmer
        u = (t - 39.0) / 7.9
        n = kb(gimg('hut', NIGHT, 0.25), u, 1.14, 1.2, (0.4, 0.5), (0.6, 0.45))
        d = kb(gimg('hut', DAWN, 0.35, 1.1), u, 1.14, 1.2, (0.4, 0.5), (0.6, 0.45))
        k = ss(39.5, 46.9, t) * 0.7
        return cv2.addWeighted(n, 1 - k, d, k, 0), None
    f = angels_dawn(t, 46.9)                      # ANIMATION: Engel, Morgenlicht
    q = C('q89', lambda: quote_card(Q89, 'Sure Al Anfal 8:9', w=1000))
    a = ss(48.6, 49.1, t)
    overlay(f, q, qx(q, 'q89'), QPOS['q89'][2], a)
    return f, ('Sure Al Anfal 8:9', a)

TRS = [3.3, 10.0, 17.8, 29.9, 39.0, 46.9]
def frame(t):
    f, src = scene(t)
    for tr in TRS:
        if tr <= t < tr + 0.6:
            p, _ = scene(tr - 0.001); k = ss(tr, tr + 0.6, t)
            f = cv2.addWeighted(p, 1 - k, f, k, 0)
    if t < 0.6: f = (f.astype(np.float32) * ss(0, 0.6, t)).astype(np.uint8)
    if t > DUR - 0.8: f = (f.astype(np.float32) * (1 - ss(DUR - 0.8, DUR, t))).astype(np.uint8)
    if src and src[1] > 0.01:
        tag = C(('src', src[0]), lambda: src_tag(src[0])); overlay(f, tag, W - tag.shape[1] - 36, 36, src[1])
    R.draw_sub(f, t)
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
