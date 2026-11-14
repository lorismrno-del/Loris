import cairo, math, random, json
W, H, FPS = 1080, 1920, 30
PI = math.pi

# ---------------- utils ----------------
def clamp(x, a=0.0, b=1.0): return a if x < a else b if x > b else x
def lerp(a, b, t): return a + (b - a) * t
def sm(t):
    t = clamp(t); return t * t * (3 - 2 * t)
def eo(t):
    t = clamp(t); return 1 - (1 - t) ** 3
def ei(t):
    t = clamp(t); return t ** 3
def ramp(t, a, b): return sm((t - a) / (b - a)) if b > a else float(t >= a)
def hexc(h, a=1.0):
    h = h.lstrip('#'); return (int(h[0:2], 16) / 255, int(h[2:4], 16) / 255, int(h[4:6], 16) / 255, a)
def C(c, a=None):
    if isinstance(c, str): c = hexc(c)
    if len(c) == 3: c = (*c, 1.0)
    if a is not None: c = (c[0], c[1], c[2], a)
    return c
def mix(c1, c2, t):
    c1, c2 = C(c1), C(c2); return tuple(lerp(c1[i], c2[i], t) for i in range(4))
def shade(c, f):
    c = C(c)
    if f >= 0: return (c[0] + (1 - c[0]) * f, c[1] + (1 - c[1]) * f, c[2] + (1 - c[2]) * f, c[3])
    f = -f; return (c[0] * (1 - f), c[1] * (1 - f), c[2] * (1 - f), c[3])
def alpha(c, a):
    c = C(c); return (c[0], c[1], c[2], c[3] * a)
def src(ctx, c, a=None):
    c = C(c); ctx.set_source_rgba(c[0], c[1], c[2], c[3] if a is None else c[3] * a)
def nz(x, seed=0.0):
    return (math.sin(x * 1.0 + seed * 1.7) * 0.5 + math.sin(x * 2.31 + seed * 3.1 + 1.3) * 0.3 +
            math.sin(x * 5.17 + seed * 0.7 + 2.1) * 0.2)
def rnd(seed):
    return random.Random(seed)

# ---------------- camera ----------------
class Cam:
    def __init__(self, x=540, y=960, z=1.0, r=0.0):
        self.x, self.y, self.z, self.r = x, y, z, r
    def apply(self, ctx, f=1.0, shake=(0, 0)):
        z = 1 + (self.z - 1) * f
        ctx.translate(W / 2 + shake[0], H / 2 + shake[1])
        ctx.rotate(self.r * f)
        ctx.scale(z, z)
        ctx.translate(-(540 + (self.x - 540) * f), -(960 + (self.y - 960) * f))

def cam_lerp(a, b, t):
    return Cam(lerp(a.x, b.x, t), lerp(a.y, b.y, t), lerp(a.z, b.z, t), lerp(a.r, b.r, t))

def keycam(keys, t):
    """keys: list of (time, Cam). smooth interpolation"""
    if t <= keys[0][0]: return keys[0][1]
    for i in range(len(keys) - 1):
        t0, c0 = keys[i]; t1, c1 = keys[i + 1]
        if t <= t1:
            return cam_lerp(c0, c1, sm((t - t0) / max(1e-6, t1 - t0)))
    return keys[-1][1]

def drift(cam, t, amt=1.0, seed=0):
    return Cam(cam.x + nz(t * 0.35, seed) * 14 * amt, cam.y + nz(t * 0.3, seed + 5) * 10 * amt,
               cam.z * (1 + 0.012 * amt * math.sin(t * 0.4 + seed)), cam.r + 0.006 * amt * nz(t * 0.25, seed + 9))

# ---------------- basic shapes ----------------
def circle(ctx, x, y, r):
    ctx.new_sub_path(); ctx.arc(x, y, max(0.01, r), 0, 2 * PI)
def ellipse(ctx, x, y, rx, ry, rot=0.0):
    ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(max(rx, 0.01), max(ry, 0.01))
    ctx.new_sub_path(); ctx.arc(0, 0, 1, 0, 2 * PI); ctx.restore()
def rrect(ctx, x, y, w, h, r):
    r = min(r, w / 2, h / 2)
    ctx.new_sub_path()
    ctx.arc(x + w - r, y + r, r, -PI / 2, 0); ctx.arc(x + w - r, y + h - r, r, 0, PI / 2)
    ctx.arc(x + r, y + h - r, r, PI / 2, PI); ctx.arc(x + r, y + r, r, PI, 1.5 * PI); ctx.close_path()
def poly(ctx, pts):
    ctx.move_to(*pts[0])
    for p in pts[1:]: ctx.line_to(*p)
    ctx.close_path()
def glow(ctx, x, y, r, c, a=1.0, add=True):
    c = C(c)
    g = cairo.RadialGradient(x, y, 0, x, y, r)
    g.add_color_stop_rgba(0, c[0], c[1], c[2], a)
    g.add_color_stop_rgba(0.35, c[0], c[1], c[2], a * 0.45)
    g.add_color_stop_rgba(1, c[0], c[1], c[2], 0)
    ctx.save()
    if add: ctx.set_operator(cairo.OPERATOR_ADD)
    ctx.set_source(g); circle(ctx, x, y, r); ctx.fill(); ctx.restore()
def lingrad(x0, y0, x1, y1, stops):
    g = cairo.LinearGradient(x0, y0, x1, y1)
    for o, c in stops:
        c = C(c); g.add_color_stop_rgba(o, *c)
    return g
def radgrad(x, y, r0, r1, stops, cx=None, cy=None):
    g = cairo.RadialGradient(x if cx is None else cx, y if cy is None else cy, r0, x, y, r1)
    for o, c in stops:
        c = C(c); g.add_color_stop_rgba(o, *c)
    return g

# ---------------- environment ----------------
def sky(ctx, top, mid, bot, y0=-600, y1=2600):
    ctx.set_source(lingrad(0, y0, 0, y1, [(0, top), (0.55, mid), (1, bot)]))
    ctx.rectangle(-2000, -2000, W + 4000, H + 4000); ctx.fill()

def stars(ctx, t, a=1.0, seed=3, n=140):
    r = rnd(seed)
    for i in range(n):
        x = r.uniform(-300, W + 300); y = r.uniform(-500, 1100); s = r.uniform(0.8, 2.6)
        tw = 0.55 + 0.45 * math.sin(t * r.uniform(1, 3) + i)
        src(ctx, (1, 1, 0.92), a * tw * r.uniform(0.4, 1)); circle(ctx, x, y, s); ctx.fill()

def sun(ctx, x, y, r, c='#fff1c4', halo='#ffb347', a=1.0):
    glow(ctx, x, y, r * 9, halo, 0.35 * a)
    glow(ctx, x, y, r * 3.2, c, 0.55 * a)
    src(ctx, c, a); circle(ctx, x, y, r); ctx.fill()

def moon(ctx, x, y, r, a=1.0):
    glow(ctx, x, y, r * 6, '#a9c3ff', 0.25 * a)
    src(ctx, '#f4f1e2', a); circle(ctx, x, y, r); ctx.fill()

def rays(ctx, x, y, t, c='#ffe2a0', a=0.12, n=9, length=2600, seed=1):
    ctx.save(); ctx.set_operator(cairo.OPERATOR_ADD)
    r = rnd(seed)
    for i in range(n):
        ang = r.uniform(0.2, PI - 0.2) + 0.05 * math.sin(t * 0.3 + i)
        wd = r.uniform(0.02, 0.07)
        aa = a * (0.5 + 0.5 * math.sin(t * 0.6 + i * 1.7))
        g = cairo.RadialGradient(x, y, 0, x, y, length)
        cc = C(c)
        g.add_color_stop_rgba(0, cc[0], cc[1], cc[2], aa)
        g.add_color_stop_rgba(1, cc[0], cc[1], cc[2], 0)
        ctx.set_source(g)
        ctx.move_to(x, y)
        ctx.line_to(x + math.cos(ang - wd) * length, y + math.sin(ang - wd) * length)
        ctx.line_to(x + math.cos(ang + wd) * length, y + math.sin(ang + wd) * length)
        ctx.close_path(); ctx.fill()
    ctx.restore()

def cloud(ctx, x, y, s, c=(1, 1, 1), a=0.8, seed=0):
    r = rnd(seed)
    for i in range(9):
        dx = r.uniform(-130, 130) * s; dy = r.uniform(-25, 20) * s - abs(dx) * 0.1
        rr = r.uniform(45, 85) * s * (1 - abs(dx) / (260 * s))
        cc = C(c)
        g = cairo.RadialGradient(x + dx, y + dy - rr * 0.3, rr * 0.1, x + dx, y + dy, rr)
        g.add_color_stop_rgba(0, cc[0], cc[1], cc[2], a)
        g.add_color_stop_rgba(0.7, cc[0] * 0.92, cc[1] * 0.92, cc[2] * 0.95, a * 0.7)
        g.add_color_stop_rgba(1, cc[0] * 0.85, cc[1] * 0.85, cc[2] * 0.9, 0)
        ctx.set_source(g); circle(ctx, x + dx, y + dy, rr); ctx.fill()

def clouds(ctx, t, y=300, c=(1, 1, 1), a=0.7, n=5, seed=7, speed=12, scale=1.0):
    r = rnd(seed)
    for i in range(n):
        x0 = r.uniform(-400, 1500); yy = y + r.uniform(-180, 180); s = r.uniform(0.7, 1.5) * scale
        x = (x0 + t * speed * r.uniform(0.6, 1.4)) % 2200 - 500
        cloud(ctx, x, yy, s, c, a * r.uniform(0.6, 1), seed=seed * 31 + i)

