"""룩 탐색 일괄 실행: 같은 구도(공간 4곳) × 화풍 16가지를 로컬 ComfyUI로 뽑는다. (look-exploration-20261127.md)

준비 (PC, 한 번만):
  ComfyUI/models/checkpoints/  sd_xl_base_1.0.safetensors (Stability AI, OpenRAIL++)  + 이미 있는 animagine-xl-4.0-opt
  ComfyUI/models/controlnet/   controlnet-union-sdxl-1.0-promax.safetensors (xinsir, Apache-2.0)
실행 (ComfyUI를 켜 둔 상태에서, 저장소 폴더에서):
  python tools/look/run_comfy_looks.py                      # 전부(4곳 × 16화풍 = 64장) 큐에 넣고 끝날 때까지 기다림
  python tools/look/run_comfy_looks.py --spaces corridor --styles S04_pencil,S06_anime_bg
  python tools/look/run_comfy_looks.py --night               # 밤 판
  python tools/look/run_comfy_looks.py --dry-run             # 보낼 워크플로만 출력(ComfyUI 없이 확인)
  python tools/look/run_comfy_looks.py --sheet "ComfyUI/output/dorm_look"   # 이미 뽑은 그림으로 비교표만
결과: ComfyUI/output/dorm_look/<공간>_<화풍>[_night]_00001_.png → --sheet 폴더에 공간별·화풍별 비교 한 장.
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


def workflow(cfg: dict, space: str, style: dict, night: bool, depth_img: str, line_img: str, seed: int, cn: float) -> dict:
	pos = f"{cfg['spaces'][space]}, {style['prompt']}" + (cfg["night_suffix"] if night else "")
	name = f"dorm_look/{space}_{style['id']}" + ("_night" if night else "")
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


def sheet(out_dir: Path, cfg: dict) -> None:
	from PIL import Image, ImageDraw, ImageFont
	try:
		font = ImageFont.truetype("malgun.ttf", 22)
	except OSError:
		font = ImageFont.load_default()
	styles = cfg["styles"]
	w, h = 448, 256
	for night in (False, True):
		suf = "_night" if night else ""
		for sp in cfg["spaces"]:
			files = []
			for st in styles:
				hits = sorted(out_dir.glob(f"{sp}_{st['id']}{suf}_*.png"))
				files.append((st, hits[-1] if hits else None))
			if not any(f for _, f in files):
				continue
			cols = 4
			rows = (len(files) + cols - 1) // cols
			img = Image.new("RGB", (cols * w, rows * (h + 28)), (16, 15, 20))
			d = ImageDraw.Draw(img)
			for i, (st, f) in enumerate(files):
				x, y = (i % cols) * w, (i // cols) * (h + 28)
				d.text((x + 6, y + 4), f"{st['id']} {st['name']}", font=font, fill=(255, 220, 120))
				if f:
					img.paste(Image.open(f).convert("RGB").resize((w - 4, h)), (x + 2, y + 28))
			p = out_dir / f"_sheet_{sp}{suf}.jpg"
			img.save(p, quality=85)
			print("비교표", p)


def main() -> None:
	ap = argparse.ArgumentParser()
	ap.add_argument("--server", default="http://127.0.0.1:8188")
	ap.add_argument("--spaces", default="")
	ap.add_argument("--styles", default="")
	ap.add_argument("--night", action="store_true")
	ap.add_argument("--seed", type=int, default=20261127)
	ap.add_argument("--cn", type=float, default=1.0, help="구도 고정 세기 배수 (0.6 = 더 자유롭게)")
	ap.add_argument("--dry-run", action="store_true")
	ap.add_argument("--no-wait", action="store_true")
	ap.add_argument("--sheet", default="", help="ComfyUI/output/dorm_look 폴더 경로 → 비교표만 만들기")
	ap.add_argument("--out", default="", help="다 뽑은 뒤 비교표를 만들 ComfyUI/output/dorm_look 경로")
	a = ap.parse_args()
	cfg = json.loads((HERE / "looks.json").read_text(encoding="utf-8"))
	if a.sheet:
		sheet(Path(a.sheet), cfg)
		return
	spaces = [s for s in cfg["spaces"] if not a.spaces or s in a.spaces.split(",")]
	styles = [s for s in cfg["styles"] if not a.styles or s["id"] in a.styles.split(",")]
	n = 0
	for sp in spaces:
		if a.dry_run:
			dimg, limg = f"dorm_look_guides/{sp}_depth.png", f"dorm_look_guides/{sp}_lines.png"
		else:
			dimg, limg = upload(a.server, GUIDES / f"{sp}_depth.png"), upload(a.server, GUIDES / f"{sp}_lines.png")
		for i, st in enumerate(styles):
			wf = workflow(cfg, sp, st, a.night, dimg, limg, a.seed + i, a.cn)
			if a.dry_run:
				if n == 0:
					print(json.dumps(wf, ensure_ascii=False, indent=1))
			else:
				http(f"{a.server}/prompt", json.dumps({"prompt": wf, "client_id": "dorm-look"}).encode(), {"Content-Type": "application/json"})
			n += 1
	print(f"{'확인만' if a.dry_run else '큐에 넣음'}: {n}장 ({len(spaces)}곳 × {len(styles)}화풍{' · 밤' if a.night else ''})")
	if not a.dry_run and not a.no_wait:
		wait_empty(a.server)
		if a.out:
			sheet(Path(a.out), cfg)


if __name__ == "__main__":
	main()
