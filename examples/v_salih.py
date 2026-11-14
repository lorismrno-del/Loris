from kit import *
st = Story('salih'); S, E, w = st.S, st.E, st.w
DUR = st.DUR
SAL = dict(robe='#e8e0cc', robe2='#5f7f52')
HZ = 1150

def city(ctx, t, cam, P, lit=0.0, sun=(840, 440), stars_a=0.0, moon=None, red=0.0):
    bg(ctx, t, cam, P, horizon=HZ, sun_pos=sun, sun_r=50, clouds_a=0.45, seed=110, far_amp=260, mid_amp=160, stars_a=stars_a, moon_pos=moon, ray_a=0.1)
    layer(ctx, cam, 0.8, lambda: (rock_houses(ctx, 540, HZ + 120, 0.9, t, c='#b07a52' if red == 0 else mix('#b07a52', '#5a2a22', red), seed=3, n=5, lit=lit),
                                  haze(ctx, P['haze'], 0.08)))
    def g():
        ground(ctx, HZ + 160, P['g1'], P['g2'])
        rocks(ctx, HZ + 200, seed=111, n=8, c=shade(P['near'], 0.2))
    layer(ctx, cam, 1.0, g)

def crowd(ctx, t, n=7, x0=60, y0=1560, demand=0.0, awe=0.0, back=0.0, fac=1, alpha_=1.0):
    pts = sorted([(y0 + ((i * 2) % 3) * 35, i) for i in range(n)])
    for y, i in pts:
        x = x0 + i * 100 - fac * back * 50 + math.sin(t * 0.8 + i * 1.7) * 6
        d_ = demand * (i % 2) * (0.8 + 0.2 * math.sin(t * 4 + i))
        idle = 0.12 * math.sin(t * 1.3 + i * 2.1)
        folk(ctx, x, y, (y - 1000) / 560, t, 60 + i, facing=fac, arms=(lerp(0.3 + idle, 2.4, max(d_, awe)), lerp(0.2 - idle, 2.0, awe)),
             elbows=(0.2 + 0.2 * d_, 0.3), tilt=-0.1 * awe + 0.03 * math.sin(t * 0.9 + i), alpha_=alpha_)

def well(ctx, x, y, s):
    box(ctx, x - 90 * s, y, 180 * s, 70 * s, 40 * s, '#8a7058')
    ctx.set_source(radgrad(x + 10 * s, y - 75 * s, 2, 70 * s, [(0, '#1a3a4a'), (1, '#0a1a24')])); ellipse(ctx, x + 10 * s, y - 72 * s, 80 * s, 14 * s); ctx.fill()

def sc_hook(ctx, t):
    P = PAL['dusk']
    keys = [(0, Cam(560, 1250, 1.35, 0.0)), (S[3] - 0.2, Cam(560, 1200, 1.15, 0.0))]
    cam = drift(keycam(keys, t), t, 0.5, 1)
    city(ctx, t, cam, P, sun=(800, 1000), lit=0.5)
    spots = [(150, 1490), (300, 1465), (830, 1470), (975, 1500), (60, 1650), (250, 1700), (870, 1690), (1030, 1630)]
    def f():
        items = sorted([(y, i, x) for i, (x, y) in enumerate(spots)] + [(1560, -1, 560)])
        for y, i, x in items:
            if i < 0:
                camel(ctx, 560, 1560, 1.1, t, facing=1, glow_a=1.0, head_down=0.2 * math.sin(t)); continue
            fc = 1 if x < 560 else -1
            back = ramp(t, 0.3 + 0.25 * i, 1.6 + 0.25 * i)
            xx = x - fc * back * 40
            aw = (0.45 + 0.35 * math.sin(t * 1.6 + i * 1.3)) if i % 3 else 0.2
            pt = 1.0 if i % 3 == 0 else 0.0
            folk(ctx, xx, y, (y - 1000) / 560, t, 60 + i, facing=fc,
                 arms=(lerp(0.3, 1.6, pt) + lerp(0, 1.4, aw), 0.2 + 1.2 * aw), elbows=(lerp(0.2, -0.1, pt), 0.3),
                 tilt=-0.08 * aw - 0.05 * back, lean=-0.06 * back)
    layer(ctx, cam, 1.0, f)

def sc_city(ctx, t):
    P = PAL['day']; lt = t - S[3]
    keys = [(0, Cam(540, 1150, 1.0, 0.0)), (4.6, Cam(600, 1180, 1.12, 0.0))]
    cam = drift(keycam(keys, lt), t, 0.5, 2)
    city(ctx, t, cam, P)
    def f():
        for i in range(8):
            x = (i * 160 + lt * 40 * (1 if i % 2 else -1)) % 1300 - 100
            folk(ctx, x, 1500 + (i % 3) * 40, 0.7, t, 70 + i, facing=1 if i % 2 else -1, walk=1, phase=t * 6 + i)
    layer(ctx, cam, 1.0, f)

