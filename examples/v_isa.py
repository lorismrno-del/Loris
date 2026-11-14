from kit import *
st = Story('isa'); S, E, w = st.S, st.E, st.w
DUR = st.DUR
MARYAM = dict(cloth='#22304a', trim='#4a5a7a')
CRX, CRY = 560, 1460

def village(ctx, t, cam, P, lit=0.4):
    bg(ctx, t, cam, P, horizon=1150, sun_pos=(840, 980), sun_r=50, clouds_a=0.4, seed=7, far_amp=260, mid_amp=150, ray_a=0.12,
       stars_a=0.4 if P is PAL['night'] else 0)
    def f():
        ground(ctx, 1210, P['g1'], P['g2'])
        town(ctx, t, 540, 1260, 0.75, seed=12, n=18, c='#a8805e', lit=lit, gap=260)
        palm(ctx, 120, 1280, 380, t, seed=2); palm(ctx, 980, 1290, 420, t, seed=5)
    layer(ctx, cam, 0.85, f)

CROWD = [(-80, 1500), (40, 1540), (170, 1490), (840, 1500), (960, 1540), (1080, 1490), (250, 1560), (780, 1560)]
def crowd(ctx, t, point=0.0, back=0.0, awe=0.0):
    pts = sorted(CROWD, key=lambda p: p[1])
    for i, (x, y) in enumerate(pts):
        f = 1 if x < CRX else -1
        x2 = x - f * back * 60
        folk(ctx, x2, y, (y - 1000) / 560, t, i, facing=f, sun_dir=1,
             arms=(lerp(0.3, 1.6, point * (i % 2)) + lerp(0, 2.2, awe), 0.3 + 1.6 * awe), elbows=(lerp(0.4, -0.2, point * (i % 2)), 0.3),
             tilt=-0.1 * awe + 0.05 * math.sin(t + i), lean=-0.05 * back)

def sc_hook(ctx, t):
    P = PAL['night']
    keys = [(0, Cam(CRX + 30, CRY - 60, 2.4, 0.03)), (S[2] - 0.2, Cam(CRX, CRY - 120, 1.6, 0.0))]
    cam = drift(keycam(keys, t), t, 0.5, 1)
    village(ctx, t, cam, P, lit=0.8)
    def f():
        glow(ctx, CRX + 30, CRY - 40, 500, '#ffe6a8', 0.25 + 0.2 * math.sin(t * 2))
        cradle(ctx, CRX, CRY, 1.2, t, rock=1)
        baby(ctx, CRX - 10, CRY - 60, 1.2, t, prophet_=True)
        dust(ctx, t, 40, c=(1, 0.9, 0.6), a=0.35)
    layer(ctx, cam, 1.0, f)

def sc_arrive(ctx, t):
    P = PAL['dusk']; lt = t - S[2]
    mx = lerp(-120, 360, clamp(lt / 3.6))
    keys = [(0, Cam(300, 1250, 1.2, 0.0)), (3.6, Cam(420, 1240, 1.3, 0.0))]
    cam = drift(keycam(keys, lt), t, 0.6, 2)
    village(ctx, t, cam, P)
    def f():
        for i, (x, y) in enumerate(sorted(CROWD, key=lambda p: p[1])[:5]):
            folk(ctx, x + 520, y - 40, (y - 1040) / 560, t, i, facing=-1, sun_dir=1)
        woman(ctx, mx, 1560, 1.05, t, facing=1, walk=1 if lt < 3.6 else 0, phase=t * 5.5, **CARRY, **MARYAM)
        dust(ctx, t, 30, a=0.25)
    layer(ctx, cam, 1.0, f)

def scene_court(ctx, t, lt, keys, point=0.0, mary_point=0.0, light=0.0, back=0.0, awe=0.0, P=None):
    P = P or PAL['dusk']
    cam = drift(keycam(keys, lt), t, 0.6, 3)
    village(ctx, t, cam, P)
    def f():
        if light > 0:
            glow(ctx, CRX, CRY - 80, 900 * light, '#ffe6a8', 0.45 * light)
            rays(ctx, CRX, CRY - 80, t, '#fff0c8', 0.18 * light, n=14, length=1600, seed=4)
        crowd(ctx, t, point=point, back=back, awe=awe)
        cradle(ctx, CRX, CRY, 1.0, t, rock=0.3)
        baby(ctx, CRX - 8, CRY - 50, 1.0, t, prophet_=True)
        woman(ctx, CRX - 200, 1560, 1.05, t, facing=1, arms=(lerp(0.2, 1.5, mary_point), 0.2), elbows=(lerp(0.3, -0.1, mary_point), 0.3),
              tilt=0.08, **MARYAM)
        dust(ctx, t, 40, c=(1, 0.9, 0.7), a=0.25 + 0.3 * light)
    layer(ctx, cam, 1.0, f)

