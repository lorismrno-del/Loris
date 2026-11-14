from kit import *
st = Story('talut'); S, E, w = st.S, st.E, st.w
DUR = st.DUR
HZ = 1150
RIVER_Y = 1520

def field(ctx, t, cam, P, sun=(820, 450), river=False, dusty=0.0):
    bg(ctx, t, cam, P, horizon=HZ, sun_pos=sun, sun_r=50, clouds_a=0.45, seed=70, far_amp=280, mid_amp=170, ray_a=0.1)
    def g():
        ground(ctx, HZ + 40, P['g1'], P['g2'])
        dune_lines(ctx, HZ + 40, t, shade(P['g2'], -0.3), seed=71, a=0.1)
        if river:
            ctx.move_to(-1500, RIVER_Y - 40)
            x = -1500
            while x <= 2600:
                ctx.line_to(x, RIVER_Y - 40 + math.sin(x * 0.004) * 20); x += 30
            x = 2600
            while x >= -1500:
                ctx.line_to(x, RIVER_Y + 60 + math.sin(x * 0.004 + 1) * 20); x -= 30
            ctx.close_path()
            ctx.set_source(lingrad(0, RIVER_Y - 50, 0, RIVER_Y + 70, [(0, '#6aa8c8'), (1, '#2a6a8a')])); ctx.fill()
            src(ctx, (1, 1, 1), 0.35); ctx.set_line_width(2.5)
            for k in range(14):
                xx = (k * 160 + t * 60) % 2200 - 400; yy = RIVER_Y + (k % 3) * 25 - 20
                ctx.move_to(xx, yy); ctx.line_to(xx + 60, yy + 2); ctx.stroke()
        rocks(ctx, HZ + 80, seed=72, n=8, c=shade(P['near'], 0.2))
    layer(ctx, cam, 1.0, g)
    if dusty: layer(ctx, cam, 1.0, lambda: dust(ctx, t, 60, a=0.35 * dusty, speed=2))

def jalut(ctx, x, y, s, t, fall=0.0, alpha_=1.0):
    ctx.save(); ctx.translate(x, y); ctx.rotate(fall * 1.45)
    soldier2(ctx, 0, 0, s, t, 99, facing=-1, giant=True, arms=(0.4, 0.5), alpha_=alpha_)
    ctx.restore()

def talut(ctx, x, y, s, t, **kw):
    d = dict(robe='#e8dcc0', robe2='#8a2a2a', turban='#f6f0e2', head='crown', cloak='#3a2a5a', beard='#2a1d14'); d.update(kw)
    person(ctx, x, y, s, t, **d)

def army_small(ctx, t, xs, y0, s, walk=0.0, drink=0.0, scared=0.0, pray=0.0, n=None, seed=0):
    for i, (x, dy) in enumerate(xs):
        d_ = drink if (i % 7) != 0 else 0.0
        if d_ > 0:
            ctx.save(); ctx.translate(x, y0 + dy)
            posed(ctx, 0, 0, d_ * 0.6, lambda: soldier2(ctx, 0, 0, s, t, i + seed, facing=1, arms=(1.8 * d_, 1.6 * d_), tilt=0.5 * d_))
            ctx.restore()
        else:
            up = pray if (i % 7) == 0 else pray * 0.6
            soldier2(ctx, x, y0 + dy, s, t, i + seed, facing=1, walk=walk, phase=t * 6 + i,
                     arms=(lerp(0.35, 2.5, up), lerp(0.5, 2.3, up)), tilt=0.25 * scared - 0.12 * up)

def sc_hook(ctx, t):
    P = PAL['storm']
    keys = [(0, Cam(620, 1000, 1.05, 0.0)), (S[2] - 0.2, Cam(600, 1050, 1.15, 0.0))]
    cam = drift(keycam(keys, t), t, 0.6, 1)
    field(ctx, t, cam, P, sun=(860, 700), dusty=1.0)
    def f():
        jalut(ctx, 820, 1520, 2.6, t)
        for i in range(5):
            soldier2(ctx, 150 + i * 70, 1560 + (i % 2) * 20, 0.75, t, i, facing=1, arms=(0.4, 0.5))
    layer(ctx, cam, 1.0, f)

def sc_king(ctx, t):
    P = PAL['day']; lt = t - S[2]
    keys = [(0, Cam(540, 1250, 1.15, 0.0)), (3.0, Cam(560, 1180, 1.8, 0.02)), (S[3] - S[2], Cam(560, 1200, 1.7, 0.02))]
    cam = drift(keycam(keys, lt), t, 0.6, 2)
    field(ctx, t, cam, P)
    def f():
        # Talut stands on a low rock, the people gather around him
        ctx.set_source(lingrad(0, 1440, 0, 1530, [(0, '#b89a74'), (1, '#7a6044')]))
        ctx.move_to(420, 1528); ctx.curve_to(450, 1470, 670, 1465, 700, 1528); ctx.close_path(); ctx.fill()
        spots = [(70, 1500), (190, 1480), (900, 1480), (1020, 1500), (300, 1500), (790, 1500),
                 (40, 1640), (190, 1620), (340, 1660), (760, 1660), (900, 1620), (1050, 1640)]
        items = [(y, 'f', x, i) for i, (x, y) in enumerate(spots)] + [(1500.5, 't', 560, 0)]
        for y, kind, x, i in sorted(items):
            if kind == 't':
                talut(ctx, 560, 1500, 0.95, t, facing=1, arms=(0.25 + 0.9 * ramp(lt, 3.2, 3.8), 0.2), elbows=(0.2, 0.3))
            else:
                folk(ctx, x, y, (y - 1000) / 600, t, i, facing=1 if x < 560 else -1,
                     arms=(0.3 + 0.8 * ramp(lt, 2.5, 3.0) * (i % 2), 0.2))
    layer(ctx, cam, 1.0, f)

