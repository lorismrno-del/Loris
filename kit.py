import json, os
WORK = os.environ.get('DAWAH_WORK', os.getcwd())
from lib import *
from scenes_common import *

# ---------------- timing ----------------
class Story:
    def __init__(self, name, pad=4.4):
        self.al = json.load(open(os.path.join(WORK, f'al_{name}.json')))
        self.SEN = self.al['sentences']
        self.S = [s['start'] for s in self.SEN]; self.E = [s['end'] for s in self.SEN]
        self.AUD = self.al['duration']; self.DUR = self.AUD + pad
        self.SUBS = build_subs(self.al)
    def w(self, si, word, nth=0):
        k = 0
        for x in self.SEN[si]['words']:
            if x[2].lower().strip('.,:;!?').startswith(word.lower()):
                if k == nth: return x[0]
                k += 1
        return self.S[si]
    def sent_of(self, text):
        for i, s in enumerate(self.SEN):
            if s['text'].startswith(text): return i
        raise KeyError(text)

def run_scenes(ctx, t, SCENES, XF=0.3):
    idx = 0
    for i, (st, fn) in enumerate(SCENES):
        if t >= st: idx = i
    st, fn = SCENES[idx]
    if idx > 0 and t < st + XF:
        ctx.push_group(); SCENES[idx - 1][1](ctx, t); ctx.pop_group_to_source(); ctx.paint()
        ctx.push_group(); fn(ctx, t); ctx.pop_group_to_source(); ctx.paint_with_alpha(sm((t - st) / XF))
    else:
        fn(ctx, t)

def lesson_card(ctx, t, t0, t1, text, y=600):
    if not (t0 <= t <= t1): return
    a = eo((t - t0) / 0.5) * clamp((t1 - t) / 0.4)
    set_font(ctx, 46, 'Lora')
    lines = wrap(ctx, text, 840)
    lh = 60
    hgt = 130 + len(lines) * lh
    ctx.save(); ctx.translate(0, (1 - eo((t - t0) / 0.6)) * 40)
    rrect(ctx, 70, y - hgt / 2, 940, hgt, 30); src(ctx, (0.04, 0.03, 0.02), 0.66 * a); ctx.fill_preserve()
    src(ctx, GOLD, 0.85 * a); ctx.set_line_width(2.5); ctx.stroke()
    set_font(ctx, 34); s = 'WAS LERNEN WIR DARAUS?'; w = text_w(ctx, s)
    ctx.move_to(540 - w / 2, y - hgt / 2 + 62); src(ctx, GOLD, a); ctx.show_text(s)
    set_font(ctx, 46, 'Lora')
    yy = y - hgt / 2 + 62 + 70
    for k, ln in enumerate(lines):
        la = a * eo((t - t0 - 0.3 - k * 0.35) / 0.5)
        w = text_w(ctx, ln); ctx.move_to(540 - w / 2, yy); src(ctx, (1, 0.97, 0.9), la); ctx.show_text(ln); yy += lh
    ctx.restore()

def cta(ctx, t, t0, t1, big, small):
    draw_kw(ctx, big, t, t0, t1, maxsize=80, col=C(GOLD))
    if small: draw_chip(ctx, small, t, t0 + 0.2, t1, y=470)

def standard_frame(ctx, t, st, world_fn, overlays, end_title, sources, grade_c='#ffb070', grade_a=0.07):
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    world_fn(ctx, t)
    grade(ctx, grade_c, grade_a)
    vignette(ctx, 0.5)
    overlays(ctx, t)
    if t < st.AUD + 0.3:
        draw_subs(ctx, st.SUBS, t)
    end_card(ctx, t, st.AUD + 0.2, end_title, sources)

def hook_text(ctx, t, t0, t1, text, y=600, size=92):
    """big centered hook for the first seconds (thumbnail friendly)"""
    if not (t0 <= t <= t1): return
    a = eo((t - t0) / 0.25) * clamp((t1 - t) / 0.3)
    set_font(ctx, 100, 'Cinzel')
    lines = text.split('|')
    sizes = [min(size, 100 * 940 / text_w(ctx, ln)) for ln in lines]
    yy = y - sum(sizes) * 0.55
    for ln, sz in zip(lines, sizes):
        set_font(ctx, sz, 'Cinzel'); w = text_w(ctx, ln)
        pop = 1 + 0.06 * (1 - eo((t - t0) / 0.4))
        ctx.save(); ctx.translate(540, yy + sz); ctx.scale(pop, pop)
        for gg in range(3):
            ctx.move_to(-w / 2, 0); ctx.text_path(ln); src(ctx, (0, 0, 0), 0.35 * a / (gg + 1)); ctx.set_line_width(14 + gg * 14); ctx.stroke()
        ctx.move_to(-w / 2, 0); ctx.text_path(ln)
        ctx.set_source(lingrad(0, -sz, 0, 0, [(0, (1, 0.97, 0.88, a)), (1, alpha(GOLD, a))])); ctx.fill()
        ctx.restore()
        yy += sz * 1.12

