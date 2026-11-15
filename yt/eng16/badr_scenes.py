# Detailed 16:9 animation scenes for the Badr demo (PyCairo, reel engine primitives).
# Each sc_* function returns an RGB numpy frame (1080, 1920, 3).
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, cairo
from kit import *

HZ = 640                                   # horizon in world coords (screen y at cam z=1)
def S_(y, k=560.0): return max(0.05, (y - HZ) / k)

def new_ctx():
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    return surf, cairo.Context(surf)

def to_np(surf):
    surf.flush()
    a = np.ndarray((H, W, 4), np.uint8, surf.get_data())
    return np.ascontiguousarray(a[:, :, 2::-1])

# ---------------- world ----------------
def bg16(ctx, t, cam, P, hz=HZ, seed=0, sun_pos=None, sun_r=40, sun_a=1.0, clouds_a=0.45, cloud_y=None, cloud_c=None,
         stars_a=0.0, moon_pos=None, ray_a=0.08, far_amp=210, mid_amp=110, haze_a=0.18):
    layer(ctx, cam, 0.04, lambda: sky(ctx, P['top'], P['mid'], P['bot'], hz - 900, hz + 120))
    if stars_a > 0: layer(ctx, cam, 0.06, lambda: stars(ctx, t, stars_a, seed=3, n=260))
    if moon_pos:
        def mo():
            glow(ctx, moon_pos[0], moon_pos[1], 260, '#7f96e0', 0.18)
            moon(ctx, moon_pos[0], moon_pos[1], 30)
            src(ctx, '#d8d4c4', 0.5); circle(ctx, moon_pos[0] - 9, moon_pos[1] - 6, 6); ctx.fill()
            circle(ctx, moon_pos[0] + 8, moon_pos[1] + 9, 4); ctx.fill()
        layer(ctx, cam, 0.08, mo)
    if sun_pos and sun_a > 0:
        layer(ctx, cam, 0.1, lambda: (sun(ctx, sun_pos[0], sun_pos[1], sun_r, P['sun'], P['halo'], sun_a),
                                       rays(ctx, sun_pos[0], sun_pos[1], t, P['light'], ray_a * sun_a, n=11)))
    if clouds_a > 0:
        cc = cloud_c or mix(P['light'], (1, 1, 1), 0.4)
        layer(ctx, cam, 0.15, lambda: clouds(ctx, t, cloud_y or hz - 430, cc, clouds_a, n=8, seed=seed + 3, speed=9, scale=0.8))
    def f1():
        pts = ridge(ctx, hz + 20, far_amp, P['far'], seed=seed + 1, freq=0.0035, color2=shade(P['far'], 0.1), sharp=0.4)
        ridge_light(ctx, pts, P['light'], 0.18)
        haze(ctx, P['haze'], haze_a)
    layer(ctx, cam, 0.3, f1)
    def f2():
        pts = ridge(ctx, hz + 60, mid_amp, P['mid_r'], seed=seed + 2, freq=0.006, color2=shade(P['mid_r'], 0.12), sharp=0.6)
        ridge_light(ctx, pts, P['light'], 0.22, 2)
        haze(ctx, P['haze'], haze_a * 0.45)
    layer(ctx, cam, 0.55, f2)

def floor16(ctx, t, P, hz=HZ, seed=0, rocks_n=14, lines_a=0.12):
    ground(ctx, hz, P['g1'], P['g2'])
    dune_lines(ctx, hz, t, shade(P['g2'], -0.3), seed=seed, a=lines_a)
    if rocks_n: rocks(ctx, hz + 30, seed=seed + 4, n=rocks_n, c=shade(P['near'], 0.2), size=(6, 26))

