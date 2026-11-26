"""Stil 2 braun, islamische Ornamentik, Stimmung pro Prophet."""
import os
from base import *
import s2b

# ---------- Themen pro Prophet ----------
THEMES = {
 'yunus':   dict(name='Yunus', acc='#2f7d74', acc2='#b8862a', sea='#2f6b78', leaf='#5f7a3a',
                 motif='wave', part='bubbles', sub='Chronik einer Rettung'),
 'musa':    dict(name='Musa', acc='#a8651e', acc2='#c89a3a', sea='#5a7a8a', leaf='#6a7a3a',
                 motif='ray', part='sand', sub='Der Stab und das Meer'),
 'nuh':     dict(name='Nuh', acc='#3a6a8a', acc2='#a8862a', sea='#3f6f88', leaf='#5a7a4a',
                 motif='drop', part='rain', sub='Neunhundertfünfzig Jahre'),
 'ibrahim': dict(name='Ibrahim', acc='#a8441e', acc2='#d8a23a', sea='#8a5a3a', leaf='#6a7a3a',
                 motif='flame', part='ember', sub='Das Feuer wurde kühl'),
}
T = THEMES[os.environ.get('THEME', 'yunus')]
P = dict(s2b.PALS['sepia'])
P.update(acc=T['acc2'], acc2=T['acc'], sea=T['sea'], leaf=T['leaf'])
s2b.P = P
s2b.STYLE_NAME = T['name']

# ---------- islamische Ornamentik ----------
def star8(ctx, x, y, r, c, a=1.0, rot=0.0, lw=0, fill=True):
    pts = []
    for k in range(16):
        ang = rot + k * PI / 8
        rr = r if k % 2 == 0 else r * 0.46
        pts.append((x + math.cos(ang) * rr, y + math.sin(ang) * rr))
    ctx.move_to(*pts[0])
    for p in pts[1:]: ctx.line_to(*p)
    ctx.close_path()
    src(ctx, c, a)
    if fill: ctx.fill()
    else: ctx.set_line_width(lw or 3); ctx.stroke()

def rosette(ctx, x, y, r, t, c=None, a=0.9):
    c = c or P['acc']
    star8(ctx, x, y, r, c, a * 0.9, rot=t * 0.12)
    star8(ctx, x, y, r * 0.62, P['p1'], a, rot=-t * 0.12)
    star8(ctx, x, y, r * 0.30, P['acc2'], a * 0.8, rot=t * 0.2)
    src(ctx, c, a); ctx.set_line_width(2.4); circle(ctx, x, y, r * 0.3); ctx.stroke()

def girih(ctx, x0, x1, y, step, t, c=None, a=0.4, s=1.0):
    """durchlaufendes Flechtband"""
    c = c or P['ink']
    src(ctx, c, a); ctx.set_line_width(2.6 * s)
    x = x0
    k = 0
    while x < x1:
        ctx.move_to(x, y)
        ctx.line_to(x + step / 2, y - step * 0.42 * s)
        ctx.line_to(x + step, y)
        ctx.line_to(x + step / 2, y + step * 0.42 * s)
        ctx.close_path(); ctx.stroke()
        if k % 2 == 0:
            star8(ctx, x + step / 2, y, step * 0.17 * s, P['acc'], a * 0.9, rot=t * 0.1)
        x += step; k += 1

def arabesque(ctx, x, y, s, t, flip=1, c=None, a=0.55):
    c = c or P['ink']
    ctx.save(); ctx.translate(x, y); ctx.scale(flip * s, s)
    src(ctx, c, a); ctx.set_line_width(3.4)
    sw = math.sin(t * 0.7) * 3
    ctx.move_to(0, 0)
    ctx.curve_to(40, -26 + sw, 86, -18, 104, 10)
    ctx.curve_to(80, 30, 44, 24, 26, 2); ctx.stroke()
    ctx.move_to(14, 2); ctx.curve_to(34, -34, 70, -50 + sw, 96, -40)
    ctx.curve_to(82, -14, 48, -4, 22, -6); ctx.stroke()
    src(ctx, P['acc'], a * 1.2); circle(ctx, 104, 10, 5); ctx.fill()
    circle(ctx, 96, -40, 4.5); ctx.fill()
    ctx.restore()

