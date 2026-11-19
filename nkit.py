from kit import *

NUH = dict(robe='#efe7d4', robe2='#5c7a8c')

def nuh_fig(ctx, x, y, s, t, **kw):
    d = dict(NUH); d.update(kw)
    prophet(ctx, x, y, s, t, **d)

# ---------------- Arche ----------------
def _hull(ctx, u):
    ctx.new_path()
    ctx.move_to(-470 * u, -178 * u)
    ctx.curve_to(-432 * u, -44 * u, -300 * u, 0, -60 * u, 2 * u)
    ctx.curve_to(220 * u, 2 * u, 424 * u, -34 * u, 522 * u, -158 * u)
    ctx.line_to(500 * u, -206 * u)
    ctx.curve_to(260 * u, -172 * u, -230 * u, -172 * u, -452 * u, -214 * u)
    ctx.close_path()

def ark(ctx, x, y, s, t, build=1.0, tilt=0.0, alpha_=1.0, house=True):
    """Holzschiff von der Seite. build 0 = Kiel und Spanten, 1 = fertiger Rumpf."""
    if alpha_ <= 0.02: return
    u = s
    if alpha_ < 1: ctx.push_group()
    ctx.save(); ctx.translate(x, y); ctx.rotate(tilt)
    W1, W2, W3 = '#6d4a2c', '#8a6238', '#4a3120'
    # Kiel
    src(ctx, W3); ctx.set_line_width(13 * u); ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.move_to(-468 * u, -168 * u)
    ctx.curve_to(-430 * u, -34 * u, -300 * u, 8 * u, -60 * u, 10 * u)
    ctx.curve_to(220 * u, 10 * u, 428 * u, -26 * u, 524 * u, -150 * u)
    ctx.stroke()
    # Spanten, nur solange gebaut wird
    rib = clamp((0.95 - build) / 0.6)
    if rib > 0.01:
        src(ctx, W3, 0.9 * rib); ctx.set_line_width(9 * u)
        for k in range(11):
            f = -0.86 + k * 0.172
            bx = f * 470 * u
            by = 8 * u - abs(f) ** 2.1 * 150 * u
            top = by - (176 - abs(f) * 20) * u
            ctx.move_to(bx, by)
            ctx.curve_to(bx - 26 * u * (1 - abs(f)), by - 90 * u, bx - 16 * u * (1 - abs(f)), top + 40 * u, bx, top)
            ctx.stroke()
    # Rumpfhaut waechst von unten nach oben
    fill = clamp((build - 0.18) / 0.72)
    if fill > 0.01:
        ctx.save()
        ctx.rectangle(-620 * u, 14 * u - 240 * u * fill, 1240 * u, 260 * u * fill + 10 * u); ctx.clip()
        _hull(ctx, u)
        ctx.set_source(lingrad(0, -220 * u, 0, 14 * u, [(0, W2), (0.55, W1), (1, W3)])); ctx.fill()
        _hull(ctx, u); ctx.clip()
        src(ctx, shade(W3, -0.2), 0.55); ctx.set_line_width(3 * u)
        for k in range(6):
            yy = -24 * u - k * 30 * u
            ctx.move_to(-520 * u, yy)
            xx = -520 * u
            while xx < 560 * u:
                ctx.line_to(xx, yy - abs(xx / (470 * u)) ** 2.2 * 44 * u); xx += 30 * u
            ctx.stroke()
        src(ctx, '#2a1b10', 0.5); ctx.set_line_width(2.5 * u)
        for k in range(16):
            px = -450 * u + k * 60 * u
            ctx.move_to(px, -30 * u - abs(px / (470 * u)) ** 2.2 * 40 * u)
            ctx.line_to(px, -160 * u)
            ctx.stroke()
        ctx.restore()
        _hull(ctx, u)
        src(ctx, '#2a1b10', 0.8 * fill); ctx.set_line_width(6 * u); ctx.stroke()
    # Deckshaus
    hs = clamp((build - 0.62) / 0.32)
    if house and hs > 0.01:
        ctx.save(); ctx.rectangle(-300 * u, -420 * u, 460 * u, (420 - 186) * u + 420 * u * hs); ctx.clip()
        hw, hh = 190 * u, 128 * u
        hx0, hy0 = -170 * u, -192 * u
        ctx.set_source(lingrad(hx0, hy0 - hh, hx0, hy0, [(0, '#9a7042'), (1, '#6a4728')]))
        ctx.rectangle(hx0, hy0 - hh, hw * 2, hh); ctx.fill()
        src(ctx, '#3a2616'); ctx.set_line_width(4 * u); ctx.rectangle(hx0, hy0 - hh, hw * 2, hh); ctx.stroke()
        src(ctx, '#4a3120')
        poly(ctx, [(hx0 - 22 * u, hy0 - hh), (hx0 + hw * 2 + 22 * u, hy0 - hh), (hx0 + hw * 2 - 10 * u, hy0 - hh - 44 * u), (hx0 + 10 * u, hy0 - hh - 44 * u)]); ctx.fill()
        src(ctx, '#241509')
        ctx.rectangle(hx0 + 48 * u, hy0 - 96 * u, 54 * u, 96 * u); ctx.fill()
        src(ctx, '#2a1b10', 0.9)
        for k in range(2):
            ctx.rectangle(hx0 + 160 * u + k * 90 * u, hy0 - 92 * u, 44 * u, 40 * u); ctx.fill()
        ctx.restore()
    ctx.restore()
    if alpha_ < 1:
        ctx.pop_group_to_source(); ctx.paint_with_alpha(alpha_)

