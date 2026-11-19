from kit import *
from hq import *
st = Story('freitag'); S, E, w = st.S, st.E, st.w
DUR = st.DUR
HZ = 1150

def glowfig(ctx, x, y, s, t, **kw):
    d = dict(robe='#f2e8d2', robe2='#3c7a6e', cloak='#2a6a66', seed=5)
    d.update(kw)
    sd = d.get('seed', 5)
    xx = x + math.sin(t * 0.72 + sd) * 4 * s + math.sin(t * 0.31 + sd * 2) * 2.5 * s
    contact(ctx, xx, y, s * 0.85, a=0.3)
    person(ctx, xx, y, s, t, **d)

def minaret(ctx, x, y, s, c='#e8dcc4', lit=0.0):
    h = 520 * s
    src(ctx, shade(c, -0.3)); rrect(ctx, x - 34 * s, y - 24 * s, 68 * s, 26 * s, 5 * s); ctx.fill()
    ctx.set_source(lingrad(x - 24 * s, y, x + 24 * s, y, [(0, shade(c, 0.2)), (0.6, c), (1, shade(c, -0.34))]))
    rrect(ctx, x - 21 * s, y - h, 42 * s, h, 6 * s); ctx.fill()
    # Balkon
    by = y - h * 0.68
    src(ctx, shade(c, -0.22)); rrect(ctx, x - 36 * s, by, 72 * s, 15 * s, 4 * s); ctx.fill()
    src(ctx, shade(c, 0.12)); rrect(ctx, x - 32 * s, by - 26 * s, 64 * s, 26 * s, 4 * s); ctx.fill()
    src(ctx, shade(c, -0.4), 0.5)
    for k in range(5):
        ctx.rectangle(x - 28 * s + k * 13 * s, by - 24 * s, 4 * s, 22 * s); ctx.fill()
    # Laternenstube
    src(ctx, shade(c, -0.1)); rrect(ctx, x - 25 * s, y - h - 4 * s, 50 * s, 46 * s, 5 * s); ctx.fill()
    if lit:
        src(ctx, '#ffd98a', 0.75 * lit); rrect(ctx, x - 18 * s, y - h + 4 * s, 36 * s, 32 * s, 4 * s); ctx.fill()
        glow(ctx, x, y - h + 18 * s, 90 * s, '#ffd27a', 0.3 * lit)
    # Spitze
    ctx.set_source(lingrad(x, y - h - 86 * s, x, y - h - 4 * s, [(0, shade(c, 0.32)), (1, shade(c, -0.14))]))
    ctx.new_path(); ctx.move_to(x - 28 * s, y - h - 4 * s)
    ctx.line_to(x, y - h - 86 * s); ctx.line_to(x + 28 * s, y - h - 4 * s)
    ctx.close_path(); ctx.fill()
    src(ctx, '#e3c46a'); ctx.set_line_width(4 * s)
    ctx.new_path(); ctx.move_to(x, y - h - 86 * s); ctx.line_to(x, y - h - 112 * s); ctx.stroke()
    circle(ctx, x, y - h - 119 * s, 8 * s); ctx.fill()

def dome(ctx, x, y, s, c='#e8dcc4', lit=0.0):
    top = y - 176 * s
    ctx.set_source(lingrad(x - 110 * s, top, x + 130 * s, y,
                           [(0, shade(c, 0.3)), (0.5, c), (1, shade(c, -0.36))]))
    ctx.new_path(); ctx.move_to(x - 150 * s, y)
    ctx.curve_to(x - 150 * s, y - 236 * s, x + 150 * s, y - 236 * s, x + 150 * s, y)
    ctx.close_path(); ctx.fill()
    src(ctx, shade(c, 0.4), 0.3)
    ctx.new_path(); ctx.move_to(x - 108 * s, y - 56 * s)
    ctx.curve_to(x - 100 * s, y - 160 * s, x - 30 * s, y - 186 * s, x - 6 * s, y - 172 * s)
    ctx.curve_to(x - 60 * s, y - 158 * s, x - 86 * s, y - 112 * s, x - 90 * s, y - 50 * s)
    ctx.close_path(); ctx.fill()
    src(ctx, shade(c, -0.3)); rrect(ctx, x - 164 * s, y - 14 * s, 328 * s, 20 * s, 5 * s); ctx.fill()
    src(ctx, '#e3c46a'); ctx.set_line_width(6 * s)
    ctx.new_path(); ctx.move_to(x, top + 4 * s); ctx.line_to(x, top - 48 * s); ctx.stroke()
    circle(ctx, x, top - 58 * s, 11 * s); ctx.fill()
    if lit:
        glow(ctx, x, top - 40 * s, 140 * s, '#ffd27a', 0.28 * lit)

