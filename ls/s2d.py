"""Yunus, gezeichnete Doku, Szenen folgen Satz fuer Satz dem Erzaehler."""
import os
from base import *
import s2b, s2c

P = s2c.P
ink = s2b.ink; curve_pts = s2b.curve_pts; along = s2b.along
T = s2c.T

# Szenengrenzen pro Satz
SC = [0.0, S[1] - 0.45, S[2] - 0.30, S[3] - 0.25, S[4] - 0.25, S[5] - 0.25,
      S[6] - 0.30, S[7] - 0.20, S[8] - 0.30, S[9] - 0.30, S[10] - 0.25, DUR]
XF = 0.38

def scene_at(t):
    for i in range(len(SC) - 1):
        if SC[i] <= t < SC[i + 1]:
            return i, t - SC[i], SC[i + 1] - SC[i]
    return len(SC) - 2, t - SC[-2], SC[-1] - SC[-2]

def cam(ctx, t, z=1.0, px=0.0, py=0.0, cx=None, cy=None):
    cx = W / 2 if cx is None else cx
    cy = H / 2 if cy is None else cy
    z = z * (1 + 0.009 * math.sin(t * 0.33))
    ctx.translate(cx, cy); ctx.scale(z, z); ctx.translate(-cx, -cy)
    ctx.translate(px + math.sin(t * 0.26) * 7, py + math.cos(t * 0.2) * 5)

# ---------------- Figuren ----------------
def fig(ctx, x, y, s, t, pose='stand', facing=1, light=False, ph=0.0, a=1.0, lw=4.5):
    """Gewandfigur in Tuschelinie, kein Gesicht, schlanke Proportionen"""
    bob = math.sin(t * 2.2 + ph) * 2.0
    sway = math.sin(t * 1.5 + ph) * 2.6
    ctx.save(); ctx.translate(x, y + bob * s); ctx.scale(s * facing, s)
    # Gewand, schmale Schultern, leicht ausgestellter Saum
    robe = [(-14, -88), (-17, -62), (-20, -30), (-23, 4), (-25, 34),
            (25, 34), (23, 4), (20, -30), (17, -62), (14, -88)]
    robe = [(px + sway * (py + 86) / 120.0, py) for px, py in robe]
    ink(ctx, robe, 1.0, lw, 0.92 * a, close=True, fill=(P['p1'], 0.88 * a), amp=0.8)
    src(ctx, P['ink'], 0.35 * a); ctx.set_line_width(2)
    for k in range(3):
        xx = -11 + k * 11
        ctx.move_to(xx, -70); ctx.curve_to(xx - 3 + sway, -34, xx + 3, -2, xx - 2 + sway, 30); ctx.stroke()
    # Guertel
    ink(ctx, [(-21, -40), (0, -37), (21, -40)], 1.0, 3.4, 0.6 * a, amp=0.7)
    # Hals
    ink(ctx, [(-6, -88), (-6, -96)], 1.0, 3.2, 0.7 * a, curve=False, amp=0.5)
    ink(ctx, [(6, -88), (6, -96)], 1.0, 3.2, 0.7 * a, curve=False, amp=0.5)
    # Kopf
    if light:
        g = cairo.RadialGradient(0, -118, 2, 0, -118, 60)
        ar, ag, ab = C(P['acc'])[:3]
        g.add_color_stop_rgba(0, 1, 0.98, 0.9, 0.95 * a)
        g.add_color_stop_rgba(0.42, 1, 0.9, 0.62, 0.5 * a)
        g.add_color_stop_rgba(1, ar, ag, ab, 0)
        ctx.set_source(g); circle(ctx, 0, -118, 60); ctx.fill()
        src(ctx, P['p1'], 0.95 * a); circle(ctx, 0, -118, 19); ctx.fill()
    else:
        ink(ctx, [(-18, -100), (-20, -120), (-11, -136), (11, -136), (20, -120), (18, -100)],
            1.0, lw * 0.9, 0.9 * a, close=True, fill=(P['p1'], 0.92 * a), amp=0.6)
        ink(ctx, [(-23, -104), (-25, -124), (-12, -142), (12, -142), (25, -124), (23, -104)],
            1.0, 3.2, 0.7 * a, amp=0.6)
        ink(ctx, [(-19, -104), (-24, -86), (-14, -84)], 1.0, 3.0, 0.6 * a, amp=0.7)
        ink(ctx, [(19, -104), (24, -86), (14, -84)], 1.0, 3.0, 0.6 * a, amp=0.7)
    # Arme
    if pose == 'point':
        ink(ctx, [(14, -80), (40, -86), (68, -96)], 1.0, lw * 0.95, 0.9 * a, amp=0.7)
        ink(ctx, [(68, -96), (80, -99)], 1.0, 3.2, 0.9 * a, curve=False, amp=0.5)
        ink(ctx, [(-14, -80), (-24, -48), (-21, -18)], 1.0, lw * 0.9, 0.8 * a, amp=0.8)
    elif pose == 'raise':
        for sgn in (-1, 1):
            ink(ctx, [(sgn * 14, -80), (sgn * 32, -116), (sgn * 24, -154 + math.sin(t * 1.8 + ph) * 4)],
                1.0, lw * 0.95, 0.9 * a, amp=0.8)
    elif pose == 'walk':
        sw = math.sin(t * 4.2 + ph) * 14
        ink(ctx, [(14, -80), (28, -52 + sw * 0.3), (30, -20 + sw * 0.5)], 1.0, lw * 0.95, 0.9 * a, amp=0.8)
        ink(ctx, [(-14, -80), (-26, -52 - sw * 0.3), (-28, -20 - sw * 0.5)], 1.0, lw * 0.9, 0.75 * a, amp=0.8)
    elif pose == 'kneel':
        ink(ctx, [(15, -80), (34, -112), (26, -150 + math.sin(t * 1.6) * 4)], 1.0, lw * 0.95, 0.9 * a, amp=0.8)
        ink(ctx, [(-15, -80), (-34, -112), (-26, -150 + math.cos(t * 1.6) * 4)], 1.0, lw * 0.95, 0.9 * a, amp=0.8)
    else:
        ink(ctx, [(15, -80), (26, -44), (23, -10)], 1.0, lw * 0.9, 0.85 * a, amp=0.8)
        ink(ctx, [(-15, -80), (-26, -44), (-23, -10)], 1.0, lw * 0.9, 0.7 * a, amp=0.8)
    ctx.restore()
    src(ctx, P['ink'], 0.16 * a); ellipse(ctx, x, y + 34 * s, 32 * s, 7 * s); ctx.fill()

