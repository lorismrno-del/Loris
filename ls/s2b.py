"""Stil 2 ausgebaut: gezeichnete Doku, durchgehende Bewegung, Bild pro Satz, mehrere Farbwelten."""
from base import *

PALS = {
 'sepia':    dict(p1='#efe4cb', p2='#e3d4b2', p3='#d0bc92', ink='#2a2118', acc='#b8862a',
                  sea='#4a6a7a', dark='#1a1510', sky='#c9b183', leaf='#6a7a3a'),
 'marine':   dict(p1='#12304a', p2='#0e2639', p3='#081a28', ink='#dce9f2', acc='#f0b957',
                  sea='#7fb8d8', dark='#04101b', sky='#1b4663', leaf='#6fc09a'),
 'nacht':    dict(p1='#1c1813', p2='#15120e', p3='#0d0b08', ink='#ecdcb6', acc='#d8a23a',
                  sea='#9a8a62', dark='#070503', sky='#2a2318', leaf='#8a9a4a'),
 'oliv':     dict(p1='#e2e6cb', p2='#d2d8b4', p3='#bcc498', ink='#22301c', acc='#8a6a1e',
                  sea='#4a7a6a', dark='#141c11', sky='#b9c493', leaf='#3f6a2a'),
 'terrakotta':dict(p1='#f2e0cb', p2='#e8cfb2', p3='#d8b893', ink='#3a1f14', acc='#b4502a',
                  sea='#8a6450', dark='#1e100a', sky='#ddb48c', leaf='#6a7a3a'),
}
P = PALS[os.environ.get('PAL', 'sepia')]
STYLE_NAME = os.environ.get('PALNAME', 'Sepia')

# Szenengrenzen, pro Satz
SC = [0.0, S[1] - 0.40, S[2] - 0.30, S[3] - 0.25, S[4] - 0.25, S[5] - 0.25,
      S[6] - 0.30, S[7] - 0.20, S[8] - 0.30, S[9] - 0.30, S[10] - 0.25, DUR]

def scene_at(t):
    for i in range(len(SC) - 1):
        if SC[i] <= t < SC[i + 1]:
            return i, t - SC[i], SC[i + 1] - SC[i]
    return len(SC) - 2, t - SC[-2], SC[-1] - SC[-2]

# ---------- Grundlagen ----------
def paper(ctx, t):
    ctx.set_source(lingrad(0, 0, W, H, [(0, P['p1']), (0.5, P['p2']), (1, P['p3'])]))
    ctx.rectangle(-80, -80, W + 160, H + 160); ctx.fill()
    r = rnd(7)
    for i in range(70):
        src(ctx, P['p3'], r.uniform(0.05, 0.16))
        ellipse(ctx, r.uniform(0, W), r.uniform(0, H), r.uniform(50, 240), r.uniform(30, 160)); ctx.fill()
    # lebende Faser
    r2 = rnd(13)
    for i in range(26):
        x = (r2.uniform(0, W) + math.sin(t * 0.3 + i) * 14) % W
        y = r2.uniform(0, H) + math.cos(t * 0.25 + i) * 10
        src(ctx, P['ink'], 0.05)
        ctx.set_line_width(1.6)
        ctx.move_to(x, y); ctx.line_to(x + r2.uniform(-50, 50), y + r2.uniform(-18, 18)); ctx.stroke()

def frame_border(ctx, t):
    src(ctx, P['ink'], 0.55); ctx.set_line_width(5)
    d = math.sin(t * 0.6) * 2
    ctx.rectangle(52 + d, 52 - d, W - 104, H - 104); ctx.stroke()
    src(ctx, P['ink'], 0.22); ctx.set_line_width(2)
    ctx.rectangle(68, 68, W - 136, H - 136); ctx.stroke()
    for cx, cy in ((68, 68), (W - 68, 68), (68, H - 68), (W - 68, H - 68)):
        src(ctx, P['acc'], 0.6); circle(ctx, cx, cy, 7); ctx.fill()

def cam(ctx, t, zx=1.0, px=0.0, py=0.0):
    """leichte Dauerbewegung, nie ein Standbild"""
    z = zx * (1 + 0.012 * math.sin(t * 0.35))
    ctx.translate(W / 2, H / 2); ctx.scale(z, z); ctx.translate(-W / 2, -H / 2)
    ctx.translate(px + math.sin(t * 0.27) * 9, py + math.cos(t * 0.21) * 7)