# ---------------- Wasser ----------------
def water_top(ctx, y, t, amp=14, x0=-300, x1=1400, step=18, ph=0.0):
    ctx.move_to(x0, y)
    x = x0
    while x <= x1:
        ctx.line_to(x, y + math.sin(x * 0.011 + t * 1.5 + ph) * amp + math.sin(x * 0.029 - t * 2.4 + ph) * amp * 0.38)
        x += step
    return x1

def water(ctx, y, t, amp=14, c1='#2f5676', c2='#132434', a=1.0, foam=True, ph=0.0, depth=2400):
    ctx.new_path()
    water_top(ctx, y, t, amp, ph=ph)
    ctx.line_to(1400, depth); ctx.line_to(-300, depth); ctx.close_path()
    ctx.set_source(lingrad(0, y - 20, 0, depth, [(0, C(c1, a)), (1, C(c2, a))])); ctx.fill()
    if foam:
        ctx.new_path(); water_top(ctx, y, t, amp, ph=ph)
        src(ctx, (0.92, 0.96, 1.0), 0.5 * a); ctx.set_line_width(5); ctx.stroke()
    src(ctx, (1, 1, 1), 0.10 * a); ctx.set_line_width(4)
    for k in range(7):
        yy = y + 50 + k * 72
        ctx.new_path(); xx = -200
        while xx < 1300:
            ctx.move_to(xx + math.sin(t * 1.1 + k) * 30, yy)
            ctx.line_to(xx + 90 + math.sin(t * 1.1 + k) * 30, yy + 4)
            xx += 260
        ctx.stroke()