# ---------------- props ----------------
def well(ctx, x, y, s, t, c='#8a7058', water='#1a3a4a', light=1.0, rope=True):
    u = s
    shadow(ctx, x + 20 * u, y + 6 * u, 170 * u, 0.3)
    # stone ring: back rim, inside, front wall built from stones
    ctx.set_source(radgrad(x, y - 70 * u, 4, 95 * u, [(0, water), (1, shade(water, -0.5))]))
    ellipse(ctx, x, y - 70 * u, 92 * u, 22 * u); ctx.fill()
    src(ctx, '#e8f4ff', 0.25 * light); ellipse(ctx, x + 20 * u, y - 72 * u, 30 * u, 4 * u); ctx.fill()
    ctx.set_source(lingrad(x - 100 * u, 0, x + 100 * u, 0, [(0, shade(c, -0.25)), (0.6, shade(c, 0.12 * light)), (1, shade(c, -0.15))]))
    ctx.move_to(x - 100 * u, y - 70 * u); ctx.curve_to(x - 100 * u, y - 40 * u, x - 100 * u, y - 10 * u, x - 96 * u, y)
    ctx.curve_to(x - 50 * u, y + 22 * u, x + 50 * u, y + 22 * u, x + 96 * u, y)
    ctx.curve_to(x + 100 * u, y - 10 * u, x + 100 * u, y - 40 * u, x + 100 * u, y - 70 * u)
    ctx.curve_to(x + 60 * u, y - 46 * u, x - 60 * u, y - 46 * u, x - 100 * u, y - 70 * u); ctx.close_path(); ctx.fill()
    r = rnd(int(x))
    for row in range(3):
        yy = y - 58 * u + row * 21 * u
        for k in range(7):
            ang = -0.92 + (k + (row % 2) * 0.5) * 0.3
            sx = x + math.sin(ang) * 98 * u; sy = yy + math.cos(ang) * 18 * u + 6 * u
            sc = shade(c, r.uniform(-0.25, 0.15))
            src(ctx, sc); rrect(ctx, sx - 13 * u, sy - 8 * u, 26 * u, 17 * u, 5 * u); ctx.fill()
            src(ctx, (0, 0, 0), 0.22); ctx.set_line_width(1.2 * u); rrect(ctx, sx - 13 * u, sy - 8 * u, 26 * u, 17 * u, 5 * u); ctx.stroke()
    # rim stones
    ctx.set_source(lingrad(0, y - 82 * u, 0, y - 62 * u, [(0, shade(c, 0.2 * light)), (1, shade(c, -0.2))]))
    ellipse(ctx, x, y - 72 * u, 104 * u, 26 * u); ctx.set_line_width(10 * u); ctx.stroke()
    # wooden frame with pulley, rope and bucket
    if rope:
        src(ctx, '#5a3d22'); ctx.set_line_width(7 * u); ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        for sx in (-70, 70):
            ctx.move_to(x + sx * u, y - 74 * u); ctx.line_to(x + sx * 0.25 * u, y - 210 * u); ctx.stroke()
        ctx.set_line_width(6 * u); ctx.move_to(x - 30 * u, y - 196 * u); ctx.line_to(x + 30 * u, y - 196 * u); ctx.stroke()
        src(ctx, '#3a2614'); circle(ctx, x, y - 196 * u, 9 * u); ctx.fill()
        sw = math.sin(t * 1.4 + x) * 6 * u
        src(ctx, '#c8b08a'); ctx.set_line_width(2 * u)
        ctx.move_to(x + 8 * u, y - 196 * u); ctx.line_to(x + 8 * u + sw, y - 120 * u); ctx.stroke()
        ctx.set_source(lingrad(x - 14 * u, 0, x + 30 * u, 0, [(0, '#4a2e18'), (1, '#8a5a30')]))
        poly(ctx, [(x - 6 * u + sw, y - 122 * u), (x + 22 * u + sw, y - 122 * u), (x + 18 * u + sw, y - 96 * u), (x - 2 * u + sw, y - 96 * u)]); ctx.fill()

def waterskin(ctx, x, y, s, c='#7a4a2a'):
    u = s
    shadow(ctx, x, y, 40 * u, 0.3)
    ctx.set_source(radgrad(x - 8 * u, y - 26 * u, 2, 36 * u, [(0, shade(c, 0.25)), (1, shade(c, -0.3))]))
    ctx.move_to(x - 30 * u, y); ctx.curve_to(x - 38 * u, y - 30 * u, x - 10 * u, y - 46 * u, x + 14 * u, y - 36 * u)
    ctx.curve_to(x + 30 * u, y - 30 * u, x + 36 * u, y - 10 * u, x + 26 * u, y); ctx.close_path(); ctx.fill()
    src(ctx, shade(c, -0.4)); ctx.set_line_width(4 * u); ctx.move_to(x + 14 * u, y - 36 * u); ctx.line_to(x + 22 * u, y - 46 * u); ctx.stroke()
    src(ctx, '#d8c8a8', 0.6); ctx.set_line_width(2 * u); ctx.move_to(x - 28 * u, y - 18 * u); ctx.curve_to(x - 5 * u, y - 30 * u, x + 10 * u, y - 26 * u, x + 26 * u, y - 14 * u); ctx.stroke()

def saddle(ctx, x, y, s, c='#6a4026'):
    u = s
    shadow(ctx, x, y, 60 * u, 0.3)
    ctx.set_source(lingrad(0, y - 40 * u, 0, y, [(0, shade(c, 0.2)), (1, shade(c, -0.3))]))
    rrect(ctx, x - 46 * u, y - 30 * u, 92 * u, 30 * u, 10 * u); ctx.fill()
    src(ctx, '#a8823a'); ctx.rectangle(x - 46 * u, y - 20 * u, 92 * u, 5 * u); ctx.fill()
    src(ctx, '#4a2e18'); ctx.set_line_width(6 * u)
    for sx in (-30, 30):
        ctx.move_to(x + sx * u, y - 30 * u); ctx.curve_to(x + sx * u, y - 60 * u, x + sx * 0.3 * u, y - 62 * u, x, y - 64 * u); ctx.stroke()

