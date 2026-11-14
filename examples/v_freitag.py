from kit import *
st = Story('freitag'); S, E, w = st.S, st.E, st.w
DUR = st.DUR
HZ = 1250

def town_mosque(ctx, t, cam, P, sun=(540, 1000), lit=0.0, ray_a=0.2):
    bg(ctx, t, cam, P, horizon=HZ, sun_pos=sun, sun_r=60, clouds_a=0.45, seed=130, far_amp=220, mid_amp=120, ray_a=ray_a)
    def f():
        ground(ctx, HZ + 40, P['g1'], P['g2'])
        town(ctx, t, 540, HZ + 120, 0.7, seed=131, n=14, c='#b8906a', lit=lit, gap=330)
        mosque(ctx, 540, HZ + 200, 1.0, c='#e8dcc4', lit=lit)
        palm(ctx, 110, HZ + 240, 360, t, seed=3); palm(ctx, 990, HZ + 250, 380, t, seed=6)
    layer(ctx, cam, 0.9, f)

def sc_hook(ctx, t):
    P = PAL['dawn']
    keys = [(0, Cam(540, 1250, 1.2, 0.0)), (S[2] - 0.2, Cam(540, 1180, 1.05, 0.0))]
    cam = drift(keycam(keys, t), t, 0.4, 1)
    town_mosque(ctx, t, cam, P, sun=(540, 1180 - t * 30), lit=0.6)

def sc_sun(ctx, t):
    P = PAL['dawn']; lt = t - S[2]
    keys = [(0, Cam(540, 1150, 1.0, 0.0)), (7.0, Cam(540, 1100, 1.12, 0.0))]
    cam = drift(keycam(keys, lt), t, 0.4, 2)
    town_mosque(ctx, t, cam, P, sun=(540, 1050 - lt * 25), lit=0.3, ray_a=0.26)
    layer(ctx, cam, 1.0, lambda: dust(ctx, t, 40, a=0.3))

def sc_garden(ctx, t):
    lt = t - S[3]
    keys = [(0, Cam(540, 1150, 1.05, 0.0)), (6.5, Cam(560, 1100, 1.2, 0.0))]
    cam = drift(keycam(keys, lt), t, 0.4, 3)
    def f():
        sky(ctx, '#7ab8e8', '#e8f4ff', '#fff8e8', -400, 1300)
        glow(ctx, 540, 500, 1200, '#fff8e0', 0.3)
        rays(ctx, 540, 200, t, '#fffbe8', 0.2, n=14, length=2600, seed=4)
        ridge(ctx, 1150, 200, '#7ab06a', seed=5, freq=0.003, color2='#a8d88a')
        ground(ctx, 1200, '#6aa84a', '#3a7a2a')
        ctx.move_to(-1500, 1500); ctx.curve_to(200, 1420, 800, 1480, 2600, 1440); ctx.line_to(2600, 1560); ctx.curve_to(800, 1600, 200, 1540, -1500, 1620); ctx.close_path()
        ctx.set_source(lingrad(0, 1430, 0, 1600, [(0, '#bfe8ff'), (1, '#5aa8d8')])); ctx.fill()
        r = rnd(6)
        for k in range(10):
            x = r.uniform(-200, 1300); y = r.uniform(1250, 1900); s_ = (y - 1000) / 400
            src(ctx, '#5a3a20'); ctx.set_line_width(14 * s_); ctx.move_to(x, y); ctx.line_to(x, y - 160 * s_); ctx.stroke()
            ctx.set_source(radgrad(x, y - 220 * s_, 10, 110 * s_, [(0, '#8ad86a'), (1, '#3a8a2a')])); circle(ctx, x, y - 220 * s_, 100 * s_); ctx.fill()
            for j in range(4):
                fx = x + r.uniform(-60, 60) * s_; fy = y - 220 * s_ + r.uniform(-60, 60) * s_
                src(ctx, r.choice(['#ffd86a', '#ff8a8a', '#ffffff'])); circle(ctx, fx, fy, 8 * s_); ctx.fill()
        dust(ctx, t, 50, c=(1, 1, 0.9), a=0.4)
    layer(ctx, cam, 1.0, f)

