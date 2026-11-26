"""얼굴 확대 칠한 그림 → 게임 얼굴 그림(눈·눈썹·코·입, 투명 바탕) + face_fit.json.

실행: python tools/char/face_from_closeup.py <폴더> <이름> <GPT 얼굴 그림.png> <출력 얼굴.png> <face_fit.json>
  <폴더>/<이름>_face_vis.png · <이름>_face_cam.json : render_face_view.py 결과
GPT 그림은 크기·위치가 조금 바뀌므로, 그림의 피부 자리 ↔ 얼굴판이 보이는 자리가 가장 잘 겹치게 맞춘 뒤(IoU),
얼굴판이 보이는 자리 안에서 피부색과 다른 곳만 남긴다. 얼굴 네모는 face_fit.json의 값을 그대로 쓴다.
"""
import json
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

d, name, src, out_png, fit_json = sys.argv[1:6]
cam = json.load(open(f"{d}/{name}_face_cam.json"))
fit = json.load(open(fit_json))
vis = np.asarray(Image.open(f"{d}/{name}_face_vis.png").convert("L")) > 127
N = cam["size"]
img = Image.open(src).convert("RGB").resize((N, N), Image.LANCZOS)
a = np.asarray(img).astype(np.float32)
top = int(N * 0.72)  # 목·깃 빼고 얼굴 쪽만 비교


def skin_mask(arr):
	lum = arr.mean(2); sat = arr.max(2) - arr.min(2)
	return (lum > 200) & (sat < 30)


sm = skin_mask(a)
best = None
small = 256
vq = np.asarray(Image.fromarray((vis[:top] * 255).astype(np.uint8)).resize((small, int(small * top / N)))) > 127
for s in np.linspace(0.85, 1.15, 16):
	g = Image.fromarray((sm * 255).astype(np.uint8)).resize((round(N * s), round(N * s)))
	for dx in range(-48, 49, 8):
		for dy in range(-48, 49, 8):
			cv = Image.new("L", (N, N), 0)
			cv.paste(g, (round(N / 2 - N * s / 2) + dx, round(N / 2 - N * s / 2) + dy))
			c = np.asarray(cv.crop((0, 0, N, top)).resize(vq.shape[::-1])) > 127
			iou = (c & vq).sum() / max(1, (c | vq).sum())
			if best is None or iou > best[0]:
				best = (iou, s, dx, dy)
iou, s, dx, dy = best
print("fit IoU", round(float(iou), 3), "scale", round(float(s), 3), "dx", dx, "dy", dy)
big = img.resize((round(N * s), round(N * s)), Image.LANCZOS)
al = Image.new("RGB", (N, N), "white")
al.paste(big, (round(N / 2 - N * s / 2) + dx, round(N / 2 - N * s / 2) + dy))
al.save(f"{d}/{name}_face_paint_fit.png")
A = np.asarray(al).astype(np.float32)
v = ndimage.binary_erosion(vis, iterations=2)
skin = np.median(A[v & skin_mask(A)], axis=0)
diff = np.abs(A - skin).sum(2)
feat = (diff > 45) & v
feat[top:] = False
feat = ndimage.binary_fill_holes(ndimage.binary_closing(feat, iterations=2)) & v
lab, n = ndimage.label(feat)
sizes = ndimage.sum(feat, lab, range(1, n + 1))
# 얼굴 네모 안 기준 세로 위치: 입(가장 아래 이목구비)보다 아래(턱선·깃)는 버림
m = int(N / 1.5)
o = (N - m) // 2
cy = ndimage.center_of_mass(feat, lab, range(1, n + 1))
keep = np.isin(lab, [i + 1 for i, (sz, c) in enumerate(zip(sizes, cy)) if sz >= 20 and (c[0] - o) / m < 0.72])
alpha = np.clip(ndimage.gaussian_filter(keep.astype(np.float32), 0.8) * 1.5, 0, 1) * v
# 얼굴 네모(face_fit) = 이 확대 화면의 가운데 1/1.5 (render_face_view.py가 네모의 1.5배를 찍음)
rgba = np.dstack([A, alpha * 255]).astype(np.uint8)[o:o + m, o:o + m]
Image.fromarray(rgba).resize((1024, 1024), Image.LANCZOS).save(out_png)
fit["skin"] = [int(x) for x in skin]
json.dump(fit, open(fit_json, "w"), indent=1)
print("face", out_png, "blobs", int(len([x for x in sizes if x >= 20])), "skin", skin.astype(int))
