"""룩 탐색 — 회차가 갈수록 배경이 카툰 → 현실로 바뀌는 시안. (look-exploration-20261127.md §10)

카툰 낮 그림(run_comfy_states.py의 D1, 없으면 새로 뽑음)을 출발점으로,
현실 끝판(R4, looks.json realism.target = 옛 비디오·리미널 사진)은 같은 구도로 새로 뽑고,
중간(R1~R3)은 카툰과 현실 끝판을 25·50·75%로 섞은 뒤 약하게 다시 그린다. (카툰에서 img2img로만 올리면 100%에서도 카툰이 남았음)
밤은 카툰 시작(R0)과 마지막 현실(R4) 두 장. 결과: ComfyUI/output/dorm_look_realism/ + 비교표·크게 보기 index.html

  python tools/look/run_comfy_realism.py --bases S06_anime_bg,S49_subcul_toon --spaces room,corridor,lounge --out "<ComfyUI>/output"
"""
import argparse
import json
from pathlib import Path

from make_viewer import PAGE
from run_comfy_looks import GUIDES, HERE, http, upload, wait_empty
from run_comfy_states import build, graded, out_file

SUB = "dorm_look_realism"


def blend(a: Path, b: Path, t: float, dst: Path) -> Path:
	"""카툰 a와 현실 b를 t 비율로 섞은 출발 그림."""
	from PIL import Image
	dst.parent.mkdir(parents=True, exist_ok=True)
	ia = Image.open(a).convert("RGB")
	Image.blend(ia, Image.open(b).convert("RGB").resize(ia.size), t).save(dst)
	return dst


def rfile(out: Path, space: str, base: str, tag: str) -> Path | None:
	fs = sorted((out / SUB).glob(f"{space}_{base}_{tag}_*.png"))
	return fs[-1] if fs else None


def queue(server: str, wf: dict, prefix: str) -> None:
	wf["14"]["inputs"]["filename_prefix"] = f"{SUB}/{prefix}"
	http(f"{server}/prompt", json.dumps({"prompt": wf}).encode(), {"Content-Type": "application/json"})


def columns(cfg: dict) -> list:
	n = len(cfg["realism"]["mix"]) + 1
	return [("R0", "R0 카툰 낮")] + [(f"R{i + 1}", f"R{i + 1} 현실 {int(100 * (i + 1) / n)}%") for i in range(n)] + [("R0night", "R0 카툰 밤"), (f"R{n}night", f"R{n} 현실 밤")]


def cell(out: Path, sp: str, base: str, tag: str) -> Path | None:
	return out_file(out, sp, base, "D1_day") if tag == "R0" else (out_file(out, sp, base, "N1_night") if tag == "R0night" else rfile(out, sp, base, tag))


def report(out: Path, cfg: dict, spaces: list, bases: list) -> None:
	from PIL import Image, ImageDraw, ImageFont
	font, small = ImageFont.truetype("malgun.ttf", 28), ImageFont.truetype("malgun.ttf", 20)
	cols = columns(cfg)
	names = {s["id"]: s["name"] for s in cfg["styles"]}
	data = []
	for b in bases:
		w, h = 640, 366
		img = Image.new("RGB", (len(cols) * w, 60 + len(spaces) * (h + 34)), (16, 15, 20))
		d = ImageDraw.Draw(img)
		d.text((10, 12), f"{b} {names[b]} → 현실(옛 비디오·리미널) — 회차가 갈수록", font=font, fill=(255, 220, 120))
		rows = []
		for r, sp in enumerate(spaces):
			y = 60 + r * (h + 34)
			cells = []
			for c, (tag, label) in enumerate(cols):
				f = cell(out, sp, b, tag)
				d.text((c * w + 6, y + 4), f"{sp} · {label}", font=small, fill=(255, 255, 255))
				if f:
					img.paste(Image.open(f).convert("RGB").resize((w - 4, h)), (c * w + 2, y + 30))
				cells.append(f"../{f.parent.name}/{f.name}" if f and f.parent.name != SUB else (f.name if f else ""))
			rows.append({"space": sp, "cells": cells})
		p = out / SUB / f"_realism_{b}.jpg"
		img.save(p, quality=88)
		print("비교표", p)
		data.append({"id": b, "name": names[b] + " → 현실", "rows": rows})
	page = PAGE.replace("__DATA__", json.dumps(data, ensure_ascii=False)).replace("__STATES__", json.dumps([c[1] for c in cols], ensure_ascii=False))
	page = page.replace("repeat(3,1fr)", f"repeat({len(cols)},1fr)")
	(out / SUB / "index.html").write_text(page, encoding="utf-8")


