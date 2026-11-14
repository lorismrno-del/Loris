from kit import *
st = Story('hajar'); S, E, w = st.S, st.E, st.w
DUR = st.DUR
HAJ = dict(cloth='#3a2a22', trim='#6a4a32')
IB = dict(robe='#e6dcc6', robe2='#6a5a3a')
HZ = 1150
SAFA, MARWA = 290, 790

def valley(ctx, t, cam, P, sun=(820, 360), heat=0.0):
    bg(ctx, t, cam, P, horizon=HZ, sun_pos=sun, sun_r=50, clouds_a=0.15, seed=60, far_amp=340, mid_amp=220, ray_a=0.1)
    def f():
        side_hills(ctx, HZ + 180, 380, P['mid_r'], seed=61, l=180, r=900, col2=shade(P['mid_r'], 0.18))
    layer(ctx, cam, 0.8, f)
    def g():
        ground(ctx, HZ + 120, P['g1'], P['g2'])
        dune_lines(ctx, HZ + 120, t, shade(P['g2'], -0.3), seed=62, a=0.12)
        rocks(ctx, HZ + 160, seed=63, n=8, c=shade(P['near'], 0.2))
        if heat > 0:
            for k in range(6):
                yy = HZ + 200 + k * 30
                src(ctx, (1, 1, 1), 0.05 * heat); ctx.set_line_width(6)
                ctx.move_to(-200, yy)
                x = -200
                while x < 1300:
                    ctx.line_to(x, yy + math.sin(x * 0.02 + t * 4 + k) * 5); x += 30
                ctx.stroke()
    layer(ctx, cam, 1.0, g)

def acacia(ctx, x, y, s, t):
    u = s
    src(ctx, '#4a3626'); ctx.set_line_width(14 * u); ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.move_to(x, y); ctx.curve_to(x - 10 * u, y - 80 * u, x + 20 * u, y - 140 * u, x + 10 * u, y - 200 * u); ctx.stroke()
    for k in range(5):
        ex = x + (-140 + k * 70) * u + math.sin(t * 0.8 + k) * 4 * u
        ctx.set_line_width(6 * u); ctx.move_to(x + 10 * u, y - 170 * u); ctx.line_to(ex, y - 230 * u); ctx.stroke()
    ctx.set_source(radgrad(x, y - 260 * u, 10 * u, 200 * u, [(0, '#6a8a3a'), (1, '#3a5a22')]))
    ellipse(ctx, x, y - 250 * u, 190 * u, 45 * u); ctx.fill()

def hajar(ctx, x, y, s, t, run=0.0, phase=0.0, facing=1, hold=True, arms=None, tilt=0.0):
    if hold and arms is None:
        woman(ctx, x, y, s, t, facing=facing, walk=run, phase=phase, tilt=tilt, lean=0.08 * run, **CARRY, **HAJ)
    else:
        woman(ctx, x, y, s, t, facing=facing, walk=run, phase=phase, arms=arms or (0.3, 0.2), elbows=(0.3, 0.3), tilt=tilt,
              lean=0.08 * run, **HAJ)

def sc_hook(ctx, t):
    P = PAL['day']
    keys = [(0, Cam(560, 1300, 1.35, 0.0)), (S[3] - 0.2, Cam(560, 1250, 1.15, 0.0))]
    cam = drift(keycam(keys, t), t, 0.5, 1)
    valley(ctx, t, cam, P, heat=1.0)
    def f():
        acacia(ctx, 760, 1480, 1.0, t)
        hajar(ctx, 560, 1540, 1.05, t, tilt=0.06)
        dust(ctx, t, 40, a=0.3)
    layer(ctx, cam, 1.0, f)