# ---------------- helpers ----------------
def posed(ctx, x, y, ang, fn):
    ctx.save(); ctx.translate(x, y); ctx.rotate(ang); fn(); ctx.restore()

def woman(ctx, x, y, s, t, cloth='#1e2433', trim='#3a4560', crown=False, **kw):
    d = dict(robe=cloth, robe2=trim, turban=cloth, beard=None, skin=shade(cloth, 0.05), head='hood', scale_x=0.82,
             cloak=shade(cloth, -0.1))
    d.update(kw)
    person(ctx, x, y, s * 0.92, t, **d)
    if crown:
        hx = x + d.get('facing', 1) * 4 * s; hy = y - 292 * s * 0.92
        ctx.set_source(lingrad(hx - 26 * s, 0, hx + 26 * s, 0, [(0, '#9c7426'), (0.5, '#f7dc8a'), (1, '#9c7426')]))
        for k in range(-2, 3):
            poly(ctx, [(hx + k * 10 * s - 5 * s, hy), (hx + k * 10 * s, hy - (18 if k == 0 else 12) * s), (hx + k * 10 * s + 5 * s, hy)]); ctx.fill()
        ctx.rectangle(hx - 28 * s, hy - 2 * s, 56 * s, 7 * s); ctx.fill()

def prophet(ctx, x, y, s, t, robe='#ece4d2', robe2='#5f7f52', **kw):
    d = dict(robe=robe, robe2=robe2, turban='#f6f2e8', prophet=True); d.update(kw)
    person(ctx, x, y, s, t, **d)

def light_presence(ctx, x, y, s, t, a=1.0):
    """the Prophet (pbuh) is never shown: only a soft light"""
    pul = 1 + 0.05 * math.sin(t * 2)
    glow(ctx, x, y - 160 * s, 360 * s * pul, '#ffe6a8', 0.45 * a)
    glow(ctx, x, y - 160 * s, 150 * s * pul, '#fff8e6', 0.7 * a)
    rays(ctx, x, y - 160 * s, t, '#fff0c8', 0.10 * a, n=10, length=420 * s, seed=11)

def baby(ctx, x, y, s, t, prophet_=False, cloth='#efe8d8'):
    ctx.save(); ctx.translate(x, y); ctx.rotate(-0.08)
    ctx.set_source(radgrad(0, 0, 4, 60 * s, [(0, shade(cloth, 0.1)), (1, shade(cloth, -0.25))]))
    ellipse(ctx, 0, 0, 58 * s, 24 * s); ctx.fill()
    src(ctx, shade(cloth, -0.3), 0.5); ctx.set_line_width(2 * s)
    for k in range(3):
        ctx.move_to(-30 * s + k * 18 * s, -20 * s); ctx.curve_to(-20 * s + k * 18 * s, 0, -30 * s + k * 18 * s, 10 * s, -24 * s + k * 18 * s, 22 * s); ctx.stroke()
    if prophet_:
        glow(ctx, 50 * s, -8 * s, 110 * s, '#ffe6a8', 0.6)
        ctx.set_source(radgrad(50 * s, -8 * s, 0, 18 * s, [(0, '#ffffff'), (1, '#ffe08a')])); circle(ctx, 50 * s, -8 * s, 17 * s); ctx.fill()
    else:
        src(ctx, SKIN); circle(ctx, 50 * s, -8 * s, 16 * s); ctx.fill()
    ctx.restore()

def cradle(ctx, x, y, s, t, rock=0.0):
    ctx.save(); ctx.translate(x, y); ctx.rotate(math.sin(t * 1.5) * 0.04 * rock)
    src(ctx, '#5a3a20'); ctx.set_line_width(8 * s)
    ctx.move_to(-90 * s, 0); ctx.curve_to(-60 * s, 26 * s, 60 * s, 26 * s, 90 * s, 0); ctx.stroke()
    ctx.set_source(lingrad(0, -60 * s, 0, 0, [(0, '#9a6e3e'), (1, '#5a3a20')]))
    ctx.move_to(-80 * s, -60 * s); ctx.line_to(80 * s, -60 * s); ctx.line_to(70 * s, -6 * s); ctx.line_to(-70 * s, -6 * s); ctx.close_path(); ctx.fill()
    ctx.restore()