TNOW = [0.0]

def _wob(pts, amp=1.6):
    t = TNOW[0]
    out = []
    for i, (x, y) in enumerate(pts):
        ph = i * 0.7
        out.append((x + math.sin(t * 1.05 + ph) * amp,
                    y + math.cos(t * 0.87 + ph * 1.3) * amp))
    return out

def _spline(ctx, pts):
    """weiche Kurve durch alle Punkte, keine geraden Teilstuecke"""
    if len(pts) < 3:
        ctx.move_to(*pts[0])
        for p in pts[1:]: ctx.line_to(*p)
        return
    ctx.move_to(*pts[0])
    for i in range(len(pts) - 1):
        p0 = pts[i - 1] if i > 0 else pts[0]
        p1 = pts[i]; p2 = pts[i + 1]
        p3 = pts[i + 2] if i + 2 < len(pts) else pts[-1]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6.0, p1[1] + (p2[1] - p0[1]) / 6.0)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6.0, p2[1] - (p3[1] - p1[1]) / 6.0)
        ctx.curve_to(c1[0], c1[1], c2[0], c2[1], p2[0], p2[1])

def ink(ctx, pts, prog=1.0, lw=6, a=0.9, c=None, close=False, fill=None, curve=True, amp=1.6):
    n = max(2, int(len(pts) * clamp(prog)))
    use = _wob(pts[:n], amp)
    src(ctx, c or P['ink'], a); ctx.set_line_width(lw)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    if curve: _spline(ctx, use)
    else:
        ctx.move_to(*use[0])
        for p in use[1:]: ctx.line_to(*p)
    if close and prog > 0.99: ctx.close_path()
    if fill is not None and prog > 0.99:
        ctx.close_path(); src(ctx, fill[0], fill[1]); ctx.fill_preserve(); src(ctx, c or P['ink'], a)
    ctx.stroke()

def curve_pts(p0, p1, p2, n=48):
    """quadratische Kurve als Punktliste, fuer Wege"""
    out = []
    for k in range(n + 1):
        u = k / n
        x = (1 - u) ** 2 * p0[0] + 2 * (1 - u) * u * p1[0] + u * u * p2[0]
        y = (1 - u) ** 2 * p0[1] + 2 * (1 - u) * u * p1[1] + u * u * p2[1]
        out.append((x, y))
    return out

def along(pts, u):
    u = clamp(u) * (len(pts) - 1)
    i = int(u); f = u - i
    j = min(i + 1, len(pts) - 1)
    return (lerp(pts[i][0], pts[j][0], f), lerp(pts[i][1], pts[j][1], f))

def hatch(ctx, t, y0, y1, a=0.5, step=26, spd=1.4):
    src(ctx, P['sea'], a); ctx.set_line_width(2.6)
    k = 0
    y = y0
    while y < y1:
        ctx.move_to(170, y)
        x = 170
        while x < W - 150:
            ctx.line_to(x, y + math.sin(x * 0.018 + t * spd + k * 0.8) * 6)
            x += 22
        ctx.stroke(); y += step; k += 1

def seaswell(ctx, t, y0, amp, a=0.55, spd=1.2, layers=3):
    for k in range(layers):
        yy = y0 + k * 58
        src(ctx, P['sea'], a * (0.4 + 0.25 * k)); ctx.set_line_width(4)
        ctx.move_to(120, yy)
        x = 120
        while x < W - 110:
            ctx.line_to(x, yy + math.sin(x * 0.0075 + t * (spd + k * 0.35) + k) * amp)
            x += 20
        ctx.stroke()

def dots(ctx, t, n=26, a=0.25, seed=21):
    r = rnd(seed)
    for i in range(n):
        x = (r.uniform(120, W - 120) + t * r.uniform(4, 16)) % (W - 240) + 120
        y = r.uniform(120, H - 160) + math.sin(t * 0.8 + i) * 16
        src(ctx, P['ink'], a * (0.3 + 0.7 * abs(math.sin(t * 0.9 + i))))
        circle(ctx, x, y, r.uniform(1.6, 3.6)); ctx.fill()