def masjid(ctx, x, y, s, lit=0.0):
    c = '#e8dcc4'
    hall = 210 * s
    roof = y - hall
    ctx.set_source(lingrad(x - 330 * s, roof, x + 330 * s, y,
                           [(0, shade(c, 0.16)), (0.55, shade(c, -0.06)), (1, shade(c, -0.34))]))
    rrect(ctx, x - 330 * s, roof, 660 * s, hall, 8 * s); ctx.fill()
    src(ctx, shade(c, -0.26)); rrect(ctx, x - 346 * s, roof - 18 * s, 692 * s, 22 * s, 5 * s); ctx.fill()
    # Boegen
    for k, bx in enumerate((-230, -115, 115, 230)):
        px = x + bx * s
        ctx.set_source(lingrad(px, roof + 44 * s, px, y, [(0, '#4e3626'), (1, '#241710')]))
        ctx.new_path(); ctx.move_to(px - 36 * s, y)
        ctx.line_to(px - 36 * s, roof + 104 * s)
        ctx.curve_to(px - 36 * s, roof + 44 * s, px + 36 * s, roof + 44 * s, px + 36 * s, roof + 104 * s)
        ctx.line_to(px + 36 * s, y); ctx.close_path(); ctx.fill()
        if lit:
            src(ctx, '#ffd98a', 0.5 * lit)
            ctx.new_path(); ctx.move_to(px - 27 * s, y)
            ctx.line_to(px - 27 * s, roof + 108 * s)
            ctx.curve_to(px - 27 * s, roof + 58 * s, px + 27 * s, roof + 58 * s, px + 27 * s, roof + 108 * s)
            ctx.line_to(px + 27 * s, y); ctx.close_path(); ctx.fill()
    # Haupttor
    ctx.set_source(lingrad(x, roof + 20 * s, x, y, [(0, '#5a3f2c'), (1, '#2a1c12')]))
    ctx.new_path(); ctx.move_to(x - 54 * s, y)
    ctx.line_to(x - 54 * s, roof + 112 * s)
    ctx.curve_to(x - 54 * s, roof + 30 * s, x + 54 * s, roof + 30 * s, x + 54 * s, roof + 112 * s)
    ctx.line_to(x + 54 * s, y); ctx.close_path(); ctx.fill()
    if lit:
        src(ctx, '#ffd98a', 0.62 * lit)
        ctx.new_path(); ctx.move_to(x - 42 * s, y)
        ctx.line_to(x - 42 * s, roof + 116 * s)
        ctx.curve_to(x - 42 * s, roof + 46 * s, x + 42 * s, roof + 46 * s, x + 42 * s, roof + 116 * s)
        ctx.line_to(x + 42 * s, y); ctx.close_path(); ctx.fill()
        glow(ctx, x, y - 70 * s, 190 * s, '#ffcf80', 0.26 * lit)
    dome(ctx, x, roof - 2 * s, s, lit=lit)
    minaret(ctx, x - 396 * s, y, s * 0.9, lit=lit)
    minaret(ctx, x + 396 * s, y, s * 0.9, lit=lit)

