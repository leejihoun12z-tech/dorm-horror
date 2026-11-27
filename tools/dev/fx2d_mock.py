"""2D 공포 연출 시안 영상: 사진 배경 위 종이인형 카드 한 장에 효과 6가지를 차례로 건다. (vibe-board-20261127.md)

python tools/dev/fx2d_mock.py 배경.jpg 카드.png 출력폴더 [--face=x,y --neck=x,y]   (카드 픽셀 좌표)
① 평소(숨쉬기) ② 지지직 ③ 검은 낙서 ④ 선 떨림·작화 퇴화 ⑤ 손전등에 종이 비침(뒷면의 진짜) ⑥ 종이 관절 애니 + 제4의 벽 자막
결과: fx2d.mp4 (24fps) + fx2d_sheet.jpg. ffmpeg 필요. 효과는 전부 시안용 근사이며 게임에서는 셰이더·프레임 그림으로 만든다.
"""
import math
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1280, 720
FPS = 24
SEG = 2.6  # 효과 하나 길이(초)
FONT = "/usr/share/fonts/opentype/unifont/unifont.otf"
LABELS = ["① 평소 — 정지 그림, 숨쉬기만", "② 지지직 — 신호가 깨지듯", "③ 검은 낙서 — 볼펜으로 마구 그은 선",
	"④ 선 떨림 → 작화 퇴화 (완성 → 선화 → 낙서)", "⑤ 손전등에 종이 비침 — 뒷면의 '진짜'", "⑥ 종이 관절 애니 + 제4의 벽"]


def arg(name: str, default: str) -> str:
	for a in sys.argv:
		if a.startswith(f"--{name}="):
			return a.split("=", 1)[1]
	return default


def paper_card(ch: Image.Image, border: int = 10) -> Image.Image:
	a = ch.split()[3].point(lambda v: 255 if v > 90 else 0)
	big = a.filter(ImageFilter.MaxFilter(border * 2 + 1)).filter(ImageFilter.GaussianBlur(1.2)).point(lambda v: 255 if v > 128 else 0)
	out = Image.new("RGBA", ch.size, (250, 248, 242, 0))
	out.putalpha(big)
	out.alpha_composite(ch)
	return out


def line_art(card: Image.Image, crude: float) -> Image.Image:
	"""XDoG 선화. crude가 클수록 굵고 거친 선."""
	g = card.convert("L")
	s1 = 1.0 + crude * 2.5
	a = np.asarray(g.filter(ImageFilter.GaussianBlur(s1)), np.float32)
	b = np.asarray(g.filter(ImageFilter.GaussianBlur(s1 * 1.6)), np.float32)
	d = a - 0.985 * b
	ink = (d < -1.5 - crude * 2).astype(np.float32)
	arr = np.full((card.height, card.width, 4), 250, np.uint8)
	arr[..., :3] = (250 - ink[..., None] * 235).astype(np.uint8)
	arr[..., 3] = np.asarray(card.split()[3])
	return Image.fromarray(arr, "RGBA")


def scribble_paths(rng, cx: float, cy: float, r: float, n: int) -> list:
	paths = []
	for _ in range(n):
		x, y = cx + rng.normal(0, r * 0.3), cy + rng.normal(0, r * 0.3)
		ang = rng.uniform(0, math.tau)
		pts = [(x, y)]
		for _ in range(70):
			ang += rng.normal(0, 0.9)
			step = rng.uniform(6, 16)
			x += math.cos(ang) * step
			y += math.sin(ang) * step
			# 얼굴 쪽으로 끌어당김
			x += (cx - x) * 0.06
			y += (cy - y) * 0.06
			pts.append((x, y))
		paths.append(pts)
	return paths


def glitch(img: np.ndarray, rng, amt: float) -> np.ndarray:
	out = img.copy()
	h = img.shape[0]
	for _ in range(int(6 + amt * 14)):
		y0 = rng.integers(0, h - 4)
		hh = rng.integers(2, 26)
		out[y0:y0 + hh] = np.roll(out[y0:y0 + hh], int(rng.normal(0, 40 * amt)), axis=1)
	sh = int(4 + amt * 10)
	out[..., 0] = np.roll(out[..., 0], sh, axis=1)
	out[..., 2] = np.roll(out[..., 2], -sh, axis=1)
	out[::3, :, :3] = (out[::3, :, :3] * 0.8).astype(out.dtype)
	if rng.random() < 0.3:
		y0 = rng.integers(0, h - 40)
		out[y0:y0 + 30, :, :3] = rng.integers(0, 255, (min(30, h - y0), out.shape[1], 3))
	return out


