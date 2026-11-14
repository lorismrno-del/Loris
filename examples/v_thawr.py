from kit import *
st = Story('thawr'); S, E, w = st.S, st.E, st.w
DUR = st.DUR
AB = dict(robe='#cdbb98', robe2='#6a4a2a', turban='#efe6d2', beard='#e8e2d6')

def _opening_pts():
    r = rnd(91); pts = []
    cx, cy, rx, ry = 550, 960, 400, 470
    n = 34
    for k in range(n + 1):
        a = PI + PI * k / n
        j = r.uniform(-1, 1) * 22 if 0 < k < n else 0
        pts.append((cx + math.cos(a) * (rx + j), cy + math.sin(a) * (ry + j) * (0.92 if k % 3 else 1.0)))
    pts.append((cx + rx, 975)); pts.append((cx - rx, 975))
    return pts
OPEN_PTS = _opening_pts()

def opening_path(ctx):
    poly(ctx, OPEN_PTS)

def rock_mass(ctx, t, light):
    # rock wall with the opening cut out
    ctx.save()
    ctx.set_fill_rule(cairo.FILL_RULE_EVEN_ODD)
    ctx.rectangle(-2000, -2000, 5000, 6000); opening_path(ctx)
    ctx.set_source(radgrad(550, 760, 300, 1500, [(0, '#3e342b'), (0.3, '#262019'), (1, '#0a0806')])); ctx.fill_preserve()
    ctx.clip()
    r = rnd(92)
    # rock facets with lit top edges
    for k in range(70):
        x = r.uniform(-300, 1400); y = r.uniform(-300, 2100)
        w_ = r.uniform(80, 260); h_ = r.uniform(50, 160)
        pts = [(x - w_ / 2 + r.uniform(-20, 20), y + r.uniform(-10, 10)), (x - w_ * 0.2, y - h_ / 2 + r.uniform(-15, 15)),
               (x + w_ * 0.3, y - h_ / 2 + r.uniform(-15, 15)), (x + w_ / 2, y + r.uniform(-10, 10)),
               (x + w_ * 0.25, y + h_ / 2), (x - w_ * 0.3, y + h_ / 2)]
        d = math.hypot(x - 550, y - 760) / 900
        poly(ctx, pts); src(ctx, (0.03, 0.025, 0.02), 0.2); ctx.fill()
        ctx.move_to(*pts[0]); ctx.line_to(*pts[1]); ctx.line_to(*pts[2]); ctx.line_to(*pts[3])
        src(ctx, (0.62, 0.68, 0.85), max(0, 0.2 - 0.18 * d)); ctx.set_line_width(2.5); ctx.stroke()
    # strata
    src(ctx, (0, 0, 0), 0.22); ctx.set_line_width(5)
    for k in range(9):
        y0 = 150 + k * 210
        ctx.move_to(-300, y0)
        x = -300
        while x < 1400:
            x += 60; ctx.line_to(x, y0 + math.sin(x * 0.006 + k) * 40 + r.uniform(-6, 6))
        ctx.stroke()
    # moon rim light around the opening
    ctx.set_source(radgrad(550, 760, 380, 760, [(0, (0.5, 0.6, 0.9, 0.2)), (1, (0, 0, 0, 0))]))
    ctx.rectangle(-300, -300, 1700, 2400); ctx.fill()
    # stalactites at the top
    r2 = rnd(93)
    for k in range(14):
        x = -40 + k * 85 + r2.uniform(-20, 20); L = r2.uniform(60, 170)
        ctx.set_source(lingrad(x - 20, 0, x + 20, 0, [(0, '#1e1813'), (0.5, '#4a3e33'), (1, '#1a140f')]))
        poly(ctx, [(x - 26, 160), (x, 160 + L), (x + 26, 160)]); ctx.fill()
    ctx.restore()
    # jagged edge of the opening
    ctx.save(); opening_path(ctx); src(ctx, '#0e0b08'); ctx.set_line_width(26); ctx.set_line_join(cairo.LINE_JOIN_ROUND); ctx.stroke()
    opening_path(ctx); src(ctx, (0.6, 0.7, 0.95), 0.35); ctx.set_line_width(4); ctx.stroke(); ctx.restore()