def coastline(ctx, prog, t, seed=3):
    pts = []
    r = rnd(seed)
    for k in range(64):
        x = 130 + k * 26
        y = 700 + math.sin(k * 0.33) * 62 + math.sin(k * 0.1) * 110 + r.uniform(-6, 6) + math.sin(t * 0.5 + k * 0.2) * 3
        pts.append((x, y))
    ink(ctx, pts, prog, 6, 0.85)
    if prog > 0.98:
        ctx.move_to(pts[0][0], H)
        for p in pts: ctx.line_to(*p)
        ctx.line_to(pts[-1][0], H); ctx.close_path()
        src(ctx, P['p3'], 0.75); ctx.fill()
        src(ctx, P['ink'], 0.18); ctx.set_line_width(2)
        for k in range(8):
            yy = 780 + k * 36
            ctx.move_to(150, yy); ctx.line_to(W - 150, yy + 14); ctx.stroke()

def city(ctx, x, y, prog, t, n=8):
    r = rnd(5)
    for k in range(n):
        p = clamp(prog * n - k)
        if p <= 0: continue
        bw = 58 + (k % 3) * 20; bh = (90 + (k % 4) * 60) * p
        bx = x + k * 78 - 300
        ink(ctx, [(bx, y), (bx, y - bh), (bx + bw, y - bh), (bx + bw, y)], 1.0, 5, 0.85, curve=False, amp=1.1)
        if k % 2 == 0 and p > 0.9:
            ink(ctx, [(bx + bw * 0.5, y - bh), (bx + bw * 0.5, y - bh - 46)], 1.0, 4, 0.7, curve=False, amp=1.0)
            src(ctx, P['acc'], 0.8); circle(ctx, bx + bw * 0.5, y - bh - 52, 6); ctx.fill()

def ship(ctx, x, y, s, t, tilt=0.0, sail=1.0):
    ctx.save(); ctx.translate(x, y); ctx.rotate(tilt + math.sin(t * 2.1) * 0.05); ctx.scale(s, s)
    ink(ctx, [(-66, 0), (66, 0), (48, 30), (-48, 30)], 1.0, 5, 0.9, close=True, fill=(P['p3'], 0.9), curve=False, amp=0.8)
    ink(ctx, [(0, 0), (0, -82)], 1.0, 5, 0.9, curve=False, amp=0.8)
    if sail > 0:
        ink(ctx, [(5, -78), (58 * sail, -26), (5, -26)], 1.0, 5, 0.9, close=True, fill=(P['p1'], 0.95), curve=False, amp=0.8)
    src(ctx, P['acc'], 0.9); circle(ctx, 0, -86, 5); ctx.fill()
    ctx.restore()

def compass(ctx, x, y, s, t, a=1.0):
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s); ctx.rotate(math.sin(t * 0.4) * 0.06)
    src(ctx, P['ink'], 0.7 * a); ctx.set_line_width(4); circle(ctx, 0, 0, 48); ctx.stroke()
    for k in range(4):
        ang = k * PI / 2 + t * 0.06
        ctx.move_to(0, 0)
        ctx.line_to(math.cos(ang) * 58, math.sin(ang) * 58)
        ctx.line_to(math.cos(ang + 0.52) * 17, math.sin(ang + 0.52) * 17)
        ctx.close_path()
        src(ctx, P['ink'] if k % 2 == 0 else P['acc'], (0.8 if k % 2 == 0 else 0.7) * a); ctx.fill()
    ctx.restore()

def lot(ctx, x, y, s, t, state=0):
    """Los Staebchen, state 0 liegt, 1 gezogen"""
    ctx.save(); ctx.translate(x, y + (-26 if state else 0)); ctx.rotate(0.12 * (1 if state else 0)); ctx.scale(s, s)
    c = P['acc'] if state else P['ink']
    ink(ctx, [(0, -60), (0, 60)], 1.0, 11, 0.9, c=c, curve=False, amp=0.9)
    if state:
        src(ctx, P['acc'], 0.5); circle(ctx, 0, 0, 34); ctx.fill()
    ctx.restore()

