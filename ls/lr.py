import os, sys, importlib, subprocess, cairo
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import base
W, H = base.W, base.H
FPS = int(os.environ.get('FPS', '30'))

def make(mod, t):
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    ctx = cairo.Context(surf)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    mod.frame(ctx, t)
    return surf

name = sys.argv[1]
mode = sys.argv[2]
mod = importlib.import_module(name)

if mode == 'still':
    os.makedirs('test', exist_ok=True)
    for a in sys.argv[3:]:
        t = float(a)
        make(mod, t).write_to_png(f'test/{name}_{t:06.2f}.png')
    print('stills ok')
else:
    a, b, out = int(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
    p = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgra',
                          '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-c:v', 'libx264',
                          '-preset', 'veryfast', '-crf', '21', '-pix_fmt', 'yuv420p', out],
                         stdin=subprocess.PIPE)
    for f in range(a, b):
        s = make(mod, f / FPS)
        p.stdin.write(bytes(s.get_data()))
        if (f - a) % 150 == 0: print(name, f, flush=True)
    p.stdin.close(); p.wait()
    print('done', out)
