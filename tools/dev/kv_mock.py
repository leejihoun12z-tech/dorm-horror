"""2D 키비주얼 시안: 진짜 배경 사진(CC0) 위에 기숙생 일러스트를 종이인형처럼 올린다. 3D 아님.

python tools/dev/kv_mock.py 배경폴더 캐릭터폴더 출력폴더
- 배경: Poly Haven 파노라마(CC0)에서 잘라 낸 원근 사진 locker.jpg(사물함 복도) · room.jpg(침대 방)
- 캐릭터: 바탕 지운 PNG (mannequin·tvhead·jangsanbeom·dokkaebi)
- 스타일: real(사진 그대로) · mini(미니어처 사진 처리 = 데포르메 느낌 근사) × day · night(같은 사진을 밤으로 + 손전등)
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageEnhance, ImageFilter

W, H = 1920, 1080
SCENES = {
	"locker": [("mannequin", 0.20, 0.80), ("jangsanbeom", 0.80, 0.72)],
	"room": [("tvhead", 0.19, 0.78), ("dokkaebi", 0.82, 0.80)],
}
LIGHT = {"locker": (0.22, 0.45), "room": (0.20, 0.45)}  # 밤 손전등 중심 (가로·세로 비율)


def paper(ch: Image.Image, border: int = 9) -> Image.Image:
	a = ch.split()[3].point(lambda v: 255 if v > 90 else 0)
	big = a.filter(ImageFilter.MaxFilter(border * 2 + 1)).filter(ImageFilter.GaussianBlur(1.0)).point(lambda v: 255 if v > 128 else 0)
	out = Image.new("RGBA", ch.size, (252, 250, 245, 0))
	out.putalpha(big)
	out.alpha_composite(ch)
	return out


def place(bg: Image.Image, ch: Image.Image, cx: float, hfrac: float, tint: np.ndarray, shadow: bool) -> tuple:
	h = int(H * hfrac)
	w = int(ch.width * h / ch.height)
	c = ch.resize((w, h), Image.LANCZOS)
	x = int(W * cx - w / 2)
	y = H - h + int(H * 0.06)  # 아래는 화면 밖으로 살짝 (가까이 선 인물)
	if shadow:
		sh = Image.new("RGBA", c.size, (0, 0, 0, 0))
		sh.putalpha(c.split()[3].point(lambda v: int(v * 0.33)))
		sh = sh.filter(ImageFilter.GaussianBlur(18))
		bg.alpha_composite(sh, (x + 28, y + 14))
	arr = np.asarray(c).astype(np.float32)
	arr[..., :3] = arr[..., :3] * (0.85 + 0.15 * tint)  # 배경 색 15% 섞기
	c = Image.fromarray(arr.clip(0, 255).astype(np.uint8), "RGBA")
	bg.alpha_composite(c, (x, y))
	return (x, y, w, h)


def miniature(im: Image.Image) -> Image.Image:
	m = im.filter(ImageFilter.MedianFilter(9)).filter(ImageFilter.SMOOTH_MORE).filter(ImageFilter.SMOOTH_MORE)
	m = ImageEnhance.Color(m).enhance(1.75)
	m = ImageEnhance.Contrast(m).enhance(1.12)
	m = ImageEnhance.Brightness(m).enhance(1.06)
	blur = m.filter(ImageFilter.GaussianBlur(14))
	yy = np.linspace(0, 1, H)[:, None]
	k = np.clip((0.42 - yy) / 0.20, 0, 1) + np.clip((yy - 0.72) / 0.14, 0, 1)  # 위·아래 흐림 (틸트시프트)
	k = np.clip(k, 0, 1)[..., None]
	a = np.asarray(m, np.float32) * (1 - k) + np.asarray(blur, np.float32) * k
	return Image.fromarray(a.clip(0, 255).astype(np.uint8))


def night_map(scene: str) -> np.ndarray:
	cx, cy = LIGHT[scene]
	xx, yy = np.meshgrid(np.linspace(0, 1, W), np.linspace(0, 1, H))
	d = np.sqrt(((xx - cx) * 1.6) ** 2 + (yy - cy) ** 2)
	cone = np.clip(1.0 - (d - 0.20) / 0.26, 0, 1) ** 1.4
	return cone


def to_night(arr: np.ndarray, cone: np.ndarray, gritty: bool) -> np.ndarray:
	gray = arr.mean(axis=2, keepdims=True)
	dark = (arr * 0.45 + gray * 0.55) * np.array([0.55, 0.68, 1.0]) * 0.30
	lit = arr * np.array([1.05, 0.98, 0.86]) * 0.95
	out = dark * (1 - cone[..., None]) + lit * cone[..., None]
	if gritty:
		out += np.random.default_rng(1).normal(0, 7, out.shape)
	return out


def main() -> None:
	bgd, chd, outd = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
	outd.mkdir(parents=True, exist_ok=True)
	chars = {p.stem: paper(Image.open(p).convert("RGBA")) for p in chd.glob("*.png")}
	for scene, cast in SCENES.items():
		base = Image.open(bgd / f"{scene}.jpg").convert("RGB").resize((W, H))
		for style in ("real", "mini"):
			bgimg = base if style == "real" else miniature(base)
			tint = np.asarray(bgimg.resize((1, 1), Image.BOX), np.float32)[0, 0] / 255.0
			tint = tint / max(tint.max(), 1e-3)
			for t in ("day", "night"):
				canvas = bgimg.convert("RGBA")
				for name, cx, hf in cast:
					place(canvas, chars[name], cx, hf, tint, shadow=(t == "day"))
				arr = np.asarray(canvas.convert("RGB"), np.float32)
				if t == "night":
					arr = to_night(arr, night_map(scene), gritty=(style == "real"))
				# 비네트
				xx, yy = np.meshgrid(np.linspace(-1, 1, W), np.linspace(-1, 1, H))
				vig = 1 - 0.28 * np.clip(xx ** 2 * 0.6 + yy ** 2 * 0.8, 0, 1)
				arr *= vig[..., None]
				Image.fromarray(arr.clip(0, 255).astype(np.uint8)).save(outd / f"{scene}_{style}_{t}.jpg", quality=90)
				print(scene, style, t)


if __name__ == "__main__":
	main()