def fish(ctx, x, y, s, t, prog=1.0, mouth=0.0):
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s)
    body = []
    for k in range(40):
        u = k / 39
        body.append((-360 + 760 * u, -170 * math.sin(u * PI) ** 0.8))
    for k in range(40):
        u = 1 - k / 39
        body.append((-360 + 760 * u, 170 * math.sin(u * PI) ** 0.8))
    ink(ctx, body, prog, 7, 0.92, close=True, fill=(P['ink'], 0.14))
    if prog > 0.95:
        ink(ctx, [(-360, 0), (-500, -110), (-452, 0), (-500, 110), (-360, 0)], 1.0, 6, 0.9, fill=(P['ink'], 0.1))
        src(ctx, P['acc'], 0.9); circle(ctx, 270, -52, 11); ctx.fill()
        src(ctx, P['ink'], 0.35); ctx.set_line_width(3)
        for k in range(5):
            ctx.move_to(-180 + k * 90, -120 + (k % 2) * 30)
            ctx.curve_to(-150 + k * 90, -40, -210 + k * 90, 40, -180 + k * 90, 120 - (k % 2) * 30)
            ctx.stroke()
        if mouth > 0:
            src(ctx, P['dark'], 0.85)
            ctx.move_to(360, -10); ctx.curve_to(290, 40 * mouth, 270, 110 * mouth, 330, 140 * mouth)
            ctx.curve_to(380, 110 * mouth, 386, 40 * mouth, 360, -10); ctx.close_path(); ctx.fill()
    ctx.restore()

def darkfill(ctx, a):
    src(ctx, P['dark'], a); ctx.rectangle(-80, -80, W + 160, H + 160); ctx.fill()

def lightburst(ctx, x, y, t, k, big=760):
    g = cairo.RadialGradient(x, y, 6, x, y, big * (0.3 + k))
    ar, ag, ab = C(P['acc'])[:3]
    g.add_color_stop_rgba(0, 1, 0.96, 0.84, 0.9 * k)
    g.add_color_stop_rgba(0.22, ar, ag, ab, 0.45 * k)
    g.add_color_stop_rgba(1, ar, ag, ab, 0)
    ctx.set_source(g); ctx.rectangle(-80, -80, W + 160, H + 160); ctx.fill()
    for i in range(14):
        ang = i * 2 * PI / 14 + t * 0.12
        ctx.save(); ctx.translate(x, y); ctx.rotate(ang)
        gg = cairo.LinearGradient(0, 0, 1500, 0)
        gg.add_color_stop_rgba(0, ar, ag, ab, 0.16 * k); gg.add_color_stop_rgba(1, ar, ag, ab, 0)
        ctx.set_source(gg)
        ctx.move_to(0, -16); ctx.line_to(1500, -110); ctx.line_to(1500, 110); ctx.line_to(0, 16)
        ctx.close_path(); ctx.fill(); ctx.restore()

# ---------- Szenen, eine pro Satz ----------
def sc0(ctx, t, lt, dl):       # Prophet verlaesst sein Volk
    cam(ctx, t, 1.02, -lt * 6, 0)
    coastline(ctx, clamp(lt / 1.8), t)
    city(ctx, 520, 700, clamp((lt - 0.4) / 1.6), t)
    label(ctx, t, SC[0] + 1.6, SC[1], 'NINIVE', x=300, y=790, size=40, col=C(P['ink'], 0.9))
    p = sm(clamp((lt - 2.2) / (dl - 2.0)))
    if p > 0:
        path = curve_pts((620, 752), (980, 620), (1330, 726))
        ink(ctx, path, p, 5, 0.75, c=P['acc'], amp=1.2)
        px, py = along(path, p)
        src(ctx, P['ink'], 0.9); circle(ctx, px, py, 11 + math.sin(t * 3) * 1.2); ctx.fill()
        src(ctx, P['acc'], 0.35); circle(ctx, px, py, 22 + math.sin(t * 3) * 3); ctx.fill()
    compass(ctx, 1660, 260, 1.0, t)
    dots(ctx, t, 20, 0.2)

def sc1(ctx, t, lt, dl):       # steigt auf ein Schiff
    cam(ctx, t, 1.03, -20 - lt * 5, 0)
    coastline(ctx, 1.0, t); hatch(ctx, t, 330, 640, 0.32)
    u = sm(clamp(lt / dl))
    path = curve_pts((430, 648), (840, 548), (1270, 632))
    ink(ctx, path, min(1.0, u + 0.08), 5, 0.6, c=P['acc'], amp=1.2)
    px, py = along(path, u)
    py += math.sin(t * 2.2) * 9
    nx, ny = along(path, min(1.0, u + 0.02))
    ship(ctx, px, py, 1.25, t, tilt=math.atan2(ny - py, max(1e-3, nx - px)) * 0.6)
    compass(ctx, 1660, 260, 1.0, t)
    dots(ctx, t, 22, 0.22)