def sc_river(ctx, t):
    P = PAL['day']; lt = t - S[3]
    stop = S[3] + 2.0
    go = clamp(lt / 2.0)
    xs = [(-900 + i * 85 + go * 300, (i % 3) * 18) for i in range(14)]
    keys = [(0, Cam(300, 1250, 1.1, 0.0)), (2.0, Cam(520, 1260, 1.15, 0.0)), (w(3, 'Allah') - S[3], Cam(700, 1240, 1.9, 0.02)),
            (S[5] - S[3], Cam(560, 1260, 1.3, 0.0))]
    cam = drift(keycam(keys, lt), t, 0.6, 3)
    field(ctx, t, cam, P, river=True)
    def f():
        army_small(ctx, t, xs, 1380, 0.63, walk=1 if t < stop else 0)
        tx = lerp(420, 720, go)
        turn = ramp(lt, 2.1, 2.4)
        talut(ctx, tx, 1440, 0.74, t, facing=1 if turn < 0.5 else -1, walk=1 if t < stop else 0, phase=t * 6,
              arms=(lerp(0.2, 1.5, ramp(t, w(3, 'Allah') - 0.3, w(3, 'Allah'))), 0.2), elbows=(0.0, 0.3))
    layer(ctx, cam, 1.0, f)

def sc_drink(ctx, t):
    P = PAL['day']; lt = t - S[5]
    xs = [(-200 + i * 85, (i % 3) * 18) for i in range(14)]
    keys = [(0, Cam(400, 1350, 1.35, 0.0)), (S[6] - S[5], Cam(150, 1300, 2.0, 0.02)), (S[7] - S[5], Cam(200, 1300, 1.8, 0.02))]
    cam = drift(keycam(keys, lt), t, 0.6, 4)
    field(ctx, t, cam, P, river=True)
    def f():
        army_small(ctx, t, xs, 1460, 0.6, drink=ramp(lt, 0.0, 0.6) * (0.85 + 0.15 * math.sin(t * 3)))
    layer(ctx, cam, 1.0, f)