def big_wave(ctx, x, y, s, t, c='#28455f', a=1.0, ph=0.0, crest=True):
    """eine hohe Welle wie ein Berg, mit klarer Schaumkante gegen das Wasser"""
    u = s
    sw = math.sin(t * 0.9 + ph) * 14 * u
    def path():
        ctx.new_path()
        ctx.move_to(x - 600 * u, y + 240 * u)
        ctx.curve_to(x - 380 * u, y + 40 * u, x - 220 * u, y - 215 * u + sw, x - 20 * u, y - 305 * u + sw)
        ctx.curve_to(x + 74 * u, y - 338 * u + sw, x + 134 * u, y - 252 * u + sw, x + 196 * u, y - 170 * u)
        ctx.curve_to(x + 340 * u, y + 14 * u, x + 450 * u, y + 140 * u, x + 620 * u, y + 250 * u)
        ctx.close_path()
    path()
    ctx.set_source(lingrad(0, y - 330 * u, 0, y + 240 * u,
                           [(0, C(shade(c, 0.5), a)), (0.4, C(c, a)), (1, C(shade(c, -0.45), a))])); ctx.fill()
    # Schaumkante entlang der ganzen Silhouette
    ctx.new_path()
    ctx.move_to(x - 600 * u, y + 240 * u)
    ctx.curve_to(x - 380 * u, y + 40 * u, x - 220 * u, y - 215 * u + sw, x - 20 * u, y - 305 * u + sw)
    ctx.curve_to(x + 74 * u, y - 338 * u + sw, x + 134 * u, y - 252 * u + sw, x + 196 * u, y - 170 * u)
    ctx.curve_to(x + 340 * u, y + 14 * u, x + 450 * u, y + 140 * u, x + 620 * u, y + 250 * u)
    src(ctx, (0.95, 0.98, 1.0), 0.75 * a); ctx.set_line_width(9 * u); ctx.stroke()
    if crest:
        r = rnd(int(ph * 100) + 5)
        for k in range(18):
            fx = x - 60 * u + r.uniform(-180, 240) * u
            fy = y - 300 * u + sw + r.uniform(-50, 70) * u
            src(ctx, (1, 1, 1), 0.42 * a * r.uniform(0.3, 1)); circle(ctx, fx, fy, r.uniform(4, 11) * u); ctx.fill()
        src(ctx, (0.9, 0.95, 1.0), 0.3 * a); ctx.set_line_width(5 * u)
        for k in range(3):
            yy = y - 180 * u + k * 90 * u
            ctx.new_path()
            ctx.move_to(x - 300 * u + k * 40 * u, yy)
            ctx.curve_to(x - 150 * u, yy - 24 * u, x + 60 * u, yy - 14 * u, x + 210 * u, yy + 20 * u)
            ctx.stroke()

def rain(ctx, t, n=130, a=0.32, seed=9, slant=0.2, speed=1.0):
    r = rnd(seed)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    for i in range(n):
        x0 = r.uniform(-300, 1400); sp = r.uniform(1100, 1900) * speed; ln = r.uniform(50, 110)
        y = (r.uniform(0, 2400) + t * sp) % 2600 - 220
        src(ctx, (0.86, 0.93, 1.0), a * r.uniform(0.35, 1))
        ctx.set_line_width(r.uniform(1.6, 3.2))
        ctx.move_to(x0, y); ctx.line_to(x0 - ln * slant, y + ln); ctx.stroke()

def splash(ctx, x, y, s, t, a=1.0, seed=3, n=16):
    r = rnd(seed)
    for i in range(n):
        ph = r.uniform(0, 6.28); sp = r.uniform(0.4, 1.0)
        u = (t * 1.6 + ph) % 1.0
        px = x + math.cos(ph) * 160 * s * u * sp
        py = y - 190 * s * math.sin(u * PI) * sp
        src(ctx, (0.9, 0.95, 1.0), a * (1 - u) * 0.75); circle(ctx, px, py, (10 - 6 * u) * s); ctx.fill()

