"""AI 텍스처의 번진 가장자리를 또렷하게: 색을 대표색 몇 개로 묶어 경계를 딱 끊는다 (모양·UV는 안 건드림).

실행: python tools/char/crisp_texture.py <입력 텍스처> <출력.png> [색 수=12] [크게=2]
순서: ① 크게 키움(경계가 계단지지 않게) ② 대표색 뽑기(k-means, Lab 비슷하게 밝기 가중)
      ③ 픽셀마다 가장 가까운 대표색 ④ 3×3 다수결 2번(점 잡티 제거) ⑤ 원래 크기로 줄이며 경계만 1픽셀 부드럽게
"""
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

src, out = sys.argv[1], sys.argv[2]
K = int(sys.argv[3]) if len(sys.argv) > 3 else 12
UP = int(sys.argv[4]) if len(sys.argv) > 4 else 2
im = Image.open(src).convert("RGB")
W, H = im.size
big = im.resize((W * UP, H * UP), Image.BICUBIC)
a = np.asarray(big).astype(np.float32) / 255.0
X = a.reshape(-1, 3)
rng = np.random.default_rng(0)
samp = X[rng.choice(len(X), 200000, replace=False)]
# 처음 중심: 멀리 떨어진 색부터 고름(작은 색 = 금·분홍도 놓치지 않게)
C = [samp[0]]
for _ in range(K - 1):
	d = np.min(((samp[:, None, :] - np.array(C)[None]) ** 2).sum(2), axis=1)
	C.append(samp[d.argmax()])
C = np.array(C)
for _ in range(25):
	lab = ((samp[:, None, :] - C[None]) ** 2).sum(2).argmin(1)
	for j in range(K):
		if (lab == j).any():
			C[j] = samp[lab == j].mean(0)
labs = np.empty(len(X), dtype=np.uint8)
for i in range(0, len(X), 2_000_000):
	labs[i:i + 2_000_000] = ((X[i:i + 2_000_000, None, :] - C[None]) ** 2).sum(2).argmin(1)
labs = labs.reshape(a.shape[:2])
for _ in range(2):
	counts = np.stack([ndimage.uniform_filter((labs == j).astype(np.float32), 3) for j in range(K)])
	labs = counts.argmax(0).astype(np.uint8)
res = (C[labs] * 255).astype(np.uint8)
Image.fromarray(res).resize((W, H), Image.LANCZOS).save(out)
print("saved", out, "colors", (C * 255).astype(int).tolist())