def camel(ctx, x, y, s, t, facing=1, walk=0.0, phase=0.0, col='#c8955a', alpha_=1.0, head_down=0.0, glow_a=0.0, fallen=0.0):
    if alpha_ <= 0.01: return
    u = s
    if alpha_ < 1: ctx.push_group()
    ctx.save(); ctx.translate(x, y); ctx.scale(facing, 1)
    if fallen > 0:
        ctx.translate(0, 0); ctx.rotate(-fallen * 0.15); ctx.translate(0, fallen * 60 * u)
    if glow_a > 0: glow(ctx, 0, -200 * u, 360 * u, '#ffe6a8', 0.4 * glow_a)
    shadow(ctx, 0, 0, 150 * u, 0.3 * (1 - fallen))
    dark = shade(col, -0.3); light = shade(col, 0.25)
    def leg(lx, off, near):
        sw = math.sin(phase + off) * 0.3 * walk
        lift = max(0, math.cos(phase + off)) * 10 * u * walk
        c = col if near else shade(col, -0.2)
        fold = fallen
        kx = lx + math.sin(sw) * 40 * u + fold * 40 * u; ky = lerp(-85 * u, -20 * u, fold)
        fx = lx + math.sin(sw) * 75 * u - fold * 30 * u; fy = -lift
        ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_line_join(cairo.LINE_JOIN_ROUND)
        src(ctx, shade(c, -0.25)); ctx.set_line_width(26 * u)
        ctx.move_to(lx, lerp(-170, -110, fold) * u); ctx.line_to(kx, ky); ctx.line_to(fx, fy - 6 * u); ctx.stroke()
        src(ctx, c); ctx.set_line_width(20 * u)
        ctx.move_to(lx, lerp(-170, -110, fold) * u); ctx.line_to(kx, ky); ctx.line_to(fx, fy - 6 * u); ctx.stroke()
        src(ctx, shade(c, -0.4)); ellipse(ctx, fx, fy - 4 * u, 16 * u, 7 * u); ctx.fill()
    leg(70 * u, PI, False); leg(-75 * u, 0, False)
    by = lerp(0, 60, fallen) * u
    # tail
    src(ctx, dark); ctx.set_line_width(5 * u)
    ctx.move_to(-110 * u, -200 * u + by); ctx.curve_to(-125 * u, -170 * u + by, -120 * u + math.sin(t * 2) * 6 * u, -140 * u + by, -118 * u, -125 * u + by); ctx.stroke()
    # body + hump
    ctx.set_source(radgrad(0, -260 * u + by, 10 * u, 160 * u, [(0, light), (0.7, col), (1, dark)], cx=-10 * u, cy=-280 * u + by))
    ctx.move_to(-115 * u, -195 * u + by)
    ctx.curve_to(-110 * u, -250 * u + by, -60 * u, -330 * u + by, -5 * u, -330 * u + by)
    ctx.curve_to(50 * u, -330 * u + by, 80 * u, -260 * u + by, 110 * u, -230 * u + by)
    ctx.curve_to(125 * u, -200 * u + by, 110 * u, -165 * u + by, 85 * u, -160 * u + by)
    ctx.curve_to(30 * u, -150 * u + by, -60 * u, -150 * u + by, -100 * u, -165 * u + by)
    ctx.close_path(); ctx.fill()
    # neck + head
    hd = head_down
    hx, hy = 205 * u, lerp(-345, -190, hd) * u + by
    ctx.set_source(lingrad(100 * u, 0, hx, 0, [(0, col), (1, light)]))
    ctx.move_to(95 * u, -235 * u + by)
    ctx.curve_to(150 * u, -240 * u + by, 150 * u, hy + 40 * u, hx - 18 * u, hy + 4 * u)
    ctx.line_to(hx - 2 * u, hy + 22 * u)
    ctx.curve_to(170 * u, hy + 60 * u, 160 * u, -185 * u + by, 105 * u, -175 * u + by); ctx.close_path(); ctx.fill()
    ctx.save(); ctx.translate(hx, hy); ctx.rotate(lerp(0.15, 0.9, hd))
    src(ctx, col); ellipse(ctx, 10 * u, 6 * u, 32 * u, 17 * u); ctx.fill()
    src(ctx, light); ellipse(ctx, 34 * u, 12 * u, 13 * u, 12 * u); ctx.fill()
    src(ctx, dark); ellipse(ctx, -8 * u, -14 * u, 6 * u, 9 * u, -0.4); ctx.fill()
    src(ctx, '#1d1814'); circle(ctx, 6 * u, -2 * u, 3 * u); ctx.fill()
    ctx.restore()
    leg(50 * u, PI * 0.5, True); leg(-55 * u, PI * 1.5, True)
    ctx.restore()
    if alpha_ < 1: ctx.pop_group_to_source(); ctx.paint_with_alpha(alpha_)