def sc_fear(ctx, t):
    P = PAL['storm']; lt = t - S[7]
    keys = [(0, Cam(700, 1050, 1.0, 0.0)), (2.4, Cam(760, 1080, 1.15, 0.0)), (w(7, 'Heute') - S[7], Cam(260, 1310, 1.9, -0.02)),
            (S[8] - S[7], Cam(260, 1310, 2.0, -0.03))]
    cam = drift(keycam(keys, lt), t, 0.7, 5)
    field(ctx, t, cam, P, sun=(860, 700), dusty=1.0)
    def f():
        for i in range(40):
            soldier2(ctx, 500 + (i % 20) * 45, 1230 + (i // 20) * 30, 0.32, t, 100 + i, facing=-1)
        jalut(ctx, 900, 1380, 1.7, t)
        xs = [(60 + i * 70, (i % 3) * 18) for i in range(6)]
        army_small(ctx, t, xs, 1560, 0.9, scared=1.0, seed=50)
    layer(ctx, cam, 1.0, f)

def sc_faith(ctx, t):
    P = PAL['dusk']; lt = t - S[8]
    keys = [(0, Cam(300, 1300, 1.6, 0.0)), (S[9] - S[8], Cam(320, 1280, 1.4, 0.0)), (S[10] - S[8], Cam(420, 1250, 1.2, 0.0))]
    cam = drift(keycam(keys, lt), t, 0.6, 6)
    field(ctx, t, cam, P, sun=(780, 1000), dusty=0.6)
    def f():
        for i in range(40):
            soldier2(ctx, 520 + (i % 20) * 45, 1230 + (i // 20) * 30, 0.32, t, 100 + i, facing=-1)
        jalut(ctx, 920, 1380, 1.7, t)
        xs = [(60 + i * 70, (i % 3) * 18) for i in range(6)]
        army_small(ctx, t, xs, 1560, 0.9, pray=ramp(t, S[9], S[9] + 0.8), seed=50)
        glow(ctx, 260, 1200, 600, '#fff0c8', 0.25 * ramp(t, S[9], S[9] + 1))
    layer(ctx, cam, 1.0, f)
    layer(ctx, cam, 0.3, lambda: rays(ctx, 300, 200, t, '#fff4d0', 0.14 * ramp(t, S[9], S[9] + 1), n=10, length=2600, seed=3))

def sc_fight(ctx, t):
    P = PAL['dusk']; lt = t - S[10]
    fall = eo(ramp(t, w(10, 'tötete') + 0.1, w(10, 'tötete') + 1.2))
    keys = [(0, Cam(560, 1300, 1.4, 0.0)), (1.0, Cam(640, 1250, 1.2, 0.0)), (S[11] - S[10], Cam(640, 1300, 1.25, 0.0))]
    sk = ramp(t, w(10, 'tötete') + 1.0, w(10, 'tötete') + 1.1) * (1 - ramp(t, w(10, 'tötete') + 1.1, w(10, 'tötete') + 1.5))
    shake = (math.sin(t * 60) * 10 * sk, math.cos(t * 55) * 8 * sk)
    cam = drift(keycam(keys, lt), t, 0.6, 7)
    field(ctx, t, cam, P, sun=(780, 1000), dusty=1.0)
    def f():
        jalut(ctx, 820, 1560, 2.0, t, fall=fall)
        if fall > 0.95: dust_cloud(ctx, 1100, 1560, 1.5, t - w(10, 'tötete') - 1.1, '#b89a70', 0.6, n=10)
        prophet(ctx, 380, 1560, 0.8, t, facing=1, robe='#d8ccb0', robe2='#4f6e8a', arms=(lerp(1.2, 2.6, ramp(t, w(10, 'tötete') - 0.4, w(10, 'tötete'))), 0.3))
    layer(ctx, cam, 1.0, f, shake)

def sc_lesson(ctx, t):
    P = PAL['dawn']; lt = t - S[11]
    keys = [(0, Cam(540, 1250, 1.0, 0.0)), (14.0, Cam(540, 1220, 1.1, 0.0))]
    cam = drift(keycam(keys, lt), t, 0.4, 8)
    field(ctx, t, cam, P, sun=(780, 1080))
    def f():
        xs = [(250 + i * 90, (i % 3) * 18) for i in range(7)]
        army_small(ctx, t, xs, 1580, 0.95, seed=50)
        person(ctx, 900, 1600, 1.0, t, robe='#5a2a20', head='helmet', prop='banner', seed=33, arms=(0.4, 0.2))
    layer(ctx, cam, 1.0, f)

SCENES = [(0.0, sc_hook), (S[2] - 0.25, sc_king), (S[3] - 0.15, sc_river), (S[5] - 0.15, sc_drink), (S[7] - 0.15, sc_fear),
          (S[8] - 0.15, sc_faith), (S[10] - 0.15, sc_fight), (S[11] - 0.2, sc_lesson)]

def overlays(ctx, t):
    hook_text(ctx, t, 0.0, S[1] - 0.05, 'KLEIN GEGEN|RIESIG')
    draw_kw(ctx, 'NICHT DIE ZAHL ENTSCHIED', t, S[1], S[2] - 0.2)
    draw_kw(ctx, 'KÖNIG TALUT', t, w(2, 'Talut') - 0.3, E[2] + 0.3)
    draw_chip(ctx, 'Sure Al Baqara 2:247', t, w(2, 'Talut'), E[2] + 0.3)
    draw_speaker(ctx, 'TALUT', t, w(3, 'Allah') - 0.1, E[4] + 0.2)
    draw_kw(ctx, 'DIE PRÜFUNG AM FLUSS', t, w(4, 'Wer') - 0.1, E[4] + 0.3)
    draw_kw(ctx, 'FAST ALLE TRANKEN', t, S[5], S[6] - 0.05)
    draw_kw(ctx, 'NUR WENIGE BLIEBEN', t, S[6], E[6] + 0.3)
    draw_speaker(ctx, 'MANCHE', t, w(7, 'Heute') - 0.1, E[7] + 0.2)
    draw_quote(ctx, 'Wie oft hat eine kleine Schar mit Allahs Erlaubnis eine grosse besiegt.', 'Sure Al Baqara 2:249', t, w(8, 'Wie') - 0.2, E[8] + 0.3, y=480)
    draw_quote(ctx, 'Unser Herr, schenke uns Geduld und festige unsere Füsse.', 'Sure Al Baqara 2:250', t, w(9, 'Unser') - 0.2, E[9] + 0.3, y=480)
    draw_kw(ctx, 'DAWUD BESIEGTE JALUT', t, w(10, 'tötete'), E[10] + 0.4)
    draw_chip(ctx, 'Sure Al Baqara 2:251', t, w(10, 'tötete') + 0.2, E[10] + 0.4)
    lesson_card(ctx, t, S[11], E[13] + 0.3, 'Nicht die Masse entscheidet, sondern Geduld und Vertrauen auf Allah. Die kleine Prüfung zeigte, wer standhaft bleibt.', y=560)
    cta(ctx, t, S[14] - 0.1, st.AUD + 0.3, 'BIST DU EINER VON DEN WENIGEN?', 'Schreib es in die Kommentare')

def frame(ctx, t):
    standard_frame(ctx, t, st, lambda c, tt: run_scenes(c, tt, SCENES), overlays, 'Talut und Jalut', ['Sure Al Baqara 2:246 bis 251'])
