"""GPT가 칠한 3칸 그림을 회색 렌더 실루엣에 맞춰 1024 칸 3장으로 되돌리고, 맞는 정도(IoU)를 잰다.

실행: python tools/char/fit_paint.py <폴더> <이름> <GPT그림.png>
GPT는 그림 비율·크기를 조금 바꾸므로, 칸마다 '그림 속 캐릭터 상자 ↔ 실루엣 상자'로 크기·위치를 맞춘다.
출력: <이름>_paint_front/right/back.png (Tripo에 넣을 그림) + 맞춤 확인 그림 <이름>_fit_check.png
"""
import sys

import numpy as np
from PIL import Image, ImageFilter

d, name, src = sys.argv[1], sys.argv[2], sys.argv[3]
img = Image.open(src).convert("RGB")
W, H = img.size
cw = W / 3
checks = []
for i, k in enumerate(("front", "right", "back")):
	cell = img.crop((round(i * cw), 0, round((i + 1) * cw), H))
	a = np.asarray(cell).astype(int)
	fg = a.min(2) < 235
	ys, xs = np.where(fg)
	m = np.asarray(Image.open(f"{d}/{name}_mask_{k}.png").convert("L")) > 127
	my, mx = np.where(m)
	# 세로(키)로 크기, 가운데·바닥으로 위치
	s0 = (my.max() - my.min()) / (ys.max() - ys.min())
	ox0 = (mx.min() + mx.max()) / 2 - (xs.min() + xs.max()) / 2 * s0
	oy0 = my.max() - ys.max() * s0
	# 상자 맞춤에서 출발해 크기 ±6%·위치 ±24px 안에서 실루엣 겹침(IoU)이 가장 큰 값 (작은 그림으로 찾기)
	fgi = Image.fromarray((fg * 255).astype(np.uint8))
	q = 4
	mq = np.asarray(Image.fromarray((m * 255).astype(np.uint8)).resize((256, 256), Image.BILINEAR)) > 127
	best = None
	for ds in np.linspace(-0.06, 0.06, 13):
		s = s0 * (1 + ds)
		g = fgi.resize((max(1, round(cell.width * s / q)), max(1, round(cell.height * s / q))), Image.BILINEAR)
		for dx in range(-6, 7):
			for dy in range(-6, 7):
				cx = (mx.min() + mx.max()) / 2 - (xs.min() + xs.max()) / 2 * s
				cy = my.max() - ys.max() * s
				cv = Image.new("L", (256, 256), 0)
				cv.paste(g, (round(cx / q) + dx, round(cy / q) + dy))
				f2 = np.asarray(cv) > 127
				iou = (f2 & mq).sum() / max(1, (f2 | mq).sum())
				if best is None or iou > best[0]:
					best = (iou, s, cx + dx * q, cy + dy * q)
	_, s, ox, oy = best
	big = cell.resize((round(cell.width * s), round(cell.height * s)), Image.LANCZOS)
	out = Image.new("RGB", (1024, 1024), "white")
	out.paste(big, (round(ox), round(oy)))
	out.save(f"{d}/{name}_paint_{k}.png")
	f2 = np.asarray(out).astype(int).min(2) < 235
	iou = (f2 & m).sum() / (f2 | m).sum()
	print(k, "IoU", round(float(iou), 3), "scale", round(s, 3))
	edge = np.asarray(Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.FIND_EDGES)) > 0
	c = np.asarray(out).copy(); c[edge] = [0, 200, 255]
	checks.append(Image.fromarray(c))
sheet = Image.new("RGB", (3072, 1024), "white")
for i, c in enumerate(checks):
	sheet.paste(c, (i * 1024, 0))
sheet.save(f"{d}/{name}_fit_check.png")