def ridge(ctx, base, amp, color, seed=0, freq=0.004, x0=-1400, x1=2500, color2=None, sharp=0.0):
    ctx.move_to(x0, 3000)
    pts = []
    x = x0
    while x <= x1:
        v = nz(x * freq, seed)
        v2 = abs(nz(x * freq * 2.7, seed + 11))
        y = base - amp * (0.55 + 0.45 * v) - amp * sharp * v2
        pts.append((x, y)); ctx.line_to(x, y); x += 14
    ctx.line_to(x1, 3000); ctx.close_path()
    if color2:
        top = min(p[1] for p in pts)
        ctx.set_source(lingrad(0, top, 0, base + 200, [(0, color2), (1, color)]))
    else:
        src(ctx, color)
    ctx.fill()
    return pts

def ridge_light(ctx, pts, c, a=0.25, w=3):
    ctx.save(); src(ctx, c, a); ctx.set_line_width(w)
    ctx.move_to(*pts[0])
    for p in pts[1:]: ctx.line_to(*p)
    ctx.stroke(); ctx.restore()

def haze(ctx, c, a, y0=-2000, y1=4000):
    src(ctx, c, a); ctx.rectangle(-3000, y0, W + 6000, y1 - y0); ctx.fill()

def ground(ctx, y, c1, c2, c3=None):
    ctx.set_source(lingrad(0, y, 0, y + 900, [(0, c1), (0.4, c2), (1, c3 or shade(c2, -0.3))]))
    ctx.rectangle(-3000, y, W + 6000, 4000); ctx.fill()

def dune_lines(ctx, y, t, c, seed=2, n=10, a=0.18):
    r = rnd(seed)
    ctx.save(); src(ctx, c, a); ctx.set_line_width(2.5)
    for i in range(n):
        yy = y + 30 + i * i * 9 + r.uniform(-8, 8)
        ctx.move_to(-1500, yy)
        x = -1500
        while x < 2600:
            ctx.line_to(x, yy + math.sin(x * 0.01 + i * 1.3) * 6 * (1 + i * 0.2))
            x += 40
        ctx.stroke()
    ctx.restore()

def rocks(ctx, y, seed=4, n=14, c='#7a5a3c', spread=(-600, 1700), size=(10, 40)):
    r = rnd(seed)
    for i in range(n):
        x = r.uniform(*spread); s = r.uniform(*size); yy = y + r.uniform(0, 260)
        k = 1 + (yy - y) / 300
        ss = s * k
        src(ctx, (0, 0, 0), 0.18); ellipse(ctx, x + ss * 0.3, yy + ss * 0.1, ss * 1.2, ss * 0.25); ctx.fill()
        ctx.set_source(lingrad(x - ss, yy - ss, x + ss, yy, [(0, shade(c, 0.25)), (1, shade(c, -0.35))]))
        ctx.move_to(x - ss, yy); ctx.curve_to(x - ss, yy - ss * 0.9, x + ss * 0.4, yy - ss * 1.1, x + ss, yy)
        ctx.close_path(); ctx.fill()

def palm(ctx, x, y, h, t, wind=1.0, seed=0, c_trunk='#6b4a2b', c_leaf='#3f6b2a', lean=0.0):
    r = rnd(seed)
    sway = (math.sin(t * 1.1 + seed) * 0.6 + nz(t * 0.8, seed) * 0.4) * 0.05 * wind
    pts = []
    for i in range(13):
        f = i / 12
        bend = (lean + sway) * f * f
        pts.append((x + math.sin(bend) * h * f * 1.0 + lean * h * 0.15 * f, y - h * f * math.cos(bend)))
    for i in range(12):
        w = lerp(14, 8, i / 12) * h / 400
        ctx.set_line_width(w * 2)
        src(ctx, shade(c_trunk, -0.1 if i % 2 else 0.05))
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.move_to(*pts[i]); ctx.line_to(*pts[i + 1]); ctx.stroke()
    tx, ty = pts[-1]
    for k in range(9):
        ang = -PI / 2 + (k - 4) * 0.42 + r.uniform(-0.1, 0.1)
        ang += math.sin(t * 2.2 + k * 0.7 + seed) * 0.07 * wind + sway * 2
        L = h * r.uniform(0.38, 0.5)
        droop = 0.9 + 0.3 * abs(math.cos(ang))
        ex = tx + math.cos(ang) * L; ey = ty + math.sin(ang) * L * 0.45 + L * 0.45 * droop
        mx = tx + math.cos(ang) * L * 0.5; my = ty + math.sin(ang) * L * 0.5 - L * 0.15
        lc = shade(c_leaf, r.uniform(-0.2, 0.15))
        nx, ny = -(ey - ty), (ex - tx); nn = math.hypot(nx, ny) or 1; nx /= nn; ny /= nn
        wd = L * 0.09
        ctx.move_to(tx, ty)
        ctx.curve_to(mx + nx * wd, my + ny * wd, ex + nx * 2, ey + ny * 2, ex, ey)
        ctx.curve_to(ex - nx * 2, ey - ny * 2, mx - nx * wd, my - ny * wd, tx, ty)
        src(ctx, lc); ctx.fill()
        # frond line
        src(ctx, shade(lc, -0.3), 0.6); ctx.set_line_width(1.5)
        ctx.move_to(tx, ty); ctx.curve_to(mx, my, ex, ey, ex, ey); ctx.stroke()
    src(ctx, '#4a3320'); circle(ctx, tx, ty + 6 * h / 400, 9 * h / 400); ctx.fill()

def grass(ctx, x, y, s, t, c='#5b5a2a', wind=1.0, seed=0, n=9):
    r = rnd(seed)
    for i in range(n):
        bx = x + r.uniform(-30, 30) * s; L = r.uniform(40, 95) * s
        sw = (math.sin(t * 2.4 + i + seed) * 0.25 + 0.3) * wind
        ex = bx + sw * L + r.uniform(-12, 12) * s; ey = y - L
        src(ctx, shade(c, r.uniform(-0.25, 0.2)))
        ctx.move_to(bx - 3 * s, y); ctx.curve_to(bx, y - L * 0.5, ex - 2, ey + 8, ex, ey)
        ctx.curve_to(ex + 1, ey + 10, bx + 4 * s, y - L * 0.4, bx + 3 * s, y); ctx.fill()

def dust(ctx, t, n=40, seed=5, c=(1, 0.93, 0.8), a=0.35, area=(-100, -100, 1280, 2100), speed=1.0):
    r = rnd(seed)
    x0, y0, x1, y1 = area
    for i in range(n):
        px = r.uniform(x0, x1); py = r.uniform(y0, y1); sp = r.uniform(5, 25) * speed; s = r.uniform(1, 3.5)
        x = x0 + (px - x0 + t * sp + nz(t * 0.4, i) * 30) % (x1 - x0)
        y = y0 + (py - y0 - t * sp * 0.3 + nz(t * 0.3, i + 3) * 20) % (y1 - y0)
        aa = a * (0.5 + 0.5 * math.sin(t * 1.3 + i))
        src(ctx, c, aa); circle(ctx, x, y, s); ctx.fill()

def dust_cloud(ctx, x, y, s, t, c='#c8a77a', a=0.5, seed=0, n=10):
    r = rnd(seed)
    for i in range(n):
        dx = r.uniform(-1, 1) * 120 * s + t * r.uniform(-20, 20)
        dy = -r.uniform(0, 70) * s - t * r.uniform(5, 25)
        rr = r.uniform(40, 90) * s * (1 + t * 0.4)
        cc = C(c)
        g = cairo.RadialGradient(x + dx, y + dy, 0, x + dx, y + dy, rr)
        g.add_color_stop_rgba(0, cc[0], cc[1], cc[2], a * 0.6)
        g.add_color_stop_rgba(1, cc[0], cc[1], cc[2], 0)
        ctx.set_source(g); circle(ctx, x + dx, y + dy, rr); ctx.fill()

def shadow(ctx, x, y, w, a=0.28, h=None):
    g = cairo.RadialGradient(x, y, 0, x, y, w)
    g.add_color_stop_rgba(0, 0, 0, 0, a); g.add_color_stop_rgba(1, 0, 0, 0, 0)
    ctx.save(); ctx.translate(x, y); ctx.scale(1, (h or w * 0.22) / w); ctx.translate(-x, -y)
    ctx.set_source(g); circle(ctx, x, y, w); ctx.fill(); ctx.restore()

# ---------------- buildings ----------------
def box(ctx, x, y, w, h, d, c, light=1, roof=True, win=0, seed=0):
    """x,y = bottom-left front; d = depth to right-up"""
    dx, dy = d * 0.8, -d * 0.45
    front = shade(c, 0.08 * light); side = shade(c, -0.28); top = shade(c, 0.22)
    ctx.set_source(lingrad(0, y - h, 0, y, [(0, front), (1, shade(front, -0.15))]))
    ctx.rectangle(x, y - h, w, h); ctx.fill()
    src(ctx, side); poly(ctx, [(x + w, y), (x + w + dx, y + dy), (x + w + dx, y - h + dy), (x + w, y - h)]); ctx.fill()
    if roof:
        src(ctx, top); poly(ctx, [(x, y - h), (x + w, y - h), (x + w + dx, y - h + dy), (x + dx, y - h + dy)]); ctx.fill()
        src(ctx, shade(c, -0.1)); ctx.rectangle(x - 2, y - h - 4, w + 4, 6); ctx.fill()
    if win:
        r = rnd(seed)
        for i in range(win):
            wx = x + w * r.uniform(0.15, 0.75); wy = y - h * r.uniform(0.35, 0.8)
            ww = max(6, w * 0.1)
            src(ctx, (0.1, 0.07, 0.05), 0.85); rrect(ctx, wx, wy, ww, ww * 1.4, ww * 0.4); ctx.fill()