def sc_preach(ctx, t):
    P = PAL['day']; lt = t - S[4]
    keys = [(0, Cam(820, 1250, 2.0, 0.02)), (S[5] - S[4], Cam(560, 1280, 1.3, 0.0)), (S[6] - S[4], Cam(560, 1280, 1.25, 0.0))]
    cam = drift(keycam(keys, lt), t, 0.6, 3)
    city(ctx, t, cam, P)
    def f():
        crowd(ctx, t, demand=ramp(t, S[5], S[5] + 0.5))
        prophet(ctx, 840, 1560, 1.05, t, facing=-1, arms=(1.4 + 0.1 * math.sin(t * 2), 0.2), elbows=(0.1, 0.3), **SAL)
    layer(ctx, cam, 1.0, f)

def sc_camel(ctx, t):
    P = PAL['day']; lt = t - S[6]
    app = ramp(t, S[6] + 0.3, S[6] + 1.6)
    keys = [(0, Cam(540, 1200, 1.1, 0.0)), (2.0, Cam(560, 1250, 1.3, 0.0)), (S[7] - S[6], Cam(700, 1250, 1.5, 0.0)),
            (S[8] - S[6], Cam(520, 1280, 1.25, 0.0)), (S[9] - S[6], Cam(520, 1280, 1.2, 0.0))]
    cam = drift(keycam(keys, lt), t, 0.6, 4)
    city(ctx, t, cam, P)
    def f():
        drink = t > S[8] - 0.2
        if drink: well(ctx, 380, 1520, 1.0)
        glow(ctx, 560, 1300, 600 * app, '#fff0c8', 0.4 * app * (1 - 0.6 * ramp(t, S[7], S[7] + 1)))
        camel(ctx, 470 if drink else 560, 1560, 1.0, t, facing=-1 if drink else 1, alpha_=app, glow_a=1 - ramp(t, S[7], S[7] + 1),
              head_down=0.85 if drink else 0.5 * ramp(t, S[7], S[7] + 1))
        crowd(ctx, t, n=4, x0=-40, y0=1620, awe=app * (1 - ramp(t, S[7], S[7] + 1)), back=app)
        prophet(ctx, 900, 1580, 1.05, t, facing=-1, arms=(lerp(0.3, 1.4, ramp(t, S[7], S[7] + 0.4)), 0.2), elbows=(0.1, 0.3), **SAL)
    layer(ctx, cam, 1.0, f)

def sc_kill(ctx, t):
    P = PAL['dusk']; lt = t - S[9]
    tk = w(9, 'tötete')
    fall = eo(ramp(t, tk + 0.1, tk + 1.0))
    keys = [(0, Cam(540, 1250, 1.2, 0.0)), (tk - S[9], Cam(560, 1350, 1.7, 0.02)), (S[10] - S[9], Cam(560, 1330, 1.5, 0.0))]
    cam = drift(keycam(keys, lt), t, 0.7, 5)
    city(ctx, t, cam, dict(P, top='#1a0a10', mid='#6a1a1a', bot='#b84a2a'), sun=(780, 1040), red=0.6)
    def f():
        camel(ctx, 640, 1560, 1.0, t, facing=-1, fallen=fall, head_down=0.3 + 0.5 * fall)
        x = lerp(120, 400, clamp(lt / (tk - S[9] + 0.01)))
        person(ctx, x, 1580, 1.05, t, facing=1, robe='#1a0e0a', robe2='#1a0e0a', turban='#1a0e0a', beard='#100806', skin='#1c120c',
               walk=1 if t < tk else 0, phase=t * 6, prop='spear', arms=(lerp(0.4, 2.8, ramp(t, tk - 0.5, tk)) if t < tk + 0.2 else 1.2, 0.3), shadow_a=0)
        src(ctx, (0.3, 0, 0), 0.25 * ramp(t, tk, tk + 0.2) * (1 - ramp(t, tk + 0.2, tk + 0.8))); ctx.rectangle(-2000, -2000, 5000, 6000); ctx.fill()
    layer(ctx, cam, 1.0, f)

def sc_warn(ctx, t):
    P = PAL['dusk']; lt = t - S[10]
    keys = [(0, Cam(560, 1250, 2.0, 0.02)), (S[11] - S[10], Cam(560, 1280, 1.6, 0.0))]
    cam = drift(keycam(keys, lt), t, 0.6, 6)
    city(ctx, t, cam, dict(P, top='#1a0a10', mid='#6a1a1a', bot='#b84a2a'), sun=(780, 1080), red=0.6)
    layer(ctx, cam, 1.0, lambda: prophet(ctx, 560, 1560, 1.05, t, facing=-1, arms=(1.4, 0.2), elbows=(0.1, 0.3), tilt=0.06, **SAL))