def main() -> None:
	ap = argparse.ArgumentParser()
	ap.add_argument("--server", default="http://127.0.0.1:8188")
	ap.add_argument("--bases", default="S06_anime_bg,S49_subcul_toon")
	ap.add_argument("--spaces", default="room,corridor,lounge")
	ap.add_argument("--seed", type=int, default=20261128)
	ap.add_argument("--out", required=True)
	ap.add_argument("--sheet", action="store_true")
	a = ap.parse_args()
	cfg = json.loads((HERE / "looks.json").read_text(encoding="utf-8"))
	out = Path(a.out)
	spaces = a.spaces.split(",")
	bases = a.bases.split(",")
	styles = {s["id"]: s for s in cfg["styles"]}
	target = styles[cfg["realism"]["target"]]
	day, night = cfg["states"][0], cfg["states"][2]
	if not a.sheet:
		guides = {sp: (upload(a.server, GUIDES / f"{sp}_depth.png"), upload(a.server, GUIDES / f"{sp}_lines.png")) for sp in spaces}
		seed = {(sp, b): a.seed + i * 7919 for i, (sp, b) in enumerate((sp, b) for b in bases for sp in spaces)}
		n = 0
		for b in bases:  # 카툰 낮·밤이 없으면 먼저 (run_comfy_states와 같은 이름)
			for sp in spaces:
				if not out_file(out, sp, b, day["id"]):
					wf = build(cfg, sp, styles[b], day, *guides[sp], seed[(sp, b)], 1.0, None)
					http(f"{a.server}/prompt", json.dumps({"prompt": wf}).encode(), {"Content-Type": "application/json"})
					n += 1
		print(f"카툰 낮 {n}장")
		wait_empty(a.server)
		real = cfg["realism"]["real_state"]
		mixes = cfg["realism"]["mix"]
		last = f"R{len(mixes) + 1}"
		n = 0
		for b in bases:  # 카툰 밤 + 현실 끝판(같은 구도로 새로)
			for sp in spaces:
				f = out_file(out, sp, b, day["id"])
				if not out_file(out, sp, b, night["id"]):
					wf = build(cfg, sp, styles[b], night, *guides[sp], seed[(sp, b)], 1.0, upload(a.server, graded(f, night, out / SUB / "_grade")))
					wf["14"]["inputs"]["filename_prefix"] = f"dorm_look_states/{sp}_{b}_{night['id']}"
					http(f"{a.server}/prompt", json.dumps({"prompt": wf}).encode(), {"Content-Type": "application/json"})
					n += 1
				if not rfile(out, sp, b, last):
					queue(a.server, build(cfg, sp, target, real, *guides[sp], seed[(sp, b)], 1.0, None), f"{sp}_{b}_{last}")
					n += 1
		print(f"카툰 밤·현실 끝판 {n}장")
		wait_empty(a.server)
		n = 0
		for b in bases:  # 중간 단계 = 카툰과 현실을 섞어 약하게 다시 그림 + 현실 밤
			for sp in spaces:
				toon, rl = out_file(out, sp, b, day["id"]), rfile(out, sp, b, last)
				if not (toon and rl):
					continue
				for i, m in enumerate(mixes):
					tag = f"R{i + 1}"
					if rfile(out, sp, b, tag):
						continue
					mixed = blend(toon, rl, m, out / SUB / "_grade" / f"{sp}_{b}_{tag}_mix.png")
					queue(a.server, build(cfg, sp, target, dict(real, id=tag, denoise=cfg["realism"]["denoise"]), *guides[sp], seed[(sp, b)], 1.0, upload(a.server, mixed)), f"{sp}_{b}_{tag}")
					n += 1
				if not rfile(out, sp, b, last + "night"):
					queue(a.server, build(cfg, sp, target, night, *guides[sp], seed[(sp, b)], 1.0, upload(a.server, graded(rl, night, out / SUB / "_grade"))), f"{sp}_{b}_{last}night")
					n += 1
		print(f"중간 단계·현실 밤 {n}장")
		wait_empty(a.server)
	report(out, cfg, spaces, bases)


if __name__ == "__main__":
	main()