def ram(ctx, x, y, s, t, facing=1, glow_a=0.0):
    u = s
    ctx.save(); ctx.translate(x, y); ctx.scale(facing, 1)
    if glow_a: glow(ctx, 0, -90 * u, 240 * u, '#fff0c8', 0.5 * glow_a)
    shadow(ctx, 0, 0, 90 * u, 0.3)
    for lx in (-45, -30, 35, 50):
        src(ctx, '#3a302a'); ctx.set_line_width(9 * u); ctx.move_to(lx * u, -70 * u); ctx.line_to(lx * u, -4 * u); ctx.stroke()
    r = rnd(4)
    for k in range(26):
        cx = r.uniform(-62, 62) * u; cy = -95 * u + r.uniform(-30, 25) * u
        ctx.set_source(radgrad(cx - 4 * u, cy - 4 * u, 1, 22 * u, [(0, '#fbf6ea'), (1, '#c9bfa8')])); circle(ctx, cx, cy, r.uniform(14, 22) * u); ctx.fill()
    src(ctx, '#4a3e36'); ellipse(ctx, 80 * u, -112 * u, 26 * u, 18 * u, 0.4); ctx.fill()
    src(ctx, '#2a221c'); circle(ctx, 86 * u, -118 * u, 2.5 * u); ctx.fill()
    ctx.set_source(lingrad(60 * u, -150 * u, 100 * u, -100 * u, [(0, '#d8c8a0'), (1, '#8a7a5a')]))
    ctx.set_line_width(11 * u); ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.move_to(74 * u, -126 * u); ctx.curve_to(50 * u, -160 * u, 20 * u, -130 * u, 44 * u, -110 * u); ctx.curve_to(56 * u, -100 * u, 66 * u, -114 * u, 58 * u, -122 * u); ctx.stroke()
    ctx.restore()

def ant(ctx, x, y, s, t, facing=1, phase=0.0, col='#2a1a12', walk=1.0, raised=0.0):
    u = s
    ctx.save(); ctx.translate(x, y); ctx.scale(facing, 1)
    shadow(ctx, 0, 2 * u, 40 * u, 0.25)
    src(ctx, col); ctx.set_line_width(2.2 * u); ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    for k, lx in enumerate((-12, 0, 12)):
        for sd in (-1, 1):
            ph = phase + k * 2.1 + (PI if sd > 0 else 0)
            fx = lx * u + math.sin(ph) * 6 * u * walk
            ctx.move_to(lx * u, -8 * u); ctx.line_to(lx * u + sd * 4 * u, -14 * u); ctx.line_to(fx + sd * 8 * u, 0); ctx.stroke()
    ctx.save(); ctx.translate(18 * u, -10 * u); ctx.rotate(-raised * 0.5)
    ctx.set_source(radgrad(-36 * u, -12 * u, 1, 18 * u, [(0, shade(col, 0.35)), (1, col)])); ellipse(ctx, -36 * u, -2 * u, 16 * u, 11 * u); ctx.fill()
    ctx.restore()
    ctx.set_source(radgrad(0, -12 * u, 1, 12 * u, [(0, shade(col, 0.35)), (1, col)])); ellipse(ctx, 0, -10 * u, 9 * u, 6 * u); ctx.fill()
    hx, hy = 14 * u, -14 * u - raised * 10 * u
    ctx.set_source(radgrad(hx, hy, 1, 9 * u, [(0, shade(col, 0.35)), (1, col)])); circle(ctx, hx, hy, 7.5 * u); ctx.fill()
    for sd in (-1, 1):
        aw = math.sin(t * 6 + sd) * 0.2
        ctx.move_to(hx + 4 * u, hy - 4 * u); ctx.curve_to(hx + 10 * u, hy - 18 * u + sd * 2 * u, hx + 16 * u, hy - 20 * u, hx + 22 * u + aw * 10 * u, hy - 16 * u + sd * 3 * u); ctx.stroke()
    ctx.restore()