def sc_bring(ctx, t):
    P = PAL['day']; lt = t - S[3]
    x = lerp(-200, 420, clamp(lt / 5.6))
    walking = 1 if lt < 5.6 else 0
    keys = [(0, Cam(300, 1280, 1.1, 0.0)), (5.6, Cam(480, 1260, 1.2, 0.0))]
    cam = drift(keycam(keys, lt), t, 0.6, 2)
    valley(ctx, t, cam, P)
    def f():
        acacia(ctx, 760, 1480, 1.0, t)
        hajar(ctx, x - 150, 1540, 1.0, t, run=walking, phase=t * 5.5)
        prophet(ctx, x, 1550, 1.05, t, facing=1, walk=walking, phase=t * 5.5 + 1, prop2=None, **IB)
        dust(ctx, t, 40, a=0.3)
    layer(ctx, cam, 1.0, f)

def sc_leave(ctx, t):
    P = PAL['day']; lt = t - S[4]
    ix = lerp(420, -400, clamp((t - S[4]) / 8.5))
    keys = [(0, Cam(380, 1270, 1.3, 0.0)), (w(4, 'Hat') - S[4], Cam(420, 1240, 2.0, 0.02)), (S[5] - S[4], Cam(250, 1250, 1.6, 0.0)),
            (S[6] - S[4], Cam(440, 1240, 2.1, -0.02)), (S[7] - S[4], Cam(420, 1250, 1.9, -0.02))]
    cam = drift(keycam(keys, lt), t, 0.6, 3)
    valley(ctx, t, cam, P)
    def f():
        acacia(ctx, 760, 1480, 1.0, t)
        prophet(ctx, ix, 1550, 1.05, t, facing=-1, walk=1, phase=t * 5.2, **IB)
        hajar(ctx, 440, 1540, 1.0, t, facing=-1, tilt=-0.05)
        dust(ctx, t, 40, a=0.3)
    layer(ctx, cam, 1.0, f)

def sc_thirst(ctx, t):
    P = PAL['day']; lt = t - S[7]
    keys = [(0, Cam(520, 1380, 2.4, 0.03)), (S[8] - S[7], Cam(470, 1370, 2.6, -0.03)), (S[9] - S[7], Cam(500, 1300, 1.8, 0.0))]
    cam = drift(keycam(keys, lt), t, 0.8, 4)
    valley(ctx, t, cam, P, sun=(600, 300), heat=1.5)
    def f():
        acacia(ctx, 760, 1480, 1.0, t)
        hajar(ctx, 440, 1540, 1.0, t, hold=False, arms=(1.6 + 0.2 * math.sin(t * 9), 0.3), tilt=0.15)
        # empty water skin
        sk = math.sin(t * 9) * 0.15
        ctx.save(); ctx.translate(560, 1380); ctx.rotate(sk)
        ctx.set_source(lingrad(-30, 0, 30, 0, [(0, '#5a3a20'), (1, '#8a5a30')])); ellipse(ctx, 0, 0, 34, 20); ctx.fill(); ctx.restore()
        wig = math.sin(t * 14) * 0.08
        ctx.save(); ctx.translate(610, 1585); ctx.rotate(wig); baby(ctx, 0, 0, 0.6, t, prophet_=True); ctx.restore()
        dust(ctx, t, 40, a=0.3)
    layer(ctx, cam, 1.0, f)

SAFA_X, MARWA_X, VALLEY_Y = 140, 940, 1640
def hill_h(x):
    h = 0.0
    for cx in (SAFA_X, MARWA_X):
        d = abs(x - cx) / 330
        if d < 1: h = max(h, 330 * math.cos(d * PI / 2) ** 1.6)
    return h
def path_y(x): return VALLEY_Y - hill_h(x)