def ornate_border(ctx, t):
    src(ctx, P['ink'], 0.5); ctx.set_line_width(5)
    ctx.rectangle(56, 56, W - 112, H - 112); ctx.stroke()
    src(ctx, P['acc'], 0.5); ctx.set_line_width(2)
    ctx.rectangle(74, 74, W - 148, H - 148); ctx.stroke()
    girih(ctx, 150, W - 150, 62, 58, t, a=0.22)
    girih(ctx, 150, W - 150, H - 62, 58, t, a=0.22)
    for (cx, cy, fx, fy) in ((112, 112, 1, 1), (W - 112, 112, -1, 1),
                             (112, H - 112, 1, -1), (W - 112, H - 112, -1, -1)):
        rosette(ctx, cx, cy, 34, t, a=0.85)
        ctx.save(); ctx.translate(cx, cy); ctx.scale(1, fy); ctx.translate(-cx, -cy)
        arabesque(ctx, cx + fx * 48, cy + 6, 0.8, t, flip=fx, a=0.4); ctx.restore()

def medallion(ctx, t, a=0.07):
    """grosses Sternmuster als Wasserzeichen"""
    cx, cy = W / 2, H / 2 - 30
    for ring, rr in enumerate((430, 300, 180)):
        n = 12 - ring * 2
        for k in range(n):
            ang = k * 2 * PI / n + t * (0.02 + ring * 0.01)
            star8(ctx, cx + math.cos(ang) * rr, cy + math.sin(ang) * rr, 34 - ring * 6,
                  P['ink'], a, rot=ang)
        src(ctx, P['ink'], a * 0.8); ctx.set_line_width(2)
        circle(ctx, cx, cy, rr); ctx.stroke()
    star8(ctx, cx, cy, 86, P['acc'], a * 1.6, rot=t * 0.05)

def cartouche(ctx, x, y, w_, h_, t, a=0.9):
    src(ctx, P['p1'], 0.85 * a)
    ctx.move_to(x - w_ / 2, y)
    ctx.curve_to(x - w_ / 2, y - h_, x + w_ / 2, y - h_, x + w_ / 2, y)
    ctx.curve_to(x + w_ / 2, y + h_, x - w_ / 2, y + h_, x - w_ / 2, y)
    ctx.close_path(); ctx.fill_preserve()
    src(ctx, P['acc'], 0.8 * a); ctx.set_line_width(3); ctx.stroke()
    star8(ctx, x - w_ / 2 - 20, y, 14, P['acc'], 0.8 * a, rot=t * 0.2)
    star8(ctx, x + w_ / 2 + 20, y, 14, P['acc'], 0.8 * a, rot=-t * 0.2)

def arch(ctx, x, y, w_, h_, t, a=0.5):
    """Mihrab Bogen"""
    src(ctx, P['ink'], a); ctx.set_line_width(4)
    ctx.move_to(x - w_ / 2, y)
    ctx.line_to(x - w_ / 2, y - h_ * 0.52)
    ctx.curve_to(x - w_ / 2, y - h_ * 0.9, x - w_ * 0.12, y - h_, x, y - h_ * 1.06)
    ctx.curve_to(x + w_ * 0.12, y - h_, x + w_ / 2, y - h_ * 0.9, x + w_ / 2, y - h_ * 0.52)
    ctx.line_to(x + w_ / 2, y); ctx.stroke()
    src(ctx, P['acc'], a * 0.7); ctx.set_line_width(2)
    ctx.move_to(x - w_ / 2 + 14, y)
    ctx.line_to(x - w_ / 2 + 14, y - h_ * 0.5)
    ctx.curve_to(x - w_ / 2 + 14, y - h_ * 0.86, x - w_ * 0.11, y - h_ * 0.96, x, y - h_ * 1.0)
    ctx.curve_to(x + w_ * 0.11, y - h_ * 0.96, x + w_ / 2 - 14, y - h_ * 0.86, x + w_ / 2 - 14, y - h_ * 0.5)
    ctx.line_to(x + w_ / 2 - 14, y); ctx.stroke()