def hoopoe(ctx, x, y, s, t, facing=1, phase=0.0, fly=1.0, crest=1.0):
    u = s
    ctx.save(); ctx.translate(x, y); ctx.scale(facing, 1)
    fl = math.sin(phase) * fly
    def wing(off, c):
        ctx.save(); ctx.translate(-4 * u, -6 * u + off)
        tip_y = -fl * 46 * u
        ctx.move_to(0, 0); ctx.curve_to(-14 * u, tip_y * 0.5 - 6 * u, -36 * u, tip_y - 6 * u, -50 * u, tip_y)
        ctx.curve_to(-36 * u, tip_y * 0.6 + 8 * u, -16 * u, 10 * u, 6 * u, 4 * u); ctx.close_path()
        src(ctx, c); ctx.fill()
        src(ctx, '#f4efe4'); ctx.set_line_width(3.5 * u)
        for k in range(3):
            f = 0.35 + k * 0.2
            ctx.move_to(lerp(0, -50 * u, f) - 4 * u, lerp(0, tip_y, f) - 6 * u); ctx.line_to(lerp(0, -50 * u, f) + 4 * u, lerp(0, tip_y, f) + 8 * u); ctx.stroke()
        ctx.restore()
    wing(-2 * u, '#1e1a16')
    src(ctx, '#1e1a16'); poly(ctx, [(-18 * u, -2 * u), (-40 * u, -6 * u), (-40 * u, 6 * u)]); ctx.fill()
    ctx.set_source(lingrad(0, -14 * u, 0, 8 * u, [(0, '#e8a060'), (1, '#c87a44')]))
    ellipse(ctx, 0, 0, 22 * u, 10 * u, -0.1); ctx.fill()
    src(ctx, '#e0965a'); circle(ctx, 20 * u, -8 * u, 8 * u); ctx.fill()
    src(ctx, '#2a1e18'); ctx.set_line_width(2.6 * u); ctx.move_to(27 * u, -8 * u); ctx.curve_to(36 * u, -6 * u, 42 * u, -2 * u, 46 * u, 2 * u); ctx.stroke()
    src(ctx, '#1d1814'); circle(ctx, 22 * u, -10 * u, 1.8 * u); ctx.fill()
    for k in range(6):
        a = -2.2 + k * 0.22 * crest
        L = (14 + k * 1.5) * u * (0.6 + 0.4 * crest)
        bx, by = 16 * u, -14 * u
        ex, ey = bx + math.cos(a) * L, by + math.sin(a) * L
        src(ctx, '#e8a060'); ctx.set_line_width(4 * u); ctx.move_to(bx, by); ctx.line_to(ex, ey); ctx.stroke()
        src(ctx, '#1e1a16'); circle(ctx, ex, ey, 2.2 * u); ctx.fill()
    wing(2 * u, '#2a241e')
    ctx.restore()

def mosque(ctx, x, y, s, c='#e8dcc4', lit=0.0):
    u = s
    box(ctx, x - 160 * u, y, 320 * u, 150 * u, 60 * u, c)
    ctx.set_source(radgrad(x, y - 230 * u, 10 * u, 120 * u, [(0, shade(c, 0.2)), (1, shade(c, -0.2))]))
    ctx.move_to(x - 100 * u, y - 150 * u); ctx.curve_to(x - 100 * u, y - 290 * u, x + 100 * u, y - 290 * u, x + 100 * u, y - 150 * u); ctx.close_path(); ctx.fill()
    src(ctx, '#d9b35a'); ctx.set_line_width(4 * u); ctx.move_to(x, y - 255 * u); ctx.line_to(x, y - 300 * u); ctx.stroke()
    circle(ctx, x, y - 306 * u, 6 * u); ctx.fill()
    for mx in (x - 220 * u, x + 230 * u):
        box(ctx, mx - 18 * u, y, 36 * u, 330 * u, 14 * u, c)
        src(ctx, shade(c, -0.1)); ctx.rectangle(mx - 26 * u, y - 250 * u, 52 * u, 12 * u); ctx.fill()
        ctx.move_to(mx - 18 * u, y - 330 * u); ctx.line_to(mx, y - 380 * u); ctx.line_to(mx + 18 * u, y - 330 * u); ctx.close_path(); ctx.fill()
    for k in range(4):
        wx = x - 120 * u + k * 70 * u
        src(ctx, '#2a1c12' if lit <= 0 else mix('#2a1c12', '#ffcf7a', lit)); ctx.move_to(wx, y - 40 * u); ctx.line_to(wx, y - 90 * u)
        ctx.curve_to(wx, y - 110 * u, wx + 30 * u, y - 110 * u, wx + 30 * u, y - 90 * u); ctx.line_to(wx + 30 * u, y - 40 * u); ctx.close_path(); ctx.fill()
        if lit > 0: glow(ctx, wx + 15 * u, y - 70 * u, 60 * u, '#ffb45a', 0.5 * lit)