def cave_floor(ctx, t, light):
    ctx.move_to(-400, 1520); ctx.curve_to(150, 1470, 500, 1500, 700, 1460); ctx.curve_to(900, 1430, 1100, 1480, 1500, 1460)
    ctx.line_to(1500, 2600); ctx.line_to(-400, 2600); ctx.close_path()
    ctx.set_source(lingrad(0, 1440, 0, 2300, [(0, '#3a3028'), (0.4, '#1e1913'), (1, '#0a0806')])); ctx.fill()
    # rocky lip under the opening
    r0 = rnd(96); pts = [(150, 975)]
    for k in range(1, 12):
        pts.append((150 + k * 72, 975 + r0.uniform(0, 30)))
    pts += [(950, 975), (1000, 1080), (760, 1150), (420, 1170), (120, 1090)]
    poly(ctx, pts); ctx.set_source(lingrad(0, 975, 0, 1170, [(0, '#2a231c'), (1, '#0e0b08')])); ctx.fill()
    # moonlight spilling on the floor
    ctx.set_source(radgrad(560, 1640, 20, 520, [(0, (0.6, 0.7, 0.95, 0.16)), (1, (0, 0, 0, 0))])); ellipse(ctx, 560, 1640, 560, 150); ctx.fill()
    r = rnd(94)
    for k in range(30):
        x = r.uniform(-200, 1300); y = r.uniform(1500, 2000)
        src(ctx, r.choice(['#1a140f', '#3a3028', '#5a4c3e']), 0.9); ellipse(ctx, x, y, r.uniform(8, 26), r.uniform(4, 10)); ctx.fill()
    glow(ctx, 450, 1500, 600, '#ffd9a0', 0.12 * light)

def cave(ctx, t, cam, enemies=0.0, leave=0.0, light=1.0, torch=1.0):
    def f():
        # outside: night valley seen through the opening
        ctx.save(); opening_path(ctx); ctx.clip()
        sky(ctx, '#03050f', '#0e1a36', '#2a3a5e', 400, 1000); stars(ctx, t, 1.0, n=120)
        glow(ctx, 760, 560, 160, '#dfe8ff', 0.5); src(ctx, '#f4f6ff'); circle(ctx, 760, 560, 34); ctx.fill()
        ridge(ctx, 900, 120, '#141a2c', seed=95, freq=0.006, x0=0, x1=1100)
        src(ctx, '#2a2a36'); ctx.rectangle(0, 930, 1100, 200); ctx.fill()
        if enemies > 0:
            for i, x0 in enumerate((290, 460, 640, 800)):
                x = x0 + leave * (900 + i * 80)
                if torch > 0 and i % 2 == 0:
                    glow(ctx, x + 30, 640, 280, '#ff9a3a', 0.45 * torch * (1 - leave))
                folk(ctx, x, 950, 1.35, t, 20 + i, facing=1 if i % 2 else -1, walk=leave if leave > 0 else 0, phase=t * 5 + i,
                     prop='torch' if i % 2 == 0 else None, shadow_a=0, alpha_=enemies)
            # they stand against the moonlight: darken into silhouettes
            src(ctx, (0.02, 0.03, 0.08), 0.45 * enemies); ctx.rectangle(0, 400, 1100, 600); ctx.fill()
        ctx.restore()
        rock_mass(ctx, t, light)
        cave_floor(ctx, t, light)
    layer(ctx, cam, 1.0, f)

def inside_people(ctx, t, whisper=0.0, calm=0.0):
    light_presence(ctx, 330, 1600, 1.0, t, a=0.9 + 0.3 * calm)
    person(ctx, 640, 1600, 1.0, t, facing=-1, arms=(lerp(0.3, 1.4, whisper), 0.2), elbows=(lerp(0.3, 1.6, whisper), 0.3),
           tilt=0.25 * whisper - 0.05 * calm, lean=0.05 * whisper, seed=8, **AB)

