"""정면·옆·뒤 그림 3장의 흰 바탕을 지워 방향 입간판 시안용으로 만든다.

python tools/dev/make_turnaround_cutouts.py [출력폴더]
- 입력: assets/art_src/char3d/mannequin_deform_20261126/mq_toon_W2(_side|_back).png (1024x1536, 흰 바탕)
- 출력(기본 .screenshots/dir_fx/, git 제외): idle_0.png(정면) · idle_2.png(뒤) · idle_3.png(옆, 오른쪽을 봄)
- 바닥: 테두리에서 이어진 거의 흰 칸만 지운다(셔츠 같은 안쪽 흰색은 남음). 발끝 기준으로 세 장의 높이를 맞춘다.
"""
import sys
from collections import deque
from pathlib import Path

from PIL import Image

SRC = Path("assets/art_src/char3d/mannequin_deform_20261126")
NAMES = {"idle_0": "mq_toon_W2.png", "idle_2": "mq_toon_W2_back.png", "idle_3": "mq_toon_W2_side.png"}


def cut(im: Image.Image, tol: int = 18) -> Image.Image:
	im = im.convert("RGBA")
	w, h = im.size
	px = im.load()
	seen = bytearray(w * h)
	q = deque()
	for x in range(w):
		q.append((x, 0))
		q.append((x, h - 1))
	for y in range(h):
		q.append((0, y))
		q.append((w - 1, y))
	while q:
		x, y = q.popleft()
		i = y * w + x
		if seen[i]:
			continue
		seen[i] = 1
		r, g, b, _ = px[x, y]
		if min(r, g, b) < 255 - tol:
			continue
		px[x, y] = (255, 255, 255, 0)
		for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
			nx, ny = x + dx, y + dy
			if 0 <= nx < w and 0 <= ny < h and not seen[ny * w + nx]:
				q.append((nx, ny))
	return im


def main() -> None:
	out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".screenshots/dir_fx")
	out.mkdir(parents=True, exist_ok=True)
	cuts = {k: cut(Image.open(SRC / v)) for k, v in NAMES.items()}
	# 같은 캔버스(발끝 = 맨 아래, 가운데 정렬): 가장 큰 bbox 기준
	boxes = {k: im.split()[3].getbbox() for k, im in cuts.items()}
	top = min(b[1] for b in boxes.values())
	width = max(b[2] - b[0] for b in boxes.values()) + 40
	for k, im in cuts.items():
		b = boxes[k]
		canvas = Image.new("RGBA", (width, b[3] - top + 4), (0, 0, 0, 0))
		piece = im.crop(b)
		canvas.alpha_composite(piece, ((width - piece.width) // 2, b[1] - top))
		canvas.save(out / f"{k}.png")
		print(k, canvas.size)


if __name__ == "__main__":
	main()
