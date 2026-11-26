import json, math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *

W, H = 1920, 1080
HERE = os.path.dirname(os.path.abspath(__file__))
AL = json.load(open(os.path.join(HERE, 'al_yunus.json')))
SEN = AL['sentences']
S = [s['start'] for s in SEN]
E = [s['end'] for s in SEN]
AUD = AL['duration']
DUR = AUD + 2.4

# sieben Beats, bei allen Stilen gleich
BEATS = [0.0, 5.05, 8.30, 13.60, 18.20, 25.85, 34.60, DUR]
NB = len(BEATS) - 1

def beat_at(t):
    for i in range(NB):
        if BEATS[i] <= t < BEATS[i + 1]:
            return i, (t - BEATS[i]), (BEATS[i + 1] - BEATS[i])
    return NB - 1, t - BEATS[NB - 1], BEATS[NB] - BEATS[NB - 1]

def xf(t, i):
    """0..1 Einblendung am Beatanfang"""
    return clamp((t - BEATS[i]) / 0.45)

# ---------------- Untertitel ----------------
def _chunks():
    out = []
    for s in SEN:
        ws = s['words']
        i = 0
        while i < len(ws):
            grp = ws[i:i + 5]
            txt = ' '.join(x[2] for x in grp)
            out.append((grp[0][0], grp[-1][1] + 0.12, txt))
            i += 5
    return out

SUBS = _chunks()

def draw_subs(ctx, t, size=46, face='Montserrat', col=(1, 1, 1), y=980, box=False, gold_key=False):
    for t0, t1, txt in SUBS:
        if t0 - 0.05 <= t <= t1:
            a = clamp((t - t0 + 0.05) / 0.12) * clamp((t1 - t) / 0.12)
            set_font(ctx, size, face)
            ww = text_w(ctx, txt)
            if box:
                rrect(ctx, W / 2 - ww / 2 - 26, y - size - 12, ww + 52, size + 34, 12)
                src(ctx, (0, 0, 0), 0.55 * a); ctx.fill()
            if gold_key:
                words = txt.split()
                total = text_w(ctx, txt)
                x = W / 2 - total / 2
                for k, wd in enumerate(words):
                    cw = text_w(ctx, wd + ' ')
                    c = C(GOLD, a) if len(wd) > 6 else (col[0], col[1], col[2], a)
                    outlined(ctx, wd, x, y, fill=c, sw=7)
                    x += cw
            else:
                outlined(ctx, txt, W / 2 - ww / 2, y, fill=(col[0], col[1], col[2], a), sw=7)
            return

def title(ctx, t, t0, t1, txt, sub=None, face='Cinzel', size=96, y=420, col=(1, 0.97, 0.9)):
    if not (t0 <= t <= t1): return
    a = eo((t - t0) / 0.5) * clamp((t1 - t) / 0.4)
    set_font(ctx, size, face)
    ww = text_w(ctx, txt)
    outlined(ctx, txt, W / 2 - ww / 2, y, fill=(col[0], col[1], col[2], a), sw=12)
    if sub:
        set_font(ctx, 38, 'Montserrat')
        w2 = text_w(ctx, sub)
        outlined(ctx, sub, W / 2 - w2 / 2, y + 62, fill=C(GOLD, a), sw=7)

def label(ctx, t, t0, t1, txt, x=None, y=150, size=44, face='Cinzel', col=None):
    if not (t0 <= t <= t1): return
    a = eo((t - t0) / 0.35) * clamp((t1 - t) / 0.3)
    set_font(ctx, size, face)
    ww = text_w(ctx, txt)
    xx = (W / 2 - ww / 2) if x is None else x
    outlined(ctx, txt, xx, y, fill=col or C(GOLD, a), sw=8)

def letterbox(ctx, h=96, a=1.0):
    src(ctx, (0, 0, 0), a)
    ctx.rectangle(0, 0, W, h); ctx.fill()
    ctx.rectangle(0, H - h, W, h); ctx.fill()

def grain(ctx, t, a=0.05, n=1400, seed=4):
    r = rnd(seed + int(t * 24))
    for i in range(n):
        src(ctx, (1, 1, 1), a * r.uniform(0.2, 1))
        ctx.rectangle(r.uniform(0, W), r.uniform(0, H), 2, 2); ctx.fill()

def vign(ctx, a=0.5):
    g = cairo.RadialGradient(W / 2, H / 2, H * 0.35, W / 2, H / 2, H * 1.02)
    g.add_color_stop_rgba(0, 0, 0, 0, 0); g.add_color_stop_rgba(1, 0, 0, 0, a)
    ctx.set_source(g); ctx.rectangle(0, 0, W, H); ctx.fill()

def endcard(ctx, t, t0, name):
    if t < t0: return
    a = clamp((t - t0) / 0.6)
    src(ctx, (0, 0, 0), 0.78 * a); ctx.rectangle(0, 0, W, H); ctx.fill()
    set_font(ctx, 78, 'Cinzel'); ww = text_w(ctx, name)
    outlined(ctx, name, W / 2 - ww / 2, H / 2 - 20, fill=(1, 0.97, 0.9, a), sw=10)
    set_font(ctx, 34, 'Montserrat')
    s2 = 'Stilmuster  ·  Sure Al Anbiya 21:87 bis 88'
    w2 = text_w(ctx, s2)
    outlined(ctx, s2, W / 2 - w2 / 2, H / 2 + 46, fill=C(GOLD, a), sw=6)
