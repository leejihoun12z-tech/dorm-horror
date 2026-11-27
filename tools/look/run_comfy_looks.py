"""룩 탐색 일괄 실행: 같은 구도(공간 4곳) × 화풍 16가지를 로컬 ComfyUI로 뽑는다. (look-exploration-20261127.md)

준비 (PC, 한 번만):
  ComfyUI/models/checkpoints/  sd_xl_base_1.0.safetensors (Stability AI, OpenRAIL++)  + 이미 있는 animagine-xl-4.0-opt
  ComfyUI/models/controlnet/   controlnet-union-sdxl-1.0-promax.safetensors (xinsir, Apache-2.0)
실행 (ComfyUI를 켜 둔 상태에서, 저장소 폴더에서). 묶음(--preset):
  1 = 화풍 44가지 × 복도·2인실 (88장, 약 40분)            ← 먼저 이것
  2 = 화풍 44가지 × 보기 8곳 전부 (352장, 약 2.5시간)
  3 = 고른 화풍(--styles, 기본 8개) × 조명 11가지 × 복도·2인실 (176장)
  4 = 무작위 섞기 --random N (보기·화풍·조명을 무작위로 N장, 기본 60) — 생각 못 한 조합 찾기
  python tools/look/run_comfy_looks.py --preset 1 --out "<ComfyUI>/output/dorm_look"
  python tools/look/run_comfy_looks.py --spaces lounge --styles S04_pencil,S26_neon --moods M01_dusk,M06_blinds --seeds 3
  python tools/look/run_comfy_looks.py --dry-run --preset 2     # 몇 장인지·워크플로만 확인
  python tools/look/run_comfy_looks.py --sheet "<ComfyUI>/output/dorm_look"   # 비교표만
결과: ComfyUI/output/dorm_look/<보기>_<화풍>_<조명>_s<번호>_00001_.png → 같은 폴더에 비교표 _sheet_*.jpg (화풍 비교·조명 비교).
구도 고정: 깊이(depth) + 선(lines) 두 ControlNet을 겹쳐 쓴다. 화풍이 구도를 너무 따르면 --cn 값을 낮춘다.
"""
import argparse
import json
import time
import urllib.request
import uuid
from pathlib import Path

HERE = Path(__file__).resolve().parent
GUIDES = HERE / "guides"


def http(url: str, data: bytes | None = None, headers: dict | None = None) -> dict:
	req = urllib.request.Request(url, data=data, headers=headers or {})
	with urllib.request.urlopen(req, timeout=60) as r:
		body = r.read()
	return json.loads(body) if body else {}


def upload(server: str, path: Path) -> str:
	bnd = uuid.uuid4().hex
	parts = []
	for k, v in (("overwrite", "true"), ("subfolder", "dorm_look_guides"), ("type", "input")):
		parts.append(f"--{bnd}\r\nContent-Disposition: form-data; name=\"{k}\"\r\n\r\n{v}\r\n".encode())
	parts.append(f"--{bnd}\r\nContent-Disposition: form-data; name=\"image\"; filename=\"{path.name}\"\r\nContent-Type: image/png\r\n\r\n".encode())
	parts.append(path.read_bytes())
	parts.append(f"\r\n--{bnd}--\r\n".encode())
	r = http(f"{server}/upload/image", b"".join(parts), {"Content-Type": f"multipart/form-data; boundary={bnd}"})
	return f"{r.get('subfolder', 'dorm_look_guides')}/{r.get('name', path.name)}"


def workflow(cfg: dict, space: str, style: dict, mood: dict | None, depth_img: str, line_img: str, seed: int, cn: float, k: int) -> dict:
	pos = f"{cfg['spaces'][space]}, {style['prompt']}" + (f", {mood['prompt']}" if mood else "")
	name = f"dorm_look/{space}_{style['id']}_{mood['id'] if mood else 'M00'}_s{k}"
	return {
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
		"11": {"class_type": "EmptyLatentImage", "inputs": {"width": 1344, "height": 768, "batch_size": 1}},
		"12": {"class_type": "KSampler", "inputs": {"model": ["1", 0], "positive": ["10", 0], "negative": ["10", 1], "latent_image": ["11", 0], "seed": seed, "steps": 30, "cfg": 6.0, "sampler_name": "dpmpp_2m", "scheduler": "karras", "denoise": 1.0}},
		"13": {"class_type": "VAEDecode", "inputs": {"samples": ["12", 0], "vae": ["1", 2]}},
		"14": {"class_type": "SaveImage", "inputs": {"images": ["13", 0], "filename_prefix": name}},
	}


