"""밤 추격 연출 시안용 임시 텍스처 (그림 대역).

python tools/dev/make_signature_mock_tex.py [출력폴더]
- 입력: assets/characters/mannequin/illust_cutout_test.png (마네킹 데포르메 정면, 462x920)
- 출력(기본 .screenshots/mock_fx/, git 제외):
  day.png     등신대 느낌: 흰 테두리 두른 원본
  shadow.png  그림자 전용: 목이 늘어나고 팔이 바닥까지 내려온 실루엣
  true.png    "진짜 모습": 어두운 몸 + 흰 선 + 뚫린 눈 + 귀까지 찢어진 입선
  s1.png      작화 붕괴 1: 색 단순화 · 선 흔들림
  s2.png      작화 붕괴 2: 종이 위 연필 선화만
  s3.png      작화 붕괴 3: 붉은 낙서 · 늘어난 몸
진짜 그림은 아트 채팅에서 그린다. 이 파일은 "어떤 느낌인지" 보는 대역일 뿐이다.
"""
import random
import sys
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageOps

SRC = Path("assets/characters/mannequin/illust_cutout_test.png")
EYES = [(200, 207), (272, 207)]  # 원본 좌표
MOUTH = (234, 250)


def edges(im: Image.Image, thr: int = 28) -> Image.Image:
	g = ImageOps.grayscale(im.convert("RGB"))
	e = g.filter(ImageFilter.FIND_EDGES).point(lambda v: 255 if v > thr else 0)
	alpha = im.split()[3]
	outline = alpha.filter(ImageFilter.MaxFilter(3))
	outline = ImageChops.subtract(outline, alpha.filter(ImageFilter.MinFilter(3)))
	inside = alpha.point(lambda v: 255 if v > 100 else 0).filter(ImageFilter.MinFilter(3))
	return ImageChops.lighter(ImageChops.multiply(e, inside), outline)


def white_border(im: Image.Image, px: int = 9) -> Image.Image:
	a = im.split()[3].point(lambda v: 255 if v > 100 else 0)
	big = a.filter(ImageFilter.MaxFilter(px * 2 + 1))
	out = Image.new("RGBA", im.size, (250, 248, 244, 0))
	out.putalpha(big)
	out.alpha_composite(im)
	return out


def jitter(mask: Image.Image, amp: int, seed: int) -> Image.Image:
	rnd = random.Random(seed)
	w, h = mask.size
	out = Image.new("L", mask.size, 0)
	band = 6
	for y in range(0, h, band):
		dx = rnd.randint(-amp, amp)
		out.paste(mask.crop((0, y, w, y + band)), (dx, y))
	return out


def main() -> None:
	out_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".screenshots/mock_fx")
	out_dir.mkdir(parents=True, exist_ok=True)
	src = Image.open(SRC).convert("RGBA")
	w, h = src.size
	alpha = src.split()[3]
	white_border(src).save(out_dir / "day.png")

	# 그림자: 목 늘이기 + 바닥까지 내려오는 긴 팔
	neck_y, lift = 330, 260
	sh = Image.new("L", (w + 160, h + lift), 0)
	ox = 80
	sh.paste(alpha.crop((0, 0, w, neck_y)), (ox, 0))
	sh.paste(alpha.crop((0, neck_y, w, h)), (ox, neck_y + lift))
	d = ImageDraw.Draw(sh)
	d.rectangle((ox + 222, neck_y - 20, ox + 246, neck_y + lift + 20), fill=255)
	for sx, ex in ((ox + 110, ox - 60), (ox + 352, ox + w + 60)):
		d.line((sx, neck_y + lift + 60, ex, h + lift - 20), fill=255, width=16)
		for k in range(4):
			d.line((ex, h + lift - 20, ex + (k - 1.5) * 18, h + lift - 2), fill=255, width=5)
	img = Image.new("RGBA", sh.size, (0, 0, 0, 0))
	img.putalpha(sh.point(lambda v: 255 if v > 100 else 0))
	img.save(out_dir / "shadow.png")

	# 진짜 모습: 어두운 몸 + 흰 선 + 뚫린 눈 + 찢어진 입
	e = edges(src)
	tru = Image.new("RGBA", (w, h), (18, 14, 20, 255))
	line = Image.new("RGBA", (w, h), (235, 228, 214, 255))
	tru.paste(line, mask=e)
	d = ImageDraw.Draw(tru)
	for ex, ey in EYES:
		d.ellipse((ex - 22, ey - 26, ex + 22, ey + 30), fill=(0, 0, 0, 255))
		d.ellipse((ex - 4, ey - 2, ex + 4, ey + 6), fill=(255, 40, 40, 255))
	mx, my = MOUTH
	d.arc((mx - 70, my - 60, mx + 70, my + 24), 15, 165, fill=(255, 50, 50, 255), width=4)
	tru.putalpha(alpha)
	tru.save(out_dir / "true.png")

	# 작화 붕괴 1: 색 줄이기 + 테두리 흔들림
	s1 = ImageOps.posterize(src.convert("RGB"), 2).convert("RGBA")
	s1 = Image.blend(s1, src, 0.35)
	s1.putalpha(jitter(alpha, 4, 1))
	s1.save(out_dir / "s1.png")

	# 작화 붕괴 2: 종이 위 연필 선
	paper = Image.new("RGBA", (w, h), (238, 232, 220, 255))
	pencil = Image.new("RGBA", (w, h), (60, 55, 60, 255))
	paper.paste(pencil, mask=jitter(e, 2, 2))
	d = ImageDraw.Draw(paper)
	for ex, ey in EYES:
		d.ellipse((ex - 16, ey - 18, ex + 16, ey + 20), outline=(60, 55, 60, 255), width=2)
	paper.putalpha(jitter(alpha, 7, 3))
	paper.save(out_dir / "s2.png")

	# 작화 붕괴 3: 붉은 낙서 · 몸이 위로 늘어남
	tall = h + 220
	s3 = Image.new("RGBA", (w, tall), (0, 0, 0, 0))
	stretched_e = e.resize((w, tall))
	stretched_a = alpha.resize((w, tall))
	body = Image.new("RGBA", (w, tall), (10, 6, 8, 235))
	body.putalpha(jitter(stretched_a, 12, 4).point(lambda v: 225 if v > 100 else 0))
	s3.alpha_composite(body)
	red = Image.new("RGBA", (w, tall), (230, 30, 35, 255))
	s3.paste(red, mask=jitter(stretched_e.filter(ImageFilter.MaxFilter(3)), 8, 5))
	rnd = random.Random(6)
	d = ImageDraw.Draw(s3)
	for _ in range(40):
		x0, y0 = rnd.randint(60, w - 60), rnd.randint(40, tall - 40)
		d.line((x0, y0, x0 + rnd.randint(-80, 80), y0 + rnd.randint(-80, 80)), fill=(230, 30, 35, 255), width=2)
	for ex, ey in EYES:
		yy = int(ey * tall / h)
		d.ellipse((ex - 26, yy - 30, ex + 26, yy + 34), fill=(0, 0, 0, 255))
		d.ellipse((ex - 5, yy, ex + 5, yy + 10), fill=(255, 255, 255, 255))
	s3.save(out_dir / "s3.png")
	print("ok", out_dir)


if __name__ == "__main__":
	main()