def sc2(ctx, t, lt, dl):       # der Sturm
    cam(ctx, t, 1.07 + 0.03 * math.sin(t * 3.4), math.sin(t * 9) * 11, math.cos(t * 7.5) * 9)
    src(ctx, P['dark'], 0.3 * clamp(lt / 0.7)); ctx.rectangle(-80, -80, W + 160, H + 160); ctx.fill()
    # Regen
    src(ctx, P['sea'], 0.4); ctx.set_line_width(2.4)
    r = rnd(31)
    for i in range(70):
        x = (r.uniform(100, W) + t * 240) % (W - 120) + 100
        y = (r.uniform(120, 900) + t * 900) % 820 + 120
        ctx.move_to(x, y); ctx.line_to(x - 16, y + 46); ctx.stroke()
    hatch(ctx, t, 300, 660, 0.55, 22, 3.2)
    seaswell(ctx, t, 620, 62, 0.85, 3.0, 5)
    # Blitze
    for k in range(3):
        ph = (t * 1.7 + k * 0.7) % 3.0
        if ph < 0.22:
            a = 1 - ph / 0.22
            bx = 420 + k * 520
            pts = [(bx, 120)]
            yy = 120
            rr = rnd(40 + k)
            while yy < 560:
                yy += 70
                pts.append((bx + rr.uniform(-60, 60), yy))
            src(ctx, P['acc'], 0.95 * a); ctx.set_line_width(7)
            ctx.move_to(*pts[0])
            for p in pts[1:]: ctx.line_to(*p)
            ctx.stroke()
            src(ctx, P['acc'], 0.14 * a); ctx.rectangle(-80, -80, W + 160, H + 160); ctx.fill()
    # Gischt
    for i in range(26):
        a = 0.3 + 0.4 * abs(math.sin(t * 3 + i))
        src(ctx, P['sea'], a * 0.5)
        circle(ctx, 300 + ((i * 137 + t * 160) % 1300), 700 + math.sin(t * 4 + i) * 60, 5); ctx.fill()
    ship(ctx, 960 + math.sin(t * 1.9) * 95, 660 + math.sin(t * 2.8) * 52, 1.5, t, tilt=math.sin(t * 2.6) * 0.34)
    seaswell(ctx, t, 820, 54, 0.8, 3.4, 3)
    label(ctx, t, SC[2] + 0.2, SC[3], 'DER STURM', y=200, size=52, col=C(P['acc'], 0.95))

def sc3(ctx, t, lt, dl):       # das Los faellt dreimal
    cam(ctx, t, 1.04, 0, -lt * 4)
    hatch(ctx, t, 320, 660, 0.4, 26, 2.0)
    seaswell(ctx, t, 690, 24, 0.6, 1.8, 3)
    ship(ctx, 960, 650, 1.2, t, tilt=math.sin(t * 2.2) * 0.16)
    for k in range(3):
        on = lt > 0.5 + k * 0.72
        lot(ctx, 700 + k * 260, 900, 1.3, t, state=1 if on else 0)
        if on:
            set_font(ctx, 46, 'Cinzel')
            s_ = str(k + 1)
            outlined(ctx, s_, 700 + k * 260 - 10, 1010, fill=C(P['acc'], 0.9), sw=6)
    label(ctx, t, SC[3] + 0.3, SC[4], 'DREIMAL', y=210, size=50, col=C(P['ink'], 0.9))

def sc4(ctx, t, lt, dl):       # ins Wasser
    cam(ctx, t, 1.06, 0, lt * 10)
    hatch(ctx, t, 300, 620, 0.45, 26, 2.2)
    seaswell(ctx, t, 640, 30, 0.7, 2.0, 4)
    yy = lerp(360, 840, sm(clamp(lt / 0.85)))
    src(ctx, P['ink'], 0.9); circle(ctx, 960, yy, 13); ctx.fill()
    src(ctx, P['ink'], 0.3); ctx.set_line_width(3)
    ctx.move_to(960, 300); ctx.line_to(960, yy - 18); ctx.stroke()
    if lt > 0.8:
        a = clamp((lt - 0.8) / 0.5)
        for k in range(14):
            ang = PI + k * PI / 13
            r_ = (lt - 0.8) * 420
            src(ctx, P['sea'], 0.7 * a * (1 - clamp((lt - 0.8) / 1.4)))
            circle(ctx, 960 + math.cos(ang) * r_, 850 + math.sin(ang) * r_ * 0.4, 7); ctx.fill()
        src(ctx, P['sea'], 0.5 * a); ctx.set_line_width(4)
        for rr in (60, 130, 210):
            circle(ctx, 960, 852, rr + (lt - 0.8) * 180); ctx.stroke()