def book(ctx, x, y, s, t, glow_a=0.5, open_=1.0):
    u = s
    if glow_a: glow(ctx, x, y - 30 * u, 260 * u, '#ffe6a8', glow_a)
    src(ctx, '#3a2414'); poly(ctx, [(x - 150 * u, y), (x + 150 * u, y), (x + 130 * u, y + 20 * u), (x - 130 * u, y + 20 * u)]); ctx.fill()
    for sd in (-1, 1):
        ctx.set_source(lingrad(x, 0, x + sd * 150 * u, 0, [(0, '#d8cdb0'), (1, '#f6f0e0')]))
        ctx.move_to(x, y - 6 * u); ctx.curve_to(x + sd * 50 * u, y - 30 * u * open_, x + sd * 110 * u, y - 30 * u * open_, x + sd * 145 * u, y - 14 * u * open_)
        ctx.line_to(x + sd * 145 * u, y + 6 * u); ctx.curve_to(x + sd * 110 * u, y - 6 * u, x + sd * 50 * u, y - 6 * u, x, y + 10 * u); ctx.close_path()
        ctx.fill_preserve()
        ctx.save(); ctx.clip()
        src(ctx, '#6a5a3a', 0.4); ctx.set_line_width(1.8 * u)
        for k in range(6):
            yy = y - 2 * u + k * 3.4 * u
            ctx.new_path()
            ctx.move_to(x + sd * 16 * u, yy)
            ctx.curve_to(x + sd * 55 * u, yy - 22 * u * open_, x + sd * 108 * u, yy - 23 * u * open_,
                         x + sd * 138 * u, yy - 9 * u * open_)
            ctx.stroke()
        ctx.restore(); ctx.new_path()

def oil_lamp(ctx, x, y, s, t, lit=1.0):
    u = s
    ctx.set_source(lingrad(x - 40 * u, 0, x + 40 * u, 0, [(0, '#6a3a1a'), (0.5, '#b8743a'), (1, '#5a2a12')]))
    ctx.move_to(x - 40 * u, y); ctx.curve_to(x - 40 * u, y - 26 * u, x + 30 * u, y - 26 * u, x + 50 * u, y - 14 * u)
    ctx.line_to(x + 56 * u, y - 18 * u); ctx.line_to(x + 52 * u, y - 6 * u); ctx.curve_to(x + 30 * u, y + 4 * u, x - 30 * u, y + 6 * u, x - 40 * u, y); ctx.fill()
    if lit > 0:
        glow(ctx, x + 54 * u, y - 30 * u, 520 * u, '#ffb45a', 0.55 * lit)
        flame(ctx, x + 54 * u, y - 18 * u, 7 * u, 34 * u, t, seed=3, a=lit)

def rock_houses(ctx, x, y, s, t, c='#b07a52', seed=1, n=5, lit=0.0):
    u = s
    r = rnd(seed)
    ctx.move_to(x - 700 * u, y + 40 * u)
    xx = x - 700 * u
    while xx < x + 700 * u:
        ctx.line_to(xx, y - 520 * u - 120 * u * abs(nz(xx * 0.004 / u, seed)))
        xx += 30 * u
    ctx.line_to(x + 700 * u, y + 40 * u); ctx.close_path()
    ctx.set_source(lingrad(0, y - 650 * u, 0, y, [(0, shade(c, 0.12)), (1, shade(c, -0.15))])); ctx.fill()
    src(ctx, shade(c, -0.3), 0.3); ctx.set_line_width(2 * u)
    for k in range(14):
        sx = x + r.uniform(-650, 650) * u
        ctx.move_to(sx, y - r.uniform(100, 500) * u); ctx.line_to(sx + r.uniform(-30, 30) * u, y - r.uniform(0, 80) * u); ctx.stroke()
    for i in range(n):
        fx = x + (-560 + i * 1120 / max(1, n - 1)) * u + r.uniform(-30, 30) * u
        fw = r.uniform(130, 190) * u; fh = r.uniform(220, 320) * u; fy = y - r.uniform(0, 60) * u
        src(ctx, shade(c, 0.08)); ctx.rectangle(fx - fw / 2, fy - fh, fw, fh); ctx.fill()
        src(ctx, shade(c, -0.12)); ctx.rectangle(fx - fw / 2, fy - fh, fw, 18 * u); ctx.fill()
        for k in range(4):
            px = fx - fw / 2 + 14 * u + k * (fw - 28 * u) / 3
            src(ctx, shade(c, -0.05)); ctx.rectangle(px - 6 * u, fy - fh + 30 * u, 12 * u, fh - 30 * u); ctx.fill()
        poly(ctx, [(fx - fw / 2 - 10 * u, fy - fh), (fx, fy - fh - 50 * u), (fx + fw / 2 + 10 * u, fy - fh)])
        src(ctx, shade(c, 0.15)); ctx.fill()
        src(ctx, '#1a100a' if lit <= 0 else mix('#1a100a', '#ffb45a', lit * 0.6)); rrect(ctx, fx - 26 * u, fy - 110 * u, 52 * u, 110 * u, 6 * u); ctx.fill()
        if lit > 0: glow(ctx, fx, fy - 60 * u, 90 * u, '#ffb45a', 0.4 * lit)

