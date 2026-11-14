from lib import *

PAL = {
    'day': dict(top='#3f6ea6', mid='#dcc49c', bot='#f2dcb2', far='#b2917a', mid_r='#8e6a52', near='#6a4632',
                g1='#dcb47e', g2='#c39563', haze='#f0dcb6', sun='#fff4d6', halo='#ffd27a', light='#ffe9b8'),
    'dawn': dict(top='#1d2b4c', mid='#d98a5c', bot='#f4bb7e', far='#7a5058', mid_r='#56363c', near='#3c262a',
                 g1='#b8825a', g2='#8e5e40', haze='#eaa678', sun='#fff0c8', halo='#ff9a4a', light='#ffc98a'),
    'dusk': dict(top='#2a2448', mid='#c86c4c', bot='#f2a866', far='#6a4250', mid_r='#4a2e38', near='#33202a',
                 g1='#a8704c', g2='#7e4e36', haze='#e0906a', sun='#ffe0a8', halo='#ff7a3a', light='#ffb070'),
    'night': dict(top='#04071a', mid='#121c44', bot='#28305e', far='#1c2240', mid_r='#141932', near='#0e1124',
                  g1='#2c2a44', g2='#1d1b30', haze='#26305c', sun='#f4f1e2', halo='#7fa0ff', light='#a8c0ff'),
    'storm': dict(top='#2a2c34', mid='#7a6a5c', bot='#b89a78', far='#6e5a4c', mid_r='#5a4436', near='#3e2c22',
                  g1='#a88660', g2='#8a6a48', haze='#a8927a', sun='#ffe8c0', halo='#d9a060', light='#e8c890'),
}

def layer(ctx, cam, f, fn, shake=(0, 0)):
    ctx.save(); cam.apply(ctx, f, shake); fn(); ctx.restore()

def bg(ctx, t, cam, P, horizon=1150, seed=0, sun_pos=(820, 520), sun_r=46, clouds_a=0.55, stars_a=0.0, moon_pos=None,
       far=True, mid=True, shake=(0, 0), sun_a=1.0, ray_a=0.08, far_amp=300, mid_amp=170):
    layer(ctx, cam, 0.04, lambda: sky(ctx, P['top'], P['mid'], P['bot'], horizon - 1500, horizon + 150), shake)
    if stars_a > 0:
        layer(ctx, cam, 0.06, lambda: stars(ctx, t, stars_a), shake)
    if moon_pos:
        layer(ctx, cam, 0.08, lambda: moon(ctx, moon_pos[0], moon_pos[1], 34), shake)
    if sun_pos and sun_a > 0:
        layer(ctx, cam, 0.1, lambda: (sun(ctx, sun_pos[0], sun_pos[1], sun_r, P['sun'], P['halo'], sun_a),
                                       rays(ctx, sun_pos[0], sun_pos[1], t, P['light'], ray_a * sun_a)), shake)
    if clouds_a > 0:
        layer(ctx, cam, 0.15, lambda: clouds(ctx, t, horizon - 750, mix(P['light'], (1, 1, 1), 0.4), clouds_a, n=6, seed=seed + 3, speed=10), shake)
    if far:
        def f1():
            pts = ridge(ctx, horizon + 20, far_amp, P['far'], seed=seed + 1, freq=0.0035, color2=shade(P['far'], 0.1), sharp=0.4)
            ridge_light(ctx, pts, P['light'], 0.18)
            haze(ctx, P['haze'], 0.18)
        layer(ctx, cam, 0.3, f1, shake)
    if mid:
        def f2():
            pts = ridge(ctx, horizon + 80, mid_amp, P['mid_r'], seed=seed + 2, freq=0.006, color2=shade(P['mid_r'], 0.12), sharp=0.6)
            ridge_light(ctx, pts, P['light'], 0.22, 2)
        layer(ctx, cam, 0.55, f2, shake)
        layer(ctx, cam, 0.55, lambda: haze(ctx, P['haze'], 0.08), shake)

def floor(ctx, t, cam, P, horizon=1150, seed=0, shake=(0, 0), rocks_n=10):
    def f():
        ground(ctx, horizon, P['g1'], P['g2'])
        dune_lines(ctx, horizon, t, shade(P['g2'], -0.3), seed=seed, a=0.12)
        if rocks_n: rocks(ctx, horizon + 40, seed=seed + 4, n=rocks_n, c=shade(P['near'], 0.2))
    layer(ctx, cam, 1.0, f, shake)

def side_hills(ctx, base, amp, col, seed=0, l=260, r=820, col2=None):
    ctx.move_to(-1600, 3000)
    x = -1600; pts = []
    while x <= 2700:
        e = sm((l - x) / 650) + sm((x - r) / 650)
        y = base - amp * e * (0.65 + 0.35 * nz(x * 0.008, seed)) - 30 * abs(nz(x * 0.02, seed + 3))
        pts.append((x, y)); ctx.line_to(x, y); x += 12
    ctx.line_to(2700, 3000); ctx.close_path()
    top = min(p[1] for p in pts)
    ctx.set_source(lingrad(0, top, 0, base + 100, [(0, col2 or shade(col, 0.15)), (1, col)])); ctx.fill()
    return pts

def town(ctx, t, cx, y, s, seed=0, n=26, c='#b88c62', lit=0.0, gap=150):
    r = rnd(seed)
    items = []
    for i in range(n):
        side = -1 if i % 2 else 1
        x = cx + side * r.uniform(gap, 560) * s
        yy = y + r.uniform(-60, 90) * s
        w = r.uniform(50, 110) * s; h = r.uniform(40, 95) * s
        items.append((yy, x, w, h, r.random()))
    items.sort()
    out = []
    for yy, x, w, h, rv in items:
        k = 1 + (yy - y) / (500 * s)
        box(ctx, x - w / 2, yy, w * k, h * k, 30 * s * k, shade(c, (rv - 0.5) * 0.25), win=2, seed=int(rv * 1000))
        if lit > 0:
            for j in range(2):
                wx = x - w / 2 + w * k * (0.25 + j * 0.4); wy = yy - h * k * 0.55
                glow(ctx, wx, wy, 26 * s * k, '#ffb45a', 0.5 * lit)
                src(ctx, '#ffcf7a', 0.9 * lit); ctx.rectangle(wx - 3 * s, wy - 5 * s, 7 * s * k, 10 * s * k); ctx.fill()
    return out