def sc_hour(ctx, t):
    lt = t - S[4]
    keys = [(0, Cam(540, 1100, 1.0, 0.0)), (3.0, Cam(540, 1050, 1.15, 0.01))]
    cam = drift(keycam(keys, lt), t, 0.8, 4)
    P = PAL['storm']
    bg(ctx, t, cam, dict(P, top='#0e0e18', mid='#3a2a3a'), horizon=HZ, sun_pos=(540, 700), sun_r=40, clouds_a=0.9, seed=132, sun_a=0.5, ray_a=0.05)
    floor(ctx, t, cam, P, HZ, rocks_n=0)

def sc_dua(ctx, t):
    P = PAL['dusk']; lt = t - S[5]
    keys = [(0, Cam(540, 1300, 1.6, 0.0)), (7.0, Cam(540, 1280, 1.35, 0.0))]
    cam = drift(keycam(keys, lt), t, 0.4, 5)
    desert_world(ctx, t, cam, P, hz=HZ, seed=133, sun_pos=(780, 1150), ray_a=0.22, rocks_n=4)
    layer(ctx, cam, 1.0, lambda: (folk(ctx, 520, 1580, 1.05, t, 1, facing=1, arms=(2.4, 2.3), elbows=(-0.3, -0.3), tilt=-0.1, sun_dir=-1),
                                   dust(ctx, t, 40, a=0.3)))

def sc_list(ctx, t):
    lt = t - S[6]
    if t < S[9] - 0.1:
        P = PAL['night']
        keys = [(0, Cam(540, 1000, 1.0, 0.0)), (8.0, Cam(540, 980, 1.1, 0.0))]
        cam = drift(keycam(keys, lt), t, 0.4, 6)
        bg(ctx, t, cam, P, horizon=1500, sun_pos=None, clouds_a=0.1, stars_a=1.0, moon_pos=(820, 520), seed=134, far=False, mid=False)
        def f():
            src(ctx, '#3a2414'); ctx.rectangle(-2000, 1500, 5000, 1500); ctx.fill()
            book(ctx, 540, 1480, 2.0, t, glow_a=0.55)
            oil_lamp(ctx, 880, 1480, 1.2, t)
        layer(ctx, cam, 1.0, f)
    elif t < S[10] - 0.1:
        P = PAL['day']; lt2 = t - S[9]
        keys = [(0, Cam(540, 1200, 1.0, 0.0)), (2.0, Cam(540, 1180, 1.08, 0.0))]
        cam = drift(keycam(keys, lt2), t, 0.4, 7)
        town_mosque(ctx, t, cam, P, sun=(860, 420), ray_a=0.1)
        def f():
            for i in range(9):
                x = -200 + i * 110 + lt2 * 80; y = 1560 + (i % 3) * 40
                folk(ctx, x, y, (y - 1100) / 480, t, 120 + i, facing=1, walk=1, phase=t * 6 + i)
        layer(ctx, cam, 1.0, f)
    else:
        P = PAL['dusk']; lt2 = t - S[10]
        keys = [(0, Cam(540, 1300, 1.3, 0.0)), (4.0, Cam(540, 1280, 1.2, 0.0))]
        cam = drift(keycam(keys, lt2), t, 0.4, 8)
        desert_world(ctx, t, cam, P, hz=HZ, seed=133, sun_pos=(540, 1180 + lt2 * 10), ray_a=0.24, rocks_n=4)
        layer(ctx, cam, 1.0, lambda: folk(ctx, 540, 1600, 1.0, t, 1, facing=1, arms=(2.4, 2.3), elbows=(-0.3, -0.3), tilt=-0.1, sun_dir=-1))

def sc_end(ctx, t):
    P = PAL['dawn']; lt = t - S[11]
    keys = [(0, Cam(540, 1200, 1.0, 0.0)), (8.0, Cam(540, 1180, 1.08, 0.0))]
    cam = drift(keycam(keys, lt), t, 0.4, 9)
    town_mosque(ctx, t, cam, P, sun=(540, 1050), lit=0.4, ray_a=0.24)