# ---------- Stimmung pro Prophet ----------
def motif_band(ctx, t, y, a=0.3):
    m = T['motif']
    src(ctx, P['acc2'], a); ctx.set_line_width(3)
    x = 150
    while x < W - 150:
        if m == 'wave':
            ctx.move_to(x, y); ctx.curve_to(x + 18, y - 14, x + 38, y - 14, x + 56, y)
            ctx.curve_to(x + 74, y + 14, x + 94, y + 14, x + 112, y)
        elif m == 'drop':
            ctx.move_to(x + 56, y - 16); ctx.curve_to(x + 76, y + 4, x + 70, y + 20, x + 56, y + 20)
            ctx.curve_to(x + 42, y + 20, x + 36, y + 4, x + 56, y - 16)
        elif m == 'ray':
            ctx.move_to(x + 20, y + 14); ctx.line_to(x + 56, y - 16); ctx.line_to(x + 92, y + 14)
        else:
            ctx.move_to(x + 56, y + 16); ctx.curve_to(x + 30, y - 8, x + 68, y - 10, x + 56, y - 26)
            ctx.curve_to(x + 84, y - 8, x + 76, y + 8, x + 56, y + 16)
        ctx.stroke(); x += 112

def ambience(ctx, t, i):
    """Partikel passend zum Propheten"""
    kind = T['part']
    r = rnd(55)
    n = 26 if i not in (6, 7, 8) else 18
    for k in range(n):
        if kind == 'bubbles':
            x = r.uniform(140, W - 140) + math.sin(t * 0.8 + k) * 22
            y = (r.uniform(0, 900) - t * r.uniform(40, 95)) % 900 + 140
            rr = r.uniform(3, 9)
            src(ctx, P['sea'], 0.26); circle(ctx, x, y, rr); ctx.fill()
            src(ctx, P['p1'], 0.4); circle(ctx, x - rr * 0.3, y - rr * 0.3, rr * 0.35); ctx.fill()
        elif kind == 'rain':
            x = (r.uniform(120, W) + t * 220) % (W - 200) + 120
            y = (r.uniform(120, 900) + t * 760) % 800 + 130
            src(ctx, P['sea'], 0.3); ctx.set_line_width(2)
            ctx.move_to(x, y); ctx.line_to(x - 12, y + 34); ctx.stroke()
        elif kind == 'sand':
            x = (r.uniform(120, W) + t * 70) % (W - 200) + 120
            y = r.uniform(150, H - 170) + math.sin(t * 1.1 + k) * 18
            src(ctx, P['acc2'], 0.3); circle(ctx, x, y, r.uniform(1.5, 3.4)); ctx.fill()
        else:
            x = r.uniform(140, W - 140) + math.sin(t * 1.4 + k) * 26
            y = (r.uniform(0, 900) - t * r.uniform(50, 120)) % 900 + 140
            src(ctx, '#e8963a', 0.3 * (0.4 + 0.6 * abs(math.sin(t * 3 + k))))
            circle(ctx, x, y, r.uniform(2, 4.5)); ctx.fill()

def frame(ctx, t):
    s2b.TNOW[0] = t
    i, lt, dl = s2b.scene_at(t)
    dark = 6 <= i <= 8
    s2b.paper(ctx, t)
    if not dark:
        medallion(ctx, t, 0.095)
    ctx.save()
    s2b.SCENES[i](ctx, t, lt, dl)
    ctx.restore()
    if dark:
        medallion(ctx, t, 0.07)
    ambience(ctx, t, i)
    if not dark:
        motif_band(ctx, t, 128, 0.26)
        motif_band(ctx, t, H - 128, 0.26)
    ornate_border(ctx, t)
    # Titel im Bogen
    if 0.3 <= t <= 4.6:
        a = eo((t - 0.3) / 0.5) * clamp((4.6 - t) / 0.4)
        arch(ctx, W / 2, 470, 760, 300, t, 0.5 * a)
        cartouche(ctx, W / 2, 398, 520, 62, t, a)
        set_font(ctx, 96, 'Cinzel')
        ww = text_w(ctx, T['name'].upper())
        outlined(ctx, T['name'].upper(), W / 2 - ww / 2, 418, fill=C(P['ink'], a), sw=10)
        set_font(ctx, 34, 'Lora')
        w2 = text_w(ctx, T['sub'])
        outlined(ctx, T['sub'], W / 2 - w2 / 2, 486, fill=C(P['acc'], a), sw=6)
        rosette(ctx, W / 2, 548, 22, t, a=0.8 * a)
    draw_subs(ctx, t, size=44, face='Lora',
              col=(1, 0.99, 0.95) if dark else C(P['ink'])[:3], y=990)
    endcard(ctx, t, AUD + 0.5, 'Stil 2 braun  ·  ' + T['name'])