def kaaba(ctx, x, y, s, t=0, light=1.0):
    w = 150 * s; h = 160 * s; d = 70 * s
    dx, dy = d * 0.8, -d * 0.45
    shadow(ctx, x + w * 0.6, y + 4 * s, w * 1.1, 0.35)
    ctx.set_source(lingrad(x, y - h, x + w, y, [(0, '#1a1a1c'), (1, '#060607')]))
    ctx.rectangle(x, y - h, w, h); ctx.fill()
    src(ctx, '#020203'); poly(ctx, [(x + w, y), (x + w + dx, y + dy), (x + w + dx, y - h + dy), (x + w, y - h)]); ctx.fill()
    src(ctx, '#2a2a2e'); poly(ctx, [(x, y - h), (x + w, y - h), (x + w + dx, y - h + dy), (x + dx, y - h + dy)]); ctx.fill()
    # gold band
    by = y - h * 0.74; bh = 12 * s
    ctx.set_source(lingrad(x, by, x + w, by, [(0, '#b8862b'), (0.5, '#f4d27a'), (1, '#b8862b')]))
    ctx.rectangle(x, by, w, bh); ctx.fill()
    src(ctx, '#8a6420'); poly(ctx, [(x + w, by), (x + w + dx, by + dy), (x + w + dx, by + bh + dy), (x + w, by + bh)]); ctx.fill()
    src(ctx, '#3a2a10', 0.6); ctx.set_line_width(1.2 * s)
    for i in range(14):
        xx = x + 6 * s + i * (w - 12 * s) / 13
        ctx.move_to(xx, by + 2 * s); ctx.line_to(xx + 4 * s, by + bh - 2 * s); ctx.stroke()
    # door
    ctx.set_source(lingrad(0, y - h * 0.55, 0, y - h * 0.12, [(0, '#f1cf6e'), (1, '#9c7426')]))
    rrect(ctx, x + w * 0.62, y - h * 0.55, w * 0.2, h * 0.43, 3 * s); ctx.fill()
    # cloth sheen
    ctx.save(); ctx.set_operator(cairo.OPERATOR_ADD)
    ctx.set_source(lingrad(x, 0, x + w, 0, [(0, (1, 1, 1, 0)), (0.3, (1, 0.9, 0.7, 0.06 * light)), (0.6, (1, 1, 1, 0))]))
    ctx.rectangle(x, y - h, w, h); ctx.fill(); ctx.restore()

def ziggurat(ctx, x, y, s, c='#a77b4f'):
    for i in range(4):
        w = (420 - i * 90) * s; h = 70 * s
        yy = y - i * h
        box(ctx, x - w / 2, yy, w, h, 60 * s * (1 - i * 0.15), c)
    src(ctx, shade(c, -0.2)); ctx.rectangle(x - 18 * s, y - 4 * 70 * s, 36 * s, 4 * 70 * s); ctx.fill()