def sc_hook(ctx, t):
    keys = [(0, Cam(540, 1100, 1.25, 0.0)), (S[2] - 0.2, Cam(540, 1150, 1.1, 0.0))]
    cam = drift(keycam(keys, t), t, 0.6, 1)
    cave(ctx, t, cam, enemies=1.0)
    layer(ctx, cam, 1.0, lambda: inside_people(ctx, t, whisper=0.5))

def sc_journey(ctx, t):
    P = PAL['night']; lt = t - S[2]
    x = lerp(100, 520, clamp(lt / 8))
    keys = [(0, Cam(400, 1250, 1.2, 0.0)), (8.0, Cam(560, 1200, 1.3, 0.0))]
    cam = drift(keycam(keys, lt), t, 0.5, 2)
    bg(ctx, t, cam, P, horizon=1150, sun_pos=None, clouds_a=0.2, stars_a=1.0, moon_pos=(820, 400), seed=80, far_amp=420, mid_amp=260)
    def f():
        ground(ctx, 1200, '#3a3448', '#22202e')
        ctx.move_to(700, 1250); ctx.curve_to(800, 900, 1000, 700, 1300, 650); ctx.line_to(1600, 1250); ctx.close_path()
        src(ctx, '#2a2636'); ctx.fill()
        src(ctx, '#0c0a10'); ellipse(ctx, 1020, 860, 50, 30); ctx.fill()
        light_presence(ctx, x + 150, 1560, 0.9, t)
        person(ctx, x, 1560, 0.95, t, facing=1, walk=1, phase=t * 5.5, seed=8, **AB)
        dust(ctx, t, 30, c=(0.8, 0.85, 1), a=0.25)
    layer(ctx, cam, 1.0, f)

def sc_search(ctx, t):
    P = PAL['night']; lt = t - S[3]
    keys = [(0, Cam(540, 1250, 1.15, 0.0)), (3.0, Cam(600, 1230, 1.3, 0.0))]
    cam = drift(keycam(keys, lt), t, 0.7, 3)
    bg(ctx, t, cam, P, horizon=1150, sun_pos=None, clouds_a=0.2, stars_a=1.0, moon_pos=(820, 400), seed=80, far_amp=420, mid_amp=260)
    def f():
        ground(ctx, 1200, '#3a3448', '#22202e')
        rocks(ctx, 1260, seed=81, n=12, c='#4a4458')
        for i in range(6):
            x = -200 + i * 170 + lt * 90
            folk(ctx, x, 1520 + (i % 2) * 40, 0.9, t, 20 + i, facing=1, walk=1, phase=t * 6 + i, prop='torch' if i % 2 == 0 else None)
            if i % 2 == 0: glow(ctx, x + 10, 1300, 300, '#ff9a3a', 0.25)
    layer(ctx, cam, 1.0, f)

def sc_feet(ctx, t):
    lt = t - S[4]
    keys = [(0, Cam(540, 1100, 1.0, 0.0)), (2.5, Cam(540, 860, 1.5, 0.0)), (S[5] - S[4], Cam(540, 880, 1.45, 0.0)),
            (S[5] - S[4] + 0.6, Cam(600, 1300, 2.0, 0.02)), (S[6] - S[4], Cam(560, 1320, 1.9, 0.02))]
    cam = drift(keycam(keys, lt), t, 0.6, 4)
    cave(ctx, t, cam, enemies=ramp(lt, 0.0, 0.8))
    layer(ctx, cam, 1.0, lambda: inside_people(ctx, t, whisper=ramp(t, S[5] - 0.2, S[5] + 0.4)))