def sc_accuse(ctx, t):
    lt = t - S[3]
    keys = [(0, Cam(960, 1220, 2.1, 0.02)), (2.2, Cam(860, 1260, 1.4, 0.0)), (4.6, Cam(600, 1260, 1.1, 0.0))]
    scene_court(ctx, t, lt, keys, point=ramp(lt, 0.3, 0.9))

def sc_point(ctx, t):
    lt = t - S[4]
    keys = [(0, Cam(CRX - 160, 1220, 2.0, -0.02)), (2.0, Cam(CRX - 60, 1300, 1.6, 0.0)), (S[6] - S[4], Cam(600, 1260, 1.2, 0.0))]
    scene_court(ctx, t, lt, keys, point=1 - ramp(lt, 2.0, 3.0), mary_point=ramp(lt, 0.2, 0.8) * (1 - ramp(lt, 2.0, 2.6)))

def sc_speak(ctx, t):
    lt = t - S[6]
    keys = [(0, Cam(CRX, CRY - 80, 2.6, 0.03)), (2.0, Cam(CRX, CRY - 140, 1.8, 0.01)), (5.0, Cam(560, 1280, 1.15, 0.0)),
            (9.0, Cam(820, 1250, 1.8, -0.02)), (S[9] - S[6], Cam(560, 1260, 1.1, 0.0))]
    scene_court(ctx, t, lt, keys, light=ramp(lt, 0.0, 1.5), back=ramp(lt, 0.3, 1.5), awe=ramp(lt, 0.4, 1.2))

def sc_isa(ctx, t):
    lt = t - S[9]
    keys = [(0, Cam(560, 1200, 1.0, 0.0)), (4.0, Cam(560, 1240, 1.1, 0.0))]
    scene_court(ctx, t, lt, keys, light=1.0, back=1.0, awe=0.7 - 0.4 * ramp(lt, 0, 3))

def sc_lesson(ctx, t):
    lt = t - S[10]
    keys = [(0, Cam(540, 1050, 1.0, 0.0)), (16.0, Cam(540, 980, 1.12, 0.0))]
    cam = drift(keycam(keys, lt), t, 0.4, 5)
    P = PAL['night']
    bg(ctx, t, cam, P, horizon=1250, sun_pos=None, clouds_a=0.15, stars_a=1.0, moon_pos=(820, 1000), seed=30, far_amp=220, mid_amp=120)
    floor(ctx, t, cam, dict(P, g1='#2a2a44', g2='#1a1a30'), 1250, rocks_n=0)
    def f():
        glow(ctx, 540, 1400, 420, '#ffe6a8', 0.35)
        cradle(ctx, 540, 1460, 0.8, t, rock=1)
        baby(ctx, 532, 1420, 0.8, t, prophet_=True)
        dust(ctx, t, 50, c=(1, 0.9, 0.7), a=0.3)
    layer(ctx, cam, 1.0, f)

SCENES = [(0.0, sc_hook), (S[2] - 0.25, sc_arrive), (S[3] - 0.15, sc_accuse), (S[4] - 0.1, sc_point), (S[6] - 0.15, sc_speak),
          (S[9] - 0.15, sc_isa), (S[10] - 0.2, sc_lesson)]

def overlays(ctx, t):
    hook_text(ctx, t, 0.0, S[1] - 0.1, 'EIN BABY|SPRICHT')
    draw_kw(ctx, 'SEINE ERSTEN WORTE', t, S[1], S[2] - 0.2)
    draw_kw(ctx, 'MARYAM', t, S[2] + 0.3, E[2] + 0.2)
    draw_speaker(ctx, 'IHR VOLK', t, w(3, 'O') - 0.1, E[3] + 0.2)
    draw_speaker(ctx, 'IHR VOLK', t, w(5, 'Wie') - 0.1, E[5] + 0.2)
    draw_quote(ctx, 'Ich bin der Diener Allahs. Er hat mir die Schrift gegeben und mich zu einem Propheten gemacht. Er hat mir das Gebet und die Almosen anbefohlen, solange ich lebe.',
               'Sure Maryam 19:30 bis 31', t, w(6, 'Ich') - 0.2, E[8] + 0.4, y=560, size=44)
    draw_kw(ctx, 'ISA, DER SOHN DER MARYAM', t, S[9], E[9] + 0.4)
    lesson_card(ctx, t, S[10], E[13] + 0.3, 'Wir lieben Isa als einen der grössten Propheten. Er selbst sagte: Allah ist mein Herr und euer Herr. So dient Ihm.', y=620)
    draw_chip(ctx, 'Sure Maryam 19:36', t, S[12], E[13] + 0.3, y=330)
    cta(ctx, t, S[14] - 0.1, st.AUD + 0.3, 'WER WAR ISA FÜR DICH?', 'Schreib es in die Kommentare')

def frame(ctx, t):
    standard_frame(ctx, t, st, lambda c, tt: run_scenes(c, tt, SCENES), overlays, 'Isa in der Wiege',
                   ['Sure Maryam 19:16 bis 36', 'Sure Al Imran 3:46'])
