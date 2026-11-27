"""2.5D 합성 시안: 배경 사진·게임 스크린샷 위에 기숙생 전신 일러스트를 '그 공간에 서 있는 종이인형'처럼 놓는다. 3D 아님.

python tools/dev/kv_mock2.py 배경폴더 캐릭터폴더 출력폴더
- 발 위치(바닥)와 원근으로 크기를 정함 · 발밑 접지 그림자 + 바닥에 눕는 그림자 · 주변 밝기·색 맞추기 · 가장자리 빛 번짐(라이트 랩)
  · 먼 인물은 흐림·옅은 안개 · 마지막에 화면 전체 같은 색 보정·입자로 묶음
- 밤: 낮 사진이면 푸르게 어둡게 + 손전등 원(사실풍), 원래 밤 스크린샷이면 그대로 + 손전등 살짝
- 장면 표 SCENES: (배경, 밤으로 바꿀지, 손전등 중심, 인물 목록[(이름, 발 x, 발 y, 키(화면 비율), 그림자 방향, 흐림)])
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageEnhance, ImageFilter

W, H = 1920, 1080

SCENES = {
	# 데포르메 느낌(게임 스크린샷, 참고용)
	"deform_day_classroom": ("d_banban", False, None, [("umbrella", 0.62, 0.66, 0.30, 1, 2.0), ("axolotl", 0.30, 0.96, 0.66, 1, 0.0)]),
	"deform_day_room": ("d_hn2", False, None, [("tvhead", 0.27, 0.93, 0.62, -1, 0.0)]),
	"deform_night_kitchen": ("d_ln2", False, (0.30, 0.55), [("zombie", 0.28, 0.93, 0.62, 1, 0.0)]),
	"deform_night_room": ("d_bendy", False, (0.62, 0.50), [("dokkaebi", 0.62, 0.95, 0.64, -1, 0.0)]),
	# 극사실(사진·실사 게임)
	"real_day_corridor": ("r_room404_0", False, None, [("tvhead", 0.60, 0.70, 0.27, 1, 2.5), ("jangsanbeom", 0.27, 0.97, 0.66, 1, 0.0)]),
	"real_day_dormroom": ("r_dormroom", False, None, [("axolotl", 0.60, 1.04, 0.80, -1, 0.0)]),
	"real_night_door": ("r_room404_5", True, (0.30, 0.48), [("umbrella", 0.29, 0.94, 0.66, 1, 0.0)]),
	"real_night_lockers": ("r_locker", True, (0.25, 0.50), [("jangsanbeom", 0.58, 0.66, 0.22, 1, 2.5), ("zombie", 0.24, 0.95, 0.62, 1, 0.0)]),
}


def paper(ch: Image.Image, border: int = 5) -> Image.Image:
	a = ch.split()[3].point(lambda v: 255 if v > 90 else 0)
	big = a.filter(ImageFilter.MaxFilter(border * 2 + 1)).filter(ImageFilter.GaussianBlur(0.8)).point(lambda v: 255 if v > 128 else 0)
	out = Image.new("RGBA", ch.size, (250, 248, 242, 0))
	out.putalpha(big)
	out.alpha_composite(ch)
	return out


def luma(a: np.ndarray) -> np.ndarray:
	return a[..., 0] * 0.299 + a[..., 1] * 0.587 + a[..., 2] * 0.114


def place(canvas: np.ndarray, bg: np.ndarray, ch: Image.Image, fx: float, fy: float, hfrac: float, sdir: int, blur: float) -> None:
	box = ch.split()[3].getbbox()
	ch = ch.crop(box)
	h = int(H * hfrac)
	w = max(1, int(ch.width * h / ch.height))
	c = ch.resize((w, h), Image.LANCZOS)
	x0 = int(W * fx - w / 2)
	y0 = int(H * fy - h)
	# 주변 배경 밝기·색
	px0, px1 = max(0, x0 - w // 2), min(W, x0 + w + w // 2)
	py0, py1 = max(0, y0), min(H, y0 + h)
	patch = bg[py0:py1, px0:px1].reshape(-1, 3)
	pm = patch.mean(axis=0)
	ca = np.asarray(c, np.float32)
	alpha = ca[..., 3:4] / 255.0
	rgb = ca[..., :3]
	cl = (luma(rgb) * alpha[..., 0]).sum() / max(alpha.sum(), 1)
	scale = np.clip((luma(pm[None])[0] / max(cl, 1)) ** 0.45, 0.35, 1.1)
	tint = pm / max(pm.mean(), 1)
	rgb = rgb * scale * (0.8 + 0.2 * tint)
	# 바닥에 눕는 그림자 (실루엣을 납작하게 기울여)
	sh_h = max(2, int(h * 0.22))
	sil = c.split()[3].resize((w, sh_h))
	shear = sdir * 0.9
	sil = sil.transform((w + int(abs(shear) * sh_h) + 2, sh_h), Image.AFFINE, (1, shear, -max(0, shear) * sh_h if shear > 0 else 0, 0, 1, 0), resample=Image.BILINEAR)
	sil = sil.transpose(Image.FLIP_TOP_BOTTOM).filter(ImageFilter.GaussianBlur(6 + h * 0.01))
	s = np.asarray(sil, np.float32) / 255.0 * 0.32
	sx = x0 + (0 if sdir > 0 else -(sil.width - w))
	_mul(canvas, s, sx, int(H * fy) - 2, 0.0)
	# 발밑 접지 그림자
	ew, eh = int(w * 0.55), max(4, int(h * 0.045))
	ell = Image.new("L", (ew * 2, eh * 4), 0)
	from PIL import ImageDraw
	ImageDraw.Draw(ell).ellipse((ew // 2, eh, ew // 2 + ew, eh + eh * 2), fill=255)
	ell = ell.filter(ImageFilter.GaussianBlur(eh * 0.8))
	_mul(canvas, np.asarray(ell, np.float32) / 255.0 * 0.55, int(W * fx - ew), int(H * fy - eh * 2), 0.0)
	# 가장자리 빛 번짐
	soft = Image.fromarray((alpha[..., 0] * 255).astype(np.uint8))
	inner = soft.filter(ImageFilter.MinFilter(7)).filter(ImageFilter.GaussianBlur(4))
	edge = np.clip((np.asarray(soft, np.float32) - np.asarray(inner, np.float32)) / 255.0, 0, 1)[..., None]
	bgblur = np.asarray(Image.fromarray(bg.astype(np.uint8)).filter(ImageFilter.GaussianBlur(25)), np.float32)
	region = _crop(bgblur, x0, y0, w, h)
	if region is not None:
		rgb = rgb * (1 - edge * 0.4) + region * edge * 0.4
	img = Image.fromarray(np.dstack([rgb.clip(0, 255), alpha * 255]).astype(np.uint8), "RGBA")
	if blur > 0:
		img = img.filter(ImageFilter.GaussianBlur(blur))
	_over(canvas, np.asarray(img, np.float32), x0, y0, haze=0.18 if blur > 0 else 0.0, haze_col=pm)


def _crop(a: np.ndarray, x: int, y: int, w: int, h: int):
	out = np.zeros((h, w, 3), np.float32)
	sx0, sy0 = max(0, x), max(0, y)
	sx1, sy1 = min(W, x + w), min(H, y + h)
	if sx1 <= sx0 or sy1 <= sy0:
		return None
	out[sy0 - y:sy1 - y, sx0 - x:sx1 - x] = a[sy0:sy1, sx0:sx1]
	return out


def _mul(canvas: np.ndarray, m: np.ndarray, x: int, y: int, _c: float) -> None:
	h, w = m.shape
	sx0, sy0 = max(0, x), max(0, y)
	sx1, sy1 = min(W, x + w), min(H, y + h)
	if sx1 <= sx0 or sy1 <= sy0:
		return
	mm = m[sy0 - y:sy1 - y, sx0 - x:sx1 - x][..., None]
	canvas[sy0:sy1, sx0:sx1] *= (1 - mm)


def _over(canvas: np.ndarray, rgba: np.ndarray, x: int, y: int, haze: float, haze_col: np.ndarray) -> None:
	h, w = rgba.shape[:2]
	sx0, sy0 = max(0, x), max(0, y)
	sx1, sy1 = min(W, x + w), min(H, y + h)
	src = rgba[sy0 - y:sy1 - y, sx0 - x:sx1 - x]
	a = src[..., 3:4] / 255.0
	col = src[..., :3] * (1 - haze) + haze_col * haze
	canvas[sy0:sy1, sx0:sx1] = canvas[sy0:sy1, sx0:sx1] * (1 - a) + col * a


def night(canvas: np.ndarray, center, from_day: bool) -> np.ndarray:
	cx, cy = center
	xx, yy = np.meshgrid(np.linspace(0, 1, W), np.linspace(0, 1, H))
	d = np.sqrt(((xx - cx) * 1.6) ** 2 + (yy - cy) ** 2)
	cone = (np.clip(1.0 - (d - 0.18) / 0.26, 0, 1) ** 1.4)[..., None]
	if from_day:
		gray = canvas.mean(axis=2, keepdims=True)
		dark = (canvas * 0.45 + gray * 0.55) * np.array([0.55, 0.68, 1.0]) * 0.28
		lit = canvas * np.array([1.05, 0.98, 0.86])
		return dark * (1 - cone) + lit * cone
	return canvas * (0.75 + 0.45 * cone)


def finish(canvas: np.ndarray, seed: int) -> np.ndarray:
	xx, yy = np.meshgrid(np.linspace(-1, 1, W), np.linspace(-1, 1, H))
	canvas = canvas * (1 - 0.22 * np.clip(xx ** 2 * 0.6 + yy ** 2 * 0.8, 0, 1))[..., None]
	canvas = canvas + np.random.default_rng(seed).normal(0, 3.5, canvas.shape)
	return canvas


def main() -> None:
	bgd, chd, outd = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
	outd.mkdir(parents=True, exist_ok=True)
	chars = {p.stem: paper(Image.open(p).convert("RGBA")) for p in chd.glob("*.png")}
	for i, (name, (bgname, to_night, light, cast)) in enumerate(SCENES.items()):
		bgimg = Image.open(bgd / f"{bgname}.jpg").convert("RGB")
		# 화면 비율 맞춰 자르기
		r = bgimg.width / bgimg.height
		if r > W / H:
			nw = int(bgimg.height * W / H)
			bgimg = bgimg.crop(((bgimg.width - nw) // 2, 0, (bgimg.width - nw) // 2 + nw, bgimg.height))
		else:
			nh = int(bgimg.width * H / W)
			bgimg = bgimg.crop((0, (bgimg.height - nh) // 2, bgimg.width, (bgimg.height - nh) // 2 + nh))
		bg = np.asarray(bgimg.resize((W, H), Image.LANCZOS), np.float32)
		canvas = bg.copy()
		for ch, fx, fy, hf, sdir, blur in sorted(cast, key=lambda c: c[2]):  # 먼 것부터
			place(canvas, bg, chars[ch], fx, fy, hf, sdir, blur)
		if light is not None:
			canvas = night(canvas, light, to_night)
		canvas = finish(canvas, i)
		Image.fromarray(canvas.clip(0, 255).astype(np.uint8)).save(outd / f"{name}.jpg", quality=90)
		print(name)


if __name__ == "__main__":
	main()