# ---------------- Orte ----------------
def ziggurat(ctx, x, y, s, prog=1.0):
    for k in range(4):
        p = clamp(prog * 4 - k)
        if p <= 0: break
        w_ = (300 - k * 62) * s; h_ = 46 * s * p
        yy = y - k * 46 * s
        ink(ctx, [(x - w_ / 2, yy), (x - w_ / 2 + 10 * s, yy - h_), (x + w_ / 2 - 10 * s, yy - h_), (x + w_ / 2, yy)],
            1.0, 4.5, 0.85, close=True, fill=(P['p3'], 0.55), curve=False, amp=1.0)
    if prog > 0.9:
        src(ctx, P['ink'], 0.3); ctx.set_line_width(2)
        for k in range(7):
            ctx.move_to(x - 120 * s + k * 40 * s, y); ctx.line_to(x - 96 * s + k * 40 * s, y - 42 * s); ctx.stroke()

def mudhouse(ctx, x, y, w_, h_, t, seed=1, door=True):
    ink(ctx, [(x, y), (x, y - h_), (x + w_, y - h_), (x + w_, y)], 1.0, 4.4, 0.88,
        close=True, fill=(P['p1'], 0.8), curve=False, amp=1.0)
    src(ctx, P['ink'], 0.35); ctx.set_line_width(2.4)
    ctx.move_to(x - 6, y - h_); ctx.line_to(x + w_ + 6, y - h_); ctx.stroke()
    r = rnd(seed)
    for k in range(int(h_ / 22)):
        yy = y - 14 - k * 22
        if yy < y - h_ + 8: break
        src(ctx, P['ink'], 0.14); ctx.set_line_width(1.8)
        ctx.move_to(x + 4, yy); ctx.line_to(x + w_ - 4, yy + r.uniform(-2, 2)); ctx.stroke()
    if door:
        dw = w_ * 0.3
        ink(ctx, [(x + w_ / 2 - dw / 2, y), (x + w_ / 2 - dw / 2, y - h_ * 0.42),
                  (x + w_ / 2, y - h_ * 0.56), (x + w_ / 2 + dw / 2, y - h_ * 0.42),
                  (x + w_ / 2 + dw / 2, y)], 1.0, 3.2, 0.7, fill=(P['ink'], 0.3), amp=0.8)

def palm(ctx, x, y, h_, t, seed=0, a=1.0):
    sw = math.sin(t * 0.9 + seed) * 5
    ink(ctx, [(x, y), (x + sw * 0.3, y - h_ * 0.45), (x + sw, y - h_)], 1.0, 5, 0.85 * a, amp=0.9)
    for k in range(6):
        ang = -PI / 2 + (k - 2.5) * 0.46
        ex = x + sw + math.cos(ang) * h_ * 0.42
        ey = y - h_ + math.sin(ang) * h_ * 0.3 + 14
        ink(ctx, [(x + sw, y - h_), ((x + sw + ex) / 2, (y - h_ + ey) / 2 - 16), (ex, ey)],
            1.0, 3.6, 0.8 * a, amp=1.1)

def mountains(ctx, t, y, hmax, a=1.0, seed=4, layers=2):
    for L in range(layers):
        r = rnd(seed + L * 7)
        base = y + L * 34
        hh = hmax * (1 - L * 0.42)
        peaks = []
        x = 60
        while x < W - 40:
            w_ = r.uniform(230, 400)
            peaks.append((x, x + w_ * 0.5, x + w_, r.uniform(0.6, 1.0) * hh))
            x += w_ * 0.82
        pts = [(40, base)]
        for (x0, xm, x1, ph_) in peaks:
            pts.append((x0 + (xm - x0) * 0.45, base - ph_ * 0.52))
            pts.append((xm, base - ph_))
            pts.append((xm + (x1 - xm) * 0.42, base - ph_ * 0.6))
            pts.append((x1, base - ph_ * 0.16))
        pts.append((W - 40, base))
        ink(ctx, pts, 1.0, 4.4 - L, (0.85 - L * 0.3) * a, fill=(P['p3'], (0.5 - L * 0.18) * a), amp=0.8)
        src(ctx, P['ink'], 0.2 * a); ctx.set_line_width(2)
        for (x0, xm, x1, ph_) in peaks:
            ctx.move_to(xm, base - ph_)
            ctx.line_to(xm + (x1 - xm) * 0.42, base - ph_ * 0.6)
            ctx.line_to(x1, base - ph_ * 0.16); ctx.stroke()
            for j in range(4):
                u = 0.2 + j * 0.18
                ctx.move_to(xm + (x1 - xm) * u * 0.7, base - ph_ * (0.86 - u * 0.5))
                ctx.line_to(xm + (x1 - xm) * (u * 0.7 + 0.1), base - ph_ * (0.56 - u * 0.42))
                ctx.stroke()