def skyline(ctx, t, x0, y, s, seed=3, n=9, lit=0.0):
    r = rnd(seed)
    for k in range(n):
        bx = x0 + k * 128 * s + r.uniform(-14, 14) * s
        bh = r.uniform(170, 330) * s
        c = mix('#8a6a4e', '#5e4a38', r.random())
        ctx.set_source(lingrad(bx, y - bh, bx, y, [(0, shade(c, 0.2)), (1, shade(c, -0.35))]))
        rrect(ctx, bx - 44 * s, y - bh, 88 * s, bh, 6 * s); ctx.fill()
        if lit:
            for wy in range(2, int(bh / (44 * s))):
                for wx in (-22, 0, 22):
                    if r.random() < 0.45: continue
                    src(ctx, '#ffd98a', 0.5 * lit * r.uniform(0.5, 1))
                    rrect(ctx, bx + wx * s - 7 * s, y - wy * 44 * s, 14 * s, 18 * s, 3 * s); ctx.fill()

def crack_sky(ctx, t, a=1.0, seed=2):
    """Risse aus Licht im Nachthimmel"""
    r = rnd(seed)
    for k in range(4):
        ph = clamp((math.sin(t * 0.5 + k * 1.3) + 1) * 0.5)
        src(ctx, '#ffe9b8', 0.5 * a * ph); ctx.set_line_width(r.uniform(3, 7))
        x = r.uniform(60, 1020); y = r.uniform(80, 520)
        ctx.new_path(); ctx.move_to(x, y)
        for i in range(5):
            x += r.uniform(-70, 70); y += r.uniform(40, 110)
            ctx.line_to(x, y)
        ctx.stroke()

def star_fall(ctx, t, n=9, seed=4, a=0.8):
    r = rnd(seed)
    for k in range(n):
        p = (t * r.uniform(0.3, 0.6) + r.uniform(0, 1)) % 1.0
        x = r.uniform(-100, 1180) + p * 240
        y = r.uniform(-60, 420) + p * 560
        src(ctx, '#fff3cf', a * (1 - p) * 0.9); ctx.set_line_width(4)
        ctx.new_path(); ctx.move_to(x, y); ctx.line_to(x - 56, y - 120); ctx.stroke()
        circle(ctx, x, y, 5 * (1 - p * 0.4)); ctx.fill()

def rays_down(ctx, x, y0, y1, w0, w1, c='#ffe6b0', a=0.3, t=0.0):
    for k in range(3):
        aa = a * (0.5 + 0.5 * math.sin(t * 1.1 + k))
        ctx.set_source(lingrad(0, y0, 0, y1, [(0, C(c, aa * 0.8)), (1, C(c, 0.0))]))
        ctx.new_path()
        ctx.move_to(x - w0 - k * 16, y0); ctx.line_to(x + w0 + k * 16, y0)
        ctx.line_to(x + w1 + k * 46, y1); ctx.line_to(x - w1 - k * 46, y1)
        ctx.close_path(); ctx.fill()

# ================== Szenen ==================
# 0: Morgen ist der beste Tag der Woche
def sc_hook(ctx, t):
    keys = [(0, Cam(540, 1180, 1.12, 0.0)), (S[1] - 0.2, Cam(540, 1150, 1.0, 0.0))]
    cam = drift(keycam(keys, t), t, 0.25, 1)
    hq_world(ctx, t, cam, 1330, sun=(540, 760), sky=SKY_DAWN, rays=0.24, seed=1,
             g1='#e6b584', g2='#996a43', soft=1900, bokeh=0.08)
    def far():
        skyline(ctx, t, -40, 1308, 0.46, seed=7, n=11, lit=0.6)
    layer(ctx, cam, 0.9, far)
    def mid():
        glow(ctx, 540, 1180, 560, '#ffd890', 0.3)
        masjid(ctx, 540, 1352, 0.82, lit=0.78)
        flock(ctx, t, (t * 80) % 1800 - 340, 520, s=1.0, n=10, a=0.5)
    layer(ctx, cam, 1.0, mid)