def sc5(ctx, t, lt, dl):       # ein Fisch verschluckt ihn
    punch = 1 + 0.05 * math.exp(-((lt - 1.25) ** 2) / 0.09)
    cam(ctx, t, 1.04 * punch, -lt * 8, 0)
    darkfill(ctx, clamp(lt / 2.4) * 0.35)
    hatch(ctx, t, 280, 560, 0.3, 30, 1.6)
    p = clamp(lt / 1.3)
    fish(ctx, lerp(-260, 880, sm(clamp(lt / (dl - 0.1)))), 640, 1.0, t, prog=p,
         mouth=clamp((lt - 1.1) / 0.7))
    if lt < 1.5:
        src(ctx, P['ink'], 0.9 * (1 - clamp((lt - 0.9) / 0.5))); circle(ctx, 1320, 640, 12); ctx.fill()
    seaswell(ctx, t, 900, 26, 0.5, 1.6, 2)

def sc6(ctx, t, lt, dl):       # Dunkelheit ueber Dunkelheit
    cam(ctx, t, 1.03 + lt * 0.004, 0, 0)
    darkfill(ctx, clamp(lt / 1.4))
    words = ['DAS MEER', 'DER FISCH', 'DIE NACHT']
    for k in range(3):
        a = clamp((lt - 0.5 - k * 1.25) / 0.8)
        if a <= 0: continue
        sh = math.sin(t * 0.9 + k) * 8
        w_ = 1180 - k * 300 + sh; h_ = 620 - k * 160 + sh * 0.5
        ink(ctx, [(960 - w_ / 2, 540 - h_ / 2), (960, 540 - h_ / 2 - 10), (960 + w_ / 2, 540 - h_ / 2),
                  (960 + w_ / 2 + 10, 540), (960 + w_ / 2, 540 + h_ / 2), (960, 540 + h_ / 2 + 10),
                  (960 - w_ / 2, 540 + h_ / 2), (960 - w_ / 2 - 10, 540),
                  (960 - w_ / 2, 540 - h_ / 2)], 1.0, 4, 0.55 * a, c=P['acc'], amp=2.2)
        src(ctx, P['dark'], 0.45 * a)
        ctx.rectangle(960 - w_ / 2, 540 - h_ / 2, w_, h_); ctx.fill()
        src(ctx, P['acc'], 0.25 * a); ctx.set_line_width(2)
        for j in range(7):
            yy = 540 - h_ / 2 + (j + 1) * h_ / 8
            ctx.move_to(960 - w_ / 2 + 14, yy)
            ctx.line_to(960 + w_ / 2 - 14, yy + math.sin(t * 1.2 + j + k) * 4); ctx.stroke()
        set_font(ctx, 30, 'Cinzel')
        ww = text_w(ctx, words[k])
        outlined(ctx, words[k], 960 - ww / 2, 540 - h_ / 2 + 42, fill=C(P['acc'], 0.9 * a), sw=5)
    dots(ctx, t, 34, 0.22)

def sc7(ctx, t, lt, dl):       # Meer, Bauch, Nacht
    cam(ctx, t, 1.02, 0, 0)
    darkfill(ctx, 1.0)
    names = ['DAS MEER', 'DER BAUCH', 'DIE NACHT']
    for k in range(3):
        a = clamp((lt - k * 0.55) / 0.4)
        if a <= 0: continue
        rr = 420 - k * 130 + math.sin(t * 1.2 + k) * 6
        src(ctx, P['acc'], 0.5 * a); ctx.set_line_width(4)
        circle(ctx, 960, 520, rr); ctx.stroke()
        set_font(ctx, 34, 'Cinzel')
        ww = text_w(ctx, names[k])
        outlined(ctx, names[k], 960 - ww / 2, 520 - rr + 48, fill=C(P['acc'], 0.95 * a), sw=6)
    dots(ctx, t, 26, 0.2)