def quay(ctx, t, y):
    ink(ctx, [(0, y), (540, y - 6), (980, y - 2)], 1.0, 6, 0.85, amp=1.0)
    src(ctx, P['p3'], 0.6); ctx.rectangle(0, y, 980, H - y); ctx.fill()
    src(ctx, P['ink'], 0.3); ctx.set_line_width(2.4)
    for k in range(9):
        ctx.move_to(60 + k * 108, y + 4); ctx.line_to(60 + k * 108, y + 56); ctx.stroke()
    for k in range(4):
        px = 170 + k * 240
        ink(ctx, [(px, y + 8), (px + 4, y + 120)], 1.0, 7, 0.6, amp=0.8)

# ---------------- Schiff ----------------
def ancient_ship(ctx, x, y, s, t, tilt=0.0, sail=1.0, a=1.0):
    """antikes Segelschiff mit Planken, Rah, Rigg und Steuerruder"""
    ctx.save(); ctx.translate(x, y); ctx.rotate(tilt); ctx.scale(s, s)
    hull = [(-150, -14), (-128, -34), (-120, -52), (-112, -30), (-96, -16),
            (96, -16), (112, -32), (124, -56), (132, -34), (150, -12),
            (118, 30), (56, 46), (-56, 46), (-118, 30)]
    ink(ctx, hull, 1.0, 5, 0.92 * a, close=True, fill=(P['p1'], 0.9 * a), amp=0.9)
    src(ctx, P['ink'], 0.3 * a); ctx.set_line_width(2.2)
    for k in range(3):
        yy = -2 + k * 13
        ctx.move_to(-132 + k * 10, yy); ctx.curve_to(-40, yy + 10 + k * 2, 40, yy + 10 + k * 2, 132 - k * 10, yy)
        ctx.stroke()
    ink(ctx, [(-146, -14), (0, -22), (146, -12)], 1.0, 3.4, 0.6 * a, amp=0.8)
    # Ruder
    ink(ctx, [(-120, 6), (-168, 34), (-178, 56)], 1.0, 4.4, 0.85 * a, amp=0.8)
    ink(ctx, [(-166, 40), (-186, 62), (-170, 70), (-156, 50)], 1.0, 3.4, 0.8 * a, close=True,
        fill=(P['p3'], 0.8 * a), amp=0.8)
    # Mast, Rah, Segel
    ink(ctx, [(0, -18), (0, -190)], 1.0, 6, 0.9 * a, curve=False, amp=0.8)
    if sail > 0.02:
        yard_w = 104 * sail
        ink(ctx, [(-yard_w, -168), (0, -174), (yard_w, -168)], 1.0, 4.6, 0.9 * a, amp=0.8)
        bel = math.sin(t * 1.1) * 9 + 14
        sailpts = [(-yard_w + 4, -166)]
        for k in range(9):
            u = k / 8
            sailpts.append((-yard_w + 4 + (2 * yard_w - 8) * u, -166 + 96 * math.sin(u * PI) * 0.18 + 2))
        sailpts.append((yard_w - 4, -166))
        for k in range(9):
            u = 1 - k / 8
            sailpts.append((-yard_w + 4 + (2 * yard_w - 8) * u, -74 + bel * math.sin(u * PI)))
        ink(ctx, sailpts, 1.0, 4.2, 0.9 * a, close=True, fill=(P['p1'], 0.95 * a), amp=0.8)
        src(ctx, P['ink'], 0.25 * a); ctx.set_line_width(2)
        for k in range(1, 4):
            u = k / 4
            xx = -yard_w + 4 + (2 * yard_w - 8) * u
            ctx.move_to(xx, -160); ctx.curve_to(xx + 4, -126, xx - 4, -102, xx, -78 + bel * 0.6); ctx.stroke()
    # Rigg
    src(ctx, P['ink'], 0.5 * a); ctx.set_line_width(2.2)
    for ex in (-132, -70, 70, 132):
        ctx.move_to(0, -186); ctx.line_to(ex, -16); ctx.stroke()
    src(ctx, P['acc'], 0.85 * a); circle(ctx, 0, -194, 5); ctx.fill()
    ctx.restore()