# 1: Und die meisten verpassen ihn
def sc_miss(ctx, t):
    keys = [(S[1], Cam(540, 1300, 1.22, 0.0)), (S[2], Cam(600, 1330, 1.38, 0.0))]
    cam = drift(keycam(keys, t), t, 0.3, 2)
    hq_world(ctx, t, cam, 1360, sun=(240, 800), sky=SKY_DAWN, rays=0.18, seed=3,
             g1='#dcae7e', g2='#8e6440', soft=1930, bokeh=0.07)
    def back():
        glow(ctx, 250, 1240, 420, '#ffd890', 0.3)
        masjid(ctx, 250, 1366, 0.52, lit=0.8)
        skyline(ctx, t, 560, 1368, 0.4, seed=9, n=6, lit=0.3)
    layer(ctx, cam, 0.92, back)
    def near():
        march(ctx, t, ((1560, 0.62, 5, 54), (1680, 0.78, 4, 68)), seed=31, draw=marcher)
        dust(ctx, t, 18, a=0.14)
    layer(ctx, cam, 1.06, near)

# 2a: Der Prophet sallallahu alayhi wa sallam sagte
def sc_hadith(ctx, t):
    keys = [(S[2], Cam(540, 1240, 1.06, 0.0)), (S[2] + 3.8, Cam(560, 1190, 1.26, 0.0))]
    cam = drift(keycam(keys, t), t, 0.26, 3)
    hq_world(ctx, t, cam, 1320, sun=(540, 700), sky=SKY_GOLD, rays=0.3, seed=5,
             g1='#eec086', g2='#9d6c42', soft=1930, bokeh=0.09)
    def f():
        glow(ctx, 540, 820, 620, '#ffe6b0', 0.34)
        light_presence(ctx, 540, 1320, 1.25, t, a=0.9)
        flock(ctx, t, (t * 95 + 300) % 1900 - 360, 470, s=1.1, n=12, a=0.6)
    layer(ctx, cam, 1.0, f)

# 2b: der beste Tag an dem die Sonne aufgeht
def sc_sunrise(ctx, t):
    keys = [(S[2] + 3.8, Cam(540, 1180, 1.1, 0.0)), (S[3], Cam(500, 1240, 1.34, 0.0))]
    cam = drift(keycam(keys, t), t, 0.3, 6)
    hq_world(ctx, t, cam, 1330, sun=(540, 980), sky=SKY_DAWN, rays=0.34, seed=8,
             g1='#eab77c', g2='#986840', soft=1920, bokeh=0.1)
    def sun_():
        pr = clamp((t - (S[2] + 3.8)) / 3.2)
        sy = 1120 - pr * 150
        ctx.set_source(radgrad(540, sy, 0, 340, [(0, C('#ffe8bc', 0.55)), (0.42, C('#ffbf78', 0.3)), (1, C('#ff9a4a', 0.0))]))
        circle(ctx, 540, sy, 340); ctx.fill()
        ctx.set_source(radgrad(540, sy, 0, 130, [(0, C('#fff6de', 1.0)), (0.76, C('#ffdc9a', 1.0)), (1, C('#ffba62', 0.92))]))
        circle(ctx, 540, sy, 128); ctx.fill()
    layer(ctx, cam, 0.5, sun_)
    def f():
        skyline(ctx, t, -60, 1300, 0.32, seed=17, n=15, lit=0.55)
        flock(ctx, t, (t * 110) % 1900 - 360, 540, s=1.15, n=13, a=0.72)
        flock(ctx, t, (t * 88 + 800) % 1900 - 360, 680, s=0.85, n=9, a=0.48)
    layer(ctx, cam, 0.94, f)
    def near():
        glowfig(ctx, 790, 1640, 0.98, t, facing=-1, arms=(0.24, -0.08), elbows=(0.3, 0.3))
    layer(ctx, cam, 1.06, near)