def spear_ground(ctx, x, y, s, lean=0.08):
    u = s
    src(ctx, '#4a3020'); ctx.set_line_width(5 * u); ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    tx, ty = x + lean * 260 * u, y - 260 * u
    ctx.move_to(x, y); ctx.line_to(tx, ty); ctx.stroke()
    src(ctx, '#bdb8aa'); poly(ctx, [(tx - 5 * u, ty + 2 * u), (tx + lean * 40 * u, ty - 36 * u), (tx + 5 * u, ty + 2 * u)]); ctx.fill()

def sleeper(ctx, x, y, s, t, i, facing=1, rim=(0.75, 0.8, 1.0), rim_a=0.25):
    """companion asleep on the ground, wrapped in his cloak; face turned away, no features"""
    u = s; r = rnd(500 + i)
    robe = shade(r.choice(['#7a6a58', '#6a5a4a', '#5a5a52', '#806a50', '#6e5a5a', '#5a4a5a']), -0.3)
    tur = shade(r.choice(['#d8ccb4', '#c9b08a', '#e8dcc4', '#a89a80']), -0.35)
    br = 1 + 0.05 * math.sin(t * 1.25 + i * 1.7)
    shadow(ctx, x, y + 2 * u, 170 * u, 0.4)
    ctx.save(); ctx.translate(x, y); ctx.scale(facing, 1)
    L = 128 * u
    # rolled cloth under the head
    src(ctx, shade(robe, -0.35)); ellipse(ctx, -L + 8 * u, -9 * u, 34 * u, 11 * u); ctx.fill()
    # body under cloak: shoulder, waist, hip, legs
    ctx.move_to(-L + 30 * u, 0)
    ctx.curve_to(-L + 22 * u, -40 * u * br, -L + 50 * u, -62 * u * br, -L + 78 * u, -60 * u * br)
    ctx.curve_to(-L + 104 * u, -58 * u * br, -L + 118 * u, -44 * u, -L + 140 * u, -44 * u)
    ctx.curve_to(-L + 162 * u, -44 * u, -L + 180 * u, -56 * u, -L + 200 * u, -50 * u)
    ctx.curve_to(L - 30 * u, -38 * u, L - 14 * u, -26 * u, L - 4 * u, -22 * u)
    ctx.curve_to(L + 8 * u, -18 * u, L + 8 * u, -4 * u, L - 2 * u, 0)
    ctx.close_path()
    ctx.set_source(lingrad(0, -60 * u, 0, 0, [(0, shade(robe, 0.15)), (0.55, robe), (1, shade(robe, -0.4))]))
    ctx.fill_preserve(); ctx.save(); ctx.clip()
    src(ctx, shade(robe, -0.35), 0.55); ctx.set_line_width(2.4 * u)
    for k in range(5):
        fx = -60 * u + k * 34 * u
        ctx.move_to(fx, -50 * u); ctx.curve_to(fx + 14 * u, -30 * u, fx + 6 * u, -14 * u, fx + 18 * u, 0); ctx.stroke()
    src(ctx, '#a8823a', 0.7); ctx.rectangle(-L, -14 * u, 2 * L, 4 * u); ctx.fill()
    ctx.restore()
    # rim light along the top
    src(ctx, rim, rim_a); ctx.set_line_width(2.5 * u)
    ctx.move_to(-L + 26 * u, -40 * u * br); ctx.curve_to(-30 * u, -60 * u * br, 10 * u, -54 * u * br, 52 * u, -46 * u * br); ctx.stroke()
    # feet
    src(ctx, '#3b2a1c'); ellipse(ctx, L + 2 * u, -8 * u, 9 * u, 6 * u); ctx.fill()
    # head turned away: back of the head with turban and tail cloth
    hx, hy = -L + 22 * u, -30 * u
    src(ctx, shade(SKIN, -0.35)); ellipse(ctx, hx + 6 * u, hy + 8 * u, 15 * u, 12 * u); ctx.fill()
    ctx.set_source(radgrad(hx - 4 * u, hy - 8 * u, 2, 30 * u, [(0, shade(tur, 0.15)), (1, shade(tur, -0.3))]))
    ellipse(ctx, hx, hy, 27 * u, 21 * u, -0.3); ctx.fill()
    src(ctx, shade(tur, -0.35), 0.6); ctx.set_line_width(1.8 * u)
    for k in range(3):
        ctx.move_to(hx - 22 * u, hy + 4 * u - k * 8 * u); ctx.curve_to(hx - 6 * u, hy + 10 * u - k * 8 * u, hx + 8 * u, hy - 6 * u - k * 8 * u, hx + 22 * u, hy - 2 * u - k * 8 * u); ctx.stroke()
    ctx.restore()