def hills(ctx, t):
    for cx, name, sd in ((SAFA_X, 'SAFA', 1), (MARWA_X, 'MARWA', 2)):
        ctx.move_to(cx - 420, VALLEY_Y + 10)
        for k in range(0, 85):
            x = cx - 420 + k * 10
            d = abs(x - cx) / 330
            hh = 330 * math.cos(min(d, 1) * PI / 2) ** 1.6 if d < 1 else 0
            ctx.line_to(x, VALLEY_Y - hh + math.sin(x * 0.09 + sd) * 4)
        ctx.line_to(cx + 420, VALLEY_Y + 10); ctx.close_path()
        ctx.set_source(lingrad(cx - 300, 0, cx + 300, 0, [(0, '#7a5a3e'), (0.5, '#a8845e'), (1, '#6a4a32')])); ctx.fill_preserve()
        ctx.save(); ctx.clip()
        r = rnd(70 + sd)
        for i in range(26):
            x = cx + r.uniform(-300, 300); y = path_y(x) + r.uniform(20, 240)
            src(ctx, r.choice(['#5e4430', '#8a6a4a', '#b8946a']), 0.8); ellipse(ctx, x, y, r.uniform(10, 30), r.uniform(6, 14)); ctx.fill()
        ctx.set_source(lingrad(0, VALLEY_Y - 330, 0, VALLEY_Y, [(0, (1, 0.95, 0.8, 0.18)), (1, (0, 0, 0, 0.15))]))
        ctx.rectangle(cx - 420, VALLEY_Y - 340, 840, 360); ctx.fill()
        ctx.restore()
        set_font(ctx, 46, 'Cinzel'); ww = text_w(ctx, name)
        lx = min(max(cx - ww / 2, 40), 1040 - ww)
        outlined(ctx, name, lx, VALLEY_Y - 40, sw=6)
    # valley floor
    ctx.set_source(lingrad(0, VALLEY_Y - 20, 0, VALLEY_Y + 300, [(0, '#c8a878'), (1, '#a8865a')]))
    ctx.rectangle(-400, VALLEY_Y - 4, 1900, 1400); ctx.fill()
    dune_lines(ctx, VALLEY_Y, t, '#8a6a46', seed=65, a=0.15)

def sc_run(ctx, t):
    P = PAL['day']; lt = t - S[9]
    T = S[11] - S[9] - 0.1
    trips = 7
    def where(tt):
        q = clamp(tt / T)
        pos = trips * q ** 1.55
        k = int(min(pos, trips - 0.001)); f = pos - k
        a_, b_ = (SAFA_X, MARWA_X) if k % 2 == 0 else (MARWA_X, SAFA_X)
        look = 0.22
        g = 0.0 if f < look else (f - look) / (1 - look)
        x = lerp(a_, b_, sm(g))
        return x, k, f < look, (1 if b_ > a_ else -1), pos
    hx, k, looking, facing, pos = where(lt)
    spd = (where(lt + 0.05)[0] - hx) / 0.05
    run = clamp(abs(spd) / 300)
    keys = [(0, Cam(540, 1400, 1.0, 0.0)), (T, Cam(540, 1390, 1.03, 0.0))]
    cam = drift(keycam(keys, lt), t, 0.5, 5)
    valley(ctx, t, cam, P, heat=0.8)
    def f_():
        hills(ctx, t)
        acacia(ctx, 560, 1700, 0.7, t)
        # ghosts when it gets fast (time passes)
        if pos > 2.5:
            for g in range(1, 4):
                gx = where(lt - g * 0.07)[0]
                woman(ctx, gx, path_y(gx), 0.95, t, facing=facing, walk=1, phase=(t - g * 0.07) * 10, arms=(0.6, 0.4), lean=0.12,
                      alpha_=0.22 / g, shadow_a=0, **HAJ)
        slope = (path_y(hx + facing * 8) - path_y(hx)) / 8
        if looking:
            lk = math.sin(lt * 3)
            woman(ctx, hx, path_y(hx), 0.95, t, facing=1 if lk > 0 else -1, arms=(2.55, 0.3), elbows=(1.55, 0.3), tilt=-0.05, **HAJ)
        else:
            woman(ctx, hx, path_y(hx), 0.95, t, facing=facing, walk=max(run, 0.6), phase=t * (7 + 5 * run), arms=(0.6, 0.4),
                  lean=0.06 + 0.06 * run + max(-0.06, min(0.06, -0.08 * slope * facing)), **HAJ)
        baby(ctx, 600, 1760, 0.55, t, prophet_=True)
        set_font(ctx, 70, 'Cinzel'); s_ = f'{max(1, k) if looking else min(k + 1, 7)}x'; ww = text_w(ctx, s_)
        outlined(ctx, s_, 540 - ww / 2, 1150, fill=C(GOLD), sw=8)
        dust(ctx, t, 40, a=0.3, speed=2)
    layer(ctx, cam, 1.0, f_)