# 3a: An ihm wurde Adam erschaffen, an ihm kam er ins Paradies
SKY_GARDEN = dict(top='#27477f', mid='#8fb4c6', low='#e8f0c0', haze='#d4e6ac')
def sc_adam(ctx, t):
    keys = [(S[3], Cam(540, 1300, 1.26, 0.0)), (S[3] + 3.6, Cam(520, 1250, 1.08, 0.0))]
    cam = drift(keycam(keys, t), t, 0.22, 7)
    hq_world(ctx, t, cam, 1360, sun=(540, 700), sky=SKY_GARDEN, rays=0.2, seed=9,
             g1='#a9c072', g2='#5c7038', soft=1930, bokeh=0.09, detail=False, ridge_base='#49683f')
    def back():
        for (px, pyy, ph, sd) in ((120, 1364, 470, 1), (930, 1360, 430, 3), (300, 1352, 360, 5), (760, 1356, 390, 7)):
            palm(ctx, px, pyy, ph, t, seed=sd)
        flock(ctx, t, (t * 70 + 500) % 1900 - 360, 430, s=0.9, n=9, a=0.42)
    layer(ctx, cam, 0.93, back)
    def f():
        pr = clamp((t - S[3]) / 2.4)
        rays_down(ctx, 540, 260, 1380, 70, 250, a=0.28, t=t)
        glow(ctx, 540, 1230, 460 * (0.55 + 0.45 * pr), '#fff2c8', 0.34 * pr)
        contact(ctx, 540, 1380, 0.85, a=0.26)
        prophet(ctx, 540 + math.sin(t * 0.7) * 4, 1380, 1.0, t, robe='#f6f0dc', robe2='#5f8f52',
                arms=(0.24, -0.08), elbows=(0.3, 0.3), alpha_=0.25 + 0.75 * eo(pr), seed=4)
    layer(ctx, cam, 1.0, f)
    def fore():
        for (bx, by, bs, sd) in ((110, 1700, 1.0, 2), (330, 1790, 1.2, 4), (790, 1740, 1.1, 6), (980, 1840, 1.3, 8)):
            bush(ctx, bx, by, bs, t, seed=sd)
        grass_band(ctx, t, cam, y=1620, c='#3f5a24', seed=12, n=9, par=1.1,
                   x0=-60, x1=1160, avoid=540, gap=240)
    layer(ctx, cam, 1.1, fore)

# 3b: und an ihm musste er es verlassen
def sc_leave(ctx, t):
    keys = [(S[3] + 3.6, Cam(540, 1290, 1.16, 0.0)), (S[4], Cam(640, 1320, 1.3, 0.0))]
    cam = drift(keycam(keys, t), t, 0.3, 11)
    hq_world(ctx, t, cam, 1360, sun=(200, 860), sky=SKY_DUSK, rays=0.18, seed=13,
             g1='#c89a6a', g2='#7e5636', soft=1930, bokeh=0.08)
    def back():
        for (px, pyy, ph, sd) in ((90, 1362, 420, 1), (240, 1356, 350, 5)):
            palm(ctx, px, pyy, ph, t, seed=sd)
        glow(ctx, 170, 1180, 420, '#ffe0a0', 0.28)
        grass_band(ctx, t, cam, y=1430, c='#4a5a30', seed=14, n=5, par=0.96, x0=-140, x1=380)
    layer(ctx, cam, 0.93, back)
    def f():
        pr = clamp((t - (S[3] + 3.6)) / 3.0)
        contact(ctx, 430 + pr * 320, 1600, 0.8, a=0.28)
        prophet(ctx, 430 + pr * 320, 1600, 0.95, t, robe='#e8dcc2', robe2='#8a6a4a',
                facing=1, walk=1.0, phase=0.4, seed=4)
        dust(ctx, t, 16, a=0.14)
    layer(ctx, cam, 1.04, f)

# 4: Und die Stunde wird an einem Freitag kommen
def sc_hour(ctx, t):
    keys = [(S[4], Cam(540, 1140, 1.0, 0.0)), (S[5], Cam(540, 1080, 1.16, 0.0))]
    cam = drift(keycam(keys, t), t, 0.35, 15)
    hq_world(ctx, t, cam, 1360, sun=(540, 300), sky=SKY_NIGHT, rays=0.0, seed=17,
             g1='#3a3550', g2='#1c1a2e', soft=1900, bokeh=0.05, stars=0.9, motes_a=0.12)
    def sky_():
        crack_sky(ctx, t, a=0.9, seed=19)
        star_fall(ctx, t, n=10, seed=21, a=0.85)
    layer(ctx, cam, 0.35, sky_)
    def f():
        skyline(ctx, t, 60, 1362, 0.5, seed=23, n=8, lit=0.12)
        masjid(ctx, 540, 1366, 0.6, lit=0.25)
    layer(ctx, cam, 1.0, f)