def checklist(ctx, t, t0, t1, items, y=560):
    if not (t0 <= t <= t1): return
    a = eo((t - t0) / 0.4) * clamp((t1 - t) / 0.4)
    hgt = 140 + len(items) * 84
    ctx.save()
    rrect(ctx, 70, y - hgt / 2, 940, hgt, 30); src(ctx, (0.04, 0.03, 0.02), 0.66 * a); ctx.fill_preserve()
    src(ctx, GOLD, 0.85 * a); ctx.set_line_width(2.5); ctx.stroke()
    set_font(ctx, 36); s = 'DEIN FREITAG'; ww = text_w(ctx, s); ctx.move_to(540 - ww / 2, y - hgt / 2 + 66); src(ctx, GOLD, a); ctx.show_text(s)
    yy = y - hgt / 2 + 140
    for k, (txt, tk) in enumerate(items):
        ia = a * eo((t - tk) / 0.35) if t >= tk else a * 0.25
        done = t >= tk
        rrect(ctx, 120, yy - 36, 46, 46, 10); src(ctx, GOLD if done else (1, 1, 1), ia if done else 0.3 * a); ctx.set_line_width(3); ctx.stroke()
        if done:
            src(ctx, GOLD, ia); ctx.set_line_width(6); ctx.move_to(130, yy - 14); ctx.line_to(142, yy - 2); ctx.line_to(160, yy - 30); ctx.stroke()
        set_font(ctx, 38, 'Lora'); ctx.move_to(190, yy); src(ctx, (1, 0.97, 0.9), max(ia, 0.3 * a)); ctx.show_text(txt)
        yy += 84
    ctx.restore()

SCENES = [(0.0, sc_hook), (S[2] - 0.2, sc_sun), (S[3] - 0.15, sc_garden), (S[4] - 0.15, sc_hour), (S[5] - 0.15, sc_dua),
          (S[6] - 0.2, sc_list), (S[11] - 0.2, sc_end)]

def overlays(ctx, t):
    hook_text(ctx, t, 0.0, S[1] - 0.05, 'DER BESTE TAG|DER WOCHE', y=380)
    draw_kw(ctx, 'DIE MEISTEN VERPASSEN IHN', t, S[1], S[2] - 0.2)
    draw_quote(ctx, 'Der beste Tag, an dem die Sonne aufgeht, ist der Freitag.', 'Sahih Muslim 854', t, w(2, 'Der', 1) - 0.2, E[2] + 0.3, y=480)
    for k, (lab, word) in enumerate((('Adam wurde erschaffen', 'erschaffen'), ('Er kam ins Paradies', 'kam'), ('Er musste es verlassen', 'musste'))):
        draw_chip(ctx, lab, t, w(3, word) - 0.4, E[3] + 0.3, y=360 + k * 80)
    draw_chip(ctx, 'Sahih Muslim 854', t, S[3] + 0.2, E[3] + 0.3, y=640)
    draw_kw(ctx, 'DIE STUNDE', t, S[4], E[4] + 0.3, maxsize=100)
    draw_quote(ctx, 'Am Freitag gibt es eine Stunde, in der Allah jedem Muslim gibt, worum er Ihn bittet.', 'Sahih al Bukhari 935', t, w(5, 'Am') - 0.2, E[5] + 0.4, y=480)
    draw_kw(ctx, 'WAS KANNST DU MORGEN TUN?', t, S[6], S[7] - 0.1)
    checklist(ctx, t, S[7] - 0.2, E[10] + 0.4, [('Sure Al Kahf lesen', S[7]), ('Viele Segenswünsche', S[8]), ('Früh zum Freitagsgebet', S[9]),
                                                ('Dua vor Sonnenuntergang', S[10])], y=560)
    cta(ctx, t, S[11] - 0.1, st.AUD + 0.3, 'SCHICK ES WEITER', 'An jemanden, der den Freitag nicht verpassen soll')

def frame(ctx, t):
    standard_frame(ctx, t, st, lambda c, tt: run_scenes(c, tt, SCENES), overlays, 'Der beste Tag der Woche',
                   ['Sahih Muslim 854', 'Sahih al Bukhari 935', 'Abu Dawud 1047 und 1048', 'Sure Al Kahf am Freitag: Al Hakim, Al Bayhaqi (sahih nach Al Albani)'])
