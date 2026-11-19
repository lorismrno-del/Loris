from kit import *

# ---------- Himmel mit Halo und Wolkenbaendern ----------
def hq_sky(ctx, t, cam, top='#1d2b4a', mid='#7a5a6e', low='#e8a05a', sun=(820, 560), sun_r=70,
           halo=1.0, bands=3, seed=1, haze='#f0c08a', hz=1150):
    ctx.set_source(lingrad(0, -200, 0, hz + 120,
                           [(0, top), (0.42, mid), (0.78, low), (1, shade(low, 0.3))]))
    ctx.rectangle(-200, -300, 1500, hz + 460); ctx.fill()
    sx, sy = sun
    if halo > 0:
        for k, (r, a) in enumerate(((760, 0.10), (470, 0.16), (260, 0.26), (140, 0.4))):
            ctx.set_source(radgrad(sx, sy, 0, r * halo, [(0, C('#fff3d0', a * halo)), (1, C('#ffb45a', 0.0))]))
            circle(ctx, sx, sy, r * halo); ctx.fill()
        ctx.set_source(radgrad(sx, sy, 0, sun_r, [(0, C('#fffaf0', 0.95)), (1, C('#ffd089', 0.55))]))
        circle(ctx, sx, sy, sun_r); ctx.fill()
    r = rnd(seed)
    for b in range(bands):
        depth = (b + 1) / bands
        y0 = 230 + b * 210 + r.uniform(-30, 30)
        a = 0.10 + 0.13 * (1 - depth)
        for k in range(5):
            cx = r.uniform(-300, 1400) + math.sin(t * (0.02 + 0.015 * depth) + k) * 60
            w = r.uniform(240, 620) * (0.6 + depth)
            h = r.uniform(22, 48) * (0.6 + depth)
            ctx.set_source(lingrad(cx, y0 - h, cx, y0 + h,
                                   [(0, C('#ffe9c8', a * 1.3)), (1, C(haze, a * 0.25))]))
            ellipse(ctx, cx, y0 + r.uniform(-18, 18), w, h); ctx.fill()

# ---------- Bergketten mit Luftperspektive ----------
def hq_ridges(ctx, t, cam, base='#6a4a52', hz=1150, n=4, seed=3, haze='#e8b07a'):
    r = rnd(seed)
    for i in range(n):
        d = i / max(1, n - 1)
        par = 0.30 + 0.22 * i
        col = mix(haze, base, 0.18 + 0.78 * d)
        amp = 70 + 120 * d
        y = hz - 120 + i * 46
        def draw(col=col, amp=amp, y=y, i=i):
            ctx.new_path(); ctx.move_to(-400, y + 400)
            x = -400
            rr = rnd(seed * 10 + i)
            ph = rr.uniform(0, 10)
            while x <= 1500:
                yy = y - abs(math.sin(x * 0.0022 + ph)) * amp - abs(math.sin(x * 0.0009 + ph * 2)) * amp * 0.7
                ctx.line_to(x, yy); x += 26
            ctx.line_to(1500, y + 400); ctx.close_path()
            ctx.set_source(lingrad(0, y - amp, 0, y + 200,
                                   [(0, shade(col, 0.14)), (1, shade(col, -0.22))])); ctx.fill()
        layer(ctx, cam, par, draw)

# ---------- Boden ----------
def hq_ground(ctx, t, cam, y=1260, c1='#d8a870', c2='#8a5f3c', seed=5, warm='#ffd9a0', lines=True):
    def g():
        ctx.set_source(lingrad(0, y - 40, 0, 2700, [(0, shade(c1, 0.2)), (0.28, c1), (0.8, c2), (1, shade(c2, -0.18))]))
        ctx.rectangle(-300, y, 1700, 3000 - y); ctx.fill()
        ctx.set_source(lingrad(0, y - 60, 0, y + 260, [(0, C(warm, 0.45)), (1, C(warm, 0.0))]))
        ctx.rectangle(-300, y - 60, 1700, 320); ctx.fill()
        if lines:
            r = rnd(seed)
            for k in range(16):
                yy = y + 30 + k * k * 5.2 + r.uniform(-8, 8)
                if yy > 2000: break
                a = 0.05 + 0.05 * (k / 16)
                src(ctx, shade(c2, -0.4), a); ctx.set_line_width(2 + k * 0.5)
                ctx.new_path(); x = -200
                ctx.move_to(x, yy)
                while x < 1400:
                    ctx.line_to(x, yy + math.sin(x * 0.006 + k) * (3 + k * 0.6)); x += 40
                ctx.stroke()
    layer(ctx, cam, 1.0, g)