# 5: Am Freitag gibt es eine Stunde in der Allah jedem Muslim gibt
def sc_hourdua(ctx, t):
    keys = [(S[5], Cam(540, 1340, 1.3, 0.0)), (S[6], Cam(548, 1400, 1.72, 0.0))]
    cam = drift(keycam(keys, t), t, 0.22, 25)
    hq_world(ctx, t, cam, 1500, sun=(540, 560), sky=SKY_GOLD, rays=0.26, seed=27,
             g1='#f0c086', g2='#9d6c42', soft=1900, bokeh=0.1)
    def back():
        masjid(ctx, 540, 1440, 0.42, lit=0.6)
    layer(ctx, cam, 0.9, back)
    def f():
        rays_down(ctx, 540, 260, 1500, 70, 250, a=0.3, t=t)
        glow(ctx, 540, 1320, 480, '#ffe6b0', 0.3)
        glowfig(ctx, 540, 1640, 1.0, t, arms=(2.04, 1.88), elbows=(0.46, 0.52))
    layer(ctx, cam, 1.0, f)

# 6: Was kannst du morgen tun?
def sc_q(ctx, t):
    keys = [(S[6], Cam(540, 1230, 1.08, 0.0)), (S[7], Cam(540, 1210, 1.18, 0.0))]
    cam = drift(keycam(keys, t), t, 0.28, 29)
    hq_world(ctx, t, cam, 1340, sun=(540, 720), sky=SKY_DAWN, rays=0.22, seed=31,
             g1='#e6b584', g2='#996a43', soft=1920, bokeh=0.08)
    def f():
        glow(ctx, 540, 1180, 520, '#ffd890', 0.26)
        masjid(ctx, 540, 1342, 0.8, lit=0.7)
        glowfig(ctx, 540, 1640, 0.85, t, arms=(0.24, -0.08), elbows=(0.3, 0.3))
    layer(ctx, cam, 1.0, f)

# 7: Lies Sure Al Kahf
def sc_kahf(ctx, t):
    keys = [(S[7], Cam(540, 1480, 1.55, 0.0)), (S[8], Cam(548, 1460, 1.78, 0.0))]
    cam = drift(keycam(keys, t), t, 0.18, 33)
    hq_world(ctx, t, cam, 1520, sun=(300, 620), sky=SKY_GOLD, rays=0.2, seed=35,
             g1='#f0c086', g2='#9d6c42', soft=1920, bokeh=0.1)
    def f():
        glow(ctx, 540, 1480, 420, '#ffe6b0', 0.3)
        book(ctx, 540, 1540, 1.5, t, glow_a=0.8)
    layer(ctx, cam, 1.0, f)

# 8: Sprich viele Segenswuensche auf den Propheten
def sc_salat(ctx, t):
    keys = [(S[8], Cam(540, 1300, 1.2, 0.0)), (S[9], Cam(540, 1270, 1.34, 0.0))]
    cam = drift(keycam(keys, t), t, 0.22, 37)
    hq_world(ctx, t, cam, 1420, sun=(540, 640), sky=SKY_GOLD, rays=0.28, seed=39,
             g1='#f0c086', g2='#9d6c42', soft=1920, bokeh=0.1)
    def f():
        rays_down(ctx, 540, 240, 1420, 80, 260, a=0.3, t=t)
        glow(ctx, 540, 1100, 560, '#ffe6b0', 0.34)
        light_presence(ctx, 540, 1400, 1.1, t, a=0.85)
        glowfig(ctx, 290, 1660, 1.0, t, facing=1, arms=(2.0, 1.84), elbows=(0.46, 0.52))
        glowfig(ctx, 810, 1640, 0.94, t, facing=-1, arms=(2.0, 1.84), elbows=(0.46, 0.52), seed=8,
                robe='#e4d8bc', robe2='#6a5a44', cloak='#7a5a3e')
    layer(ctx, cam, 1.0, f)

