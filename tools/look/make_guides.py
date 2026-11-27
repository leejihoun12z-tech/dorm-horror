"""look_spaces.gd 결과(clay·depth·normal) → ComfyUI ControlNet 입력 그림으로 정리한다.

python tools/look/make_guides.py 렌더폴더 tools/look/guides
- depth.png : 깊이를 그림마다 1~99% 범위로 늘림 (가까울수록 흰색)
- lines.png : 깊이가 크게 튀는 곳 + 면 방향이 바뀌는 곳 = 흰 선 / 검은 바탕 (ControlNet canny·lineart 입력)
- clay.png  : 그대로 복사 (사람이 보는 구도 확인용, img2img 바탕으로도 씀)
- guides_sheet.jpg : 4곳 × 3종 한 장
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

SPACES = ["corridor", "corridor_b", "room", "room_b", "office", "stairs", "laundry", "lounge"]


def depth(p: Path) -> Image.Image:
	a = np.asarray(Image.open(p).convert("L"), np.float32)
	lo, hi = np.percentile(a, 1), np.percentile(a, 99.5)
	a = np.clip((a - lo) / max(hi - lo, 1), 0, 1)
	return Image.fromarray((a * 255).astype(np.uint8))


def lines(dp: Path, np_: Path) -> Image.Image:
	d = np.asarray(Image.open(dp).convert("L"), np.float32) / 255.0
	n = np.asarray(Image.open(np_).convert("RGB"), np.float32) / 255.0
	def grad(x: np.ndarray) -> np.ndarray:
		gx = np.abs(np.diff(x, axis=1, append=x[:, -1:]))
		gy = np.abs(np.diff(x, axis=0, append=x[-1:, :]))
		return np.maximum(gx, gy)
	gd = grad(d) / np.maximum(d, 0.05)  # 먼 곳도 같은 비율로
	gn = sum(grad(n[..., c]) for c in range(3))
	e = ((gd > 0.04) | (gn > 0.18)).astype(np.uint8) * 255
	img = Image.fromarray(e).filter(ImageFilter.MaxFilter(3))
	return img


def main() -> None:
	src, out = Path(sys.argv[1]), Path(sys.argv[2])
	out.mkdir(parents=True, exist_ok=True)
	tiles = []
	for sp in SPACES:
		c = Image.open(src / f"{sp}_clay.png").convert("RGB")
		c.save(out / f"{sp}_clay.png")
		dimg = depth(src / f"{sp}_depth.png")
		dimg.save(out / f"{sp}_depth.png")
		limg = lines(src / f"{sp}_depth.png", src / f"{sp}_normal.png")
		limg.save(out / f"{sp}_lines.png")
		tiles.append([c, dimg.convert("RGB"), limg.convert("RGB")])
	w, h = 448, 256
	sheet = Image.new("RGB", (3 * w, len(tiles) * h))
	for i, row in enumerate(tiles):
		for j, im in enumerate(row):
			sheet.paste(im.resize((w, h)), (j * w, i * h))
	sheet.save(out / "guides_sheet.jpg", quality=85)
	print("ok", out)


if __name__ == "__main__":
	main()
