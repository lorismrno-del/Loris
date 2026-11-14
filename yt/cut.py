# Freisteller aus vorhandenen KI Bildern (keine Credits): python3 cut.py <bild.jpg> x0 y0 x1 y1 <out.png>
# Koordinaten im Bild selbst. Behaelt nur das groesste Objekt.
import sys, cv2, numpy as np
from rembg import remove, new_session
src, x0, y0, x1, y1, out = sys.argv[1], *map(int, sys.argv[2:6]), sys.argv[6]
im = cv2.imread(src)
c = cv2.resize(im[y0:y1, x0:x1], None, fx=2, fy=2, interpolation=cv2.INTER_LANCZOS4)
rgba = np.array(remove(cv2.cvtColor(c, cv2.COLOR_BGR2RGBA), session=new_session('u2net'))).copy()
a = rgba[..., 3].copy()
n, lab, st, _ = cv2.connectedComponentsWithStats((a > 128).astype(np.uint8))
k = 1 + np.argmax(st[1:, 4]); keep = cv2.dilate((lab == k).astype(np.uint8), np.ones((5, 5), np.uint8))
rgba[..., 3] = (a * keep).astype(np.uint8)
ys, xs = np.where(rgba[..., 3] > 20)
rgba = rgba[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
cv2.imwrite(out, cv2.cvtColor(rgba, cv2.COLOR_RGBA2BGRA)); print(out, rgba.shape)