# ---------------- Wasser ----------------
def water(ctx, t, y0, amp=18, layers=4, a=0.5, spd=1.1, crest=False):
    for k in range(layers):
        yy = y0 + k * 46
        pts = []
        x = 60
        while x < W - 50:
            pts.append((x, yy + math.sin(x * 0.0062 + t * (spd + k * 0.3) + k * 1.1) * amp
                        + math.sin(x * 0.015 + t * (spd * 1.7)) * amp * 0.3))
            x += 42
        ink(ctx, pts, 1.0, 3.6 - k * 0.3, a * (0.55 + 0.15 * k), c=P['sea'], amp=0.9)
        if crest and k >= layers - 2:
            r = rnd(60 + k)
            for i in range(7):
                px = 140 + i * 250 + math.sin(t * 1.3 + i) * 40
                py = yy + math.sin(px * 0.0062 + t * (spd + k * 0.3) + k * 1.1) * amp
                ink(ctx, [(px - 26, py + 6), (px - 6, py - 16), (px + 20, py - 4), (px + 10, py + 8)],
                    1.0, 3, a * 0.8, c=P['sea'], amp=1.2)

def bigwave(ctx, t, base, rise, a=0.75):
    """grosse Welle, die aufsteigt und sich kraeuselt"""
    h = 90 + 240 * rise
    x0 = 60
    pts = [(x0, H + 40)]
    x = x0
    while x < W - 40:
        u = (x - x0) / (W - 100)
        yy = base - h * math.sin(u * PI) ** 2.2 + math.sin(x * 0.009 + t * 2.4) * 16
        pts.append((x, yy))
        x += 46
    pts.append((W - 40, H + 40))
    ink(ctx, pts, 1.0, 5.0, a, c=P['sea'], close=True, fill=(P['sea'], 0.22), amp=1.2)
    # Kamm
    cx = W / 2 + math.sin(t * 1.1) * 160
    cy = base - h + math.sin(cx * 0.009 + t * 2.4) * 16
    ink(ctx, [(cx - 120, cy + 26), (cx - 50, cy - 34), (cx + 40, cy - 16), (cx + 16, cy + 18)],
        1.0, 4, a, c=P['sea'], amp=1.4)
    r = rnd(77)
    for i in range(22):
        src(ctx, P['sea'], a * 0.5 * r.uniform(0.3, 1))
        circle(ctx, cx + r.uniform(-200, 200), cy - r.uniform(0, 90) - math.sin(t * 3 + i) * 10,
               r.uniform(2, 5.5)); ctx.fill()

def rain(ctx, t, n=80, a=0.35):
    src(ctx, P['sea'], a); ctx.set_line_width(2.2)
    r = rnd(31)
    for i in range(n):
        x = (r.uniform(80, W) + t * 300) % (W - 140) + 80
        y = (r.uniform(90, 940) + t * 1100) % 860 + 90
        ctx.move_to(x, y); ctx.line_to(x - 18, y + 48); ctx.stroke()

def lightning(ctx, t, seed=0, every=2.6):
    for k in range(3):
        ph = (t * 1.6 + k * 0.9) % every
        if ph < 0.2:
            al = 1 - ph / 0.2
            bx = 380 + k * 540
            pts = [(bx, 110)]
            yy = 110
            r = rnd(seed + k * 5)
            while yy < 540:
                yy += 62
                pts.append((bx + r.uniform(-54, 54), yy))
            ink(ctx, pts, 1.0, 6, 0.95 * al, c=P['acc'], curve=False, amp=0)
            src(ctx, P['acc'], 0.12 * al); ctx.rectangle(-80, -80, W + 160, H + 160); ctx.fill()

# ---------------- Szenen ----------------
def sc0(ctx, t, lt, dl):
    """Ein Prophet verlaesst sein Volk"""
    push = 1.0 + 0.06 * clamp(lt / dl)
    walk = sm(clamp((lt - 2.0) / (dl - 1.9)))
    cam(ctx, t, push, -walk * 90, 0)
    mountains(ctx, t, 560, 150, 0.55, seed=9, layers=2)
    ziggurat(ctx, 300, 700, 0.85, clamp(lt / 1.2))
    for k, (bx, bw, bh) in enumerate(((520, 150, 118), (690, 120, 92), (840, 170, 140),
                                      (1040, 130, 100), (1210, 160, 126))):
        if clamp(lt * 3 - k * 0.5) > 0.2:
            mudhouse(ctx, bx, 706, bw, bh * clamp(lt * 2 - k * 0.3), t, seed=k + 2)
    palm(ctx, 470, 706, 150, t, 1); palm(ctx, 1400, 710, 170, t, 2)
    ink(ctx, [(60, 712), (520, 704), (1100, 710), (W - 60, 702)], 1.0, 5, 0.6, amp=1.0)
    src(ctx, P['p3'], 0.45); ctx.rectangle(0, 712, W, H - 712); ctx.fill()
    # Volk im Halbkreis um ihn, mehrere zeigen auf ihn
    cx0 = 880
    crowd = [(-430, 0.74, 1, 772), (-320, 0.82, 1, 800), (-215, 0.92, 1, 832),
             (-120, 1.0, 1, 866), (160, 1.0, -1, 866), (250, 0.92, -1, 832),
             (355, 0.82, -1, 800), (460, 0.74, -1, 772), (-50, 0.68, 1, 752), (95, 0.68, -1, 752)]
    order = sorted(crowd, key=lambda c: c[3])
    for i, (dx, sc, fa, dy) in enumerate(order):
        pose = 'point' if (lt > 0.8 and i % 2 == 1) else 'stand'
        fig(ctx, cx0 + dx, dy, 1.02 * sc, t, pose=pose, facing=fa, ph=i * 1.3, a=0.95)
    # Yunus, vorne und groesser
    yx = cx0 + 20 + walk * 700
    fig(ctx, yx, 968, 1.5, t, pose='walk' if walk > 0.02 else 'stand', facing=1, light=True, ph=0.4)
    label(ctx, t, 1.3, SC[1], 'NINIVE', x=250, y=760, size=36, col=C(P['ink'], 0.85))