# ---------------- Backofen ----------------
def tannur(ctx, x, y, s, t, gush=0.0, lit=0.0):
    u = s
    shadow(ctx, x, y, 120 * u, 0.3)
    ctx.set_source(lingrad(x, y - 210 * u, x, y, [(0, '#c49a6c'), (1, '#7a5c3e')]))
    ctx.new_path()
    ctx.move_to(x - 112 * u, y)
    ctx.curve_to(x - 108 * u, y - 152 * u, x - 70 * u, y - 198 * u, x - 46 * u, y - 206 * u)
    ctx.line_to(x + 46 * u, y - 206 * u)
    ctx.curve_to(x + 70 * u, y - 198 * u, x + 108 * u, y - 152 * u, x + 112 * u, y)
    ctx.close_path(); ctx.fill()
    src(ctx, '#56402c', 0.45); ctx.set_line_width(3 * u)
    for k in range(4):
        yy = y - 36 * u - k * 44 * u
        ctx.move_to(x - 110 * u + k * 7 * u, yy); ctx.line_to(x + 110 * u - k * 7 * u, yy); ctx.stroke()
    src(ctx, '#3a2a1c')
    ellipse(ctx, x, y - 206 * u, 50 * u, 17 * u); ctx.fill()
    if lit > 0:
        glow(ctx, x, y - 200 * u, 110 * u, '#ff9a3a', 0.45 * lit)
        ctx.set_source(radgrad(x, y - 206 * u, 0, 44 * u, [(0, C('#ffcc70', lit)), (1, C('#8a3a10', lit * 0.5))]))
        ellipse(ctx, x, y - 206 * u, 44 * u, 14 * u); ctx.fill()
    if gush > 0.01:
        g = clamp(gush)
        # Wasser steht randvoll und laeuft ueber beide Seiten
        ctx.set_source(radgrad(x, y - 210 * u, 0, 52 * u, [(0, C('#dff0fb', 0.95)), (1, C('#7fb4d4', 0.95))]))
        ellipse(ctx, x, y - 208 * u - 6 * u * g, 48 * u, 16 * u); ctx.fill()
        for sgn in (-1, 1):
            ctx.new_path()
            ctx.move_to(x + sgn * 30 * u, y - 212 * u)
            ctx.curve_to(x + sgn * 62 * u, y - 206 * u, x + sgn * 86 * u, y - 150 * u * g, x + sgn * 96 * u, y - 10 * u)
            ctx.line_to(x + sgn * 52 * u, y - 10 * u)
            ctx.curve_to(x + sgn * 48 * u, y - 120 * u * g, x + sgn * 30 * u, y - 190 * u, x + sgn * 12 * u, y - 212 * u)
            ctx.close_path()
            ctx.set_source(lingrad(0, y - 210 * u, 0, y, [(0, C('#e6f3fc', 0.9 * g)), (1, C('#6aa6c8', 0.85 * g))])); ctx.fill()
        src(ctx, (1, 1, 1), 0.5 * g); ctx.set_line_width(3 * u)
        for k in range(3):
            ph = (t * 1.3 + k * 0.33) % 1.0
            yy = y - 200 * u + ph * 180 * u
            ctx.move_to(x - 86 * u, yy); ctx.line_to(x - 70 * u, yy + 10 * u); ctx.stroke()
            ctx.move_to(x + 86 * u, yy); ctx.line_to(x + 70 * u, yy + 10 * u); ctx.stroke()
        ctx.set_source(lingrad(x, y - 24 * u, x, y + 30 * u, [(0, C('#9cc8e0', 0.9)), (1, C('#35627f', 0.9))]))
        ellipse(ctx, x, y + 4 * u, (130 + 230 * g) * u, (20 + 20 * g) * u); ctx.fill()
        src(ctx, (1, 1, 1), 0.35 * g); ctx.set_line_width(3 * u)
        ellipse(ctx, x, y + 4 * u, (130 + 230 * g) * u, (20 + 20 * g) * u); ctx.stroke()
        splash(ctx, x, y - 200 * u, 0.6 * u, t, a=g, seed=21, n=10)

# ---------------- Berg ----------------
def mountain(ctx, x, y, s, c='#5a4636', c2=None, snow=0.0, seed=2):
    c2 = c2 or shade(c, -0.3)
    u = s
    ctx.new_path()
    ctx.move_to(x - 620 * u, y)
    ctx.line_to(x - 300 * u, y - 320 * u)
    ctx.line_to(x - 200 * u, y - 262 * u)
    ctx.line_to(x - 130 * u, y - 452 * u)
    ctx.line_to(x + 210 * u, y - 448 * u)
    ctx.line_to(x + 300 * u, y - 280 * u)
    ctx.line_to(x + 420 * u, y - 350 * u)
    ctx.line_to(x + 680 * u, y)
    ctx.close_path()
    ctx.set_source(lingrad(x, y - 470 * u, x, y, [(0, c), (1, c2)])); ctx.fill()
    src(ctx, shade(c, 0.25), 0.5); ctx.set_line_width(5 * u)
    ctx.move_to(x - 130 * u, y - 452 * u); ctx.line_to(x - 60 * u, y - 180 * u); ctx.line_to(x - 20 * u, y - 60 * u); ctx.stroke()

