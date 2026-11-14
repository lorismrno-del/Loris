import os
YT = os.environ.get('YT_ROOT', os.path.expanduser('~/yt_engine/yt'))
import sys, math, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, cv2
from badr_base import *   # helpers: night_bg, medallion, quote_card, glow_text, map_scene, overlay, draw_sub, src_tag, C, ss, eio, GOLD, W, H, FPS, DUR, cinzel

GOLD_F = np.float32(GOLD)
WHITE = (235, 230, 220)
GREEN = (140, 210, 160)
RED = (220, 110, 90)

def person(f, x, y, s, col, a=1.0):
    if a <= 0.02: return
    c = tuple(int(v * a) for v in col)
    cv2.circle(f, (int(x), int(y - 15 * s)), max(1, int(4.5 * s)), c, -1, cv2.LINE_AA)
    cv2.ellipse(f, (int(x), int(y)), (max(1, int(6 * s)), max(1, int(9 * s))), 0, 180, 360, c, -1, cv2.LINE_AA)
    cv2.rectangle(f, (int(x - 6 * s), int(y)), (int(x + 6 * s), int(y + 4 * s)), c, -1)

def camel(f, x, y, s, col, a=1.0, ph=0.0):
    c = tuple(int(v * a) for v in col)
    cv2.ellipse(f, (int(x), int(y)), (int(14 * s), int(7 * s)), 0, 0, 360, c, -1, cv2.LINE_AA)
    cv2.ellipse(f, (int(x - 2 * s), int(y - 6 * s)), (int(6 * s), int(6 * s)), 0, 180, 360, c, -1, cv2.LINE_AA)
    cv2.line(f, (int(x + 12 * s), int(y - 2 * s)), (int(x + 18 * s), int(y - 14 * s)), c, max(1, int(3 * s)), cv2.LINE_AA)
    cv2.circle(f, (int(x + 20 * s), int(y - 15 * s)), max(1, int(3 * s)), c, -1, cv2.LINE_AA)
    for k, lx in enumerate((-9, -4, 6, 11)):
        sw = 3 * s * math.sin(ph + k * 1.6)
        cv2.line(f, (int(x + lx * s), int(y + 4 * s)), (int(x + lx * s + sw), int(y + 16 * s)), c, max(1, int(2 * s)), cv2.LINE_AA)

def horse(f, x, y, s, col, a=1.0, ph=0.0):
    c = tuple(int(v * a) for v in col)
    cv2.ellipse(f, (int(x), int(y)), (int(14 * s), int(6 * s)), 0, 0, 360, c, -1, cv2.LINE_AA)
    pts = np.array([(x + 10 * s, y - 3 * s), (x + 20 * s, y - 16 * s), (x + 26 * s, y - 14 * s), (x + 16 * s, y)], np.int32)
    cv2.fillPoly(f, [pts], c, cv2.LINE_AA)
    cv2.line(f, (int(x - 13 * s), int(y - 2 * s)), (int(x - 20 * s), int(y + 8 * s)), c, max(1, int(2 * s)), cv2.LINE_AA)
    for k, lx in enumerate((-10, -5, 7, 12)):
        sw = 4 * s * math.sin(ph + k * 1.7)
        cv2.line(f, (int(x + lx * s), int(y + 4 * s)), (int(x + lx * s + sw), int(y + 17 * s)), c, max(1, int(2 * s)), cv2.LINE_AA)

def glowify(f, amt=0.6):
    g = cv2.GaussianBlur(f, (0, 0), 6)
    return cv2.addWeighted(f, 1.0, g, amt, 0)

_SP = {}
def sprite(name, h, tint=None):
    k = (name, h, tint)
    if k not in _SP:
        im = cv2.imread(YT + '/assets/cut/' + name + '.png', cv2.IMREAD_UNCHANGED)
        im = cv2.resize(im, (max(1, int(im.shape[1] * h / im.shape[0])), int(h)), interpolation=cv2.INTER_AREA)
        rgba = np.dstack([im[:, :, 2::-1], im[:, :, 3]]).copy()
        if tint is not None:
            rgba[..., :3] = np.clip(rgba[..., :3].astype(np.float32) * np.float32(tint), 0, 255).astype(np.uint8)
        _SP[k] = rgba
    return _SP[k]

