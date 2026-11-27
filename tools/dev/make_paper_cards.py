"""종이인형 카드 시안용: 바탕 지운 그림에 흰 칼선 테두리를 두른다.

python tools/dev/make_paper_cards.py [입력폴더] [출력폴더]
- 입력(기본 .screenshots/dir_fx/): make_turnaround_cutouts.py 결과 idle_0(앞)·idle_2(뒤)·idle_3(옆)
- 출력(기본 .screenshots/paper_fx/, git 제외): front.png · back.png · pose_side.png(상황 그림 자리 대역)
"""
import sys
from pathlib import Path

from PIL import Image, ImageFilter

BORDER = 14


def card(im: Image.Image) -> Image.Image:
	pad = BORDER + 4
	base = Image.new("RGBA", (im.width + pad * 2, im.height + pad * 2), (0, 0, 0, 0))
	base.alpha_composite(im, (pad, pad))
	a = base.split()[3].point(lambda v: 255 if v > 100 else 0)
	big = a.filter(ImageFilter.MaxFilter(BORDER * 2 + 1)).filter(ImageFilter.GaussianBlur(1.2)).point(lambda v: 255 if v > 128 else 0)
	out = Image.new("RGBA", base.size, (252, 250, 245, 0))
	out.putalpha(big)
	out.alpha_composite(base)
	return out


def main() -> None:
	src = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".screenshots/dir_fx")
	dst = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(".screenshots/paper_fx")
	dst.mkdir(parents=True, exist_ok=True)
	for a, b in (("idle_0", "front"), ("idle_2", "back"), ("idle_3", "pose_side")):
		card(Image.open(src / f"{a}.png").convert("RGBA")).save(dst / f"{b}.png")
		print(b)


if __name__ == "__main__":
	main()