# 9: Geh frueh zum Freitagsgebet
def sc_mosque(ctx, t):
    keys = [(S[9], Cam(540, 1290, 1.12, 0.0)), (S[10], Cam(520, 1320, 1.26, 0.0))]
    cam = drift(keycam(keys, t), t, 0.28, 41)
    hq_world(ctx, t, cam, 1360, sun=(820, 680), sky=SKY_DAWN, rays=0.22, seed=43,
             g1='#e6b584', g2='#996a43', soft=1920, bokeh=0.08)
    def back():
        glow(ctx, 540, 1200, 520, '#ffd890', 0.3)
        masjid(ctx, 540, 1362, 0.86, lit=0.8)
    layer(ctx, cam, 0.94, back)
    def near():
        march(ctx, t, ((1520, 0.56, 5, 44), (1650, 0.72, 4, 56)), seed=45, draw=marcher)
        dust(ctx, t, 14, a=0.12)
    layer(ctx, cam, 1.05, near)

# 10: Und mach Dua, besonders in der letzten Stunde vor Sonnenuntergang
def sc_sunset(ctx, t):
    keys = [(S[10], Cam(540, 1360, 1.3, 0.0)), (S[11], Cam(548, 1420, 1.72, 0.0))]
    cam = drift(keycam(keys, t), t, 0.2, 47)
    hq_world(ctx, t, cam, 1520, sun=(540, 1080), sky=SKY_DUSK, rays=0.3, seed=49,
             g1='#e8a870', g2='#8e5a38', soft=1900, bokeh=0.11)
    def back():
        ctx.set_source(radgrad(540, 1150, 0, 330, [(0, C('#ffe8bc', 0.55)), (0.42, C('#ffb268', 0.3)), (1, C('#ff8a3a', 0.0))]))
        circle(ctx, 540, 1150, 330); ctx.fill()
        ctx.set_source(radgrad(540, 1150, 0, 126, [(0, C('#fff4d6', 1.0)), (0.78, C('#ffd98a', 1.0)), (1, C('#ffb45e', 0.9))]))
        circle(ctx, 540, 1150, 124); ctx.fill()
    layer(ctx, cam, 0.5, back)
    def f():
        glow(ctx, 540, 1340, 520, '#ffcf8a', 0.3)
        glowfig(ctx, 540, 1660, 1.0, t, arms=(2.02, 1.86), elbows=(0.46, 0.52))
    layer(ctx, cam, 1.0, f)

# 11: Schick dieses Video weiter
def sc_cta(ctx, t):
    keys = [(S[11], Cam(540, 1240, 1.1, 0.0)), (DUR, Cam(540, 1210, 1.22, 0.0))]
    cam = drift(keycam(keys, t), t, 0.24, 51)
    hq_world(ctx, t, cam, 1350, sun=(540, 740), sky=SKY_GOLD, rays=0.26, seed=53,
             g1='#eec086', g2='#9d6c42', soft=1910, bokeh=0.1)
    def f():
        glow(ctx, 540, 1180, 560, '#ffe6b0', 0.3)
        masjid(ctx, 540, 1352, 0.82, lit=0.8)
        flock(ctx, t, (t * 85 + 200) % 1900 - 360, 470, s=1.0, n=11, a=0.55)
    layer(ctx, cam, 1.0, f)

SCENES = [(0.0, sc_hook), (S[1] - 0.2, sc_miss), (S[2] - 0.2, sc_hadith), (S[2] + 3.8, sc_sunrise), (S[3] - 0.2, sc_adam),
          (S[3] + 3.6, sc_leave), (S[4] - 0.2, sc_hour), (S[5] - 0.2, sc_hourdua),
          (S[6] - 0.3, sc_q), (S[7] - 0.2, sc_kahf), (S[8] - 0.2, sc_salat),
          (S[9] - 0.2, sc_mosque), (S[10] - 0.2, sc_sunset), (S[11] - 0.2, sc_cta)]