def sc1(ctx, t, lt, dl):
    """Yunus steigt auf ein Schiff"""
    u = sm(clamp(lt / (dl * 0.62)))
    cam(ctx, t, 1.04 + 0.05 * u, -u * 70, 0)
    mountains(ctx, t, 520, 120, 0.4, seed=15, layers=1)
    water(ctx, t, 600, 14, 4, 0.45, 1.0)
    quay(ctx, t, 790)
    palm(ctx, 120, 790, 160, t, 5)
    ancient_ship(ctx, 1320, 716, 1.35, t, tilt=math.sin(t * 1.4) * 0.035, sail=clamp((lt - 1.1) / 1.0))
    # Steg
    ink(ctx, [(980, 782), (1110, 740), (1180, 706)], 1.0, 6, 0.8, amp=0.9)
    yx = lerp(300, 1150, u)
    yy = 790 - max(0.0, (yx - 980) / 200.0) * 76
    fig(ctx, yx, yy, 1.45, t, pose='walk', facing=1, light=True, ph=0.2)
    if lt > dl * 0.72:
        a = clamp((lt - dl * 0.72) / 0.5)
        src(ctx, P['sea'], 0.5 * a)
        for k in range(10):
            circle(ctx, 1180 + k * 26, 762 + math.sin(t * 3 + k) * 6, 4); ctx.fill()

def sc2(ctx, t, lt, dl):
    """Mitten auf dem Meer kommt der Sturm"""
    rise = clamp(lt / (dl * 0.8))
    shake = rise * 9
    cam(ctx, t, 1.05 + 0.04 * rise, math.sin(t * 11) * shake, math.cos(t * 9) * shake * 0.7)
    src(ctx, P['dark'], 0.22 * rise); ctx.rectangle(-80, -80, W + 160, H + 160); ctx.fill()
    rain(ctx, t, int(40 + 70 * rise), 0.3 + 0.1 * rise)
    lightning(ctx, t, 3)
    water(ctx, t, 470, 20 + 24 * rise, 3, 0.45, 1.8)
    ancient_ship(ctx, 940 + math.sin(t * 1.5) * 90, 650 + math.sin(t * 2.2) * 44, 1.2, t,
                 tilt=math.sin(t * 2.0) * 0.3, sail=max(0.15, 1 - rise * 0.6))
    bigwave(ctx, t, 940 - 120 * rise, rise, 0.8)
    label(ctx, t, SC[2] + 0.25, SC[3] - 0.1, 'DER STURM', y=206, size=54, col=C(P['acc'], 0.95))

def sc3(ctx, t, lt, dl):
    """Das Los faellt auf ihn, dreimal"""
    seg = dl / 3.0
    k = min(2, int(lt / seg))
    u = (lt - k * seg) / seg
    zoom = 1.0 + 1.5 * math.exp(-((u - 0.45) ** 2) / 0.045)
    cam(ctx, t, zoom, 0, -60 * (zoom - 1))
    water(ctx, t, 520, 26, 3, 0.4, 1.6)
    ancient_ship(ctx, 960, 706, 1.15, t, tilt=math.sin(t * 1.8) * 0.16, sail=0.35)
    # drei Lose auf dem Deck
    for j in range(3):
        drawn = j < k or (j == k and u > 0.35)
        lx = 820 + j * 140
        ly = 648 - (26 if drawn else 0)
        ink(ctx, [(lx, ly - 46), (lx + (3 if drawn else 0), ly + 40)], 1.0, 9,
            0.9, c=P['acc'] if drawn else P['ink'], curve=False, amp=0.9)
        if drawn:
            src(ctx, P['acc'], 0.3); circle(ctx, lx, ly, 26); ctx.fill()
    # Nahaufnahme des gezogenen Loses mit Namen
    if u > 0.3:
        a = clamp((u - 0.3) / 0.2) * clamp((1.0 - u) / 0.25)
        bx, by = 960, 420
        ink(ctx, [(bx - 150, by - 54), (bx + 150, by - 60), (bx + 152, by + 54), (bx - 148, by + 58),
                  (bx - 150, by - 54)], 1.0, 5, 0.9 * a, close=True, fill=(P['p1'], 0.95 * a), amp=1.2)
        set_font(ctx, 54, 'Cinzel')
        ww = text_w(ctx, 'YUNUS')
        outlined(ctx, 'YUNUS', bx - ww / 2, by + 18, fill=C(P['ink'], a), sw=7)
        s2c.star8(ctx, bx - 178, by, 16, P['acc'], 0.85 * a, rot=t * 0.3)
        s2c.star8(ctx, bx + 178, by, 16, P['acc'], 0.85 * a, rot=-t * 0.3)
        set_font(ctx, 30, 'Lora')
        s_ = ['Das erste Los', 'Das zweite Los', 'Das dritte Los'][k]
        w2 = text_w(ctx, s_)
        outlined(ctx, s_, bx - w2 / 2, by - 86, fill=C(P['acc'], a), sw=5)
    label(ctx, t, SC[3] + 0.2, SC[4] - 0.1, 'DREIMAL', y=200, size=50, col=C(P['ink'], 0.9))