def ledge(ctx, x0, x1, ytop, ybot, c='#6b4a34', seed=1):
    """Felsvorsprung mit schraegen Flanken und zackiger Oberkante"""
    r = rnd(seed)
    w = x1 - x0
    pts = []
    n = 9
    for k in range(n + 1):
        px = x0 + w * k / n
        py = ytop + r.uniform(-12, 10) + (1 - math.sin(k / n * PI)) * 16
        pts.append((px, py))
    ctx.new_path()
    ctx.move_to(x0 - w * 0.22, ybot + 14)
    ctx.line_to(x0 - w * 0.07, ytop + 46)
    for px, py in pts:
        ctx.line_to(px, py)
    ctx.line_to(x1 + w * 0.08, ytop + 52)
    ctx.line_to(x1 + w * 0.24, ybot + 14)
    ctx.close_path()
    ctx.set_source(lingrad(0, ytop, 0, ybot + 14, [(0, shade(c, 0.3)), (0.3, c), (1, shade(c, -0.45))])); ctx.fill()
    ctx.new_path(); ctx.move_to(x0 - w * 0.07, ytop + 46)
    for px, py in pts:
        ctx.line_to(px, py)
    ctx.line_to(x1 + w * 0.08, ytop + 52)
    src(ctx, shade(c, 0.5), 0.7); ctx.set_line_width(6); ctx.stroke()
    src(ctx, shade(c, -0.5), 0.45); ctx.set_line_width(4)
    for k in range(5):
        px = x0 + w * (0.12 + 0.19 * k) + r.uniform(-14, 14)
        ctx.move_to(px, ytop + 34); ctx.line_to(px + r.uniform(-24, 24), ybot + 6); ctx.stroke()
    for k in range(4):
        bx = x0 + w * r.uniform(-0.2, 1.2); br = r.uniform(12, 26)
        src(ctx, shade(c, -0.25)); ellipse(ctx, bx, ybot + 6, br, br * 0.6); ctx.fill()

def sea_world(ctx, t, cam, P, wy=1150, seed=40, rain_a=0.0, stars_a=0.0, sun=(820, 460), cl=0.6, rays_a=0.05, amp=16,
              c1='#2f5676', c2='#132434'):
    """Himmel plus Wasserflaeche bis zum Horizont"""
    bg(ctx, t, cam, P, horizon=wy, sun_pos=sun, sun_r=44, clouds_a=cl, seed=seed, far_amp=120, mid_amp=60,
       stars_a=stars_a, ray_a=rays_a)
    def g():
        water(ctx, wy, t, amp=amp, c1=c1, c2=c2)
    layer(ctx, cam, 1.0, g)

# ---------------- Split Screen Vergleich ----------------
MIDY = 960

def split(ctx, top_fn, bot_fn, line=True, gap=10):
    ctx.save(); ctx.rectangle(0, 0, 1080, MIDY - gap); ctx.clip(); ctx.translate(0, -480); top_fn(); ctx.restore()
    ctx.save(); ctx.rectangle(0, MIDY + gap, 1080, 1920 - MIDY - gap); ctx.clip(); ctx.translate(0, 480); bot_fn(); ctx.restore()
    if line:
        ctx.set_source(lingrad(0, MIDY - 18, 0, MIDY + 18,
                               [(0, C('#000000', 0.0)), (0.5, C(GOLD, 0.5)), (1, C('#000000', 0.0))]))
        ctx.rectangle(0, MIDY - 18, 1080, 36); ctx.fill()

def side_label(ctx, text, t, t0, t1, top=True, col=None):
    """kleines gesperrtes Label am linken Rand einer Haelfte"""
    if not (t0 <= t <= t1): return
    a = eo((t - t0) / 0.3) * clamp((t1 - t) / 0.3)
    y = 150 if top else 1110
    set_font(ctx, 30, 'Cinzel')
    s = '  '.join(list(text)) if False else text
    src(ctx, col or GOLD, 0.85 * a)
    ctx.move_to(60, y); ctx.show_text(s)

def counter(ctx, text, t, t0, t1, y=250, size=112):
    """grosser Tageszaehler in der Mitte"""
    if not (t0 <= t <= t1): return
    a = eo((t - t0) / 0.18) * clamp((t1 - t) / 0.2)
    pop = 1 + 0.1 * (1 - eo((t - t0) / 0.3))
    set_font(ctx, size, 'Cinzel'); w = text_w(ctx, text)
    ctx.save(); ctx.translate(540, y); ctx.scale(pop, pop)
    for g in range(3):
        ctx.move_to(-w / 2, 0); ctx.text_path(text)
        src(ctx, (0, 0, 0), 0.35 * a / (g + 1)); ctx.set_line_width(12 + g * 12); ctx.stroke()
    ctx.move_to(-w / 2, 0); ctx.text_path(text)
    ctx.set_source(lingrad(0, -size, 0, 0, [(0, (1, 0.97, 0.88, a)), (1, alpha(GOLD, a))])); ctx.fill()
    ctx.restore()