# ---------- Gottesstrahlen ----------
def godrays(ctx, x, y, a=0.14, n=11, spread=0.2, c='#ffe6b0', length=2600, t=0.0, fade_to=1150):
    ctx.save()
    ctx.rectangle(-300, -400, 1700, fade_to + 400); ctx.clip()
    for k in range(n):
        ang = -PI / 2 + (k - (n - 1) / 2) * spread + math.sin(t * 0.12 + k) * 0.012
        w = 0.016 + 0.02 * ((k * 7) % 3) / 3
        ctx.new_path(); ctx.move_to(x, y)
        ctx.line_to(x + math.cos(ang - w) * length, y - math.sin(ang - w) * length)
        ctx.line_to(x + math.cos(ang + w) * length, y - math.sin(ang + w) * length)
        ctx.close_path()
        ctx.set_source(lingrad(x, y, x, y - length, [(0, C(c, a)), (1, C(c, 0.0))])); ctx.fill()
    ctx.restore()

# ---------- Vordergrund, dunkel und weich ----------
def fg_rocks(ctx, t, cam, c='#2a1c16', a=0.85, seed=7, y=2075, par=1.45):
    """dunkle Bodenkante am unteren Rand, weich auslaufend"""
    def f():
        r = rnd(seed)
        ctx.new_path(); ctx.move_to(-300, 2200)
        x = -300
        while x <= 1400:
            h = 60 + 46 * math.sin(x * 0.0035 + r.uniform(0, 1)) + 30 * math.sin(x * 0.011)
            ctx.line_to(x, y - h); x += 34
        ctx.line_to(1400, 2200); ctx.close_path()
        ctx.set_source(lingrad(0, y - 150, 0, 2200, [(0, C(c, a * 0.75)), (0.5, C(c, a)), (1, C(shade(c, -0.4), a))]))
        ctx.fill()
        src(ctx, shade(c, 0.5), 0.12 * a); ctx.set_line_width(5)
        ctx.new_path(); x = -300
        while x <= 1400:
            h = 60 + 46 * math.sin(x * 0.0035 + 0.5) + 30 * math.sin(x * 0.011)
            ctx.line_to(x, y - h); x += 34
        ctx.stroke()
    layer(ctx, cam, par, f)

def fg_grass(ctx, t, cam, c='#241a12', a=0.7, seed=9, y=2070, n=70, par=1.5):
    def f():
        r = rnd(seed)
        for k in range(n):
            x = r.uniform(-150, 1250)
            h = r.uniform(90, 300)
            sw = math.sin(t * 1.2 + k * 0.7) * (12 + h * 0.06)
            src(ctx, c, a * r.uniform(0.45, 1))
            ctx.set_line_width(r.uniform(2.5, 6)); ctx.set_line_cap(cairo.LINE_CAP_ROUND)
            ctx.move_to(x, y)
            ctx.curve_to(x + sw * 0.2, y - h * 0.55, x + sw * 0.7, y - h * 0.85, x + sw, y - h)
            ctx.stroke()
    layer(ctx, cam, par, f)

def fg_bokeh(ctx, t, cam, c='#ffd9a0', a=0.1, seed=11, n=14, par=1.8):
    def f():
        r = rnd(seed)
        for k in range(n):
            x = r.uniform(-200, 1300) + math.sin(t * 0.3 + k) * 22
            y = r.uniform(300, 1900) + math.cos(t * 0.24 + k * 1.7) * 18
            rad = r.uniform(26, 78)
            ctx.set_source(radgrad(x, y, rad * 0.3, rad, [(0, C(c, a * 1.4)), (1, C(c, 0.0))]))
            circle(ctx, x, y, rad); ctx.fill()
    layer(ctx, cam, par, f)