# ---------------- people ----------------
SKIN = '#c8946a'
def person(ctx, x, y, s, t, facing=1, robe='#d8c8a8', robe2='#8a6a44', turban='#efe6d2', beard='#2a1d14', skin=SKIN,
           walk=0.0, phase=0.0, arms=(0.1, -0.05), elbows=(0.3, 0.3), tilt=0.0, prophet=False, head='turban',
           prop=None, prop2=None, cloak=None, alpha_=1.0, sun_dir=1, wind=0.6, seed=0, bob=True, lean=0.0,
           shadow_a=0.28, scale_x=1.0, thrown=0.0, lift=0.0, swing=1.0):
    u = s
    if alpha_ <= 0.01: return
    if alpha_ < 1: ctx.push_group()
    ctx.save()
    if shadow_a > 0 and lift < 1:
        shadow(ctx, x - sun_dir * 8 * u, y, 46 * u, shadow_a * (1 - lift))
    ctx.translate(x, y)
    ctx.scale(scale_x, 1)
    if thrown:
        ctx.translate(0, -150 * u); ctx.rotate(thrown); ctx.translate(0, 150 * u)
    br = math.sin(t * 1.7 + seed) * 1.6 * u
    sw = math.sin(t * 0.7 + seed * 2) * 1.5 * u
    by = -abs(math.sin(phase)) * 6 * u * walk if bob else 0
    ctx.translate(sw * (1 - walk), by)
    ctx.rotate(facing * (walk * 0.05 + lean))
    st = math.sin(phase)
    # feet
    for k, sgn in ((0, 1), (1, -1)):
        fx = facing * st * sgn * 17 * u * walk + (6 if k else -6) * u
        fy = -max(0, math.cos(phase) * sgn) * 7 * u * walk
        src(ctx, '#3b2a1c'); ellipse(ctx, fx + facing * 5 * u, fy - 3 * u, 12 * u, 5 * u); ctx.fill()
    shY = -232 * u + br; hemY = -10 * u
    lightc = shade(robe, 0.12); darkc = shade(robe, -0.3)
    # back arm
    def arm(side, a, e, front, hold=None):
        sx = side * 26 * u + facing * 2 * u; sy = shY + 8 * u
        ex = sx + math.sin(a) * facing * 52 * u; ey = sy + math.cos(a) * 52 * u
        hx = ex + math.sin(a + e) * facing * 46 * u; hy = ey + math.cos(a + e) * 46 * u
        col = robe if front else shade(robe, -0.22)
        if cloak: col = cloak if front else shade(cloak, -0.22)
        if hold and not front: draw_prop(ctx, hold, hx, hy, a + e, u, t, facing)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_line_join(cairo.LINE_JOIN_ROUND)
        src(ctx, shade(col, -0.35)); ctx.set_line_width(25 * u)
        ctx.move_to(sx, sy); ctx.line_to(ex, ey); ctx.line_to(hx, hy); ctx.stroke()
        src(ctx, col); ctx.set_line_width(21 * u)
        ctx.move_to(sx, sy); ctx.line_to(ex, ey); ctx.line_to(hx, hy); ctx.stroke()
        src(ctx, shade(skin, -0.05 if front else -0.2)); circle(ctx, hx, hy, 8.5 * u); ctx.fill()
        if hold and front: draw_prop(ctx, hold, hx, hy, a + e, u, t, facing)
    a0 = arms[0] + st * 0.35 * walk * swing; a1 = arms[1] - st * 0.35 * walk * swing
    arm(-facing, a1, elbows[1], False, prop2)
    # robe
    flut = wind * (math.sin(t * 3.1 + seed) * 0.5 + 0.7) * 7 * u
    hl = -46 * u - facing * st * 6 * u * walk - facing * flut * 0.5
    hr = 46 * u - facing * st * 6 * u * walk - facing * flut * 0.5 * 0
    if facing < 0: hl, hr = hl + flut, hr + flut
    else: hl, hr = hl - flut, hr - flut * 0.2
    ctx.move_to(-30 * u, shY)
    ctx.curve_to(-38 * u, shY + 80 * u, -40 * u, hemY - 80 * u, hl, hemY)
    ctx.curve_to(hl * 0.3, hemY + 5 * u, hr * 0.3, hemY + 5 * u, hr, hemY)
    ctx.curve_to(40 * u, hemY - 80 * u, 38 * u, shY + 80 * u, 30 * u, shY)
    ctx.curve_to(10 * u, shY - 8 * u, -10 * u, shY - 8 * u, -30 * u, shY)
    ctx.close_path()
    g = lingrad(-45 * u * sun_dir, 0, 45 * u * sun_dir, 0, [(0, darkc), (0.55, robe), (1, lightc)])
    ctx.set_source(g); ctx.fill_preserve()
    ctx.save(); ctx.clip()
    # folds
    src(ctx, shade(robe, -0.25), 0.35); ctx.set_line_width(2.5 * u)
    for k in range(4):
        fx = (-24 + k * 16) * u
        ctx.move_to(fx, -130 * u)
        ctx.curve_to(fx + math.sin(t * 2 + k) * 3 * u, -80 * u, fx - facing * st * 8 * u * walk, -40 * u,
                     fx * 1.3 - facing * st * 10 * u * walk, hemY)
        ctx.stroke()
    # bottom shade
    ctx.set_source(lingrad(0, -60 * u, 0, hemY, [(0, (0, 0, 0, 0)), (1, (0, 0, 0, 0.25))]))
    ctx.rectangle(-80 * u, -60 * u, 160 * u, 60 * u); ctx.fill()
    ctx.restore()
    if cloak:
        cc = C(cloak)
        for sd in (-1, 1):
            ctx.move_to(sd * 30 * u, shY)
            ctx.curve_to(sd * 44 * u, shY + 90 * u, sd * 50 * u, -60 * u, sd * 52 * u - facing * flut * 0.6, hemY - 4 * u)
            ctx.line_to(sd * 22 * u - facing * flut * 0.3, hemY - 4 * u)
            ctx.curve_to(sd * 20 * u, -100 * u, sd * 14 * u, shY + 40 * u, sd * 12 * u, shY - 4 * u)
            ctx.close_path()
            ctx.set_source(lingrad(sd * 50 * u, 0, sd * 12 * u, 0, [(0, shade(cc, -0.35)), (1, shade(cc, 0.05))]))
            ctx.fill()
        src(ctx, '#d9b35a'); ctx.set_line_width(2.5 * u)
        for sd in (-1, 1):
            ctx.move_to(sd * 12 * u, shY - 4 * u); ctx.curve_to(sd * 14 * u, shY + 40 * u, sd * 20 * u, -100 * u, sd * 22 * u - facing * flut * 0.3, hemY - 4 * u)
            ctx.stroke()
    # sash
    src(ctx, robe2); ctx.move_to(-37 * u, -128 * u); ctx.curve_to(0, -122 * u, 0, -122 * u, 37 * u, -128 * u)
    ctx.line_to(37 * u, -114 * u); ctx.curve_to(0, -108 * u, 0, -108 * u, -37 * u, -114 * u); ctx.close_path(); ctx.fill()
    # head
    hx0, hy0 = facing * 3 * u, shY - 6 * u
    ctx.save(); ctx.translate(hx0, hy0); ctx.rotate(facing * tilt); ctx.translate(-hx0, -hy0)
    hx, hy = facing * 5 * u, shY - 34 * u
    if prophet:
        src(ctx, shade(skin, -0.2)); ctx.rectangle(hx - 8 * u, hy + 14 * u, 16 * u, 18 * u); ctx.fill()
        pul = 1 + 0.05 * math.sin(t * 2.3)
        glow(ctx, hx, hy, 120 * u * pul, '#ffd98a', 0.55)
        glow(ctx, hx, hy, 55 * u * pul, '#fff6dc', 0.9)
        ctx.set_source(radgrad(hx, hy, 0, 30 * u, [(0, '#ffffff'), (0.6, '#fff3cf'), (1, '#ffe08a')]))
        circle(ctx, hx, hy, 29 * u); ctx.fill()
        rays(ctx, hx, hy, t, '#fff0c0', 0.10, n=8, length=170 * u, seed=seed + 4)
    else:
        src(ctx, shade(skin, -0.25)); ctx.rectangle(hx - 8 * u, hy + 14 * u, 16 * u, 18 * u); ctx.fill()
        ctx.set_source(radgrad(hx + sun_dir * 8 * u, hy - 6 * u, 2 * u, 34 * u, [(0, shade(skin, 0.15)), (1, shade(skin, -0.2))]))
        ellipse(ctx, hx, hy, 25 * u, 28 * u); ctx.fill()
        # ear
        src(ctx, shade(skin, -0.2)); ellipse(ctx, hx - facing * 23 * u, hy + 2 * u, 5 * u, 8 * u); ctx.fill()
        fx = hx + facing * 5 * u
        # nose
        src(ctx, shade(skin, -0.18), 0.9)
        poly(ctx, [(fx + facing * 6 * u, hy - 6 * u), (fx + facing * 12 * u, hy + 7 * u), (fx + facing * 4 * u, hy + 8 * u)]); ctx.fill()
        # beard
        if beard:
            ctx.set_source(lingrad(0, hy, 0, hy + 46 * u, [(0, shade(beard, 0.1)), (1, shade(beard, -0.15))]))
            ctx.move_to(hx - 23 * u, hy - 2 * u)
            ctx.curve_to(hx - 24 * u, hy + 26 * u, fx - 12 * u, hy + 46 * u, fx, hy + 47 * u)
            ctx.curve_to(fx + 12 * u, hy + 46 * u, hx + 24 * u, hy + 26 * u, hx + 23 * u, hy - 2 * u)
            ctx.curve_to(hx + 20 * u, hy + 8 * u, hx + 16 * u, hy + 12 * u, fx + 10 * u, hy + 13 * u)
            ctx.curve_to(fx + 4 * u, hy + 10 * u, fx - 4 * u, hy + 10 * u, fx - 10 * u, hy + 13 * u)
            ctx.curve_to(hx - 16 * u, hy + 12 * u, hx - 20 * u, hy + 8 * u, hx - 23 * u, hy - 2 * u)
            ctx.close_path(); ctx.fill()
            # mouth hint
            src(ctx, shade(skin, -0.45), 0.7); ctx.set_line_width(2 * u)
            ctx.move_to(fx - 6 * u, hy + 20 * u); ctx.curve_to(fx - 2 * u, hy + 22 * u, fx + 2 * u, hy + 22 * u, fx + 6 * u, hy + 20 * u); ctx.stroke()
            src(ctx, shade(beard, 0.2), 0.45); ctx.set_line_width(1.2 * u)
            for k in range(5):
                xx = hx + (-16 + k * 8) * u
                ctx.move_to(xx, hy + 24 * u); ctx.line_to(xx + (fx - hx) * 0.3, hy + 38 * u); ctx.stroke()
    if head == 'turban' or head == 'crown':
        tc = C(turban)
        if prophet: tc = mix(tc, '#ffffff', 0.3)
        ctx.set_source(radgrad(hx + sun_dir * 6 * u, hy - 26 * u, 2 * u, 40 * u, [(0, shade(tc, 0.18)), (1, shade(tc, -0.25))]))
        ellipse(ctx, hx - facing * 2 * u, hy - 17 * u, 31 * u, 21 * u); ctx.fill()
        src(ctx, shade(tc, -0.3), 0.6); ctx.set_line_width(2 * u)
        for k in range(3):
            ctx.move_to(hx - 30 * u, hy - 12 * u - k * 9 * u)
            ctx.curve_to(hx - 8 * u, hy - 4 * u - k * 9 * u, hx + 10 * u, hy - 22 * u - k * 9 * u, hx + 30 * u, hy - 14 * u - k * 9 * u)
            ctx.stroke()
        # tail cloth
        ctx.set_source(lingrad(0, hy - 10 * u, 0, hy + 40 * u, [(0, shade(tc, -0.1)), (1, shade(tc, -0.35))]))
        tw = math.sin(t * 2.5 + seed) * 4 * u * wind
        ctx.move_to(hx - facing * 24 * u, hy - 10 * u)
        ctx.curve_to(hx - facing * 34 * u + tw, hy + 10 * u, hx - facing * 32 * u + tw * 1.5, hy + 30 * u, hx - facing * 30 * u + tw * 2, hy + 44 * u)
        ctx.line_to(hx - facing * 20 * u + tw * 2, hy + 40 * u)
        ctx.curve_to(hx - facing * 22 * u, hy + 20 * u, hx - facing * 18 * u, hy, hx - facing * 14 * u, hy - 8 * u)
        ctx.close_path(); ctx.fill()
        if head == 'crown':
            ctx.set_source(lingrad(hx - 30 * u, 0, hx + 30 * u, 0, [(0, '#9c7426'), (0.5, '#f7dc8a'), (1, '#9c7426')]))
            ctx.rectangle(hx - 30 * u, hy - 20 * u, 60 * u, 7 * u); ctx.fill()
            src(ctx, '#c0262a'); circle(ctx, hx + facing * 4 * u, hy - 16 * u, 5 * u); ctx.fill()
            src(ctx, '#f7dc8a')
            for k in range(-2, 3):
                poly(ctx, [(hx + k * 11 * u - 5 * u, hy - 20 * u), (hx + k * 11 * u, hy - 34 * u - (6 * u if k == 0 else 0)), (hx + k * 11 * u + 5 * u, hy - 20 * u)]); ctx.fill()
    elif head == 'helmet':
        src(ctx, '#3a2c22'); ellipse(ctx, hx - facing * 6 * u, hy + 4 * u, 25 * u, 26 * u); ctx.fill()
        ctx.set_source(radgrad(hx + 8 * u, hy - 26 * u, 2 * u, 40 * u, [(0, '#d9d4c7'), (0.5, '#8a8577'), (1, '#45423a')]))
        ctx.move_to(hx - 29 * u, hy - 4 * u); ctx.curve_to(hx - 30 * u, hy - 44 * u, hx + 30 * u, hy - 44 * u, hx + 29 * u, hy - 4 * u)
        ctx.close_path(); ctx.fill()
        src(ctx, '#e8e2d0'); poly(ctx, [(hx - 2 * u, hy - 38 * u), (hx, hy - 52 * u), (hx + 2 * u, hy - 38 * u)]); ctx.fill()
        src(ctx, '#5a554b'); ctx.rectangle(hx - 29 * u, hy - 8 * u, 58 * u, 5 * u); ctx.fill()
    elif head == 'hood':
        src(ctx, turban); ctx.move_to(hx - 30 * u, hy + 30 * u)
        ctx.curve_to(hx - 36 * u, hy - 40 * u, hx + 36 * u, hy - 40 * u, hx + 30 * u, hy + 30 * u); ctx.close_path(); ctx.fill()
    ctx.restore()
    # front arm
    arm(facing, a0, elbows[0], True, prop)
    ctx.restore()
    if alpha_ < 1:
        ctx.pop_group_to_source(); ctx.paint_with_alpha(alpha_)