def punch(ctx, text, t, t0, t1, y=820, size=74):
    """Punchline in Serifenschrift, zwei Zeilen mit |"""
    if not (t0 <= t <= t1): return
    a = eo((t - t0) / 0.45) * clamp((t1 - t) / 0.4)
    lines = text.split('|')
    set_font(ctx, size, 'Lora')
    yy = y - len(lines) * size * 0.6
    for k, ln in enumerate(lines):
        la = a * eo((t - t0 - k * 0.45) / 0.5)
        w = text_w(ctx, ln)
        ctx.move_to(540 - w / 2, yy); ctx.text_path(ln)
        src(ctx, (0, 0, 0), 0.5 * la); ctx.set_line_width(10); ctx.stroke()
        ctx.move_to(540 - w / 2, yy); src(ctx, (1, 0.98, 0.92), la); ctx.show_text(ln)
        yy += size * 1.3

# ---------------- Tuer im Lehmhaus ----------------
def door(ctx, x, y, s, t, open_=0.0, glow_a=0.0, wall=True):
    u = s
    if wall:
        ctx.set_source(lingrad(x, y - 820 * u, x, y + 400 * u, [(0, '#51402f'), (0.45, '#6b5240'), (1, '#3a2c20')]))
        ctx.rectangle(x - 1100 * u, y - 820 * u, 2200 * u, 1300 * u); ctx.fill()
        src(ctx, '#3a2c1e', 0.35); ctx.set_line_width(4 * u)
        for k in range(8):
            yy = y - 60 * u - k * 112 * u
            ctx.move_to(x - 1100 * u, yy); ctx.line_to(x + 1100 * u, yy); ctx.stroke()
        src(ctx, '#2e2316', 0.3); ctx.set_line_width(4 * u)
        for k in range(9):
            px = x - 1000 * u + k * 250 * u + (k % 2) * 60 * u
            ctx.move_to(px, y - 816 * u); ctx.line_to(px, y - 60 * u); ctx.stroke()
        src(ctx, '#2a2016', 0.5)
        ctx.rectangle(x - 1100 * u, y - 12 * u, 2200 * u, 26 * u); ctx.fill()
    # Rahmen
    def arch(ctx, w, h):
        ctx.new_path()
        ctx.move_to(x - w, y)
        ctx.line_to(x - w, y - h * 0.62)
        ctx.curve_to(x - w, y - h * 0.94, x + w, y - h * 0.94, x + w, y - h * 0.62)
        ctx.line_to(x + w, y)
        ctx.close_path()
    arch(ctx, 168 * u, 420 * u)
    src(ctx, '#2e2114'); ctx.fill()
    if glow_a > 0.01:
        glow(ctx, x, y - 230 * u, 420 * u, '#ffd98a', 0.55 * glow_a)
        arch(ctx, 150 * u, 396 * u)
        ctx.set_source(radgrad(x, y - 180 * u, 10 * u, 400 * u,
                               [(0, C('#fff6dc', glow_a)), (1, C('#f0b44a', glow_a))])); ctx.fill()
    ow = 150 * u * (1 - clamp(open_))
    if ow > 2:
        ctx.save()
        arch(ctx, 150 * u, 396 * u); ctx.clip()
        ctx.set_source(lingrad(x - 150 * u, 0, x + 150 * u, 0, [(0, '#5a3a1e'), (0.5, '#7a5228'), (1, '#4a3018')]))
        ctx.rectangle(x - ow, y - 400 * u, ow * 2, 400 * u); ctx.fill()
        src(ctx, '#3a2412', 0.6); ctx.set_line_width(4 * u)
        for k in range(5):
            px = x - ow + ow * 2 * (k + 0.5) / 5
            ctx.move_to(px, y - 392 * u); ctx.line_to(px, y); ctx.stroke()
        ctx.set_source(lingrad(x, y - 290 * u, x, y - 230 * u, [(0, '#d9b35a'), (1, '#9c7426')]))
        for k in range(8):
            ang = k / 8 * 2 * PI
            poly(ctx, [(x + math.cos(ang) * 10 * u, y - 260 * u + math.sin(ang) * 10 * u),
                       (x + math.cos(ang + 0.3) * 34 * u, y - 260 * u + math.sin(ang + 0.3) * 34 * u),
                       (x + math.cos(ang + 0.78) * 10 * u, y - 260 * u + math.sin(ang + 0.78) * 10 * u)]); ctx.fill()
        src(ctx, '#d9b35a'); circle(ctx, x, y - 260 * u, 11 * u); ctx.fill()
        src(ctx, '#c9a24a'); circle(ctx, x + ow * 0.6, y - 200 * u, 9 * u); ctx.fill()
        ctx.restore()
    arch(ctx, 168 * u, 420 * u)
    src(ctx, '#3a2a18'); ctx.set_line_width(12 * u); ctx.stroke()