def sc_zamzam(ctx, t):
    P = PAL['day']; lt = t - S[11]
    light = ramp(t, S[11] + 0.2, S[12])
    water = ramp(t, w(12, 'bis') - 0.2, E[12] + 0.5)
    keys = [(0, Cam(540, 1300, 1.3, 0.0)), (S[12] - S[11], Cam(540, 1420, 1.8, 0.0)), (S[13] - S[11], Cam(540, 1380, 2.1, 0.02)),
            (S[14] - S[11], Cam(540, 1380, 2.2, 0.03))]
    cam = drift(keycam(keys, lt), t, 0.6, 6)
    valley(ctx, t, cam, P)
    def f():
        acacia(ctx, 800, 1480, 1.0, t)
        glow(ctx, 540, 1560, 500 * (0.4 + light), '#fff2c8', 0.5 * light)
        if water > 0:
            ctx.set_source(radgrad(540, 1580, 10, 220 * water, [(0, '#9ad8f0'), (0.7, '#4a98c0'), (1, (0.3, 0.6, 0.8, 0))]))
            ellipse(ctx, 540, 1585, 220 * water, 40 * water); ctx.fill()
            r = rnd(3)
            for i in range(60):
                ph = (t * 1.3 + i * 0.07) % 1
                ang = r.uniform(-0.5, 0.5) - PI / 2; sp = r.uniform(200, 420) * water
                x = 540 + math.cos(ang) * sp * ph; y = 1575 + math.sin(ang) * sp * ph + 500 * ph * ph
                src(ctx, '#d8f2ff', 0.8 * (1 - ph)); circle(ctx, x, y, r.uniform(3, 7)); ctx.fill()
        hajar(ctx, 320, 1540, 1.0, t, facing=1, hold=False, arms=(lerp(0.3, 2.3, water), lerp(0.2, 2.2, water)), tilt=-0.1 * water)
        baby(ctx, 560, 1620, 0.6, t, prophet_=True)
        dust(ctx, t, 50, c=(0.85, 0.95, 1), a=0.3 + 0.3 * water)
    layer(ctx, cam, 1.0, f)