CHECK = [('Sure Al Kahf lesen', 7),
         ('Segenswünsche auf den Propheten', 8),
         ('Früh zum Freitagsgebet', 9),
         ('Dua vor Sonnenuntergang', 10)]

def checklist(ctx, t, t0, t1):
    if not (t0 <= t <= t1): return
    a = eo(clamp((t - t0) / 0.45)) * clamp((t1 - t) / 0.4)
    x0, y0, w = 76, 296, 928
    h = 128 + len(CHECK) * 94
    ctx.set_source(lingrad(0, y0, 0, y0 + h, [(0, C('#2e2218', 0.9 * a)), (1, C('#191109', 0.93 * a))]))
    rrect(ctx, x0, y0, w, h, 28); ctx.fill()
    src(ctx, GOLD, 0.7 * a); ctx.set_line_width(3)
    rrect(ctx, x0, y0, w, h, 28); ctx.stroke()
    set_font(ctx, 44, 'Cinzel')
    title = 'DEINE FREITAG CHECKLISTE'
    tw = text_w(ctx, title)
    src(ctx, GOLD, a); ctx.move_to(540 - tw / 2, y0 + 72); ctx.show_text(title)
    src(ctx, GOLD, 0.4 * a); ctx.rectangle(x0 + 60, y0 + 92, w - 120, 2); ctx.fill()
    for i, (txt, si) in enumerate(CHECK):
        ry = y0 + 168 + i * 94
        act = clamp((t - (S[si] - 0.25)) / 0.3)
        tick = clamp((t - (S[si] + 0.45)) / 0.28)
        bx = x0 + 52
        src(ctx, '#ffffff', (0.28 + 0.45 * act) * a); ctx.set_line_width(4)
        rrect(ctx, bx, ry - 38, 50, 50, 11); ctx.stroke()
        if tick > 0:
            src(ctx, '#3fbf6a', 0.92 * a * tick); rrect(ctx, bx, ry - 38, 50, 50, 11); ctx.fill()
            ctx.save(); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_line_join(cairo.LINE_JOIN_ROUND)
            src(ctx, '#ffffff', a * tick); ctx.set_line_width(8)
            ctx.new_path(); ctx.move_to(bx + 12, ry - 14)
            ctx.line_to(bx + 21, ry - 3); ctx.line_to(bx + 39, ry - 29); ctx.stroke(); ctx.restore()
        set_font(ctx, 38)
        src(ctx, (1, 1, 1), (0.42 + 0.58 * act) * a)
        ctx.move_to(bx + 78, ry); ctx.show_text(txt)

def overlays(ctx, t):
    cine(ctx, a=0.07, vig=0.16)
    hook_text(ctx, t, 0.3, 2.2, 'DER BESTE|TAG DER WOCHE', y=520)
    draw_quote(ctx, 'Der beste Tag, an dem die Sonne aufgeht, ist der Freitag.',
               'Sahih Muslim 854', t, S[2] + 2.6, S[3] - 0.25, y=430)
    draw_kw(ctx, 'ADAM  PARADIES  DIE STUNDE', t, S[3] + 0.3, S[4] + 1.6, y=300)
    draw_quote(ctx, 'Am Freitag gibt es eine Stunde, in der Allah jedem Muslim gibt, worum er Ihn bittet.',
               'Sahih al Bukhari 935', t, S[5] + 1.4, S[6] - 0.35, y=440)
    checklist(ctx, t, S[6] + 0.45, S[11] - 0.15)
    cta(ctx, t, S[11] + 0.2, DUR, 'SCHICK ES WEITER', 'Welchen Punkt vergisst du am meisten?')

def frame(ctx, t):
    standard_frame(ctx, t, st, lambda c, tt: run_scenes(c, tt, SCENES), overlays,
                   'Der beste Tag der Woche',
                   ['Sahih Muslim 854', 'Sahih al Bukhari 935', 'Abu Dawud 1047 und 1048'])
