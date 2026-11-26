"""두 색(빨강·검정)뿐인 텍스처에서 경계의 어중간한 색만 한쪽으로 확정해 경계를 끊는다.

실행: python tools/char/snap_two_tone.py <입력.jpg> <출력.jpg> [경계값=85]
빨강 정도 = R - max(G,B). 12~경계값 → 붉은 기를 뺀 검정(원래 밝기 유지) · 경계값~165 → 원래 색조의 선명한 빨강.
이미 선명한 빨강(165 이상)과 검정(12 미만)은 그대로. 모양·UV는 건드리지 않는다.
"""
import sys
import numpy as np
from PIL import Image

src, out = sys.argv[1], sys.argv[2]
cut = float(sys.argv[3]) if len(sys.argv) > 3 else 85.0
a = np.array(Image.open(src).convert("RGB")).astype(np.float32)
r, g, b = a[..., 0], a[..., 1], a[..., 2]
red = r - np.maximum(g, b)
lo = (red >= 12) & (red < cut)
hi = (red >= cut) & (red < 165)
a[..., 0] = np.where(lo, np.maximum(g, b) + 6, r)
scale = np.where(hi, 205.0 / np.maximum(r, 1), 1.0)
a = np.clip(a * scale[..., None], 0, 255)
Image.fromarray(a.astype(np.uint8)).save(out, quality=95, subsampling=0)
print("snapped", int(lo.sum()), "to black,", int(hi.sum()), "to red, of", red.size)