def cave_interior(ctx, t, glow_x=540, glow_y=1300, glow_a=0.6):
    ctx.set_source(radgrad(glow_x, glow_y, 40, 1400, [(0, '#5a4636'), (0.4, '#2e241c'), (1, '#0c0907')]))
    ctx.rectangle(-2000, -2000, 5000, 6000); ctx.fill()
    r = rnd(4)
    for k in range(40):
        x = r.uniform(-300, 1400); y = r.uniform(-200, 2200); rr = r.uniform(60, 220)
        ctx.set_source(radgrad(x, y, 0, rr, [(0, (0.25, 0.2, 0.15, 0.35)), (1, (0, 0, 0, 0))])); circle(ctx, x, y, rr); ctx.fill()
    glow(ctx, glow_x, glow_y, 700, '#ffd9a0', 0.2 * glow_a)

def scroll(ctx, x, y, s, t, open_=1.0, seal=True):
    u = s
    w = 220 * u * open_ + 30 * u
    ctx.set_source(lingrad(x - w / 2, 0, x + w / 2, 0, [(0, '#d8c090'), (0.5, '#f4e6c4'), (1, '#d8c090')]))
    ctx.rectangle(x - w / 2, y - 140 * u, w, 280 * u); ctx.fill()
    src(ctx, '#7a5a30', 0.6); ctx.set_line_width(2 * u)
    for k in range(int(8 * open_)):
        yy = y - 100 * u + k * 26 * u
        ctx.move_to(x - w / 2 + 24 * u, yy); ctx.line_to(x + w / 2 - 24 * u, yy); ctx.stroke()
    for sd in (-1, 1):
        ctx.set_source(lingrad(0, y - 150 * u, 0, y + 150 * u, [(0, '#8a5a2a'), (0.5, '#c08a4a'), (1, '#8a5a2a')]))
        rrect(ctx, x + sd * w / 2 - 14 * u, y - 155 * u, 28 * u, 310 * u, 14 * u); ctx.fill()
    if seal and open_ < 0.3:
        src(ctx, '#a0262a'); circle(ctx, x, y, 22 * u); ctx.fill()

def palace_hall(ctx, t, c='#c9a77a', lamps=True):
    ctx.set_source(lingrad(0, 0, 0, 1300, [(0, shade(c, -0.35)), (1, shade(c, -0.1))]))
    ctx.rectangle(-2000, -2000, 5000, 3400); ctx.fill()
    for k in range(-3, 9):
        cx = k * 220
        ctx.set_source(lingrad(cx - 36, 0, cx + 36, 0, [(0, shade(c, -0.3)), (0.5, shade(c, 0.2)), (1, shade(c, -0.35))]))
        ctx.rectangle(cx - 36, 300, 72, 1000); ctx.fill()
        src(ctx, shade(c, -0.15)); ctx.rectangle(cx - 50, 290, 100, 24); ctx.fill()
        if k < 8:
            src(ctx, shade(c, -0.25)); ctx.move_to(cx + 36, 420); ctx.curve_to(cx + 60, 300, cx + 160, 300, cx + 184, 420); ctx.line_to(cx + 184, 400); ctx.curve_to(cx + 160, 320, cx + 60, 320, cx + 36, 400); ctx.fill()
        if lamps:
            glow(ctx, cx + 110, 520, 160, '#ffb45a', 0.35)
            src(ctx, '#d9b35a'); circle(ctx, cx + 110, 520, 9); ctx.fill()
    ctx.set_source(lingrad(0, 1300, 0, 2400, [(0, '#6a4a32'), (1, '#2a1a10')]))
    ctx.rectangle(-2000, 1300, 5000, 1500); ctx.fill()
    src(ctx, (0, 0, 0), 0.12); ctx.set_line_width(2)
    for i in range(-20, 40):
        ctx.move_to(540 + i * 110, 1300); ctx.line_to(540 + (i * 110) * 3.0, 2400); ctx.stroke()

