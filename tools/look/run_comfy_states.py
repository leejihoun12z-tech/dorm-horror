"""룩 탐색 — 같은 배경의 하루 변화: 낮(밝고 따뜻한 미연시) → 후반 낮(기시감) → 밤(공포). (look-exploration-20261127.md §9)

1) 낮(D1)을 구도 그림(깊이+선 ControlNet)으로 새로 뽑는다.
2) 후반 낮(D2)·밤(N1)은 그 낮 그림을 바탕으로 img2img(looks.json states의 denoise)로 만든다 → 같은 방이 유지된다.
결과: ComfyUI/output/dorm_look_states/<보기>_<화풍>_<상태>_00001_.png → 화풍마다 큰 비교표 _states_<화풍>.jpg (줄 = 보기, 칸 = 상태)

  python tools/look/run_comfy_states.py --spaces room,corridor,lounge --styles S48_ghibli_like,S07_oil --out "<ComfyUI>/output"
  python tools/look/run_comfy_states.py --sheet "<ComfyUI>/output" --styles ...     # 비교표만
"""
import argparse
import json
from pathlib import Path

from run_comfy_looks import GUIDES, HERE, http, upload, wait_empty


def build(cfg: dict, space: str, style: dict, state: dict, depth_img: str, line_img: str, seed: int, cn: float, day_img: str | None) -> dict:
	pos = f"{cfg['spaces'][space]}, {style['prompt']}, {state['prompt']}"
	wf = {
		"1": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": cfg["models"][style.get("ckpt", "base")]}},
		"2": {"class_type": "CLIPTextEncode", "inputs": {"text": pos, "clip": ["1", 1]}},
		"3": {"class_type": "CLIPTextEncode", "inputs": {"text": cfg["negative"], "clip": ["1", 1]}},
		"4": {"class_type": "ControlNetLoader", "inputs": {"control_net_name": cfg["controlnet"]}},
		"5": {"class_type": "SetUnionControlNetType", "inputs": {"control_net": ["4", 0], "type": "depth"}},
		"6": {"class_type": "LoadImage", "inputs": {"image": depth_img}},
		"7": {"class_type": "ControlNetApplyAdvanced", "inputs": {"positive": ["2", 0], "negative": ["3", 0], "control_net": ["5", 0], "image": ["6", 0], "strength": round(0.65 * cn, 3), "start_percent": 0.0, "end_percent": 0.7}},
		"8": {"class_type": "SetUnionControlNetType", "inputs": {"control_net": ["4", 0], "type": "canny/lineart/anime_lineart/mlsd"}},
		"9": {"class_type": "LoadImage", "inputs": {"image": line_img}},
		"10": {"class_type": "ControlNetApplyAdvanced", "inputs": {"positive": ["7", 0], "negative": ["7", 1], "control_net": ["8", 0], "image": ["9", 0], "strength": round(0.45 * cn, 3), "start_percent": 0.0, "end_percent": 0.5}},
		"12": {"class_type": "KSampler", "inputs": {"model": ["1", 0], "positive": ["10", 0], "negative": ["10", 1], "latent_image": ["11", 0], "seed": seed, "steps": 30, "cfg": 6.0, "sampler_name": "dpmpp_2m", "scheduler": "karras", "denoise": state.get("denoise", 1.0)}},
		"13": {"class_type": "VAEDecode", "inputs": {"samples": ["12", 0], "vae": ["1", 2]}},
		"14": {"class_type": "SaveImage", "inputs": {"images": ["13", 0], "filename_prefix": f"dorm_look_states/{space}_{style['id']}_{state['id']}"}},
	}
	if day_img:  # 낮 그림(색·밝기 바꾼 판)에서 출발 → 같은 배경. 구조는 그림이 붙잡으니 깊이만 약하게, 선은 뺀다(선까지 걸면 거칠게 깨짐).
		wf["7"]["inputs"]["strength"] = round(0.35 * cn, 3)
		wf["12"]["inputs"]["positive"], wf["12"]["inputs"]["negative"] = ["7", 0], ["7", 1]
		for k in ("8", "9", "10"):
			del wf[k]
		wf["20"] = {"class_type": "LoadImage", "inputs": {"image": day_img}}
		wf["21"] = {"class_type": "ImageScale", "inputs": {"image": ["20", 0], "upscale_method": "lanczos", "width": 1344, "height": 768, "crop": "disabled"}}
		wf["11"] = {"class_type": "VAEEncode", "inputs": {"pixels": ["21", 0], "vae": ["1", 2]}}
	else:
		wf["11"] = {"class_type": "EmptyLatentImage", "inputs": {"width": 1344, "height": 768, "batch_size": 1}}
	return wf