def wait_empty(server: str) -> None:
	while True:
		q = http(f"{server}/queue")
		n = len(q.get("queue_running", [])) + len(q.get("queue_pending", []))
		print(f"\r남은 작업 {n}  ", end="", flush=True)
		if n == 0:
			print()
			return
		time.sleep(5)


def parse(name: str, cfg: dict):
	"""<보기>_<화풍>_<조명>_s<k>_00001_.png → (보기, 화풍, 조명, k)"""
	for v in sorted(cfg["spaces"], key=len, reverse=True):
		if not name.startswith(v + "_"):
			continue
		rest = name[len(v) + 1:]
		for st in cfg["styles"]:
			if rest.startswith(st["id"] + "_"):
				r2 = rest[len(st["id"]) + 1:]
				mood, _, tail = r2.partition("_s")
				return v, st["id"], mood, tail.split("_")[0]
	return None


def sheet(out_dir: Path, cfg: dict) -> None:
	from PIL import Image, ImageDraw, ImageFont
	try:
		font = ImageFont.truetype("malgun.ttf", 20)
	except OSError:
		font = ImageFont.load_default()
	names = {st["id"]: st["name"] for st in cfg["styles"]}
	names.update({m["id"]: m["name"] for m in cfg.get("moods", [])})
	names["M00"] = "기본 빛"
	items = {}
	for f in sorted(out_dir.glob("*.png")):
		p = parse(f.stem, cfg)
		if p:
			items[p] = f  # 같은 이름이면 마지막 것
	def grid(title: str, cells: list, path: Path) -> None:
		w, h, cols = 448, 256, 4
		rows = (len(cells) + cols - 1) // cols
		img = Image.new("RGB", (cols * w, 40 + rows * (h + 26)), (16, 15, 20))
		d = ImageDraw.Draw(img)
		d.text((8, 8), title, font=font, fill=(255, 220, 120))
		for i, (label, f) in enumerate(cells):
			x, y = (i % cols) * w, 40 + (i // cols) * (h + 26)
			d.text((x + 6, y + 3), label, font=font, fill=(255, 255, 255))
			img.paste(Image.open(f).convert("RGB").resize((w - 4, h)), (x + 2, y + 24))
		img.save(path, quality=84)
		print("비교표", path)
	keys = set((v, m, k) for v, st, m, k in items)
	for v, m, k in sorted(keys):  # 화풍 비교: 보기·조명·번호 고정
		cells = [(f"{st} {names.get(st, '')}", items[(v, st, m, k)]) for st in [s["id"] for s in cfg["styles"]] if (v, st, m, k) in items]
		if len(cells) >= 2:
			grid(f"{v} · {names.get(m, m)} · s{k} — 화풍 비교", cells, out_dir / f"_sheet_style_{v}_{m}_s{k}.jpg")
	keys2 = set((v, st, k) for v, st, m, k in items)
	for v, st, k in sorted(keys2):  # 조명 비교: 보기·화풍·번호 고정
		cells = [(f"{m} {names.get(m, '')}", f) for (v2, st2, m, k2), f in sorted(items.items()) if (v2, st2, k2) == (v, st, k)]
		if len(cells) >= 3:
			grid(f"{v} · {st} {names.get(st, '')} · s{k} — 조명 비교", cells, out_dir / f"_sheet_mood_{v}_{st}_s{k}.jpg")


PRESET_STYLES_3 = "S01_photo,S03_dollhouse,S04_pencil,S06_anime_bg,S08_ligne_claire,S10_papercraft,S15_stage,S16_clay"


def main() -> None:
	import random
	ap = argparse.ArgumentParser()
	ap.add_argument("--server", default="http://127.0.0.1:8188")
	ap.add_argument("--preset", type=int, default=0)
	ap.add_argument("--spaces", default="")
	ap.add_argument("--styles", default="")
	ap.add_argument("--moods", default="", help="조명 id 목록 또는 all (비우면 기본 빛)")
	ap.add_argument("--night", action="store_true", help="기본 밤(night_suffix)을 조명처럼 씀")
	ap.add_argument("--seeds", type=int, default=1, help="같은 조합을 몇 장씩")
	ap.add_argument("--random", type=int, default=0, help="무작위 조합 N장")
	ap.add_argument("--seed", type=int, default=20261127)
	ap.add_argument("--cn", type=float, default=1.0, help="구도 고정 세기 배수 (0.6 = 더 자유롭게)")
	ap.add_argument("--dry-run", action="store_true")
	ap.add_argument("--no-wait", action="store_true")
	ap.add_argument("--sheet", default="", help="ComfyUI/output/dorm_look 폴더 → 비교표만 만들기")
	ap.add_argument("--out", default="", help="다 뽑은 뒤 비교표를 만들 ComfyUI/output/dorm_look 경로")
	a = ap.parse_args()
	cfg = json.loads((HERE / "looks.json").read_text(encoding="utf-8"))
	if a.sheet:
		sheet(Path(a.sheet), cfg)
		return
	if a.preset == 1:
		a.spaces = a.spaces or "corridor,room"
	elif a.preset == 3:
		a.spaces = a.spaces or "corridor,room"
		a.styles = a.styles or PRESET_STYLES_3
		a.moods = a.moods or "all"
	elif a.preset == 4:
		a.random = a.random or 60
	spaces = [s for s in cfg["spaces"] if not a.spaces or s in a.spaces.split(",")]
	styles = [s for s in cfg["styles"] if not a.styles or s["id"] in a.styles.split(",")]
	all_moods = cfg.get("moods", [])
	if a.moods == "all":
		moods = list(all_moods)
	elif a.moods:
		moods = [m for m in all_moods if m["id"] in a.moods.split(",")]
	elif a.night:
		moods = [{"id": "M00night", "name": "밤", "prompt": cfg["night_suffix"].lstrip(", ")}]
	else:
		moods = [None]
	jobs = []
	if a.random:
		rng = random.Random(a.seed)
		for _ in range(a.random):
			jobs.append((rng.choice(spaces), rng.choice(styles), rng.choice([None] + all_moods), 0))
	else:
		for sp in spaces:
			for st in styles:
				for m in moods:
					for k in range(a.seeds):
						jobs.append((sp, st, m, k))
	guides = {}
	# 8GB 그래픽카드에서 체크포인트를 자주 바꾸면 느려서, 같은 체크포인트끼리 묶어 보낸다(시드는 원래 순번 그대로).
	order = sorted(enumerate(jobs), key=lambda t: t[1][1].get("ckpt", "base"))
	for i, (sp, st, m, k) in order:
		if sp not in guides:
			guides[sp] = (f"dorm_look_guides/{sp}_depth.png", f"dorm_look_guides/{sp}_lines.png") if a.dry_run else (upload(a.server, GUIDES / f"{sp}_depth.png"), upload(a.server, GUIDES / f"{sp}_lines.png"))
		wf = workflow(cfg, sp, st, m, guides[sp][0], guides[sp][1], a.seed + i * 7919 + k, a.cn, k)
		if a.dry_run:
			if i == 0:
				print(json.dumps(wf, ensure_ascii=False, indent=1))
		else:
			http(f"{a.server}/prompt", json.dumps({"prompt": wf, "client_id": "dorm-look"}).encode(), {"Content-Type": "application/json"})
	n_sp = len(set(j[0] for j in jobs))
	print(f"{'확인만' if a.dry_run else '큐에 넣음'}: {len(jobs)}장 (보기 {n_sp}곳, 약 {len(jobs) * 25 // 60}분 @ 장당 25초)")
	if not a.dry_run and not a.no_wait:
		wait_empty(a.server)
		if a.out:
			sheet(Path(a.out), cfg)


if __name__ == "__main__":
	main()
