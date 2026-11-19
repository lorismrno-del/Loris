import sys, importlib, subprocess, cairo, os
from lib import W, H, FPS

SCALE = float(os.environ.get('SCALE', '1'))

def make_frame(mod, t):
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, int(W * SCALE), int(H * SCALE))
    ctx = cairo.Context(surf)
    if SCALE != 1:
        ctx.scale(SCALE, SCALE)
    mod.frame(ctx, t)
    surf.flush()
    return surf

if __name__ == '__main__':
    name = sys.argv[1]; mode = sys.argv[2]
    mod = importlib.import_module(name)
    if mode == 'still':
        for ts in sys.argv[3:]:
            t = float(ts)
            s = make_frame(mod, t)
            s.write_to_png(f'test/{name}_{t:06.2f}.png')
    else:
        f0, f1, out = int(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
        p = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgra', '-s', f'{int(W*SCALE)}x{int(H*SCALE)}', '-r', str(FPS),
                              '-i', '-', '-c:v', 'libx264', '-preset', 'faster', '-crf', '19', '-pix_fmt', 'yuv420p', out],
                             stdin=subprocess.PIPE)
        for f in range(f0, f1):
            s = make_frame(mod, f / FPS)
            p.stdin.write(bytes(s.get_data()))
            if f % 150 == 0:
                print(name, f, flush=True)
        p.stdin.close(); p.wait()
        print('done', out, flush=True)