def graded(src: Path, state: dict, tmp: Path) -> Path:
	"""낮 그림을 상태에 맞게 먼저 보정(밝기·채도·대비·색조) → img2img 출발점."""
	from PIL import Image, ImageEnhance
	g = state.get("grade")
	if not g:
		return src
	im = Image.open(src).convert("RGB")
	im = ImageEnhance.Color(im).enhance(g.get("sat", 1.0))
	im = ImageEnhance.Contrast(im).enhance(g.get("contrast", 1.0))
	im = ImageEnhance.Brightness(im).enhance(g.get("bright", 1.0))
	r, gg, b = im.split()
	t = g.get("tint", [1, 1, 1])
	im = Image.merge("RGB", [ch.point(lambda v, m=m: min(255, int(v * m))) for ch, m in zip((r, gg, b), t)])
	tmp.mkdir(parents=True, exist_ok=True)
	p = tmp / f"{src.stem}_{state['id']}_grade.png"
	im.save(p)
	return p


def out_file(out: Path, space: str, sid: str, state_id: str) -> Path | None:
	fs = sorted((out / "dorm_look_states").glob(f"{space}_{sid}_{state_id}_*.png"))
	return fs[-1] if fs else None


def sheet(out: Path, cfg: dict, spaces: list, styles: list) -> None:
	from PIL import Image, ImageDraw, ImageFont
	font = ImageFont.truetype("malgun.ttf", 28)
	small = ImageFont.truetype("malgun.ttf", 22)
	states = cfg["states"]
	w, h = 896, 512  # 칸 하나를 크게
	for st in styles:
		rows = [sp for sp in spaces if out_file(out, sp, st["id"], states[0]["id"])]
		if not rows:
			continue
		img = Image.new("RGB", (len(states) * w, 60 + len(rows) * (h + 40)), (16, 15, 20))
		d = ImageDraw.Draw(img)
		d.text((10, 12), f"{st['id']} {st['name']} — 낮 → 후반 낮 → 밤", font=font, fill=(255, 220, 120))
		for r, sp in enumerate(rows):
			y = 60 + r * (h + 40)
			for c, s in enumerate(states):
				f = out_file(out, sp, st["id"], s["id"])
				d.text((c * w + 8, y + 4), f"{sp} · {s['name']}", font=small, fill=(255, 255, 255))
				if f:
					img.paste(Image.open(f).convert("RGB").resize((w - 6, h)), (c * w + 3, y + 36))
		p = out / "dorm_look_states" / f"_states_{st['id']}.jpg"
		img.save(p, quality=88)
		print("비교표", p)


def main() -> None:
	ap = argparse.ArgumentParser()
	ap.add_argument("--server", default="http://127.0.0.1:8188")
	ap.add_argument("--spaces", default="room,corridor,lounge")
	ap.add_argument("--styles", required=True)
	ap.add_argument("--seed", type=int, default=20261128)
	ap.add_argument("--cn", type=float, default=1.0)
	ap.add_argument("--out", required=True, help="ComfyUI/output 폴더")
	ap.add_argument("--sheet", action="store_true", help="비교표만")
	ap.add_argument("--redo-later", action="store_true", help="후반 낮·밤을 이미 있어도 다시 뽑기(낮은 그대로)")
	a = ap.parse_args()
	cfg = json.loads((HERE / "looks.json").read_text(encoding="utf-8"))
	out = Path(a.out)
	spaces = [s for s in a.spaces.split(",") if s in cfg["spaces"]]
	styles = [s for s in cfg["styles"] if s["id"] in a.styles.split(",")]
	styles.sort(key=lambda s: s.get("ckpt", "base"))  # 체크포인트 바꾸기 줄이기
	if not a.sheet:
		day, later = cfg["states"][0], cfg["states"][1:]
		guides = {sp: (upload(a.server, GUIDES / f"{sp}_depth.png"), upload(a.server, GUIDES / f"{sp}_lines.png")) for sp in spaces}
		seeds = {(sp, st["id"]): a.seed + i * 7919 for i, (sp, st) in enumerate((sp, st) for st in styles for sp in spaces)}
		n = 0
		for st in styles:  # 1) 낮
			for sp in spaces:
				if out_file(out, sp, st["id"], day["id"]):
					continue
				http(f"{a.server}/prompt", json.dumps({"prompt": build(cfg, sp, st, day, *guides[sp], seeds[(sp, st["id"])], a.cn, None)}).encode(), {"Content-Type": "application/json"})
				n += 1
		print(f"낮 {n}장 큐에 넣음")
		wait_empty(a.server)
		n = 0
		for st in styles:  # 2) 후반 낮·밤 = 낮 그림에서
			for sp in spaces:
				f = out_file(out, sp, st["id"], day["id"])
				if not f:
					print("낮 그림 없음", sp, st["id"])
					continue
				for s in later:
					if a.redo_later or not out_file(out, sp, st["id"], s["id"]):
						day_img = upload(a.server, graded(f, s, out / "dorm_look_states" / "_grade"))
						http(f"{a.server}/prompt", json.dumps({"prompt": build(cfg, sp, st, s, *guides[sp], seeds[(sp, st["id"])], a.cn, day_img)}).encode(), {"Content-Type": "application/json"})
					n += 1
		print(f"후반 낮·밤 {n}장 큐에 넣음")
		wait_empty(a.server)
	sheet(out, cfg, spaces, styles)


if __name__ == "__main__":
	main()
