"""시트 B(고친 판)의 한 부위(금색으로 고름)를 시트 A(원본)의 같은 자리에 옮겨 붙인다. 원본의 옛 부위는 먼저 지움 (GPT가 다시 그리며 생긴 납작해짐 등을 피하려고, 바꿀 부위만 옮김).

실행: python tools/char/paste_part.py <원본 시트> <고친 시트> <출력> <원본 상자들> <고친 상자들>
  상자 = "x0,y0,x1,y1;..." (칸마다 하나, 같은 순서). 고친 상자 안에서 금색(리본) 픽셀만 오려 원본 상자 가운데에 붙임.
  크기는 두 시트의 캐릭터 키 비율로 맞춘다.
"""
import sys

import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage

src, fix, out, boxes_a, boxes_b = sys.argv[1:6]
A = Image.open(src).convert("RGB")
B = Image.open(fix).convert("RGB")


def figure_h(im):
	a = np.asarray(im).astype(int)
	k = im.width // 3
	ys = np.where((a[:, :k].min(2) < 230).any(1))[0]
	return ys.max() - ys.min()


def gold_mask(img):
	c = np.asarray(img.convert("HSV")).astype(int)
	h, sat, val = c[..., 0], c[..., 1], c[..., 2]
	return (h > 15) & (h < 45) & (sat > 90) & (val > 110)


s = figure_h(A) / figure_h(B)
# 먼저 원본의 옛 부위를 지움: 상자 안 금색(+2칸)을 가장 가까운 다른 색으로 채움
arr = np.asarray(A).copy()
for ba in boxes_a.split(";"):
	ax0, ay0, ax1, ay1 = map(int, ba.split(","))
	x0, y0, x1, y1 = ax0 - 8, ay0 - 8, ax1 + 8, ay1 + 8
	sub = arr[y0:y1, x0:x1]
	cc = np.asarray(Image.fromarray(sub).convert("HSV")).astype(int)
	old = (cc[..., 0] > 8) & (cc[..., 0] < 50) & (cc[..., 1] > 60) & (cc[..., 2] > 60)  # 금색 + 갈색 테두리
	m = ndimage.binary_dilation(old, iterations=4)
	_, (iy, ix) = ndimage.distance_transform_edt(m, return_indices=True)
	arr[y0:y1, x0:x1] = sub[iy, ix]
res = Image.fromarray(arr)
for ba, bb in zip(boxes_a.split(";"), boxes_b.split(";")):
	ax0, ay0, ax1, ay1 = map(int, ba.split(","))
	bx0, by0, bx1, by1 = map(int, bb.split(","))
	pad = 6
	crop = B.crop((bx0 - pad, by0 - pad, bx1 + pad, by1 + pad))
	mask = gold_mask(crop)  # 금색·주황 그늘까지
	mask = ndimage.binary_closing(mask, iterations=2)
	mask = ndimage.binary_fill_holes(mask)
	lab, n = ndimage.label(mask)
	if n:
		sizes = ndimage.sum(mask, lab, range(1, n + 1))
		mask = lab == (int(np.argmax(sizes)) + 1)
	mask = ndimage.binary_dilation(mask, iterations=1)  # 바깥 어두운 테두리 1칸
	alpha = Image.fromarray((mask * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.6))
	nw, nh = round(crop.width * s), round(crop.height * s)
	crop = crop.resize((nw, nh), Image.LANCZOS)
	alpha = alpha.resize((nw, nh), Image.LANCZOS)
	cx, cy = (ax0 + ax1) / 2, (ay0 + ay1) / 2
	res.paste(crop, (round(cx - nw / 2), round(cy - nh / 2)), alpha)
res.save(out)
print("saved", out, "scale", round(s, 3))