def knock_waves(ctx, x, y, s, t, a=1.0, n=3):
    for k in range(n):
        ph = (t * 1.8 + k * 0.33) % 1.0
        src(ctx, GOLD, a * (1 - ph) * 0.5); ctx.set_line_width(5 * s)
        ctx.new_path(); ctx.arc(x, y, (20 + ph * 90) * s, -0.9, 0.9); ctx.stroke()

# ---------------- Stapel aus Lichtpunkten ----------------
def light_pile(ctx, x, y, n, t, s=1.0, c='#ffd98a', a=1.0, seed=1, cols=7):
    r = rnd(seed)
    n = int(max(0, n))
    for i in range(n):
        row = i // cols; col = i % cols
        px = x + (col - (cols - 1) / 2) * 34 * s + r.uniform(-4, 4) * s
        py = y - row * 30 * s - 14 * s + math.sin(t * 1.4 + i * 0.4) * 2 * s
        glow(ctx, px, py, 26 * s, c, 0.3 * a)
        ctx.set_source(radgrad(px, py, 0, 15 * s, [(0, C('#fffbe8', a)), (1, C(c, a * 0.5))]))
        circle(ctx, px, py, 14 * s); ctx.fill()

def hourglass(ctx, x, y, s, t, fill=0.5, a=1.0):
    u = s
    src(ctx, '#6a4a2c', a); ctx.set_line_width(10 * u)
    ctx.move_to(x - 90 * u, y - 200 * u); ctx.line_to(x + 90 * u, y - 200 * u); ctx.stroke()
    ctx.move_to(x - 90 * u, y); ctx.line_to(x + 90 * u, y); ctx.stroke()
    ctx.new_path()
    ctx.move_to(x - 72 * u, y - 194 * u); ctx.line_to(x + 72 * u, y - 194 * u)
    ctx.line_to(x + 8 * u, y - 100 * u); ctx.line_to(x + 72 * u, y - 6 * u)
    ctx.line_to(x - 72 * u, y - 6 * u); ctx.line_to(x - 8 * u, y - 100 * u)
    ctx.close_path()
    src(ctx, '#cfe0ea', 0.18 * a); ctx.fill_preserve()
    src(ctx, '#8a9aa6', 0.5 * a); ctx.set_line_width(4 * u); ctx.stroke()
    f = clamp(fill)
    ctx.save(); ctx.rectangle(x - 80 * u, y - 194 * u, 160 * u, 92 * u * f); ctx.clip()
    ctx.new_path(); ctx.move_to(x - 72 * u, y - 194 * u); ctx.line_to(x + 72 * u, y - 194 * u)
    ctx.line_to(x + 8 * u, y - 100 * u); ctx.line_to(x - 8 * u, y - 100 * u); ctx.close_path()
    src(ctx, '#e8c072', a); ctx.fill(); ctx.restore()
    bot = 1 - f
    ctx.save(); ctx.rectangle(x - 80 * u, y - 6 * u - 90 * u * bot, 160 * u, 90 * u * bot + 6 * u); ctx.clip()
    ctx.new_path(); ctx.move_to(x - 8 * u, y - 100 * u); ctx.line_to(x + 8 * u, y - 100 * u)
    ctx.line_to(x + 72 * u, y - 6 * u); ctx.line_to(x - 72 * u, y - 6 * u); ctx.close_path()
    src(ctx, '#e8c072', a); ctx.fill(); ctx.restore()
    if 0.02 < f < 0.99:
        src(ctx, '#e8c072', a); ctx.set_line_width(3 * u)
        ctx.move_to(x, y - 98 * u); ctx.line_to(x, y - 10 * u); ctx.stroke()