def draw_prop(ctx, kind, hx, hy, ang, u, t, facing):
    ctx.save(); ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    if kind == 'spear':
        src(ctx, '#5a3d22'); ctx.set_line_width(5 * u)
        ctx.move_to(hx - facing * 6 * u, hy + 90 * u); ctx.line_to(hx + facing * 10 * u, hy - 170 * u); ctx.stroke()
        src(ctx, '#cfcabd'); poly(ctx, [(hx + facing * 7 * u, hy - 166 * u), (hx + facing * 14 * u, hy - 205 * u), (hx + facing * 17 * u, hy - 166 * u)]); ctx.fill()
    elif kind == 'shield':
        ctx.set_source(radgrad(hx, hy, 0, 40 * u, [(0, '#b8892e'), (0.8, '#7a4e1e'), (1, '#3b2610')]))
        circle(ctx, hx + facing * 6 * u, hy - 10 * u, 38 * u); ctx.fill()
        src(ctx, '#e3c46a'); circle(ctx, hx + facing * 6 * u, hy - 10 * u, 8 * u); ctx.fill()
    elif kind == 'torch':
        src(ctx, '#4a3020'); ctx.set_line_width(7 * u)
        ctx.move_to(hx, hy + 30 * u); ctx.line_to(hx + facing * 6 * u, hy - 50 * u); ctx.stroke()
        flame(ctx, hx + facing * 6 * u, hy - 52 * u, 22 * u, 60 * u, t, seed=int(hx) % 17)
    elif kind == 'axe':
        ctx.save(); ctx.translate(hx, hy); ctx.rotate(facing * (PI - ang) * 1.0)
        src(ctx, '#5a3d22'); ctx.set_line_width(6 * u)
        ctx.move_to(0, 10 * u); ctx.line_to(0, -95 * u); ctx.stroke()
        ctx.set_source(lingrad(0, -100 * u, facing * 40 * u, -70 * u, [(0, '#e6e6e0'), (1, '#6f6d66')]))
        ctx.move_to(0, -96 * u); ctx.curve_to(facing * 30 * u, -110 * u, facing * 44 * u, -90 * u, facing * 40 * u, -62 * u)
        ctx.curve_to(facing * 28 * u, -68 * u, facing * 10 * u, -70 * u, 0, -72 * u); ctx.close_path(); ctx.fill()
        ctx.restore()
    elif kind == 'banner':
        src(ctx, '#4a3020'); ctx.set_line_width(5 * u)
        ctx.move_to(hx, hy + 60 * u); ctx.line_to(hx, hy - 220 * u); ctx.stroke()
        wv = math.sin(t * 3) * 10 * u
        ctx.move_to(hx, hy - 215 * u)
        ctx.curve_to(hx - facing * 40 * u, hy - 225 * u + wv, hx - facing * 80 * u, hy - 205 * u - wv, hx - facing * 110 * u, hy - 212 * u + wv)
        ctx.line_to(hx - facing * 110 * u, hy - 150 * u + wv)
        ctx.curve_to(hx - facing * 80 * u, hy - 145 * u - wv, hx - facing * 40 * u, hy - 165 * u + wv, hx, hy - 155 * u)
        ctx.close_path(); src(ctx, '#8e1f1f'); ctx.fill()
    ctx.restore()

# ---------------- fire ----------------
def flame(ctx, x, y, w, h, t, seed=0, cool=0.0, a=1.0):
    ctx.save(); ctx.set_operator(cairo.OPERATOR_ADD)
    for k in range(3):
        ph = t * 9 + seed + k * 2.1
        hh = h * (0.75 + 0.25 * math.sin(ph) + 0.1 * math.sin(ph * 2.3)) * (1 - k * 0.22)
        ww = w * (1 - k * 0.25)
        tip = math.sin(ph * 0.7) * ww * 0.5
        outer = mix('#ff5a1a', '#4fb4ff', cool); mid = mix('#ffb12e', '#9fe0ff', cool); core = mix('#fff1b0', '#cfefff', cool)
        g = lingrad(0, y, 0, y - hh, [(0, alpha(core, 0.42 * a)), (0.3, alpha(mid, 0.4 * a)), (0.7, alpha(outer, 0.3 * a)), (1, alpha(outer, 0))])
        ctx.set_source(g)
        ctx.move_to(x - ww, y)
        ctx.curve_to(x - ww, y - hh * 0.5, x + tip - ww * 0.2, y - hh * 0.8, x + tip, y - hh)
        ctx.curve_to(x + tip + ww * 0.2, y - hh * 0.8, x + ww, y - hh * 0.5, x + ww, y)
        ctx.curve_to(x + ww * 0.5, y + ww * 0.4, x - ww * 0.5, y + ww * 0.4, x - ww, y)
        ctx.close_path(); ctx.fill()
    ctx.restore()

def bonfire(ctx, x, y, w, h, t, cool=0.0, seed=1, n=20, intensity=1.0):
    r = rnd(seed)
    glow(ctx, x, y - h * 0.35, w * 1.4, mix('#ff6a1a', '#7fd4ff', cool), 0.32 * intensity)
    ctx.set_source(radgrad(x, y, 0, w * 0.6, [(0, mix('#ffb04a', '#cdeeff', cool)), (0.5, mix('#a8380e', '#3a7a9a', cool)), (1, (0.1, 0.05, 0.03, 0))]))
    ellipse(ctx, x, y + 10, w * 0.6, 40); ctx.fill()
    # logs
    for i in range(10):
        lx = x + r.uniform(-0.8, 0.8) * w * 0.5; ang = r.uniform(-0.5, 0.5)
        ctx.save(); ctx.translate(lx, y - r.uniform(0, 20)); ctx.rotate(ang)
        src(ctx, mix('#2a1a10', '#1a2a33', cool)); rrect(ctx, -w * 0.18, -9, w * 0.36, 18, 8); ctx.fill()
        src(ctx, mix('#ff6a1a', '#8fe8ff', cool), 0.6 * intensity); ctx.rectangle(-w * 0.16, -2, w * 0.32, 4); ctx.fill()
        ctx.restore()
    for i in range(n):
        fx = x + r.uniform(-1, 1) * w * 0.48 * (1 - 0.3 * r.random())
        cen = 1 - abs(fx - x) / (w * 0.5)
        fh = h * (0.35 + 0.65 * cen) * r.uniform(0.6, 1.1) * intensity * (1 - 0.55 * cool)
        flame(ctx, fx, y + r.uniform(-10, 10), w * r.uniform(0.07, 0.12), fh, t, seed=r.uniform(0, 50), cool=cool, a=0.75 + 0.25 * cen)
    # embers
    for i in range(40):
        ph = r.uniform(0, 1); sp = r.uniform(0.25, 0.6)
        life = (t * sp + ph) % 1.0
        ex = x + r.uniform(-0.5, 0.5) * w + math.sin(t * 2 + i) * 30 * life
        ey = y - life * h * 1.6
        src(ctx, mix('#ffcf6a', '#d9f6ff', cool), (1 - life) * 0.9 * intensity)
        circle(ctx, ex, ey, r.uniform(1.5, 4)); ctx.fill()

def smoke(ctx, x, y, t, s=1.0, a=0.35, seed=2, n=10, c='#2b2622'):
    r = rnd(seed)
    for i in range(n):
        ph = r.uniform(0, 1); life = (t * 0.08 + ph) % 1.0
        sx = x + r.uniform(-60, 60) * s + life * 160 * s + math.sin(t * 0.5 + i) * 20 * s
        sy = y - life * 900 * s
        rr = (60 + life * 220) * s
        cc = C(c)
        g = cairo.RadialGradient(sx, sy, 0, sx, sy, rr)
        g.add_color_stop_rgba(0, cc[0], cc[1], cc[2], a * math.sin(life * PI))
        g.add_color_stop_rgba(1, cc[0], cc[1], cc[2], 0)
        ctx.set_source(g); circle(ctx, sx, sy, rr); ctx.fill()

