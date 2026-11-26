"""칠한 정면 그림(3D 렌더 위에 칠함)에서 얼굴 그림(눈·눈썹·입)을 오려 게임 얼굴 텍스처로.

실행: python tools/char/face_from_paint.py <폴더> <이름> <출력 얼굴.png> <face_fit.json>
  <폴더>/<이름>_paint_front.png  : fit_paint.py 결과 (렌더와 같은 칸)
  <폴더>/<이름>_facevis_front.png: 얼굴판이 보이는 자리 (render_ref_views.py)
  <폴더>/<이름>_cam.json         : 카메라 값
그림이 3D 모양 위에 칠해졌으므로 눈·입이 3D 얼굴의 코·턱 자리에 맞는다.
얼굴 네모 = 얼굴판이 보이는 자리의 상자 → face_fit.json(키 1.0·바닥 0 기준 중심·크기)에 적고
split_tripo_textured.py가 그 값을 쓴다.
"""
import json
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

d, name, out_png, out_json = sys.argv[1:5]
cam = json.load(open(f"{d}/{name}_cam.json"))
paint = np.asarray(Image.open(f"{d}/{name}_paint_front.png").convert("RGB")).astype(np.float32)
vis = np.asarray(Image.open(f"{d}/{name}_facevis_front.png").convert("L")) > 127
N, S = cam["size"], cam["ortho"]
cx, cz = cam["center"][0], cam["center"][2]
lo_z, h = cam["lo"][2], cam["height"]
ys, xs = np.where(vis)
# 얼굴 네모: 보이는 얼굴판 상자를 정사각형으로 (조금 여유)
x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
side = int(max(x1 - x0, y1 - y0) * 1.04)
mx, my = (x0 + x1) / 2, (y0 + y1) / 2
bx0, by0 = int(mx - side / 2), int(my - side / 2)
crop = paint[by0:by0 + side, bx0:bx0 + side]
cvis = vis[by0:by0 + side, bx0:bx0 + side]
# 피부색 = 보이는 얼굴판의 밝은 쪽 중앙값, 그와 다른 곳 = 눈·눈썹·입 (흰자는 눈 안 구멍 메우기로)
skin = np.median(crop[cvis][crop[cvis].mean(1) > np.percentile(crop[cvis].mean(1), 40)], axis=0)
diff = np.abs(crop - skin).sum(2)
feat = (diff > 60) & cvis
feat = ndimage.binary_opening(feat, iterations=1)
feat = ndimage.binary_fill_holes(ndimage.binary_closing(feat, iterations=2)) & cvis
lab, n = ndimage.label(feat)
sizes = ndimage.sum(feat, lab, range(1, n + 1))
keep = np.isin(lab, [i + 1 for i, sz in enumerate(sizes) if sz >= 12])
alpha = ndimage.gaussian_filter(keep.astype(np.float32), 0.7)
alpha = np.clip(alpha * 1.6, 0, 1) * cvis
rgba = np.dstack([crop, alpha * 255]).astype(np.uint8)
Image.fromarray(rgba).resize((512, 512), Image.LANCZOS).save(out_png)
# 픽셀 → 모델(키 1.0·바닥 0) 좌표
def px2model(px, py):
	x = cx + (px / N - 0.5) * S
	z = cz - (py / N - 0.5) * S
	return x / h, (z - lo_z) / h
cxn, czn = px2model(mx, my)
size_n = side / N * S / h
json.dump({"center": [round(cxn, 5), round(czn, 5)], "size": round(size_n, 5), "skin": [int(v) for v in skin]},
	open(out_json, "w"), indent=1)
print("face", out_png, "center", round(cxn, 4), round(czn, 4), "size", round(size_n, 4), "skin", skin.astype(int), "blobs", int(keep.max() and n))