def sc_lesson(ctx, t):
    P = PAL['dawn']; lt = t - S[14]
    keys = [(0, Cam(540, 1250, 1.0, 0.0)), (17.0, Cam(560, 1230, 1.1, 0.0))]
    cam = drift(keycam(keys, lt), t, 0.4, 7)
    bg(ctx, t, cam, P, horizon=HZ, sun_pos=(820, 1000), sun_r=55, clouds_a=0.4, seed=64, ray_a=0.16)
    def f():
        ground(ctx, HZ + 40, '#e8dcc6', '#c8b898', '#9a8a6e')
        for k in range(-4, 10):
            cx = k * 180
            src(ctx, '#d8ccb0'); ctx.rectangle(cx - 20, 800, 40, 560); ctx.fill()
            src(ctx, '#c8bca0'); ctx.move_to(cx + 20, 900); ctx.curve_to(cx + 40, 800, cx + 140, 800, cx + 160, 900); ctx.line_to(cx + 160, 870); ctx.curve_to(cx + 140, 790, cx + 40, 790, cx + 20, 870); ctx.fill()
        src(ctx, '#c8bca0'); ctx.rectangle(-2000, 760, 5000, 50); ctx.fill()
        r = rnd(9)
        ppl = []
        for i in range(36):
            y = r.uniform(1380, 1820); x = (r.uniform(-200, 1300) + lt * (40 if i % 2 else -40) * (y / 1500)) % 1500 - 200
            ppl.append((y, x, i))
        ppl.sort()
        for y, x, i in ppl:
            sc_ = (y - 1100) / 560; fc = 1 if i % 2 else -1
            if i % 5 in (1, 3):
                woman(ctx, x, y, sc_, t, facing=fc, walk=1, phase=t * 6 + i, seed=5000 + i, shadow_a=0.15,
                      **[dict(cloth='#f2efe8', trim='#c8bfa8'), dict(cloth='#26262c', trim='#45454e'), dict(cloth='#2e3a52', trim='#4a5a78')][i % 3])
            else:
                person(ctx, x, y, sc_, t, facing=fc, robe='#f4f1ea', robe2='#e0dbd0', turban='#f4f1ea', head=None,
                       walk=1, phase=t * 6 + i, seed=5000 + i, shadow_a=0.15)
    layer(ctx, cam, 1.0, f)

SCENES = [(0.0, sc_hook), (S[3] - 0.25, sc_bring), (S[4] - 0.15, sc_leave), (S[7] - 0.15, sc_thirst), (S[9] - 0.15, sc_run),
          (S[11] - 0.15, sc_zamzam), (S[14] - 0.2, sc_lesson)]

def overlays(ctx, t):
    hook_text(ctx, t, 0.0, S[1] - 0.05, 'ALLEIN IN|DER WÜSTE')
    draw_chip(ctx, 'Kein Wasser', t, S[1] - 0.05, S[3] - 0.2, y=360)
    draw_chip(ctx, 'Kein Mensch', t, S[2] - 0.05, S[3] - 0.2, y=440)
    draw_kw(ctx, 'DAS TAL VON MEKKA', t, w(3, 'leeres') - 0.2, E[3] + 0.3)
    draw_speaker(ctx, 'HAJAR', t, w(4, 'Hat') - 0.1, E[4] + 0.2)
    draw_speaker(ctx, 'IBRAHIM', t, w(5, 'Ja') - 0.1, E[5] + 0.2)
    draw_quote(ctx, 'Dann wird Er uns nicht im Stich lassen.', 'Sahih al Bukhari 3364', t, w(6, 'Dann') - 0.2, E[6] + 0.4, y=480)
    draw_kw(ctx, 'DAS WASSER GING AUS', t, S[7], E[8] + 0.2)
    draw_kw(ctx, 'ZAMZAM', t, S[13] - 0.1, S[14] - 0.1, maxsize=110, col=(0.85, 0.95, 1, 1), glowc='#9ad8f0')
    draw_chip(ctx, 'Sahih al Bukhari 3364', t, S[12], S[14] - 0.1)
    lesson_card(ctx, t, S[14], E[16] + 0.3, 'Hajar vertraute auf Allah, und trotzdem rannte sie. Vertrauen heisst nicht sitzen und warten.', y=560)
    draw_kw(ctx, 'BIS HEUTE', t, S[17], E[17] + 0.3)
    draw_chip(ctx, 'Sure Al Baqara 2:158', t, S[17] + 0.2, E[17] + 0.3)
    cta(ctx, t, S[18] - 0.1, st.AUD + 0.3, 'SUBHANALLAH', 'Schreib es in die Kommentare')

def frame(ctx, t):
    standard_frame(ctx, t, st, lambda c, tt: run_scenes(c, tt, SCENES), overlays, 'Hajar und Zamzam',
                   ['Sahih al Bukhari 3364', 'Sure Al Baqara 2:158', 'Sure Ibrahim 14:37'])