# ---------------- animals ----------------
def elephant(ctx, x, y, s, t, facing=1, walk=0.0, phase=0.0, kneel=0.0, trunk=0.0, sun_dir=1, deco=True, ear_speed=1.0):
    u = s
    ctx.save(); ctx.translate(x, y); ctx.scale(facing, 1)
    shadow(ctx, -10 * u * sun_dir * facing, 0, 230 * u, 0.32)
    drop = kneel * 105 * u
    pitch = math.atan2(drop, 220 * u)
    gray = '#7b7570'; dark = '#4c4743'; light = '#a39c95'
    hipx, hipy = -115 * u, -195 * u
    def bodyT(px, py):
        # rotate around hip
        dx, dy = px - hipx, py - hipy
        c, sn = math.cos(pitch), math.sin(pitch)
        return hipx + dx * c - dy * sn, hipy + dx * sn + dy * c
    def leg(jx, jy, phase_off, near, front):
        col = gray if near else dark
        sw = math.sin(phase + phase_off) * 0.28 * walk
        lift_ = max(0, math.cos(phase + phase_off)) * 14 * u * walk
        if front and kneel > 0:
            kx_s, ky_s = jx + math.sin(sw) * 70 * u, jy + 75 * u
            fx_s, fy_s = jx + math.sin(sw) * 110 * u * 0.4, -lift_
            kx_k, ky_k = jx + 30 * u, -18 * u
            fx_k, fy_k = jx - 55 * u, -12 * u
            kx, ky = lerp(kx_s, kx_k, kneel), lerp(ky_s, ky_k, kneel)
            fx, fy = lerp(fx_s, fx_k, kneel), lerp(fy_s, fy_k, kneel)
        else:
            kx, ky = jx + math.sin(sw) * 36 * u, jy + (0 - jy) * 0.5
            fx, fy = jx + math.sin(sw) * 80 * u, -lift_
        ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_line_join(cairo.LINE_JOIN_ROUND)
        src(ctx, shade(col, -0.25)); ctx.set_line_width(64 * u)
        ctx.move_to(jx, jy); ctx.line_to(kx, ky); ctx.line_to(fx, fy - 12 * u); ctx.stroke()
        src(ctx, col); ctx.set_line_width(56 * u)
        ctx.move_to(jx, jy); ctx.line_to(kx, ky); ctx.line_to(fx, fy - 12 * u); ctx.stroke()
        src(ctx, shade(col, -0.35), 0.5); ctx.set_line_width(1.5 * u)
        for k in range(3):
            yy = lerp(ky, fy, 0.3 + k * 0.2)
            xx = lerp(kx, fx, 0.3 + k * 0.2)
            ctx.move_to(xx - 18 * u, yy); ctx.line_to(xx + 18 * u, yy + 3 * u); ctx.stroke()
        src(ctx, '#d8d2c6'); ellipse(ctx, fx, fy - 4 * u, 26 * u, 9 * u); ctx.fill()
    # far legs
    leg(*bodyT(95 * u, -150 * u), PI, False, True)
    leg(-110 * u, -150 * u, 0, False, False)
    # body
    ctx.save()
    ctx.translate(hipx, hipy); ctx.rotate(pitch); ctx.translate(-hipx, -hipy)
    ctx.set_source(radgrad(0, -230 * u, 10 * u, 200 * u, [(0, light), (0.6, gray), (1, dark)], cx=sun_dir * facing * 40 * u, cy=-290 * u))
    ellipse(ctx, 0, -215 * u, 170 * u, 108 * u); ctx.fill()
    # tail
    src(ctx, dark); ctx.set_line_width(7 * u)
    tw = math.sin(t * 2.2) * 12 * u
    ctx.move_to(-165 * u, -240 * u); ctx.curve_to(-185 * u, -200 * u, -180 * u + tw, -160 * u, -176 * u + tw, -130 * u); ctx.stroke()
    if deco:
        # caparison
        ctx.set_source(lingrad(0, -300 * u, 0, -140 * u, [(0, '#a3222a'), (1, '#5e1016')]))
        ctx.move_to(-110 * u, -305 * u); ctx.curve_to(-40 * u, -330 * u, 50 * u, -330 * u, 110 * u, -300 * u)
        ctx.line_to(100 * u, -165 * u); ctx.curve_to(40 * u, -150 * u, -40 * u, -150 * u, -100 * u, -165 * u); ctx.close_path(); ctx.fill()
        src(ctx, '#e7c063'); ctx.set_line_width(6 * u)
        ctx.move_to(100 * u, -170 * u); ctx.curve_to(40 * u, -155 * u, -40 * u, -155 * u, -100 * u, -170 * u); ctx.stroke()
        for k in range(9):
            xx = -90 * u + k * 22.5 * u
            yy = -160 * u - 8 * u * math.sin(k / 8 * PI)
            src(ctx, '#e7c063'); circle(ctx, xx, yy + 10 * u, 5 * u); ctx.fill()
        ctx.set_line_width(3 * u); src(ctx, '#e7c063')
        ctx.move_to(-60 * u, -300 * u); ctx.line_to(-50 * u, -180 * u); ctx.stroke()
        ctx.move_to(60 * u, -300 * u); ctx.line_to(50 * u, -180 * u); ctx.stroke()
        # howdah
        ctx.set_source(lingrad(-70 * u, 0, 70 * u, 0, [(0, '#6e4a1f'), (0.5, '#c9973f'), (1, '#6e4a1f')]))
        rrect(ctx, -55 * u, -360 * u, 110 * u, 48 * u, 8 * u); ctx.fill()
        src(ctx, '#3a250f')
        for k in range(4):
            rrect(ctx, -44 * u + k * 24 * u, -352 * u, 14 * u, 28 * u, 6 * u); ctx.fill()
        ctx.set_source(lingrad(0, -400 * u, 0, -360 * u, [(0, '#f0d48a'), (1, '#a5782c')]))
        ctx.move_to(-66 * u, -360 * u); ctx.curve_to(-50 * u, -396 * u, 50 * u, -396 * u, 66 * u, -360 * u); ctx.close_path(); ctx.fill()
        src(ctx, '#f0d48a'); circle(ctx, 0, -394 * u, 6 * u); ctx.fill()
    ctx.restore()
    # near legs
    leg(-85 * u, -150 * u, PI * 0.5, True, False)
    jx, jy = bodyT(120 * u, -150 * u)
    leg(jx, jy, PI * 1.5, True, True)
    # head
    hx, hy = bodyT(175 * u, -250 * u)
    hy += kneel * 25 * u
    ctx.save(); ctx.translate(hx, hy); ctx.rotate(pitch * 1.4 + kneel * 0.15)
    ef = math.sin(t * 2.0 * ear_speed) * 0.12
    # ear
    ctx.save(); ctx.translate(-30 * u, -20 * u); ctx.scale(1 + ef, 1)
    ctx.set_source(radgrad(0, 0, 5 * u, 110 * u, [(0, '#8e8782'), (1, '#5a5450')]))
    ctx.move_to(0, -70 * u); ctx.curve_to(-110 * u, -90 * u, -120 * u, 40 * u, -60 * u, 90 * u)
    ctx.curve_to(-30 * u, 110 * u, 0, 70 * u, 10 * u, 40 * u); ctx.close_path(); ctx.fill()
    src(ctx, '#4a4440', 0.6); ctx.set_line_width(2 * u)
    ctx.move_to(-20 * u, -40 * u); ctx.curve_to(-70 * u, -40 * u, -80 * u, 30 * u, -50 * u, 70 * u); ctx.stroke()
    ctx.restore()
    ctx.set_source(radgrad(10 * u, -10 * u, 5 * u, 100 * u, [(0, light), (0.7, gray), (1, dark)], cx=30 * u, cy=-40 * u))
    ellipse(ctx, 20 * u, 0, 72 * u, 78 * u); ctx.fill()
    if deco:
        ctx.set_source(lingrad(0, -80 * u, 0, -20 * u, [(0, '#c0262a'), (1, '#6e1218')]))
        ctx.move_to(-10 * u, -74 * u); ctx.curve_to(40 * u, -84 * u, 80 * u, -60 * u, 88 * u, -20 * u)
        ctx.curve_to(60 * u, -10 * u, 30 * u, -30 * u, 0, -20 * u); ctx.close_path(); ctx.fill()
        src(ctx, '#e7c063'); circle(ctx, 60 * u, -40 * u, 7 * u); ctx.fill()
    # eye
    src(ctx, '#1d1a18'); ellipse(ctx, 52 * u, -14 * u, 5 * u, 4 * u); ctx.fill()
    src(ctx, shade(dark, -0.2), 0.7); ctx.set_line_width(2 * u)
    ctx.move_to(42 * u, -22 * u); ctx.curve_to(50 * u, -26 * u, 58 * u, -24 * u, 62 * u, -19 * u); ctx.stroke()
    # trunk
    pts = [(70 * u, 20 * u)]
    ang = PI / 2 - 0.25 - trunk * 1.6
    seg = 22 * u
    for i in range(11):
        sway = math.sin(t * 1.4 - i * 0.35) * 0.06 * (1 + i * 0.15)
        ang += (0.05 + trunk * 0.12) * (1 if i > 5 else 0.4) + sway
        if trunk > 0 and i > 6: ang -= trunk * 0.5
        px, py = pts[-1]
        pts.append((px + math.cos(ang) * seg, py + math.sin(ang) * seg))
    for i in range(len(pts) - 1):
        wd = lerp(52, 16, i / (len(pts) - 1)) * u
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        src(ctx, shade(gray, -0.15 - 0.15 * (i / 11))); ctx.set_line_width(wd)
        ctx.move_to(*pts[i]); ctx.line_to(*pts[i + 1]); ctx.stroke()
    src(ctx, shade(dark, -0.2), 0.5); ctx.set_line_width(1.5 * u)
    for i in range(1, len(pts) - 1):
        px, py = pts[i]; nx, ny = pts[i + 1][0] - px, pts[i + 1][1] - py; nn = math.hypot(nx, ny)
        wd = lerp(52, 16, i / (len(pts) - 1)) * u * 0.45
        ctx.move_to(px - ny / nn * wd, py + nx / nn * wd); ctx.line_to(px + ny / nn * wd, py - nx / nn * wd); ctx.stroke()
    # tusk
    ctx.set_source(lingrad(60 * u, 30 * u, 120 * u, 70 * u, [(0, '#f6f0df'), (1, '#c9bfa4')]))
    ctx.move_to(56 * u, 36 * u); ctx.curve_to(80 * u, 80 * u, 120 * u, 86 * u, 140 * u, 62 * u)
    ctx.curve_to(115 * u, 70 * u, 86 * u, 60 * u, 74 * u, 28 * u); ctx.close_path(); ctx.fill()
    ctx.restore()
    ctx.restore()