def sc_cry(ctx, t):
    lt = t - S[11]
    tm = w(11, 'Morgen')
    morning = ramp(t, tm - 0.3, tm + 0.3)
    k = ramp(t, S[11], S[11] + 0.4) * (1 - morning)
    shake = (math.sin(t * 50) * 12 * k, math.cos(t * 47) * 10 * k)
    P = PAL['storm'] if morning < 0.5 else PAL['dawn']
    keys = [(0, Cam(540, 1200, 1.1, 0.0)), (tm - S[11], Cam(540, 1180, 1.05, 0.0)), (S[12] - S[11], Cam(560, 1200, 1.12, 0.0))]
    cam = drift(keycam(keys, lt), t, 0.5, 7)
    city(ctx, t, cam, P, sun=(820, 900) if morning > 0.5 else None)
    def f():
        if morning < 0.5:
            for r_ in range(5):
                rr = ((t - S[11]) * 900 + r_ * 300) % 1500
                ctx.save(); src(ctx, (1, 0.9, 0.8), 0.25 * (1 - rr / 1500)); ctx.set_line_width(16); circle(ctx, 540, 900, rr); ctx.stroke(); ctx.restore()
        else:
            dust(ctx, t, 40, a=0.3)
    layer(ctx, cam, 1.0, f, shake)

def sc_lesson(ctx, t):
    P = PAL['dawn']; lt = t - S[12]
    keys = [(0, Cam(540, 1200, 1.0, 0.0)), (12.0, Cam(560, 1180, 1.1, 0.0))]
    cam = drift(keycam(keys, lt), t, 0.4, 8)
    city(ctx, t, cam, P, sun=(820, 900))
    layer(ctx, cam, 1.0, lambda: dust(ctx, t, 40, a=0.3))

SCENES = [(0.0, sc_hook), (S[3] - 0.25, sc_city), (S[4] - 0.15, sc_preach), (S[6] - 0.15, sc_camel), (S[9] - 0.15, sc_kill),
          (S[10] - 0.15, sc_warn), (S[11] - 0.15, sc_cry), (S[12] - 0.2, sc_lesson)]

def overlays(ctx, t):
    hook_text(ctx, t, 0.0, S[1] - 0.05, 'SIE VERLANGTEN|EIN WUNDER', y=380)
    draw_kw(ctx, 'ALLAH GAB ES IHNEN', t, S[1], S[2] - 0.05)
    draw_kw(ctx, 'UND SIE TÖTETEN ES', t, S[2], S[3] - 0.2, col=(1, 0.6, 0.5, 1), glowc='#ff6a3a')
    draw_kw(ctx, 'DAS VOLK THAMUD', t, S[3] + 0.2, E[3] + 0.3)
    draw_chip(ctx, 'Sure Al Araf 7:74', t, S[3] + 0.5, E[3] + 0.3)
    draw_kw(ctx, 'PROPHET SALIH', t, S[4], E[4] + 0.1)
    draw_kw(ctx, 'SIE WOLLTEN EIN ZEICHEN', t, S[5], E[5] + 0.3)
    draw_kw(ctx, 'DIE KAMELSTUTE', t, S[6] + 0.3, E[6] + 0.3)
    draw_quote(ctx, 'Lasst sie auf Allahs Erde weiden und tut ihr nichts Böses an.', 'Sure Al Araf 7:73', t, w(7, 'Lasst') - 0.2, E[7] + 0.3, y=480)
    draw_chip(ctx, 'Sure Asch Schuara 26:155', t, S[8], E[8] + 0.3)
    draw_kw(ctx, 'DER ELENDSTE VON IHNEN', t, S[9], E[9] + 0.3, col=(1, 0.6, 0.5, 1), glowc='#ff6a3a')
    draw_chip(ctx, 'Sure Asch Schams 91:12', t, S[9] + 0.3, E[9] + 0.3)
    draw_quote(ctx, 'Geniesst euer Leben noch drei Tage.', 'Sure Hud 11:65', t, w(10, 'Geniesst') - 0.2, E[10] + 0.3, y=480)
    draw_kw(ctx, 'DER SCHREI', t, w(11, 'Schrei') - 0.2, w(11, 'Morgen') + 0.2, maxsize=100)
    draw_chip(ctx, 'Sure Hud 11:67', t, w(11, 'Schrei'), E[11] + 0.3)
    lesson_card(ctx, t, S[12], E[14] + 0.3, 'Ein Zeichen von Allah zu sehen reicht nicht. Entscheidend ist, was du damit machst.', y=560)
    cta(ctx, t, S[15] - 0.1, st.AUD + 0.3, 'WELCHES ZEICHEN HAT ALLAH DIR GEZEIGT?', 'Schreib es in die Kommentare')

def frame(ctx, t):
    standard_frame(ctx, t, st, lambda c, tt: run_scenes(c, tt, SCENES), overlays, 'Salih und die Kamelstute',
                   ['Sure Al Araf 7:73 bis 79', 'Sure Hud 11:61 bis 68', 'Sure Asch Schuara 26:141 bis 158', 'Sure Asch Schams 91:11 bis 15'])