def sc4(ctx, t, lt, dl):
    """Sie werfen ihn ins Wasser"""
    fall = clamp((lt - 0.55) / 0.75)
    cam(ctx, t, 1.8 - 0.5 * fall, 0, -180 + 240 * fall)
    # Nahaufnahme Bootsrand
    rail = [(-200, 640), (240, 596), (760, 580), (1280, 598), (1760, 644), (2000, 690)]
    water(ctx, t, 700, 26, 3, 0.45, 1.7)
    ink(ctx, rail + [(2000, 1200), (-200, 1200)], 1.0, 6, 0.9, close=True, fill=(P['p1'], 0.9), amp=1.0)
    src(ctx, P['ink'], 0.28); ctx.set_line_width(2.4)
    for k in range(4):
        ctx.move_to(-180, 600 + k * 40); ctx.curve_to(600, 572 + k * 40, 1200, 576 + k * 40, 1960, 620 + k * 40)
        ctx.stroke()
    # zwei Haende/Figuren am Rand
    for i, px in enumerate((620, 1320)):
        fig(ctx, px, 600, 1.7, t, pose='point', facing=1 if i == 0 else -1, ph=i * 2.0, a=0.95)
    # Yunus faellt
    yx = 960 + fall * 50
    yy = 540 + fall * 520
    rot = fall * 0.5
    ctx.save(); ctx.translate(yx, yy); ctx.rotate(rot); ctx.translate(-yx, -yy)
    fig(ctx, yx, yy, 1.8 - 0.45 * fall, t, pose='raise', facing=1, light=True, ph=0.9)
    ctx.restore()
    if fall > 0.85:
        a = clamp((fall - 0.85) / 0.15)
        for k in range(18):
            ang = PI + k * PI / 17
            r_ = (fall - 0.85) * 1400
            src(ctx, P['sea'], 0.6 * a)
            circle(ctx, 960 + math.cos(ang) * r_, 990 + math.sin(ang) * r_ * 0.35, 8); ctx.fill()

def sc5(ctx, t, lt, dl):
    """Und dann verschluckt ihn ein Fisch"""
    p = sm(clamp(lt / (dl * 0.75)))
    punch = 1 + 0.08 * math.exp(-((lt - dl * 0.72) ** 2) / 0.05)
    cam(ctx, t, (1.02 + 0.08 * p) * punch, -p * 40, 0)
    src(ctx, P['dark'], 0.3 + 0.35 * p); ctx.rectangle(-80, -80, W + 160, H + 160); ctx.fill()
    water(ctx, t, 180, 14, 2, 0.3, 1.2)
    for i in range(26):
        r = rnd(90 + i)
        bx = r.uniform(140, W - 140)
        by = (r.uniform(0, 900) - t * r.uniform(50, 110)) % 900 + 150
        src(ctx, P['sea'], 0.3); circle(ctx, bx, by, r.uniform(3, 8)); ctx.fill()
    # sinkende Figur
    fy = 420 + p * 180
    fig(ctx, 1240 - p * 130, fy, 1.25 - 0.25 * p, t, pose='raise', light=True, ph=1.4, a=1 - 0.5 * p)
    # Fisch kommt aus der Tiefe
    fx = lerp(-700, 820, p)
    mouth = clamp((lt - dl * 0.55) / 0.5)
    ctx.save(); ctx.translate(fx, 620); ctx.scale(1.15, 1.15)
    body = []
    for k in range(34):
        u = k / 33
        body.append((-380 + 780 * u, -190 * math.sin(u * PI) ** 0.75))
    for k in range(34):
        u = 1 - k / 33
        body.append((-380 + 780 * u, 190 * math.sin(u * PI) ** 0.75))
    ink(ctx, body, 1.0, 7, 0.95, c=P['p1'], close=True, fill=(P['p3'], 0.5), amp=1.1)
    ink(ctx, [(-380, 0), (-520, -130), (-468, 0), (-520, 130), (-380, 0)], 1.0, 6, 0.9, c=P['p1'],
        fill=(P['p3'], 0.42), amp=1.1)
    src(ctx, P['ink'], 0.45); ctx.set_line_width(2.8)
    for k in range(6):
        xx = -230 + k * 96
        ctx.move_to(xx, -130); ctx.curve_to(xx + 26, -40, xx - 26, 40, xx, 130); ctx.stroke()
    src(ctx, P['acc'], 0.9); circle(ctx, 276, -62, 12); ctx.fill()
    src(ctx, P['dark'], 0.9 * mouth)
    ctx.move_to(392, -24); ctx.curve_to(300, 40 * mouth, 286, 130 * mouth, 352, 166 * mouth)
    ctx.curve_to(406, 128 * mouth, 414, 40 * mouth, 392, -24); ctx.close_path(); ctx.fill()
    ctx.restore()