def bird(ctx, x, y, s, t, facing=1, phase=0.0, stones=True, c='#1d1814', glide=0.0):
    u = s
    ctx.save(); ctx.translate(x, y); ctx.scale(facing, 1)
    fl = math.sin(phase) * (1 - glide) + glide * 0.25
    def wing(sx, sy, L, col, k):
        wx, wy = sx - 4 * u, sy - fl * L * 0.48
        tx, ty = sx - 30 * u * k, sy - fl * L - 4 * u
        pts = [(sx, sy), (wx, wy - 3 * u), (tx, ty)]
        # trailing feathers
        n = 6
        for i in range(1, n + 1):
            f = i / n
            bx = lerp(tx, sx - 22 * u, f); by = lerp(ty, sy + 2 * u, f)
            px = bx - 7 * u * (1 - f * 0.5); py = by + 3 * u * (1 if fl >= 0 else -1) * (1 - f)
            pts.append((px, py)); pts.append((bx, by))
        ctx.move_to(*pts[0])
        ctx.curve_to(sx + 2 * u, (sy + wy) / 2, wx + 2 * u, wy, wx, wy - 3 * u)
        for p in pts[2:]: ctx.line_to(*p)
        ctx.close_path()
        ctx.set_source(lingrad(sx, sy, tx, ty, [(0, shade(col, 0.15)), (1, shade(col, -0.2))])); ctx.fill()
        src(ctx, shade(col, 0.3), 0.35); ctx.set_line_width(max(0.6, 0.8 * u))
        for i in range(1, 5):
            f = i / 5
            ctx.move_to(lerp(sx, wx, 0.5), lerp(sy, wy, 0.5)); ctx.line_to(lerp(tx, sx - 22 * u, f), lerp(ty, sy + 2 * u, f)); ctx.stroke()
    wing(-2 * u, -4 * u, 50 * u, shade(c, 0.18), 0.8)
    # tail
    src(ctx, shade(c, -0.05))
    poly(ctx, [(-18 * u, -3 * u), (-42 * u, -10 * u), (-46 * u, -2 * u), (-44 * u, 6 * u), (-18 * u, 3 * u)]); ctx.fill()
    # body
    ctx.set_source(lingrad(0, -10 * u, 0, 8 * u, [(0, shade(c, 0.2)), (1, shade(c, -0.15))]))
    ctx.move_to(-20 * u, 0)
    ctx.curve_to(-12 * u, -10 * u, 8 * u, -11 * u, 18 * u, -9 * u)
    ctx.curve_to(26 * u, -8 * u, 26 * u, 0, 18 * u, 2 * u)
    ctx.curve_to(6 * u, 9 * u, -12 * u, 7 * u, -20 * u, 0)
    ctx.close_path(); ctx.fill()
    src(ctx, shade(c, 0.1)); circle(ctx, 20 * u, -7 * u, 6.5 * u); ctx.fill()
    src(ctx, '#b07a2a'); poly(ctx, [(25 * u, -9 * u), (33 * u, -6 * u), (25 * u, -4 * u)]); ctx.fill()
    if stones:
        ctx.set_source(radgrad(33 * u, -6 * u, 0, 4 * u, [(0, '#d06a3a'), (1, '#6e2a16')])); circle(ctx, 33.5 * u, -6 * u, 3.4 * u); ctx.fill()
        for dx in (-7, 5):
            src(ctx, '#3a2a1c'); ctx.set_line_width(max(0.8, 1.6 * u)); ctx.move_to(dx * u, 4 * u); ctx.line_to(dx * u - 2 * u, 11 * u); ctx.stroke()
            ctx.set_source(radgrad(dx * u - 2 * u, 14 * u, 0, 5 * u, [(0, '#d06a3a'), (1, '#6e2a16')])); circle(ctx, dx * u - 2 * u, 14 * u, 4.2 * u); ctx.fill()
    wing(2 * u, -5 * u, 62 * u, c, 1.0)
    ctx.restore()

# ---------------- idols ----------------
STONE = '#9a8670'
def idol_parts(kind, s):
    """humanoid statue: list of (polygon, shade, color override)"""
    k = {'big': 1.0, 'mid': 0.66, 'small': 0.48}[kind] * s
    def P(pts): return [(px * k, py * k) for px, py in pts]
    parts = []
    parts.append((P([(-72, 0), (72, 0), (64, -34), (-64, -34)]), -0.3, None))
    parts.append((P([(-52, -34), (52, -34), (40, -168), (-40, -168)]), 0.0, None))
    parts.append((P([(-42, -168), (42, -168), (60, -248), (34, -262), (-34, -262), (-60, -248)]), 0.06, None))
    parts.append((P([(-60, -248), (-46, -244), (-44, -150), (-52, -140), (-66, -150)]), -0.12, None))
    parts.append((P([(60, -248), (46, -244), (44, -150), (52, -140), (66, -150)]), -0.12, None))
    oc = [(math.cos(i / 8 * 2 * PI) * 28, -292 + math.sin(i / 8 * 2 * PI) * 32) for i in range(8)]
    parts.append((P(oc), 0.1, None))
    if kind == 'big':
        parts.append((P([(-32, -316), (-24, -352), (-12, -324), (0, -364), (12, -324), (24, -352), (32, -316)]), 0.1, '#c9a24a'))
        parts.append((P([(-40, -248), (40, -248), (28, -228), (0, -220), (-28, -228)]), 0.0, '#c9a24a'))
    elif kind == 'mid':
        parts.append((P([(-30, -318), (30, -318), (22, -340), (-22, -340)]), 0.15, None))
    return parts

def idol(ctx, x, y, s, kind='mid', c=STONE, brk=-1.0, t=0.0, seed=0, floor=None, sun_dir=1, glow_a=0.0):
    parts = idol_parts(kind, s)
    r = rnd(seed)
    floor = y if floor is None else floor
    if brk < 0:
        shadow(ctx, x - sun_dir * 10 * s, y, 70 * s * (1.4 if kind == 'big' else 1), 0.3)
    if glow_a > 0:
        glow(ctx, x, y - 120 * s, 200 * s, '#ffb35a', glow_a)
    for i, (pts, sh, ovc) in enumerate(parts):
        pc = ovc or c
        cx = sum(p[0] for p in pts) / len(pts); cy = sum(p[1] for p in pts) / len(pts)
        vx = r.uniform(-260, 260) * s; vy = r.uniform(-420, -150) * s; vr = r.uniform(-6, 6)
        ctx.save()
        if brk >= 0 and i > 0:
            tt = brk
            g = 1600 * s
            px = cx + vx * tt; py = cy + vy * tt + 0.5 * g * tt * tt
            # ground contact
            lim = (floor - y) - 12 * s - r.uniform(0, 8) * s
            rot = vr * tt
            if py > lim:
                # find landing time
                a_, b_, c_ = 0.5 * g, vy, cy - lim
                disc = b_ * b_ - 4 * a_ * c_
                tl = (-b_ + math.sqrt(max(0, disc))) / (2 * a_)
                px = cx + vx * tl + vx * 0.15 * (1 - math.exp(-(tt - tl) * 6))
                py = lim
                rot = vr * tl + vr * 0.1 * (1 - math.exp(-(tt - tl) * 6))
            ctx.translate(x + px, y + py); ctx.rotate(rot); ctx.translate(-cx, -cy)
        else:
            ctx.translate(x, y)
        poly(ctx, pts)
        ctx.set_source(lingrad(-60 * s * sun_dir, 0, 60 * s * sun_dir, 0, [(0, shade(pc, sh - 0.25)), (1, shade(pc, sh + 0.15))]))
        ctx.fill_preserve()
        src(ctx, shade(pc, -0.45), 0.6); ctx.set_line_width(1.5 * s); ctx.stroke()
        # carved lines
        src(ctx, shade(pc, -0.35), 0.22); ctx.set_line_width(1.5 * s)
        xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
        if max(ys) - min(ys) > 100 * s:
            for k in range(1):
                yy = lerp(min(ys), max(ys), 0.3 + k * 0.35)
                ctx.move_to(min(xs) + 6 * s, yy); ctx.line_to(max(xs) - 6 * s, yy + 2 * s); ctx.stroke()
        ctx.restore()

def pedestal(ctx, x, y, w, h, c='#8b7258'):
    box(ctx, x - w / 2, y, w, h, 30, c)