def throne(ctx, x, y, s, c='#d9b35a'):
    u = s
    ctx.set_source(lingrad(x - 120 * u, 0, x + 120 * u, 0, [(0, shade(c, -0.3)), (0.5, shade(c, 0.25)), (1, shade(c, -0.3))]))
    rrect(ctx, x - 110 * u, y - 380 * u, 220 * u, 300 * u, 30 * u); ctx.fill()
    src(ctx, '#7a1a2a'); rrect(ctx, x - 80 * u, y - 340 * u, 160 * u, 240 * u, 20 * u); ctx.fill()
    ctx.set_source(lingrad(0, y - 120 * u, 0, y, [(0, shade(c, 0.1)), (1, shade(c, -0.3))]))
    ctx.rectangle(x - 140 * u, y - 120 * u, 280 * u, 120 * u); ctx.fill()

def soldier2(ctx, x, y, s, t, i, facing=1, walk=0.0, phase=0.0, alpha_=1.0, arms=None, giant=False, tilt=0.0):
    r = rnd(4000 + i)
    robe = shade(r.choice(['#6e3b2a', '#5a4632', '#7a4a30', '#4e3a2c', '#4a4a3a']), r.uniform(-0.1, 0.1))
    person(ctx, x, y, s, t, facing=facing, robe=robe if not giant else '#3a3a40', robe2='#2e1c12', head='helmet', beard='#221610',
           walk=walk, phase=phase, prop='spear', prop2='shield', arms=arms or (0.35, 0.5), elbows=(0.9, 0.6), seed=4000 + i,
           alpha_=alpha_, skin=shade(SKIN, r.uniform(-0.2, 0.05)), tilt=tilt, cloak='#2a2a30' if giant else None)

def folk(ctx, x, y, s, t, i, **kw):
    r = rnd(3000 + i)
    d = dict(robe=r.choice(['#7a4a5a', '#5a4a3a', '#8a6a44', '#4e5a6a', '#6e3b2a', '#9a7a5a', '#5a3a4a', '#6a6a4a']),
             robe2=r.choice(['#3a2418', '#a8823a', '#2a3a4a']), turban=r.choice(['#d8c8a8', '#8a6a4a', '#c9b08a', '#a8564a', '#e8dcc4']),
             beard=r.choice(['#2a1d14', '#3a2a1c', '#cfc8bc', '#1a120c']), skin=shade(SKIN, r.uniform(-0.2, 0.08)), seed=3000 + i)
    d.update(kw)
    person(ctx, x, y, s, t, **d)

def desert_world(ctx, t, cam, P, hz=1150, seed=0, far_amp=300, mid_amp=170, sun_pos=(820, 520), clouds_a=0.5, rocks_n=8, stars_a=0.0, moon_pos=None, ray_a=0.08):
    bg(ctx, t, cam, P, horizon=hz, sun_pos=sun_pos, clouds_a=clouds_a, seed=seed, far_amp=far_amp, mid_amp=mid_amp, stars_a=stars_a, moon_pos=moon_pos, ray_a=ray_a)
    floor(ctx, t, cam, P, hz, seed=seed + 1, rocks_n=rocks_n)

# ---- baby carried in the arm (drawn with the front arm, so it moves with her) ----
import lib as _lib
_dp_orig = _lib.draw_prop
def _dp_baby(ctx, kind, hx, hy, ang, u, t, facing):
    if kind in ('baby', 'baby_p'):
        dx, dy = math.sin(ang), math.cos(ang)
        cx = hx - facing * dx * 36 * u; cy = hy - dy * 36 * u - 12 * u
        ctx.save(); ctx.translate(cx, cy); ctx.scale(facing, 1); ctx.rotate(math.atan2(dy, dx) + 0.08); ctx.scale(-1, 1)
        baby(ctx, 0, 0, 0.55 * u, t, prophet_=(kind == 'baby_p'))
        ctx.restore()
        # hand over the bundle
        src(ctx, shade('#3a2a22', 0.0), 0.0)
        return
    return _dp_orig(ctx, kind, hx, hy, ang, u, t, facing)
_lib.draw_prop = _dp_baby
CARRY = dict(arms=(0.35, 0.55), elbows=(1.25, 1.0), swing=0.12, prop='baby_p')