def sc6(ctx, t, lt, dl):
    """Dunkelheit ueber Dunkelheit ueber Dunkelheit"""
    cam(ctx, t, 1.02 + lt * 0.006)
    src(ctx, P['dark'], clamp(lt / 1.2)); ctx.rectangle(-80, -80, W + 160, H + 160); ctx.fill()
    words = ['DAS MEER', 'DER FISCH', 'DIE NACHT']
    for k in range(3):
        a = clamp((lt - 0.5 - k * 1.3) / 0.9)
        if a <= 0: continue
        rr = 470 - k * 130 + math.sin(t * 0.9 + k) * 10
        arc = []
        for j in range(34):
            ang = -PI * 0.92 + j * (PI * 1.84) / 33
            arc.append((960 + math.cos(ang) * rr * 1.5, 560 + math.sin(ang) * rr))
        ink(ctx, arc, 1.0, 4, 0.5 * a, c=P['acc'], amp=2.0)
        src(ctx, P['dark'], 0.4 * a)
        ctx.move_to(*arc[0])
        for pnt in arc[1:]: ctx.line_to(*pnt)
        ctx.close_path(); ctx.fill()
        set_font(ctx, 30, 'Cinzel')
        ww = text_w(ctx, words[k])
        outlined(ctx, words[k], 960 - ww / 2, 560 - rr + 54, fill=C(P['acc'], 0.9 * a), sw=5)
    fig(ctx, 960, 800, 1.15, t, pose='kneel', light=True, a=0.5 + 0.3 * math.sin(t * 1.2))

def sc7(ctx, t, lt, dl):
    """Das Meer, der Bauch des Fisches, die Nacht"""
    cam(ctx, t, 1.02)
    src(ctx, P['dark'], 1.0); ctx.rectangle(-80, -80, W + 160, H + 160); ctx.fill()
    # Rippen im Bauch
    for k in range(7):
        a = clamp((lt - k * 0.12) / 0.4) * 0.5
        xx = 220 + k * 250
        ink(ctx, [(xx, 180), (xx - 60, 540), (xx, 900)], 1.0, 4, a, c=P['acc'], amp=1.6)
    names = ['DAS MEER', 'DER BAUCH', 'DIE NACHT']
    for k in range(3):
        a = clamp((lt - k * 0.5) / 0.4)
        if a <= 0: continue
        rr = 400 - k * 120 + math.sin(t * 1.2 + k) * 7
        src(ctx, P['acc'], 0.45 * a); ctx.set_line_width(3.5)
        circle(ctx, 960, 520, rr); ctx.stroke()
        set_font(ctx, 32, 'Cinzel')
        ww = text_w(ctx, names[k])
        outlined(ctx, names[k], 960 - ww / 2, 520 - rr + 46, fill=C(P['acc'], 0.95 * a), sw=5)
    fig(ctx, 960, 820, 1.2, t, pose='kneel', light=True, a=0.75)

def sc8(ctx, t, lt, dl):
    """das Bittgebet"""
    k = ramp(t, SC[8] + 0.2, SC[8] + 2.8)
    cam(ctx, t, 1.02 + 0.05 * k)
    src(ctx, P['dark'], 1.0); ctx.rectangle(-80, -80, W + 160, H + 160); ctx.fill()
    for j in range(7):
        xx = 220 + j * 250
        ink(ctx, [(xx, 180), (xx - 60, 540), (xx, 900)], 1.0, 4, 0.25, c=P['acc'], amp=1.6)
    s2c.medallion(ctx, t, 0.05 + 0.05 * k)
    g = cairo.RadialGradient(960, 560, 6, 960, 560, 800 * (0.3 + k))
    ar, ag, ab = C(P['acc'])[:3]
    g.add_color_stop_rgba(0, 1, 0.97, 0.86, 0.85 * k)
    g.add_color_stop_rgba(0.22, ar, ag, ab, 0.4 * k)
    g.add_color_stop_rgba(1, ar, ag, ab, 0)
    ctx.set_source(g); ctx.rectangle(-80, -80, W + 160, H + 160); ctx.fill()
    fig(ctx, 960, 860, 1.7, t, pose='raise', light=True, a=1.0)
    if lt > 1.8:
        a = clamp((lt - 1.8) / 0.8) * clamp((dl - lt) / 0.8)
        set_font(ctx, 40, 'Lora')
        for j, line in enumerate(['Es gibt keinen Gott ausser Dir,', 'erhaben bist Du,',
                                  'ich gehörte zu den Ungerechten.']):
            ww = text_w(ctx, line)
            outlined(ctx, line, 960 - ww / 2, 270 + j * 52, fill=(1, 0.98, 0.92, a), sw=7)