def sc8(ctx, t, lt, dl):       # das Bittgebet
    cam(ctx, t, 1.02, 0, 0)
    darkfill(ctx, 1.0)
    k = ramp(t, SC[8] + 0.2, SC[8] + 2.6)
    lightburst(ctx, 960, 470, t, k)
    if lt > 1.6:
        a = clamp((lt - 1.6) / 0.8) * clamp((dl - lt) / 0.8)
        set_font(ctx, 44, 'Lora')
        for j, line in enumerate(['Es gibt keinen Gott ausser Dir,',
                                  'erhaben bist Du,',
                                  'ich gehörte zu den Ungerechten.']):
            ww = text_w(ctx, line)
            outlined(ctx, line, 960 - ww / 2, 700 + j * 58, fill=(1, 0.98, 0.92, a), sw=7)
    dots(ctx, t, 30, 0.25)

def sc9(ctx, t, lt, dl):       # der Koranvers
    cam(ctx, t, 1.02, lt * 4, 0)
    darkfill(ctx, max(0.0, 1 - clamp(lt / 1.6)))
    paper_a = clamp(lt / 1.6)
    if paper_a > 0:
        ctx.push_group(); paper(ctx, t); coastline(ctx, 1.0, t); hatch(ctx, t, 320, 640, 0.3)
        ctx.pop_group_to_source(); ctx.paint_with_alpha(paper_a)
    lightburst(ctx, 1480, 300, t, 0.45 * paper_a, 620)
    if lt > 1.2:
        a = clamp((lt - 1.2) / 0.7) * clamp((dl - lt) / 0.7)
        set_font(ctx, 42, 'Lora')
        for j, line in enumerate(['Wir erhörten ihn und erretteten ihn aus der Bedrängnis.',
                                  'Und so erretten Wir die Gläubigen.']):
            ww = text_w(ctx, line)
            outlined(ctx, line, 960 - ww / 2, 250 + j * 56, fill=C(P['ink'], a), sw=7)
        set_font(ctx, 30, 'Montserrat')
        s_ = 'Sure Al Anbiya 21:88'
        ww = text_w(ctx, s_)
        outlined(ctx, s_, 960 - ww / 2, 370, fill=C(P['acc'], a), sw=5)
    compass(ctx, 1660, 820, 0.9, t, paper_a)

def sc10(ctx, t, lt, dl):      # Rettung, Kueste
    cam(ctx, t, 1.02 + lt * 0.003, 0, 0)
    coastline(ctx, 1.0, t); hatch(ctx, t, 330, 620, 0.26)
    lightburst(ctx, 1460, 280, t, 0.5, 700)
    p = clamp(lt / 1.6)
    ink(ctx, [(430, 900), (424, 840), (440, 790), (436, 740)], p, 7, 0.9)
    for k in range(5):
        a = clamp((lt - 0.5 - k * 0.14) / 0.3)
        if a <= 0: continue
        ctx.save(); ctx.translate(436, 744); ctx.rotate(-PI / 2 + (k - 2) * 0.46 + math.sin(t * 1.4 + k) * 0.05)
        src(ctx, P['leaf'], 0.8 * a); ellipse(ctx, 62, 0, 62, 15); ctx.fill()
        src(ctx, P['ink'], 0.5 * a); ctx.set_line_width(2.5); ellipse(ctx, 62, 0, 62, 15); ctx.stroke()
        ctx.restore()
    compass(ctx, 1660, 820, 0.9, t)
    dots(ctx, t, 24, 0.2)

SCENES = [sc0, sc1, sc2, sc3, sc4, sc5, sc6, sc7, sc8, sc9, sc10]

def frame(ctx, t):
    i, lt, dl = scene_at(t)
    ctx.save()
    paper(ctx, t)
    ctx.save()
    SCENES[i](ctx, t, lt, dl)
    ctx.restore()
    ctx.restore()
    frame_border(ctx, t)
    dark = 6 <= i <= 8
    title(ctx, t, 0.35, 4.5, 'YUNUS', sub='Chronik einer Rettung', size=104, y=380,
          col=C(P['ink'])[:3] if not dark else (1, 1, 1))
    draw_subs(ctx, t, size=44, face='Lora',
              col=(1, 0.99, 0.95) if dark else C(P['ink'])[:3], y=990)
    endcard(ctx, t, AUD + 0.5, 'Stil 2  ·  ' + STYLE_NAME)