def main() -> None:
	bg_path, card_path, outd = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
	outd.mkdir(parents=True, exist_ok=True)
	fx, fy = (float(v) for v in arg("face", "515,370").split(","))
	nx, ny = (float(v) for v in arg("neck", "500,470").split(","))
	bg = Image.open(bg_path).convert("RGB").resize((W, H))
	bg = Image.fromarray((np.asarray(bg, np.float32) * np.array([0.62, 0.66, 0.78])).astype(np.uint8))
	src = Image.open(card_path).convert("RGBA")
	card = paper_card(src)
	ch = int(H * 0.86)
	k = ch / card.height
	cw = int(card.width * k)
	card = card.resize((cw, ch), Image.LANCZOS)
	fx, fy, nx, ny = fx * k, fy * k, nx * k, ny * k
	cx0, cy0 = int(W * 0.62 - cw / 2), H - ch - 6
	lines = [line_art(card, 0.0), line_art(card, 0.6), line_art(card, 1.2)]
	# 뒷면 그림(종이 비침용): 같은 실루엣을 검게, 큰 눈 여러 개와 입을 낙서로
	back = Image.new("RGBA", card.size, (0, 0, 0, 0))
	sil = card.split()[3].filter(ImageFilter.MaxFilter(9))
	back.paste((30, 10, 14, 255), (0, 0), sil)
	bd = ImageDraw.Draw(back)
	# 뒤집어 붙이므로 좌우를 미리 반대로 잡는다
	ex, ey = cw - fx, fy + 10
	bd.ellipse((ex - 34, ey - 58, ex + 34, ey + 58), fill=(235, 228, 205, 255))  # 세로로 찢어진 큰 외눈
	bd.ellipse((ex - 12, ey - 30, ex + 12, ey + 30), fill=(120, 0, 0, 255))
	bd.ellipse((ex - 5, ey - 14, ex + 5, ey + 14), fill=(5, 0, 0, 255))
	my = fy + 230
	bd.ellipse((ex - 120, my - 40, ex + 120, my + 60), fill=(5, 0, 0, 255))  # 몸통을 가로지르는 입
	for i in range(11):
		tx = ex - 105 + i * 21
		bd.polygon([(tx, my - 30), (tx + 18, my - 30), (tx + 9, my + 8)], fill=(235, 228, 205, 255))
		bd.polygon([(tx, my + 50), (tx + 18, my + 50), (tx + 9, my + 14)], fill=(235, 228, 205, 255))
	back = back.transpose(Image.FLIP_LEFT_RIGHT)  # 뒤에서 비치니 좌우 반전
	scr = scribble_paths(np.random.default_rng(9), fx, fy, 70, 9)
	font = ImageFont.truetype(FONT, 26)
	sub_font = ImageFont.truetype(FONT, 30)
	shadow = Image.new("RGBA", card.size, (0, 0, 0, 0))
	shadow.putalpha(card.split()[3].point(lambda v: int(v * 0.45)))
	shadow = shadow.filter(ImageFilter.GaussianBlur(14))
	nseg = len(LABELS)
	total = int(SEG * FPS) * nseg
	frames_dir = outd / "_frames"
	frames_dir.mkdir(exist_ok=True)
	sheet_frames = {}
	rng = np.random.default_rng(1)
	for f in range(total):
		t = f / FPS
		seg = min(nseg - 1, int(t // SEG))
		u = (t - seg * SEG) / SEG  # 0~1
		frame = bg.copy().convert("RGBA")
		c = card.copy()
		dx, dy, rot = 0, 0, 0.0
		if seg == 0:
			s = 1.0 + 0.006 * math.sin(t * 3.0)
			c = c.resize((cw, int(ch * s)))
			dy = ch - c.height
		elif seg == 1:
			amt = 0.3 + 0.7 * (1 if (f // 3) % 4 == 0 else rng.random() * 0.4)
			if rng.random() < 0.75:
				arr = glitch(np.asarray(c), rng, amt)
				c = Image.fromarray(arr, "RGBA")
				dx = int(rng.normal(0, 6))
		elif seg == 2:
			d = ImageDraw.Draw(c)
			prog = min(1.0, u * 1.4)
			for i, p in enumerate(scr):
				n = int(len(p) * min(1.0, max(0.0, prog * len(scr) - i)))
				if n > 1:
					jit = [(x + rng.normal(0, 0.8), y + rng.normal(0, 0.8)) for x, y in p[:n]]
					d.line(jit, fill=(12, 10, 12, 255), width=4, joint="curve")
			mask = card.split()[3]
			c.putalpha(mask)
		elif seg == 3:
			stage = 0 if u < 0.33 else (1 if u < 0.66 else 2)
			if u < 0.12:
				la = lines[0]
				c = Image.blend(c, la, u / 0.12)
			else:
				c = lines[stage].copy()
			# 2프레임마다 선이 떨림 (boiling)
			if (f // 2) % 3:
				ox, oy = ((f // 2) % 3) - 1, ((f // 5) % 3) - 1
				c = c.transform(c.size, Image.AFFINE, (1, 0.004 * ox, ox, 0.004 * oy, 1, oy), resample=Image.BILINEAR)
		elif seg == 4:
			lx = cx0 + cw * (0.15 + 0.7 * u)
			ly = cy0 + fy + 120 * math.sin(u * 5)
			xx, yy = np.meshgrid(np.arange(cw), np.arange(ch))
			dist = np.sqrt(((xx + cx0 - lx) / 1.0) ** 2 + (yy + cy0 - ly) ** 2)
			light = np.clip(1 - (dist - 110) / 90, 0, 1)
			ca = np.asarray(c, np.float32)
			ba = np.asarray(back, np.float32)
			see = (light * (ba[..., 3] / 255.0) * 0.85)[..., None]
			lit = ca[..., :3] * (0.45 + 0.75 * light[..., None])
			rgb = lit * (1 - see) + (ba[..., :3] * 0.9 + lit * 0.1) * see
			c = Image.fromarray(np.dstack([rgb.clip(0, 255), ca[..., 3]]).astype(np.uint8), "RGBA")
			# 바깥은 어둡게, 손전등 원
			fr = np.asarray(frame, np.float32)
			X, Y = np.meshgrid(np.arange(W), np.arange(H))
			L = np.clip(1 - (np.sqrt((X - lx) ** 2 + (Y - ly) ** 2) - 140) / 160, 0, 1)
			fr[..., :3] *= (0.25 + 0.85 * L)[..., None]
			frame = Image.fromarray(fr.clip(0, 255).astype(np.uint8), "RGBA")
		elif seg == 5:
			# 머리 조각이 할핀 관절에서 끊어지듯 기움 (8fps 리미티드 애니)
			steps = [0, 0, 6, 6, 6, 14, 14, 24, 24, 24, 38, 38, 38, 38, 52, 52]
			a = steps[min(len(steps) - 1, int(u * 20))]
			top = c.crop((0, 0, cw, int(ny)))
			bot = c.crop((0, int(ny) - 4, cw, ch))
			c2 = Image.new("RGBA", c.size, (0, 0, 0, 0))
			c2.alpha_composite(bot, (0, int(ny) - 4))
			top_r = top.rotate(-a, resample=Image.BICUBIC, center=(nx, ny), expand=False)
			c2.alpha_composite(top_r, (0, 0))
			pd = ImageDraw.Draw(c2)
			pd.ellipse((nx - 7, ny - 7, nx + 7, ny + 7), fill=(170, 150, 90, 255), outline=(60, 50, 30, 255), width=2)
			c = c2
		frame.alpha_composite(shadow, (cx0 + dx + 22, cy0 + dy + 10))
		frame.alpha_composite(c, (cx0 + dx, cy0 + dy))
		img = frame.convert("RGB")
		dd = ImageDraw.Draw(img)
		if seg == 5:
			txt = "……사감님. 거기, 화면 앞에 있는 사람 말고."
			n = int(len(txt) * min(1.0, max(0.0, (u - 0.45) * 2.4)))
			if n > 0:
				dd.rectangle((120, H - 150, W - 120, H - 70), fill=(8, 6, 10))
				dd.rectangle((120, H - 150, W - 120, H - 70), outline=(200, 190, 170), width=2)
				dd.text((150, H - 125), txt[:n], font=sub_font, fill=(240, 230, 215))
			if u > 0.85:
				arr = glitch(np.asarray(img).copy(), rng, 1.0)
				img = Image.fromarray(arr)
				dd = ImageDraw.Draw(img)
		lab = LABELS[seg]
		dd.rectangle((0, 0, int(dd.textlength(lab, font=font)) + 24, 40), fill=(0, 0, 0))
		dd.text((12, 7), lab, font=font, fill=(255, 210, 90))
		dd.text((W - 330, H - 30), "시안 · 개발 중 화면 · 배경 사진 CC0", font=ImageFont.truetype(FONT, 18), fill=(200, 200, 200))
		img.save(frames_dir / f"{f:05d}.png")
		if abs(u - 0.7) < 0.5 / (SEG * FPS):
			sheet_frames[seg] = img.copy()
	subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-framerate", str(FPS), "-i", str(frames_dir / "%05d.png"),
		"-vf", "format=yuv420p", "-c:v", "libx264", "-crf", "24", str(outd / "fx2d.mp4")], check=True)
	for p in frames_dir.glob("*.png"):
		p.unlink()
	frames_dir.rmdir()
	sheet = Image.new("RGB", (3 * 640, 2 * 360))
	for i in range(nseg):
		if i in sheet_frames:
			sheet.paste(sheet_frames[i].resize((640, 360)), ((i % 3) * 640, (i // 3) * 360))
	sheet.save(outd / "fx2d_sheet.jpg", quality=86)
	print("done", total, "frames")


if __name__ == "__main__":
	main()