# ---------------- text ----------------
GOLD = '#f5c542'
def set_font(ctx, size, face='Montserrat', bold=True):
    ctx.select_font_face(face, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD if bold else cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(size)

def text_w(ctx, s):
    return ctx.text_extents(s).x_advance

def outlined(ctx, s, x, y, fill=(1, 1, 1, 1), stroke=(0, 0, 0, 0.85), sw=8, shadow_=True):
    if shadow_:
        ctx.move_to(x + 3, y + 5); ctx.text_path(s); src(ctx, (0, 0, 0), 0.35); ctx.fill()
    ctx.move_to(x, y); ctx.text_path(s)
    src(ctx, stroke); ctx.set_line_width(sw); ctx.set_line_join(cairo.LINE_JOIN_ROUND); ctx.stroke_preserve()
    src(ctx, fill); ctx.fill()

def chunk_words(words, maxc=22):
    chunks = []; cur = []
    for w in words:
        L = sum(len(x[2]) + 1 for x in cur) + len(w[2])
        if cur and (L > maxc or cur[-1][2][-1] in '.,:!?' and len(cur) >= 2):
            chunks.append(cur); cur = []
        cur.append(w)
    if cur: chunks.append(cur)
    return chunks

def build_subs(al):
    subs = []
    for si, s in enumerate(al['sentences']):
        for ch in chunk_words(s['words']):
            subs.append({'si': si, 'start': ch[0][0], 'end': ch[-1][1], 'words': ch})
    for i in range(len(subs) - 1):
        if subs[i + 1]['start'] - subs[i]['end'] < 0.6:
            subs[i]['end'] = subs[i + 1]['start']
    for i in range(len(subs)):
        subs[i]['hide'] = subs[i + 1]['start'] - 0.05 if i + 1 < len(subs) else subs[i]['end'] + 0.4
    return subs

def draw_subs(ctx, subs, t, y=1560, size=66):
    for sb in subs:
        hide = min(sb['end'] + 0.3, sb['hide'])
        if sb['start'] - 0.05 <= t < hide:
            a = clamp((t - sb['start'] + 0.05) / 0.06) * (1 if sb['hide'] < sb['end'] + 0.3 else clamp((hide - t) / 0.2))
            set_font(ctx, size)
            words = [w[2] for w in sb['words']]
            sp = text_w(ctx, ' ') * 1.35
            ws = [text_w(ctx, w) for w in words]
            total = sum(ws) + sp * (len(ws) - 1)
            sc = min(1.0, 960 / total)
            ctx.save(); ctx.translate(540, y); ctx.scale(sc, sc)
            x = -total / 2
            for k, w in enumerate(sb['words']):
                active = w[0] <= t < w[1] + 0.02
                done = t >= w[1]
                pop = 1 + 0.08 * clamp(1 - (t - w[0]) / 0.18) if active else 1
                col = C(GOLD) if active else (1, 1, 1, 1)
                ctx.save(); ctx.translate(x + ws[k] / 2, 0); ctx.scale(pop, pop)
                outlined(ctx, w[2], -ws[k] / 2, 0, fill=alpha(col, a), stroke=(0, 0, 0, 0.85 * a), sw=9)
                ctx.restore()
                x += ws[k] + sp
            ctx.restore()

def draw_kw(ctx, text, t, t0, t1, y=330, col=(1, 1, 1, 1), face='Cinzel', maxsize=68, glowc=GOLD):
    if not (t0 <= t <= t1): return
    a = eo((t - t0) / 0.35) * clamp((t1 - t) / 0.35)
    sc_in = 0.9 + 0.1 * eo((t - t0) / 0.5)
    set_font(ctx, 100, face)
    nat = text_w(ctx, text)
    size = min(maxsize, 100 * 860 / nat)
    lines = [text]
    if size < 46:
        ws = text.split()
        best = None
        for k in range(1, len(ws)):
            l1 = ' '.join(ws[:k]); l2 = ' '.join(ws[k:])
            m = max(text_w(ctx, l1), text_w(ctx, l2))
            if best is None or m < best[0]: best = (m, l1, l2)
        if best:
            lines = [best[1], best[2]]
            size = min(maxsize, 100 * 860 / best[0])
    set_font(ctx, size, face)
    ctx.save(); ctx.translate(540, y); ctx.scale(sc_in, sc_in)
    lh = size * 1.15
    y0 = -(len(lines) - 1) * lh / 2
    for i, ln in enumerate(lines):
        w = text_w(ctx, ln)
        ext = ctx.text_extents(ln)
        yy = y0 + i * lh + ext.height / 2
        # soft glow
        for gg in range(3):
            ctx.move_to(-w / 2, yy); ctx.text_path(ln)
            src(ctx, (0, 0, 0), 0.22 * a / (gg + 1)); ctx.set_line_width(10 + gg * 10); ctx.stroke()
        ctx.move_to(-w / 2, yy); ctx.text_path(ln)
        src(ctx, alpha(col, a)); ctx.fill()
    if len(lines) == 1:
        w = text_w(ctx, lines[0])
        src(ctx, glowc, 0.8 * a); ctx.set_line_width(3)
        L = 70 * eo((t - t0) / 0.6)
        ctx.move_to(-w / 2 - 24, 0); ctx.line_to(-w / 2 - 24 - L, 0); ctx.stroke()
        ctx.move_to(w / 2 + 24, 0); ctx.line_to(w / 2 + 24 + L, 0); ctx.stroke()
    ctx.restore()

def draw_chip(ctx, text, t, t0, t1, y=440, col=GOLD):
    if not (t0 <= t <= t1): return
    a = eo((t - t0) / 0.3) * clamp((t1 - t) / 0.3)
    set_font(ctx, 34)
    w = text_w(ctx, text)
    sc = min(1.0, 900 / (w + 60))
    ctx.save(); ctx.translate(540, y); ctx.scale(sc, sc)
    rrect(ctx, -w / 2 - 28, -30, w + 56, 60, 30); src(ctx, (0.05, 0.04, 0.03), 0.6 * a); ctx.fill_preserve()
    src(ctx, col, 0.9 * a); ctx.set_line_width(2.5); ctx.stroke()
    ctx.move_to(-w / 2, 12); src(ctx, (1, 0.97, 0.9), a); ctx.show_text(text)
    ctx.restore()

def wrap(ctx, text, maxw):
    lines = []; cur = ''
    for w in text.split():
        tst = (cur + ' ' + w).strip()
        if text_w(ctx, tst) > maxw and cur:
            lines.append(cur); cur = w
        else:
            cur = tst
    if cur: lines.append(cur)
    return lines

def draw_quote(ctx, text, ref, t, t0, t1, y=560, size=50, face='Lora'):
    if not (t0 <= t <= t1): return
    a = eo((t - t0) / 0.5) * clamp((t1 - t) / 0.4)
    set_font(ctx, size, face)
    lines = wrap(ctx, text, 860)
    lh = size * 1.3
    hgt = len(lines) * lh + 110
    ctx.save(); ctx.translate(0, (1 - eo((t - t0) / 0.6)) * 30)
    rrect(ctx, 70, y - hgt / 2, 940, hgt, 28)
    src(ctx, (0.04, 0.03, 0.02), 0.55 * a); ctx.fill_preserve()
    src(ctx, GOLD, 0.7 * a); ctx.set_line_width(2); ctx.stroke()
    set_font(ctx, 90, 'Lora'); src(ctx, GOLD, 0.8 * a); ctx.move_to(96, y - hgt / 2 + 74); ctx.show_text('„')
    set_font(ctx, size, face)
    yy = y - hgt / 2 + 46 + lh * 0.75
    for ln in lines:
        w = text_w(ctx, ln)
        ctx.move_to(540 - w / 2, yy); src(ctx, (1, 0.98, 0.92), a); ctx.show_text(ln); yy += lh
    set_font(ctx, 30); w = text_w(ctx, ref)
    ctx.move_to(540 - w / 2, y + hgt / 2 - 26); src(ctx, GOLD, a); ctx.show_text(ref)
    ctx.restore()

def draw_speaker(ctx, name, t, t0, t1, y=1452):
    if not (t0 <= t <= t1): return
    a = eo((t - t0) / 0.25) * clamp((t1 - t) / 0.25)
    set_font(ctx, 32); w = text_w(ctx, name)
    rrect(ctx, 540 - w / 2 - 22, y - 26, w + 44, 48, 12); src(ctx, GOLD, 0.92 * a); ctx.fill()
    ctx.move_to(540 - w / 2, y + 10); src(ctx, (0.1, 0.07, 0.03), a); ctx.show_text(name)

def draw_title(ctx, title, sub, t, t0, t1, y=760):
    if not (t0 <= t <= t1): return
    a = eo((t - t0) / 0.6) * clamp((t1 - t) / 0.5)
    set_font(ctx, 100, 'Cinzel')
    lines = title.split('|')
    sizes = []
    for ln in lines:
        sizes.append(min(110, 100 * 900 / text_w(ctx, ln)))
    yy = y
    for ln, sz in zip(lines, sizes):
        set_font(ctx, sz, 'Cinzel')
        w = text_w(ctx, ln)
        sp = 1 + 0.04 * (1 - eo((t - t0) / 1.2))
        ctx.save(); ctx.translate(540, yy); ctx.scale(sp, sp)
        for gg in range(3):
            ctx.move_to(-w / 2, 0); ctx.text_path(ln); src(ctx, (0, 0, 0), 0.25 * a / (gg + 1)); ctx.set_line_width(12 + 12 * gg); ctx.stroke()
        ctx.move_to(-w / 2, 0); ctx.text_path(ln)
        ctx.set_source(lingrad(0, -sz, 0, 0, [(0, (1, 0.95, 0.8, a)), (1, alpha(GOLD, a))])); ctx.fill()
        ctx.restore()
        yy += sz * 1.12
    if sub:
        draw_chip(ctx, sub, t, t0 + 0.4, t1, y=yy + 20)

def end_card(ctx, t, t0, title, lines, note='Hinweis: Die Figuren sind nur symbolisch dargestellt.'):
    if t < t0: return
    a = eo((t - t0) / 0.7)
    src(ctx, (0.03, 0.025, 0.02), 0.78 * a); ctx.rectangle(0, 0, W, H); ctx.fill()
    set_font(ctx, 58, 'Cinzel'); w = text_w(ctx, title); sc = min(1, 900 / w)
    ctx.save(); ctx.translate(540, 640); ctx.scale(sc, sc); ctx.move_to(-w / 2, 0); src(ctx, GOLD, a); ctx.show_text(title); ctx.restore()
    src(ctx, GOLD, 0.6 * a); ctx.set_line_width(2); ctx.move_to(390, 690); ctx.line_to(690, 690); ctx.stroke()
    set_font(ctx, 36); src(ctx, (1, 1, 1), 0.7 * a)
    w = text_w(ctx, 'QUELLEN'); ctx.move_to(540 - w / 2, 770); ctx.show_text('QUELLEN')
    yy = 850
    for i, ln in enumerate(lines):
        aa = a * eo((t - t0 - 0.3 - i * 0.15) / 0.5)
        set_font(ctx, 40, 'Lora', bold=False)
        for sub in wrap(ctx, ln, 880):
            w = text_w(ctx, sub); ctx.move_to(540 - w / 2, yy); src(ctx, (1, 0.97, 0.9), aa); ctx.show_text(sub); yy += 54
        yy += 18
    set_font(ctx, 30, 'Montserrat', bold=False)
    for sub in wrap(ctx, note, 900):
        w = text_w(ctx, sub); ctx.move_to(540 - w / 2, yy + 60); src(ctx, (1, 1, 1), 0.55 * a); ctx.show_text(sub); yy += 40
    set_font(ctx, 44, 'Montserrat')
    s = 'einfach.dawah'; w = text_w(ctx, s)
    ctx.move_to(540 - w / 2, 1640); src(ctx, GOLD, a * eo((t - t0 - 1.0) / 0.6)); ctx.show_text(s)

_VIG = None
def vignette(ctx, a=0.45):
    global _VIG
    if _VIG is None:
        _VIG = cairo.RadialGradient(540, 960, 500, 540, 960, 1250)
        _VIG.add_color_stop_rgba(0, 0, 0, 0, 0); _VIG.add_color_stop_rgba(1, 0, 0, 0, 1)
    ctx.save(); ctx.set_source(_VIG); ctx.paint_with_alpha(a); ctx.restore()

def grade(ctx, c, a, op=cairo.OPERATOR_SOFT_LIGHT):
    ctx.save(); ctx.set_operator(op); src(ctx, c, a); ctx.paint(); ctx.restore()

def flash(ctx, a, c=(1, 1, 1)):
    if a > 0: src(ctx, c, a); ctx.paint()