def resting_camel(ctx, x, y, s, t, facing=1, col='#b8875a', i=0, rim=None, rim_a=0.0):
    """camel couched on the ground, legs folded, slow chewing"""
    u = s
    shadow(ctx, x, y + 2 * u, 170 * u, 0.4)
    ctx.save(); ctx.translate(x, y); ctx.scale(facing, 1)
    dark = shade(col, -0.32); light = shade(col, 0.22)
    # folded legs
    src(ctx, shade(col, -0.25))
    for lx in (-70, 40):
        rrect(ctx, (lx - 28) * u, -26 * u, 70 * u, 24 * u, 11 * u); ctx.fill()
    # body with hump
    ctx.set_source(radgrad(-10 * u, -120 * u, 6 * u, 150 * u, [(0, light), (0.65, col), (1, dark)], cx=-20 * u, cy=-150 * u))
    ctx.move_to(-120 * u, -18 * u)
    ctx.curve_to(-130 * u, -70 * u, -70 * u, -170 * u, -10 * u, -168 * u)
    ctx.curve_to(50 * u, -168 * u, 80 * u, -100 * u, 110 * u, -80 * u)
    ctx.curve_to(128 * u, -50 * u, 120 * u, -16 * u, 96 * u, -10 * u)
    ctx.curve_to(40 * u, -2 * u, -60 * u, -2 * u, -120 * u, -18 * u); ctx.close_path(); ctx.fill()
    # saddle blanket
    src(ctx, '#7a2e22', 0.85); ctx.move_to(-60 * u, -150 * u); ctx.curve_to(-20 * u, -168 * u, 30 * u, -160 * u, 50 * u, -140 * u)
    ctx.line_to(56 * u, -90 * u); ctx.curve_to(10 * u, -84 * u, -40 * u, -88 * u, -70 * u, -100 * u); ctx.close_path(); ctx.fill()
    src(ctx, '#d9b35a', 0.8); ctx.set_line_width(3 * u); ctx.move_to(-70 * u, -100 * u); ctx.curve_to(-40 * u, -88 * u, 10 * u, -84 * u, 56 * u, -90 * u); ctx.stroke()
    # neck + head, slow chew
    chew = math.sin(t * 2.2 + i) * 2 * u
    nod = math.sin(t * 0.5 + i) * 6 * u
    hx, hy = 210 * u, -150 * u + nod
    ctx.set_source(lingrad(100 * u, 0, hx, 0, [(0, col), (1, light)]))
    ctx.move_to(100 * u, -90 * u)
    ctx.curve_to(150 * u, -96 * u, 150 * u, hy + 40 * u, hx - 18 * u, hy + 4 * u)
    ctx.line_to(hx - 2 * u, hy + 22 * u)
    ctx.curve_to(170 * u, hy + 60 * u, 160 * u, -40 * u, 112 * u, -36 * u); ctx.close_path(); ctx.fill()
    ctx.save(); ctx.translate(hx, hy); ctx.rotate(0.25)
    src(ctx, col); ellipse(ctx, 10 * u, 6 * u, 32 * u, 17 * u); ctx.fill()
    src(ctx, light); ellipse(ctx, 34 * u, 12 * u + chew, 13 * u, 12 * u); ctx.fill()
    src(ctx, dark); ellipse(ctx, -8 * u, -14 * u, 6 * u, 9 * u, -0.4); ctx.fill()
    src(ctx, '#1d1814'); circle(ctx, 6 * u, -2 * u, 3 * u); ctx.fill()
    ctx.restore()
    if rim and rim_a > 0:
        src(ctx, rim, rim_a); ctx.set_line_width(3 * u)
        ctx.move_to(-110 * u, -60 * u); ctx.curve_to(-70 * u, -170 * u, -10 * u, -168 * u, 50 * u, -150 * u); ctx.stroke()
    ctx.restore()

def puddle(ctx, x, y, w, t, c='#9fb4ff', a=0.35):
    ctx.set_source(radgrad(x, y, 2, w, [(0, alpha(shade(c, -0.55), 0.8)), (1, alpha(shade(c, -0.7), 0))]))
    ellipse(ctx, x, y, w, w * 0.16); ctx.fill()
    src(ctx, c, a * (0.7 + 0.3 * math.sin(t * 1.7 + x))); ellipse(ctx, x - w * 0.15, y - w * 0.02, w * 0.45, w * 0.035); ctx.fill()
    # ripples from the last drops
    for k in range(2):
        ph = (t * 0.6 + k * 0.5 + x * 0.01) % 1
        src(ctx, c, a * 0.5 * (1 - ph)); ctx.set_line_width(1.2)
        ellipse(ctx, x + (k - 0.5) * w * 0.4, y, w * 0.12 * (0.3 + ph), w * 0.02 * (0.3 + ph)); ctx.stroke()

