# Badr demo: same 50/50 schedule as badr_nacht_demo, but the animated parts use the
# detailed PyCairo engine (eng16): figures with robes, wells, palms, couched camels, the hut, light.
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, '..', 'eng16'))
import numpy as np
import badr_nacht_demo as N
import badr_scenes as B

N.day_scene = lambda t, u: B.sc_day(t, u)
N.camp_night = B.sc_camp
N.prayer_night = B.sc_prayer
N.angels_dawn = B.sc_angels
N.QPOS.update({'qm': ('right', 0, 330), 'q89': ('center', 0, 110)})
frame, DUR, FPS = N.frame, N.DUR, N.FPS

if __name__ == '__main__':
    import cv2
    if sys.argv[1] == 'still':
        ts = [float(x) for x in sys.argv[3:]]
        tiles = [cv2.resize(frame(t), (640, 360)) for t in ts]
        while len(tiles) % 3: tiles.append(np.zeros_like(tiles[0]))
        cv2.imwrite(sys.argv[2], np.vstack([np.hstack(tiles[i:i + 3]) for i in range(0, len(tiles), 3)])[:, :, ::-1])
    else:   # chunk render: python3 badr_detail_demo.py chunk i n > raw
        i, n = int(sys.argv[2]), int(sys.argv[3])
        N_ = int(DUR * FPS); a, b = N_ * i // n, N_ * (i + 1) // n
        wr = sys.stdout.buffer
        for k in range(a, b): wr.write(np.ascontiguousarray(frame(k / FPS)).tobytes())