# ---------- Lichtkante an Figuren ----------
def rim(ctx, fn, dx=-7, dy=-5, c='#ffd9a0', a=0.55, blur=3):
    """zeichnet fn mehrfach versetzt als Lichtkante, dann normal darueber"""
    for k in range(blur):
        ctx.push_group()
        fn()
        ctx.pop_group_to_source()
        ctx.save(); ctx.translate(dx * (1 + k * 0.5), dy * (1 + k * 0.5))
        ctx.paint_with_alpha(0)
        ctx.restore()
    ctx.push_group(); fn(); pat = ctx.pop_group()
    ctx.save(); ctx.translate(dx, dy)
    ctx.set_source(pat); ctx.paint_with_alpha(1.0)
    ctx.restore()

def glowfig(ctx, fn, x, y, s, c='#ffd9a0', a=0.3, r=160):
    glow(ctx, x, y, r * s, c, a)
    fn()

# ---------- Luft und Staub in Tiefen ----------
def motes(ctx, t, cam, n=26, c='#ffe6c0', a=0.3, seed=13, lo=0.7, hi=1.5):
    for band, par in enumerate((lo, 1.0, hi)):
        def f(band=band, par=par):
            r = rnd(seed + band * 17)
            sc = 0.6 + band * 0.7
            for k in range(n // 3 + 2):
                bx = r.uniform(-200, 1300); by = r.uniform(400, 1900)
                x = bx + math.sin(t * (0.25 + 0.1 * band) + k * 1.3) * (30 + band * 20)
                y = by + math.cos(t * (0.18 + 0.08 * band) + k) * (22 + band * 14) - (t * (6 + band * 10)) % 400
                rad = r.uniform(2.5, 6) * sc
                src(ctx, c, a * r.uniform(0.3, 1) * (0.5 + 0.4 * band))
                circle(ctx, x, y % 2000, rad); ctx.fill()
        layer(ctx, cam, par, f)

def heat(ctx, t, y=1260, a=0.07, c='#ffdca8'):
    for k in range(5):
        yy = y + k * 26 + math.sin(t * 1.6 + k) * 4
        src(ctx, c, a)
        ctx.set_line_width(10 + k * 3)
        ctx.new_path(); x = -200
        ctx.move_to(x, yy)
        while x < 1400:
            ctx.line_to(x, yy + math.sin(x * 0.02 + t * 2 + k) * 4); x += 30
        ctx.stroke()

def cine(ctx, warm='#ff9a4a', cool='#2a3a6a', a=0.1, vig=0.5):
    ctx.set_source(lingrad(0, 0, 0, 1920, [(0, C(cool, a * 0.7)), (0.5, C(warm, a * 0.5)), (1, C(cool, a * 0.9))]))
    ctx.rectangle(0, 0, 1080, 1920); ctx.fill()
    ctx.set_source(radgrad(540, 960, 420, 1250, [(0, C('#000000', 0.0)), (1, C('#000000', vig))]))
    ctx.rectangle(0, 0, 1080, 1920); ctx.fill()

# ---------- Positionen ohne Ueberlappung ----------
def scatter(n, x0, x1, y0, y1, dmin=70, seed=1, tries=60):
    """gibt bis zu n Punkte mit Mindestabstand dmin (in Bildpixeln, tiefenskaliert)"""
    r = rnd(seed); pts = []
    for _ in range(n * tries):
        if len(pts) >= n: break
        x = r.uniform(x0, x1); y = r.uniform(y0, y1)
        f = 0.45 + 0.55 * (y - y0) / max(1.0, (y1 - y0))
        ok = True
        for (px, py, pf) in pts:
            if (x - px) ** 2 + ((y - py) * 2.2) ** 2 < (dmin * (f + pf) * 0.5) ** 2:
                ok = False; break
        if ok: pts.append((x, y, f))
    return pts

# ---------- Sanddüne als Vordergrund, nicht schwarz ----------
def dune_fg(ctx, t, cam, y=2010, c='#6a4830', c2='#3a2418', seed=7, par=1.4, amp=58, a=1.0):
    def f():
        r = rnd(seed); ph = r.uniform(0, 6)
        def edge(x):
            return y - (amp + 30 * math.sin(x * 0.0032 + ph) + 16 * math.sin(x * 0.009 + ph * 2))
        ctx.new_path(); ctx.move_to(-300, 2300)
        x = -300
        while x <= 1400:
            ctx.line_to(x, edge(x)); x += 26
        ctx.line_to(1400, 2300); ctx.close_path()
        ctx.set_source(lingrad(0, y - amp - 60, 0, 2300,
                               [(0, C(c, a)), (0.45, C(shade(c, -0.3), a)), (1, C(c2, a))])); ctx.fill()
        # heller Lichtsaum auf der Kante
        ctx.new_path(); x = -300
        ctx.move_to(x, edge(x))
        while x <= 1400:
            ctx.line_to(x, edge(x)); x += 26
        src(ctx, shade(c, 0.55), 0.3 * a); ctx.set_line_width(6); ctx.stroke()
    layer(ctx, cam, par, f)

def grass_tuft(ctx, x, y, s, t, c='#3a2a18', n=7, seed=1, a=0.9):
    """Grasbüschel mit Erdbasis, damit es nicht aus dem Nichts kommt"""
    r = rnd(seed)
    src(ctx, shade(c, -0.25), 0.55 * a)
    ellipse(ctx, x, y, 34 * s, 9 * s); ctx.fill()
    for k in range(n):
        dx = r.uniform(-26, 26) * s
        h = r.uniform(60, 150) * s
        sw = math.sin(t * 1.15 + k * 0.8 + x * 0.01) * (9 + h * 0.08)
        src(ctx, c, a * r.uniform(0.55, 1))
        ctx.set_line_width(r.uniform(2.6, 5.5) * s); ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.move_to(x + dx, y)
        ctx.curve_to(x + dx + sw * 0.2, y - h * 0.55, x + dx + sw * 0.7, y - h * 0.85, x + dx + sw, y - h)
        ctx.stroke()

def grass_band(ctx, t, cam, y=1980, c='#3a2a18', n=9, seed=9, par=1.35, x0=-200, x1=1300, a=0.9, avoid=None, gap=210):
    def f():
        r = rnd(seed)
        for k in range(n):
            x = x0 + (x1 - x0) * (k + r.uniform(0.15, 0.85)) / n
            if avoid is not None and abs(x - avoid) < gap:
                continue
            grass_tuft(ctx, x, y + r.uniform(-14, 14), r.uniform(0.8, 1.5), t, c=c, seed=seed * 7 + k, a=a)
    layer(ctx, cam, par, f)

def soft_bottom(ctx, t, cam, y=1700, c='#4a3220', a=0.78, par=1.0, h=760):
    """weicher dunkler Saum am unteren Rand, keine harte Kante, laeuft mit dem Boden"""
    def f():
        ctx.set_source(lingrad(0, y, 0, y + h, [(0, C(c, 0.0)), (0.4, C(c, a * 0.14)), (0.72, C(c, a * 0.45)), (1, C(c, a))]))
        ctx.rectangle(-300, y, 1700, h + 400); ctx.fill()
    layer(ctx, cam, par, f)

def sand_detail(ctx, t, cam, y=1400, c='#8a5f3c', seed=3, par=1.0, n=10):
    """kleine Steinchen und Rippel auf dem Sand, damit der Boden nicht leer ist"""
    def f():
        r = rnd(seed)
        for k in range(n):
            x = r.uniform(-150, 1250); yy = y + r.uniform(60, 560)
            s = 0.4 + (yy - y) / 560
            src(ctx, shade(c, -0.3), 0.35)
            ellipse(ctx, x, yy, 13 * s, 6 * s); ctx.fill()
            src(ctx, shade(c, 0.3), 0.25)
            ellipse(ctx, x - 2 * s, yy - 2 * s, 9 * s, 4 * s); ctx.fill()
    layer(ctx, cam, par, f)

ROBES = [('#6a5a46', '#44382c', '#cdbfa6'), ('#7a5a4a', '#4e3a30', '#e0d2b8'),
         ('#5a6a5a', '#3a4438', '#c8bca2'), ('#7a6a4a', '#504432', '#d8cab0'),
         ('#6a5050', '#443434', '#cfc2a8'), ('#55605a', '#363e3a', '#c2b69c'),
         ('#806a52', '#54442f', '#e6d8be'), ('#5e5a6a', '#3c3844', '#cbc0a6')]

def march(ctx, t, rows, seed=1, x0=-360, x1=1460, draw=None):
    """Figuren ziehen wirklich durchs Bild. rows: (y, scale, anzahl, speed)"""
    r = rnd(seed)
    span = x1 - x0
    for ri, (ry, rs, rn, sp) in enumerate(rows):
        for k in range(rn):
            off = span * (k + r.uniform(0.08, 0.92)) / rn
            x = x0 + (off + t * sp) % span
            dy = r.uniform(-7, 7)
            sc = rs * r.uniform(0.86, 1.16)
            kind = r.uniform(0, 1)
            draw(ctx, x, ry + dy, sc, t, ri * 100 + k, kind, sp)

def bundle(ctx, x, y, s, t, i, c='#8a6f4a'):
    """Sack auf dem Ruecken, wird VOR der Figur gezeichnet damit er dahinter liegt"""
    ph = (i * 0.7) % 6.28
    by = y - 172 * s + math.sin(t * 6.4 + ph) * 4 * s
    bx = x - 46 * s
    ctx.set_source(radgrad(bx - 10 * s, by - 16 * s, 0, 54 * s,
                           [(0, shade(c, 0.3)), (0.65, shade(c, -0.05)), (1, shade(c, -0.4))]))
    ctx.new_path()
    ctx.move_to(bx - 34 * s, by + 18 * s)
    ctx.curve_to(bx - 42 * s, by - 26 * s, bx - 20 * s, by - 48 * s, bx + 2 * s, by - 44 * s)
    ctx.curve_to(bx + 26 * s, by - 40 * s, bx + 36 * s, by - 8 * s, bx + 30 * s, by + 20 * s)
    ctx.close_path(); ctx.fill()
    src(ctx, shade(c, -0.5), 0.55); ctx.set_line_width(4 * s)
    ctx.new_path(); ctx.move_to(bx - 28 * s, by - 14 * s)
    ctx.curve_to(bx - 6 * s, by - 24 * s, bx + 14 * s, by - 20 * s, bx + 26 * s, by - 2 * s); ctx.stroke()
    src(ctx, shade(c, -0.35)); ellipse(ctx, bx + 2 * s, by - 46 * s, 11 * s, 8 * s); ctx.fill()

def jar(ctx, x, y, s, t, i, c='#9a6a4a'):
    """Krug auf dem Kopf, sitzt direkt auf der Kopfbedeckung"""
    ph = (i * 0.7) % 6.28
    jy = y - 252 * s + math.sin(t * 6.4 + ph) * 3 * s
    ctx.set_source(lingrad(x - 20 * s, jy, x + 20 * s, jy,
                           [(0, shade(c, 0.22)), (0.55, shade(c, -0.1)), (1, shade(c, -0.42))]))
    ctx.new_path()
    ctx.move_to(x - 9 * s, jy)
    ctx.curve_to(x - 25 * s, jy - 12 * s, x - 23 * s, jy - 44 * s, x - 8 * s, jy - 50 * s)
    ctx.line_to(x + 8 * s, jy - 50 * s)
    ctx.curve_to(x + 23 * s, jy - 44 * s, x + 25 * s, jy - 12 * s, x + 9 * s, jy)
    ctx.close_path(); ctx.fill()
    src(ctx, shade(c, -0.5)); rrect(ctx, x - 12 * s, jy - 56 * s, 24 * s, 8 * s, 4 * s); ctx.fill()

WOMAN_CLOTH = [('#2a3246', '#46506a'), ('#3a2c40', '#5a4a60'), ('#263a38', '#3e5a56'),
               ('#42313a', '#64505a'), ('#2e3440', '#4a5260')]

def marcher(ctx, x, y, s, t, i, kind, sp):
    """Ein Mitglied des Zuges. Rolle, Groesse, Farbe und Gang variieren."""
    rb, rb2, tb = ROBES[i % len(ROBES)]
    hb = 0.84 + ((i * 37) % 23) / 23.0 * 0.34
    s = s * hb
    ph = (i * 0.83 + (i % 5) * 0.41) % 6.28
    wk = (0.82 + ((i * 53) % 17) / 17.0 * 0.5) if sp else 0.0
    if sp:
        ph += t * 2.0 * PI * sp / max(18.0, 74.0 * s * wk)
    contact(ctx, x, y, s * 0.78, a=0.3)
    if kind < 0.17:
        cl, tr = WOMAN_CLOTH[i % len(WOMAN_CLOTH)]
        ws = s * 0.95
        woman(ctx, x, y, ws, t, cloth=cl, trim=tr, facing=1, walk=wk, phase=ph, seed=340 + i)
        if kind < 0.07:
            jar(ctx, x, y, ws * 0.92, t, i)
        return
    if 0.17 <= kind < 0.28:
        bundle(ctx, x, y, s, t, i)
    prop = None
    if kind > 0.88: prop = 'spear'
    elif kind > 0.80: prop = 'banner'
    elif kind > 0.72: prop = 'shield'
    person(ctx, x, y, s, t, facing=1, walk=wk, phase=ph,
           robe=rb, robe2=rb2, turban=tb, beard='#2a2018' if kind > 0.34 else None,
           prop=prop, arms=(0.2, -0.08) if prop is None else (0.1, -0.05),
           elbows=(0.26, 0.26), seed=300 + i, lean=0.0,
           legs=bool(sp), hem_lift=22 if sp else 0.0)

def standers(ctx, t, rows, seed=1, draw=None):
    """Stehender Zug: feste Plaetze, aber Gewichtsverlagerung und Blickwechsel"""
    r = rnd(seed)
    for ri, (ry, rs, rn, x0, x1) in enumerate(rows):
        for k in range(rn):
            x = x0 + (x1 - x0) * (k + r.uniform(0.2, 0.8)) / rn
            ph = r.uniform(0, 6.28)
            sway = math.sin(t * 0.9 + ph) * 4
            draw(ctx, x + sway, ry + r.uniform(-6, 6), rs * r.uniform(0.86, 1.16), t,
                 ri * 100 + k + 500, r.uniform(0, 1), 0)

def jinn_big(ctx, x, y, s, t, i, a=0.72):
    """Dschinn: schlanke, schwebende Lichtgestalt mit Kopf, Schultern und Schweif"""
    ph = i * 1.37
    fl = math.sin(t * 1.25 + ph)
    sw = math.sin(t * 0.95 + ph) * 10 * s
    base = y - 50 * s - fl * 12 * s
    hy = base - 300 * s                      # Schulterhoehe
    cx = x + sw
    glow(ctx, cx, hy + 40 * s, 190 * s, '#b49cff', 0.22 * a)
    ctx.new_path()
    ctx.move_to(cx - 4 * s, base)
    ctx.curve_to(cx - 26 * s, base - 70 * s, cx - 36 * s, hy + 180 * s, cx - 38 * s, hy + 120 * s)
    ctx.curve_to(cx - 44 * s, hy + 70 * s, cx - 50 * s, hy + 40 * s, cx - 46 * s, hy + 18 * s)
    ctx.curve_to(cx - 34 * s, hy - 6 * s, cx - 16 * s, hy - 14 * s, cx, hy - 14 * s)
    ctx.curve_to(cx + 16 * s, hy - 14 * s, cx + 34 * s, hy - 6 * s, cx + 46 * s, hy + 18 * s)
    ctx.curve_to(cx + 50 * s, hy + 40 * s, cx + 44 * s, hy + 70 * s, cx + 38 * s, hy + 120 * s)
    ctx.curve_to(cx + 36 * s, hy + 180 * s, cx + 26 * s, base - 70 * s, cx + 4 * s, base)
    ctx.close_path()
    ctx.set_source(lingrad(0, hy - 30 * s, 0, base,
                           [(0, C('#efe8ff', 0.52 * a)), (0.3, C('#c4aeff', 0.46 * a)),
                            (0.66, C('#9a7cf0', 0.3 * a)), (1, C('#7a5ad8', 0.0))]))
    ctx.fill()
    # heller Kern in der Mitte
    ctx.set_source(lingrad(0, hy, 0, base - 40 * s,
                           [(0, C('#ffffff', 0.5 * a)), (0.55, C('#e8dcff', 0.22 * a)), (1, C('#e8dcff', 0.0))]))
    ctx.new_path()
    ctx.move_to(cx - 15 * s, hy + 10 * s)
    ctx.curve_to(cx - 20 * s, hy + 120 * s, cx - 12 * s, base - 120 * s, cx - 3 * s, base - 40 * s)
    ctx.line_to(cx + 3 * s, base - 40 * s)
    ctx.curve_to(cx + 12 * s, base - 120 * s, cx + 20 * s, hy + 120 * s, cx + 15 * s, hy + 10 * s)
    ctx.close_path(); ctx.fill()
    # Arme als Schlieren
    src(ctx, '#ddd0ff', 0.34 * a); ctx.set_line_width(11 * s); ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    for sd in (-1, 1):
        ctx.new_path()
        ctx.move_to(cx + sd * 40 * s, hy + 34 * s)
        ctx.curve_to(cx + sd * 76 * s, hy + 76 * s + fl * 10 * s,
                     cx + sd * 70 * s, hy + 146 * s, cx + sd * 46 * s, hy + 182 * s)
        ctx.stroke()
    # Kopf, deutlich abgesetzt
    ctx.set_source(radgrad(cx - 8 * s, hy - 56 * s, 0, 44 * s,
                           [(0, C('#ffffff', 0.92 * a)), (0.52, C('#e2d6ff', 0.6 * a)), (1, C('#a98cf4', 0.0))]))
    circle(ctx, cx, hy - 46 * s, 38 * s); ctx.fill()
    r = rnd(500 + i)
    for k in range(6):
        pp = (t * 0.5 + k * 0.17 + ph) % 1.0
        px = cx + r.uniform(-34, 34) * s + math.sin(t * 1.4 + k) * 10 * s
        py = hy - 80 * s - pp * 230 * s
        src(ctx, '#d8c8ff', 0.5 * a * (1 - pp)); circle(ctx, px, py, 6 * s * (1 - pp * 0.6)); ctx.fill()
    src(ctx, '#2a1a3a', 0.12 * a)
    ellipse(ctx, x + sw * 0.4, y + 4 * s, 50 * s, 10 * s); ctx.fill()

def flock(ctx, t, x, y, s=1.0, n=11, seed=5, a=0.85, c='#2e2740'):
    """V-Formation, zieht sichtbar durchs Bild"""
    for k in range(n):
        row = k // 2; side = 1 if k % 2 else -1
        bx = x - row * 56 * s * 1.0 + 0
        by = y + row * 26 * s * 0 + side * row * 30 * s
        bx += math.sin(t * 1.2 + k) * 7 * s
        by += math.cos(t * 1.4 + k * 0.8) * 6 * s
        f = math.sin(t * 7.5 + k * 0.6)
        ss = s * (1.0 - row * 0.04)
        src(ctx, c, a); ctx.set_line_width(5.5 * ss); ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.new_path()
        ctx.move_to(bx - 22 * ss, by + f * 11 * ss)
        ctx.curve_to(bx - 10 * ss, by - 9 * ss, bx - 4 * ss, by - 9 * ss, bx, by)
        ctx.curve_to(bx + 4 * ss, by - 9 * ss, bx + 10 * ss, by - 9 * ss, bx + 22 * ss, by + f * 11 * ss)
        ctx.stroke()

def pebbles(ctx, t, cam, y0, y1, x0=-100, x1=1200, n=14, seed=1, c='#8a6a44', par=1.0,
            avoid=None, gapx=230, gapy=190, smin=0.5, smax=1.5):
    """kleine Steine fuer Massstab in Makro Szenen, nie auf der Hauptfigur"""
    def f():
        r = rnd(seed)
        for k in range(n):
            x = x0 + (x1 - x0) * (k + r.uniform(0.1, 0.9)) / n
            y = r.uniform(y0, y1)
            sc = r.uniform(smin, smax)
            if avoid is not None and abs(x - avoid[0]) < gapx and abs(y - avoid[1]) < gapy:
                continue
            shadow(ctx, x + 7 * sc, y + 4 * sc, 25 * sc, 0.2)
            ctx.set_source(radgrad(x - 6 * sc, y - 8 * sc, 0, 27 * sc,
                                   [(0, shade(c, 0.38)), (0.6, shade(c, -0.02)), (1, shade(c, -0.34))]))
            ellipse(ctx, x, y, 19 * sc, 12.5 * sc); ctx.fill()
            src(ctx, shade(c, 0.5), 0.3)
            ellipse(ctx, x - 5 * sc, y - 4 * sc, 7 * sc, 4 * sc); ctx.fill()
    layer(ctx, cam, par, f)

SKY_DAWN = dict(top='#17254a', mid='#8a5668', low='#f2a455', haze='#f2c48e')
SKY_DAY = dict(top='#27477f', mid='#86a6c6', low='#f4d8a8', haze='#ead2b0')
SKY_GOLD = dict(top='#3a2a50', mid='#b06a4e', low='#ffbc62', haze='#ffd9a8')
SKY_NIGHT = dict(top='#05091a', mid='#111a36', low='#2a2c4e', haze='#4c4f74')
SKY_DUSK = dict(top='#1b1a3c', mid='#6b4a6a', low='#d98a56', haze='#e0ab82')

def hq_world(ctx, t, cam, gy, hz=1150, sun=(840, 540), sky=None, rays=0.13, seed=1,
             g1='#e0b078', g2='#9a6c44', bokeh=0.08, ridges=4, soft=None, detail=True,
             stars=0.0, motes_a=0.26, ridge_base='#6a4a52'):
    """Standardwelt in 4K Qualitaet: Himmel, Strahlen, Kaemme, Dunst, Boden, Hitze, Staub"""
    sky = sky or SKY_DAWN
    hq_sky(ctx, t, cam, sun=sun, seed=seed, hz=hz, **sky)
    if stars > 0:
        def st_():
            r = rnd(seed + 40)
            for k in range(120):
                sx = r.uniform(-200, 1300); sy = r.uniform(-50, hz - 120)
                a = stars * r.uniform(0.25, 1.0) * (0.6 + 0.4 * math.sin(t * 1.6 + k))
                src(ctx, '#ffffff', a); circle(ctx, sx, sy, r.uniform(1.4, 3.4)); ctx.fill()
        layer(ctx, cam, 0.3, st_)
    if rays > 0:
        godrays(ctx, sun[0], sun[1], a=rays, t=t, c='#ffe6b0', fade_to=hz + 60)
    hq_ridges(ctx, t, cam, base=ridge_base, hz=hz, n=ridges, seed=seed + 2, haze=sky['haze'])
    def hazeband():
        ctx.set_source(lingrad(0, gy - 190, 0, gy + 70,
                               [(0, C(sky['haze'], 0.0)), (0.6, C(sky['haze'], 0.38)), (1, C(sky['haze'], 0.62))]))
        ctx.rectangle(-300, gy - 190, 1700, 260); ctx.fill()
    layer(ctx, cam, 1.0, hazeband)
    hq_ground(ctx, t, cam, y=gy, c1=g1, c2=g2, seed=seed + 4, warm=sky['haze'])
    def h():
        heat(ctx, t, y=gy - 8, a=0.05, c=sky['haze'])
    layer(ctx, cam, 1.0, h)
    if detail:
        sand_detail(ctx, t, cam, y=gy, c=g2, seed=seed + 5, n=16)
    motes(ctx, t, cam, n=22, c='#ffe6c0', a=motes_a, seed=seed + 6)
    if soft:
        soft_bottom(ctx, t, cam, y=soft, c=shade(g2, -0.55), a=0.8)
    if bokeh:
        fg_bokeh(ctx, t, cam, a=bokeh, seed=seed + 11)


def bush(ctx, x, y, s, t, c='#3f5a24', seed=1):
    r = rnd(seed)
    sw = math.sin(t * 1.3 + seed) * 3 * s
    src(ctx, '#000000', 0.16); ellipse(ctx, x, y + 3 * s, 54 * s, 12 * s); ctx.fill()
    for k in range(5):
        bx = x + r.uniform(-34, 34) * s + sw * r.uniform(0.3, 1)
        by = y - r.uniform(6, 40) * s
        rr = r.uniform(26, 44) * s
        ctx.set_source(radgrad(bx - rr * 0.3, by - rr * 0.4, 0, rr * 1.2,
                               [(0, shade(c, 0.34)), (0.6, c), (1, shade(c, -0.34))]))
        circle(ctx, bx, by, rr); ctx.fill()


def contact(ctx, x, y, s, a=0.46):
    """weicher Bodenschatten direkt unter den Fuessen, damit niemand schwebt"""
    ctx.save(); ctx.translate(x, y + 5 * s); ctx.scale(1.0, 0.17)
    ctx.set_source(radgrad(0, 0, 0, 165 * s,
                           [(0, C('#2a1a10', a)), (0.45, C('#2a1a10', a * 0.6)),
                            (0.8, C('#2a1a10', a * 0.18)), (1, C('#2a1a10', 0.0))]))
    circle(ctx, 0, 0, 165 * s); ctx.fill(); ctx.restore()