def embers(ctx, x, y, s, t, a=1.0):
    u = s
    glow(ctx, x, y - 10 * u, 260 * u, '#ff7a2a', 0.28 * a)
    for k in range(4):
        ctx.save(); ctx.translate(x + (k - 1.5) * 16 * u, y - 4 * u); ctx.rotate((k - 1.5) * 0.5)
        src(ctx, '#2a1a10'); rrect(ctx, -26 * u, -5 * u, 52 * u, 10 * u, 5 * u); ctx.fill()
        src(ctx, '#ff6a1a', 0.55 + 0.25 * math.sin(t * 5 + k)); ctx.rectangle(-20 * u, -1.5 * u, 40 * u, 3 * u); ctx.fill()
        ctx.restore()
    flame(ctx, x, y - 6 * u, 10 * u, 34 * u, t, seed=2, a=0.7 * a)
    r = rnd(int(x))
    for i in range(14):
        life = (t * r.uniform(0.25, 0.5) + r.random()) % 1
        src(ctx, '#ffcf6a', (1 - life) * 0.8 * a)
        circle(ctx, x + r.uniform(-20, 20) * u + math.sin(t * 2 + i) * 14 * u * life, y - life * 160 * u, r.uniform(1.2, 2.6)); ctx.fill()

def frond_roof(ctx, x0, x1, y, t, c='#4a5a2e', seed=0, depth=36, lit=None, lit_a=0.0):
    """layered palm frond roof: overlapping leaf strokes"""
    r = rnd(seed)
    for row in range(4):
        yy = y - row * depth * 0.3
        n = int((x1 - x0) / 11)
        for k in range(n):
            x = x0 + k * (x1 - x0) / n + r.uniform(-6, 6)
            L = r.uniform(40, 70); ang = r.uniform(1.25, 1.9) + math.sin(t * 1.3 + k) * 0.02
            lc = shade(c, r.uniform(-0.3, 0.12) - row * 0.08)
            ex, ey = x + math.cos(ang) * L, yy + math.sin(ang) * L * 0.6
            src(ctx, lc); ctx.set_line_width(r.uniform(5, 9)); ctx.set_line_cap(cairo.LINE_CAP_ROUND)
            ctx.move_to(x, yy - depth * 0.5); ctx.curve_to(x, yy, ex - 4, ey - 8, ex, ey); ctx.stroke()
            if lit_a > 0 and row == 0:
                src(ctx, lit, lit_a * r.uniform(0.3, 1)); ctx.set_line_width(2)
                ctx.move_to(x, yy - depth * 0.4); ctx.curve_to(x, yy, ex - 4, ey - 8, ex, ey); ctx.stroke()

def arish(ctx, x, y, s, t, glow_k=1.0):
    """the hut of palm branches ('Arisch) seen from outside at night; inside only light"""
    u = s
    shadow(ctx, x, y + 4 * u, 300 * u, 0.45)
    # warm interior light
    fl = 0.85 + 0.1 * math.sin(t * 7.1) + 0.05 * math.sin(t * 13.3)
    glow(ctx, x, y - 90 * u, 420 * u, '#ff9a3a', 0.35 * glow_k * fl)
    # back wall of fronds
    src(ctx, '#1a160f'); ctx.rectangle(x - 190 * u, y - 205 * u, 380 * u, 205 * u); ctx.fill()
    ctx.set_source(radgrad(x, y - 80 * u, 10 * u, 230 * u, [(0, alpha('#ffcf7a', 0.95 * glow_k * fl)), (0.5, alpha('#c86a22', 0.6 * glow_k * fl)), (1, alpha('#3a2010', 0.0))]))
    ctx.rectangle(x - 190 * u, y - 205 * u, 380 * u, 205 * u); ctx.fill()
    r = rnd(77)
    for k in range(34):
        bx = x - 185 * u + k * 11 * u
        src(ctx, '#2a2414', 0.75); ctx.set_line_width(3 * u)
        ctx.move_to(bx, y - 200 * u); ctx.curve_to(bx + r.uniform(-8, 8) * u, y - 140 * u, bx + r.uniform(-8, 8) * u, y - 70 * u, bx + r.uniform(-5, 5) * u, y); ctx.stroke()
    # floor mat
    src(ctx, '#7a5a30', 0.9); poly(ctx, [(x - 120 * u, y - 4 * u), (x + 120 * u, y - 4 * u), (x + 150 * u, y + 14 * u), (x - 150 * u, y + 14 * u)]); ctx.fill()
    src(ctx, '#a8823a', 0.6); ctx.set_line_width(2 * u)
    for k in range(5):
        ctx.move_to(x - 130 * u + k * 60 * u, y - 4 * u); ctx.line_to(x - 140 * u + k * 70 * u, y + 14 * u); ctx.stroke()
    # posts: palm trunks with rings
    for px, w_, sh in ((-200, 24, -0.1), (200, 24, -0.25), (-120, 16, -0.45), (120, 16, -0.5)):
        pxx = x + px * u
        ctx.set_source(lingrad(pxx - w_ * u, 0, pxx + w_ * u, 0, [(0, shade('#5a3d22', sh - 0.2)), (0.5, shade('#7a5634', sh)), (1, shade('#3a2614', sh - 0.2))]))
        ctx.rectangle(pxx - w_ / 2 * u, y - 235 * u, w_ * u, 240 * u); ctx.fill()
        src(ctx, '#2a1a0c', 0.6); ctx.set_line_width(1.5 * u)
        for k in range(10):
            yy = y - 225 * u + k * 23 * u
            ctx.move_to(pxx - w_ / 2 * u, yy); ctx.curve_to(pxx, yy + 4 * u, pxx, yy + 4 * u, pxx + w_ / 2 * u, yy); ctx.stroke()
        if px in (-200, 200):
            src(ctx, '#ffb45a', 0.35 * glow_k * fl); ctx.rectangle(pxx - (w_ / 2 - 3 if px > 0 else -w_ / 2 + 6) * u * (1 if px > 0 else -1), y - 230 * u, 3 * u, 230 * u); ctx.fill()
    # beam + roof
    src(ctx, '#3a2614'); ctx.rectangle(x - 230 * u, y - 245 * u, 460 * u, 14 * u); ctx.fill()
    ctx.save(); ctx.translate(x, y - 250 * u); ctx.scale(u, u)
    frond_roof(ctx, -260, 260, 0, t, c='#3d4a28', seed=5, lit='#ffb45a', lit_a=0.35 * glow_k)
    ctx.restore()

