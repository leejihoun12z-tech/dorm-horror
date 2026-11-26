"""render_ref_views.py 결과(투명 바탕) → 흰 바탕 3장 + 3칸 시트 + 실루엣.

실행: python tools/char/ref_sheet.py <폴더> <이름>
"""
import sys

from PIL import Image

d, name = sys.argv[1], sys.argv[2]
tiles = []
for k in ("front", "right", "back"):
	im = Image.open(f"{d}/{name}_rgba_{k}.png").convert("RGBA")
	white = Image.new("RGBA", im.size, (255, 255, 255, 255))
	white.alpha_composite(im)
	white.convert("RGB").save(f"{d}/{name}_{k}.png")
	im.getchannel("A").point(lambda a: 255 if a > 127 else 0).save(f"{d}/{name}_mask_{k}.png")
	tiles.append(white.convert("RGB"))
sheet = Image.new("RGB", (1024 * 3, 1024), "white")
for i, t in enumerate(tiles):
	sheet.paste(t, (i * 1024, 0))
sheet.save(f"{d}/{name}_sheet.png")
print("sheet", f"{d}/{name}_sheet.png")