def sc9(ctx, t, lt, dl):
    """Wir erhoerten ihn und erretteten ihn"""
    op = clamp(lt / 1.8)
    cam(ctx, t, 1.03 - 0.02 * op, op * 20, 0)
    src(ctx, P['dark'], max(0.0, 1 - op)); ctx.rectangle(-80, -80, W + 160, H + 160); ctx.fill()
    if op > 0.02:
        ctx.push_group()
        mountains(ctx, t, 560, 130, 0.5, seed=21, layers=2)
        water(ctx, t, 700, 16, 4, 0.45, 1.0)
        ink(ctx, [(60, 880), (560, 858), (1200, 868), (W - 60, 850)], 1.0, 5, 0.7, amp=1.0)
        src(ctx, P['p3'], 0.5); ctx.rectangle(0, 876, W, H - 876); ctx.fill()
        fig(ctx, 740, 966, 1.45, t, pose='kneel', light=True, ph=0.3)
        ctx.pop_group_to_source(); ctx.paint_with_alpha(op)
    g = cairo.RadialGradient(1480, 300, 20, 1480, 300, 760)
    ar, ag, ab = C(P['acc'])[:3]
    g.add_color_stop_rgba(0, 1, 0.95, 0.8, 0.5 * op); g.add_color_stop_rgba(1, ar, ag, ab, 0)
    ctx.set_source(g); ctx.rectangle(-80, -80, W + 160, H + 160); ctx.fill()
    if lt > 1.4:
        a = clamp((lt - 1.4) / 0.7) * clamp((dl - lt) / 0.7)
        set_font(ctx, 40, 'Lora')
        for j, line in enumerate(['Wir erhörten ihn und erretteten ihn aus der Bedrängnis.',
                                  'Und so erretten Wir die Gläubigen.']):
            ww = text_w(ctx, line)
            outlined(ctx, line, 960 - ww / 2, 250 + j * 54, fill=C(P['ink'], a), sw=7)
        set_font(ctx, 28, 'Montserrat')
        s_ = 'Sure Al Anbiya 21:88'
        ww = text_w(ctx, s_)
        outlined(ctx, s_, 960 - ww / 2, 356, fill=C(P['acc'], a), sw=5)

def sc10(ctx, t, lt, dl):
    """Und so erretten Wir die Glaeubigen"""
    cam(ctx, t, 1.02 + lt * 0.004, 0, 0)
    mountains(ctx, t, 560, 130, 0.5, seed=21, layers=2)
    water(ctx, t, 700, 14, 4, 0.4, 0.9)
    ink(ctx, [(60, 880), (560, 858), (1200, 868), (W - 60, 850)], 1.0, 5, 0.7, amp=1.0)
    src(ctx, P['p3'], 0.5); ctx.rectangle(0, 876, W, H - 876); ctx.fill()
    g = cairo.RadialGradient(1460, 270, 20, 1460, 270, 820)
    ar, ag, ab = C(P['acc'])[:3]
    g.add_color_stop_rgba(0, 1, 0.95, 0.8, 0.55); g.add_color_stop_rgba(1, ar, ag, ab, 0)
    ctx.set_source(g); ctx.rectangle(-80, -80, W + 160, H + 160); ctx.fill()
    fig(ctx, 680, 966, 1.5, t, pose='stand', light=True, ph=0.3)
    # Kuerbispflanze waechst
    p = clamp(lt / 1.8)
    ink(ctx, [(1180, 950), (1172, 892), (1192, 846), (1186, 800)], p, 7, 0.9, c=P['leaf'], amp=1.2)
    for k in range(6):
        a = clamp((lt - 0.5 - k * 0.16) / 0.35)
        if a <= 0: continue
        ctx.save(); ctx.translate(1186, 804); ctx.rotate(-PI / 2 + (k - 2.5) * 0.44 + math.sin(t * 1.3 + k) * 0.05)
        src(ctx, P['leaf'], 0.8 * a); ellipse(ctx, 64, 0, 64, 17); ctx.fill()
        src(ctx, P['ink'], 0.45 * a); ctx.set_line_width(2.4); ellipse(ctx, 64, 0, 64, 17); ctx.stroke()
        ctx.restore()

SCENES = [sc0, sc1, sc2, sc3, sc4, sc5, sc6, sc7, sc8, sc9, sc10]

def _draw(ctx, i, t):
    lt = t - SC[i]
    dl = SC[i + 1] - SC[i]
    ctx.save(); SCENES[i](ctx, t, lt, dl); ctx.restore()

def frame(ctx, t):
    s2b.TNOW[0] = t
    i, lt, dl = scene_at(t)
    dark = 6 <= i <= 8
    s2c.P = P
    s2b.paper(ctx, t)
    if not dark: s2c.medallion(ctx, t, 0.075)
    if lt < XF and i > 0:
        _draw(ctx, i - 1, t)
        ctx.push_group(); _draw(ctx, i, t)
        ctx.pop_group_to_source(); ctx.paint_with_alpha(eo(lt / XF))
    else:
        _draw(ctx, i, t)
    if dark: s2c.medallion(ctx, t, 0.05)
    s2c.ambience(ctx, t, i)
    if not dark:
        s2c.motif_band(ctx, t, 128, 0.24)
        s2c.motif_band(ctx, t, H - 128, 0.24)
    s2c.ornate_border(ctx, t)
    if 0.3 <= t <= 4.4:
        a = eo((t - 0.3) / 0.5) * clamp((4.4 - t) / 0.4)
        s2c.cartouche(ctx, W / 2, 250, 520, 60, t, a)
        set_font(ctx, 92, 'Cinzel')
        ww = text_w(ctx, 'YUNUS')
        outlined(ctx, 'YUNUS', W / 2 - ww / 2, 270, fill=C(P['ink'], a), sw=10)
        set_font(ctx, 32, 'Lora')
        w2 = text_w(ctx, T['sub'])
        outlined(ctx, T['sub'], W / 2 - w2 / 2, 334, fill=C(P['acc'], a), sw=6)
    draw_subs(ctx, t, size=44, face='Lora',
              col=(1, 0.99, 0.95) if dark else C(P['ink'])[:3], y=992)
    endcard(ctx, t, AUD + 0.5, 'Yunus alayhi salam')