def light_motes(ctx, x, y, t, n=70, spread=220, height=620, a=1.0, seed=9):
    r = rnd(seed)
    for i in range(n):
        sp = r.uniform(25, 60); ph = r.random()
        life = (t * sp / height + ph) % 1
        mx = x + r.uniform(-0.5, 0.5) * spread * (1 - 0.6 * life) + math.sin(t * 0.8 + i) * 20
        my = y - life * height
        aa = a * math.sin(life * PI) * r.uniform(0.5, 1)
        glow(ctx, mx, my, r.uniform(8, 16), '#ffd88a', 0.5 * aa)
        src(ctx, '#fff4d6', aa); circle(ctx, mx, my, r.uniform(1.4, 2.6)); ctx.fill()

# ---------------- scenes ----------------
def sc_day(t, u):
    """Die Brunnen von Badr: warm day, men and camels arrive at the wells (far, small)"""
    surf, ctx = new_ctx(); P = PAL['day']
    cam = drift(Cam(lerp(900, 1010, u), 540, lerp(1.0, 1.06, u)), t, 0.4, 2)
    bg16(ctx, t, cam, P, seed=4, sun_pos=(1560, 190), sun_r=38, clouds_a=0.45, far_amp=200, mid_amp=95, ray_a=0.07)
    def g():
        floor16(ctx, t, P, seed=5, rocks_n=18)
        items = []
        for wx, wy, ws in ((1300, 790, 0.62), (1560, 860, 0.8)):
            items.append((wy, 'well', wx, ws))
        for px, py, ph in ((1180, 740, 1.6), (1700, 760, 1.9), (1430, 720, 1.3)):
            items.append((py, 'palm', px, ph))
        for i in range(16):
            row = i % 2
            y = 820 + row * 46 + (i % 3) * 6
            x = -150 + (i // 2) * 120 + row * 50 + t * 70
            items.append((y, 'man', x, i))
        for i in range(4):
            y = 800 + (i % 2) * 70
            x = -260 + i * 230 + t * 70
            items.append((y, 'camel', x, i))
        for y, kind, x, k in sorted(items):
            if kind == 'well': well(ctx, x, y, k, t)
            elif kind == 'palm': palm(ctx, x, y, 300 * k / 1.6, t, seed=int(x))
            elif kind == 'man':
                s = S_(y) * 0.9
                folk(ctx, x, y, s, t, 40 + k, facing=1, walk=1.0, phase=t * 5.2 + k * 1.3, sun_dir=1)
            else:
                camel(ctx, x, y, S_(y) * 0.95, t, facing=1, walk=1.0, phase=t * 3.4 + k, col=['#c8955a', '#b07a48', '#d4a46a', '#a8784a'][k])
        dust(ctx, t, n=50, seed=8, c=(1, 0.92, 0.75), a=0.35, area=(-100, 600, 2020, 1100), speed=1.5)
    layer(ctx, cam, 1.0, g)
    vignette(ctx, 0.35)
    return to_np(surf)

def sc_camp(t):
    """night after the rain: companions asleep on the firm wet sand, camels couched, moon"""
    surf, ctx = new_ctx(); P = PAL['night']
    u = ramp(t, 10.0, 18.4)
    cam = drift(Cam(lerp(940, 1000, u), lerp(560, 575, u), lerp(1.04, 1.14, u)), t, 0.35, 3)
    bg16(ctx, t, cam, P, seed=2, moon_pos=(1640, 150), stars_a=0.9, clouds_a=0.28, cloud_y=250, cloud_c='#5a6a9a',
         far_amp=180, mid_amp=90, haze_a=0.12)
    rim = (0.72, 0.8, 1.0)
    def g():
        floor16(ctx, t, P, seed=3, rocks_n=10, lines_a=0.08)
        # wet sheen in the moonlight
        for px, py, pw in ((1330, 735, 50), (760, 1040, 110), (1760, 950, 90), (300, 790, 45), (1020, 880, 70)):
            puddle(ctx, px, py, pw, t)
        items = []
        for x, y, f_ in ((420, 735, 1), (1560, 742, -1), (1180, 705, 1)):
            items.append((y, 'camel', x, f_))
        sl = [(250, 800, 1), (640, 820, -1), (980, 790, 1), (1330, 815, 1), (1760, 805, -1),
              (120, 960, -1), (560, 1010, 1), (1080, 975, -1), (1560, 1020, 1), (1900, 1080, -1),
              (800, 735, 1), (1000, 718, -1), (1820, 728, -1), (90, 730, 1),
              (420, 900, -1), (820, 925, 1), (1480, 880, 1), (1180, 845, -1), (1900, 870, 1), (40, 860, 1)]
        for i, (x, y, f_) in enumerate(sl):
            items.append((y, 'sleep', x, (i, f_)))
        for x, y in ((1280, 900), (380, 880)):
            items.append((y, 'fire', x, 0))
        for x, y in ((860, 860), (1660, 905), (300, 1060)):
            items.append((y, 'gear', x, 0))
        for x, y in ((1120, 760), (1150, 762), (620, 752)):
            items.append((y, 'spear', x, 0))
        for y, kind, x, k in sorted(items):
            s = S_(y, 320)
            if kind == 'camel': resting_camel(ctx, x, y, s * 0.75, t, facing=k, col='#7a6458', i=int(x), rim=rim, rim_a=0.3)
            elif kind == 'sleep': sleeper(ctx, x, y, s * 0.82, t, k[0], facing=k[1], rim=rim, rim_a=0.28)
            elif kind == 'fire': embers(ctx, x, y, s * 0.6, t, a=ramp(t, 11.0, 13.5))
            elif kind == 'gear': waterskin(ctx, x, y, s * 0.8); saddle(ctx, x + 70 * s, y + 8 * s, s * 0.8)
            else: spear_ground(ctx, x, y, s * 0.9, lean=0.06 if x % 2 else -0.05)
        dust(ctx, t, n=30, seed=4, c=(0.75, 0.82, 1.0), a=0.18, area=(-100, 200, 2020, 1100), speed=0.5)
    layer(ctx, cam, 1.0, g)
    grade(ctx, '#3a4a9a', 0.18)
    vignette(ctx, 0.5)
    return to_np(surf)

def sc_prayer(t):
    """night: the 'Arisch on the hill above the plain, warm light inside, light rising to the sky (no person shown)"""
    surf, ctx = new_ctx(); P = PAL['night']
    u = ramp(t, 29.9, 39.6)
    cam = drift(Cam(lerp(870, 900, u), lerp(560, 500, u), lerp(1.06, 1.12, u)), t, 0.3, 6)
    bg16(ctx, t, cam, P, seed=7, moon_pos=(1500, 120), stars_a=1.0, clouds_a=0.2, cloud_y=200, cloud_c='#4a5a8a',
         far_amp=170, mid_amp=80, haze_a=0.1)
    def g():
        floor16(ctx, t, P, seed=8, rocks_n=8, lines_a=0.07)
        # distant sleeping camp on the plain: tiny shapes, embers
        r = rnd(3)
        camp = sorted([(690 + r.uniform(0, 70), 1000 + r.uniform(0, 880), r.choice((-1, 1))) for i in range(34)])
        for i, (y, x, f_) in enumerate(camp):
            sleeper(ctx, x, y, S_(y, 700) * 0.5, t, 200 + i, facing=f_, rim=(0.72, 0.8, 1.0), rim_a=0.3)
        for x, y in ((1150, 722), (1480, 738), (1760, 715)):
            embers(ctx, x, y, 0.18, t)
        # the hill with the hut
        pts = []
        ctx.move_to(-400, 1300)
        for k in range(0, 160):
            x = -400 + k * 20
            y = 770 - 120 * math.exp(-((x - 340) / 520) ** 2)
            pts.append((x, y)); ctx.line_to(x, y)
        ctx.line_to(2800, 1300); ctx.close_path()
        ctx.set_source(lingrad(0, 640, 0, 1100, [(0, '#2a2840'), (1, '#0e0c18')])); ctx.fill()
        ridge_light(ctx, pts, '#8aa0ff', 0.2, 2)
        rocks(ctx, 700, seed=12, n=12, c='#22203a', spread=(-300, 900), size=(8, 26))
        arish(ctx, 340, 652, 0.95, t)
        spear_ground(ctx, 580, 664, 0.7, lean=-0.12)
        spear_ground(ctx, 605, 666, 0.7, lean=-0.08)
        light_motes(ctx, 340, 560, t, n=90, spread=300, height=600, a=ramp(t, 30.2, 31.5))
        dust(ctx, t, n=25, seed=6, c=(0.75, 0.82, 1.0), a=0.15, area=(-100, 100, 2020, 1100), speed=0.4)
    layer(ctx, cam, 1.0, g)
    grade(ctx, '#3a4a9a', 0.15)
    vignette(ctx, 0.5)
    return to_np(surf)

def sc_angels(t, t0):
    """dawn: the Muslims in rows on the plain far away, waves of light descend from the clouds (no figures for the angels)"""
    surf, ctx = new_ctx(); P = PAL['dawn']
    u = ramp(t, t0, t0 + 7.0)
    cam = drift(Cam(960, lerp(560, 520, u), lerp(1.03, 1.1, u)), t, 0.3, 8)
    bg16(ctx, t, cam, P, seed=9, sun_pos=(980, 650), sun_r=44, sun_a=0.9, clouds_a=0.6, cloud_y=330, ray_a=0.12,
         far_amp=170, mid_amp=80)
    def g():
        floor16(ctx, t, P, seed=10, rocks_n=14)
        # rows of the Muslims far away, small silhouettes
        for row in range(4):
            y = 720 + row * 22
            s = S_(y) * 0.55
            for k in range(46):
                x = 380 + k * 26 + row * 9
                person(ctx, x, y, s, t, facing=1, robe='#3a2830', robe2='#2a1a20', turban='#5a4048', beard='#1a1010', skin='#3a2620',
                       seed=row * 60 + k, shadow_a=0.15, sun_dir=-1)
        # waves of light descending, one after the other
        r = rnd(21)
        for i in range(260):
            wave = i // 52
            st = t0 + 1.0 + wave * 0.9 + r.uniform(0, 0.6)
            if t < st: continue
            p = min(1.0, (t - st) / 2.6); e = 1 - (1 - p) ** 3
            x = 340 + r.uniform(0, 1240) + math.sin(t * 0.7 + i) * 8
            y0 = 300 + r.uniform(-40, 30); y1 = 560 + r.uniform(0, 110)
            y = lerp(y0, y1, e)
            aa = min(1, (t - st) / 0.4) * (0.65 + 0.35 * math.sin(t * 3 + i))
            ctx.set_source(lingrad(x, y - 70, x, y, [(0, alpha('#fff4d6', 0)), (1, alpha('#fff4d6', 0.45 * aa * (1 - p * 0.6)))]))
            ctx.set_line_width(2.2); ctx.move_to(x, y - 70 * (1 - p * 0.7)); ctx.line_to(x, y); ctx.stroke()
            glow(ctx, x, y, 22, '#ffe6a8', 0.5 * aa)
            src(ctx, '#ffffff', 0.9 * aa); circle(ctx, x, y, 2.2); ctx.fill()
        dust(ctx, t, n=40, seed=11, c=(1, 0.9, 0.8), a=0.3, area=(-100, 500, 2020, 1100), speed=0.8)
    layer(ctx, cam, 1.0, g)
    grade(ctx, '#ff9a6a', 0.08)
    vignette(ctx, 0.4)
    return to_np(surf)

if __name__ == '__main__':
    import cv2
    out = sys.argv[1]; which = sys.argv[2:]
    fs = []
    for w in which:
        name, tt = w.split('@'); tt = float(tt)
        f = {'day': lambda: sc_day(tt, tt / 3.3), 'camp': lambda: sc_camp(tt), 'prayer': lambda: sc_prayer(tt),
             'angels': lambda: sc_angels(tt, 46.9)}[name]()
        fs.append(cv2.resize(f, (960, 540)))
    while len(fs) % 2: fs.append(np.zeros_like(fs[0]))
    cv2.imwrite(out, np.vstack([np.hstack(fs[i:i + 2]) for i in range(0, len(fs), 2)])[:, :, ::-1])