def ground(f, y0=640):
    g = np.clip((np.arange(H, dtype=np.float32) - y0) / 260, 0, 1)[:, None, None]
    sand = np.float32([70, 52, 50])
    f[:] = (f.astype(np.float32) * (1 - g * 0.85) + sand * g * 0.85).astype(np.uint8)
    cv2.line(f, (0, y0), (W, y0), (120, 95, 80), 1, cv2.LINE_AA)

RNG = np.random.default_rng(11)
GRID313 = []
cols = 24
for i in range(313):
    r, c_ = divmod(i, cols)
    GRID313.append((c_, r))
ORDER313 = RNG.permutation(313)

def counter(f, n, x, y, size=150, sub=None):
    tx = C(('num', n, size), lambda: glow_text(str(n), cinzel(size)))
    overlay(f, tx, x - tx.shape[1] // 2, y - tx.shape[0] // 2)
    if sub:
        st = C(('sub', sub), lambda: glow_text(sub, cinzel(40), fill=(235, 225, 205), glow=False, pad=14))
        overlay(f, st, x - st.shape[1] // 2, y + size // 2 + 10)

def river(f, t, y0=760):
    for k in range(5):
        pts = []
        for x in range(0, W + 40, 40):
            pts.append((x, int(y0 + k * 22 + 10 * math.sin(x / 140 + t * 1.6 + k))))
        cv2.polylines(f, [np.array(pts, np.int32)], False, (90 + 20 * k, 120 + 15 * k, 200), 2, cv2.LINE_AA)

def scene(t):
    f = night_bg(t)
    if t < 3.05:
        # 313 men appear as a formation, counter rolls up
        k = ss(0.1, 2.4, t)
        n = int(313 * k)
        shown = set(ORDER313[:n].tolist())
        ox, oy, sp = W // 2 - (cols - 1) * 26 // 2, 500, 26
        for i in range(313):
            if i in shown:
                cx, ry = GRID313[i]
                person(f, ox + cx * sp, oy + ry * 26, 0.95, GREEN)
        f = glowify(f, 0.35)
        counter(f, n, W // 2, 250, 170, 'Mann')
        return f, None
    if t < 9.55:
        # nothing to animate: desert image with the quote
        u = (t - 3.05) / 6.5
        f = kb(img('march'), u, 1.0, 1.08, (0.5, 0.55), (0.45, 0.58))
        q = C('q1', lambda: quote_card('„Wir sprachen davon, dass die Leute von Badr so viele waren wie die Gefährten Taluts, die mit ihm den Fluss überquerten.“', 'Sahih al Bukhari 3957'))
        a2 = min(ss(3.15, 3.6, t), 1 - ss(9.2, 9.55, t))
        overlay(f, q, W // 2 - q.shape[1] // 2, 230, a2)
        return f, ('Sahih al Bukhari 3957', ss(3.15, 3.6, t))
    if t < 14.05:
        # 2 horses and 70 camels (cut out from the AI images) march away from camera
        u = t - 9.55
        ground(f, 600)
        for i, tint in enumerate((None, (0.55, 0.5, 0.5))):
            a = ss(0.1 + i * 0.25, 0.5 + i * 0.25, u)
            sp = sprite('horses', 330, tint)
            bob = int(4 * math.sin(t * 8 + i * 2))
            overlay(f, sp, 330 + i * 190, 560 + bob - (1 - i) * 20, a)
        items = []
        VPX, VPY = 1250, 600
        for i in range(70):
            col, r = divmod(i, 14)               # 5 columns, 14 deep
            d = r / 13.0
            sc = 210 * (1 - d) ** 1.6 + 26
            baseX = 760 + col * 230
            x = VPX + (baseX - VPX) * (1 - d) ** 1.6 - sc * 0.3
            y = VPY + (930 - VPY) * (1 - d) ** 1.6
            a = ss(0.9 + (69 - i) * 0.0, 1.0, u) * ss(0.9 + (13 - r) * 0.08, 1.3 + (13 - r) * 0.08, u)
            items.append((y, x, sc, a, i))
        for y, x, sc, a, i in sorted(items):
            sp = sprite('camel', max(8, int(sc)))
            bob = int(sc / 60 * math.sin(t * 6 + i * 0.7))
            overlay(f, sp, int(x), int(y - sc + bob), a)
        m1 = C('m2b', lambda: glow_text('2 Pferde', cinzel(56)))
        m2 = C('m70b', lambda: glow_text('70 Kamele', cinzel(56)))
        overlay(f, m1, 520 - m1.shape[1] // 2, 220, ss(9.65, 10.1, t))
        overlay(f, m2, 1300 - m2.shape[1] // 2, 220, ss(10.6, 11.1, t))
        return f, None
    if t < 23.3:
        u = (t - 14.05) / 9.25
        f = map_scene(t, u)
        # messenger dot running Badr area -> Mecca at "Boten nach Mekka"
        mk = ss(16.6, 18.9, t)
        if 16.6 < t < 23.3:
            a = np.array([880, 400]); b = np.array([1180, 760]); p = a + (b - a) * mk
            cv2.circle(f, tuple(map(int, p)), 9, (255, 240, 200), -1, cv2.LINE_AA)
            lab = C('bote', lambda: glow_text('Bote', cinzel(30), glow=False, pad=10))
            overlay(f, lab, int(p[0]) + 14, int(p[1]) - 40, min(1, mk * 4) * (1 - ss(19.5, 20.0, t)))
        f = glowify(f, 0.25)
        ti = C('tmap', lambda: glow_text('Der Weg der Karawane', cinzel(64)))
        overlay(f, ti, W // 2 - ti.shape[1] // 2 + 260, 40, ss(14.1, 14.6, t))
        return f, None
    # 313 vs 1000 formations
    u = t - 23.3
    kL = 1.0; kR = ss(0.4, 3.5, u)
    for i in range(313):
        r, c_ = divmod(i, 16)
        person(f, 260 + c_ * 22, 400 + r * 23, 0.75, GREEN, kL)
    nR = int(1000 * kR)
    for i in range(nR):
        r, c_ = divmod(i, 40)
        person(f, 960 + c_ * 22, 400 + r * 18, 0.62, RED)
    f = glowify(f, 0.3)
    counter(f, 313, 425, 230, 110, 'Muslime')
    counter(f, nR, 1390, 230, 110, 'Quraisch')
    g = C('geg', lambda: glow_text('gegen', cinzel(54)))
    overlay(f, g, 760 - g.shape[1] // 2, 560, ss(25.9, 26.4, t))
    for k, (txt, t0) in enumerate((('Pferde', 28.3), ('Rüstungen', 29.0), ('Vorräte', 29.8))):
        pass
    for k, (txt, t0) in enumerate((('Pferde', 28.3), ('Rüstungen', 29.0), ('Vorräte', 29.8))):
        ch = C(('ch', txt), lambda: glow_text(txt, cinzel(40), pad=16))
        overlay(f, ch, 1010 + k * 290, 860, ss(t0, t0 + 0.4, t))
    return f, None

import badr_base as R
R.scene = scene
frame = R.frame

if __name__ == '__main__':
    if sys.argv[1] == 'still':
        ts = [float(x) for x in sys.argv[3:]]
        tiles = [cv2.resize(frame(t), (640, 360)) for t in ts]
        while len(tiles) % 3: tiles.append(np.zeros_like(tiles[0]))
        cv2.imwrite(sys.argv[2], np.vstack([np.hstack(tiles[i:i + 3]) for i in range(0, len(tiles), 3)])[:, :, ::-1])
    else:
        wr = sys.stdout.buffer
        for n in range(int(DUR * FPS)): wr.write(np.ascontiguousarray(frame(n / FPS)).tobytes())