def sc_answer(ctx, t):
    lt = t - S[6]
    leave = ramp(t, S[8] + 0.2, E[8] + 0.2)
    keys = [(0, Cam(380, 1300, 2.0, -0.02)), (S[7] - S[6], Cam(500, 1250, 1.35, 0.0)), (S[8] - S[6], Cam(540, 950, 1.3, 0.0)),
            (S[9] - S[6], Cam(540, 1000, 1.2, 0.0))]
    cam = drift(keycam(keys, lt), t, 0.5, 5)
    cave(ctx, t, cam, enemies=1.0, leave=leave, torch=1 - leave, light=1 + ramp(lt, 0, 2))
    def f():
        glow(ctx, 330, 1400, 700 * ramp(lt, 0, 2), '#fff0c8', 0.3)
        inside_people(ctx, t, whisper=1 - ramp(lt, 0.3, 1.5), calm=ramp(lt, 0.3, 1.5))
    layer(ctx, cam, 1.0, f)

def sc_lesson(ctx, t):
    P = PAL['dawn']; lt = t - S[9]
    keys = [(0, Cam(540, 1200, 1.0, 0.0)), (13.0, Cam(560, 1170, 1.1, 0.0))]
    cam = drift(keycam(keys, lt), t, 0.4, 6)
    bg(ctx, t, cam, P, horizon=1150, sun_pos=(780, 1020), sun_r=55, clouds_a=0.45, seed=82, far_amp=380, mid_amp=240, ray_a=0.18)
    def f():
        ground(ctx, 1200, P['g1'], P['g2'])
        ctx.move_to(200, 1300); ctx.curve_to(350, 850, 600, 700, 900, 680); ctx.line_to(1400, 1300); ctx.close_path()
        ctx.set_source(lingrad(0, 680, 0, 1300, [(0, shade(P['mid_r'], 0.2)), (1, P['mid_r'])])); ctx.fill()
        src(ctx, '#1a120c'); ellipse(ctx, 640, 900, 46, 30); ctx.fill()
        glow(ctx, 640, 900, 160, '#ffe6a8', 0.4)
        dust(ctx, t, 40, a=0.3)
    layer(ctx, cam, 1.0, f)

SCENES = [(0.0, sc_hook), (S[2] - 0.25, sc_journey), (S[3] - 0.15, sc_search), (S[4] - 0.15, sc_feet), (S[6] - 0.15, sc_answer),
          (S[9] - 0.2, sc_lesson)]

def overlays(ctx, t):
    hook_text(ctx, t, 0.0, S[1] - 0.05, 'ZWEI MÄNNER|IN EINER HÖHLE', y=380)
    draw_kw(ctx, 'DIE FEINDE STEHEN DAVOR', t, S[1], S[2] - 0.2, y=300)
    draw_kw(ctx, 'DIE AUSWANDERUNG', t, S[2] + 0.4, E[2] + 0.3)
    draw_chip(ctx, 'Die Höhle Thawr', t, w(2, 'versteckte'), E[2] + 0.3)
    draw_kw(ctx, 'SIE SUCHTEN ÜBERALL', t, S[3], E[3] + 0.2)
    draw_speaker(ctx, 'ABU BAKR', t, w(5, 'O') - 0.1, E[5] + 0.2)
    draw_quote(ctx, 'Was denkst du von zwei, deren Dritter Allah ist?', 'Sahih al Bukhari 3653', t, w(6, 'Was') - 0.2, E[6] + 0.3, y=480)
    draw_quote(ctx, 'Sei nicht traurig, Allah ist mit uns.', 'Sure At Tawba 9:40', t, w(7, 'Sei') - 0.2, E[7] + 0.4, y=480)
    draw_kw(ctx, 'SIE ZOGEN WEITER', t, S[8], E[8] + 0.3)
    lesson_card(ctx, t, S[9], E[11] + 0.3, 'Tu alles, was du kannst, und überlass den Rest Allah. Mit Ihm bist du nie allein.', y=560)
    cta(ctx, t, S[12] - 0.1, st.AUD + 0.3, 'SEGENSWÜNSCHE AUF DEN PROPHETEN', 'Schreib sie in die Kommentare')

def frame(ctx, t):
    standard_frame(ctx, t, st, lambda c, tt: run_scenes(c, tt, SCENES), overlays, 'Die Höhle Thawr',
                   ['Sure At Tawba 9:40', 'Sahih al Bukhari 3653', 'Sahih Muslim 2381'])
