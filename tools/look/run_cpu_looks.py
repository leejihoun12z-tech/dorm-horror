"""룩 탐색 — 그래픽카드 없는 곳(클라우드 CPU)용 저화질 시안. PC 본판은 run_comfy_looks.py(SDXL).

SD 1.5 (CreativeML OpenRAIL-M) + ControlNet 깊이·선화 (lllyasviel v1.1, OpenRAIL) + LCM-LoRA (OpenRAIL++)로
같은 구도(tools/look/guides)에 looks.json 화풍을 입힌다. 768×448, 6단계. 4코어 CPU 기준 장당 약 1분.

python tools/look/run_cpu_looks.py 출력폴더 --spaces corridor,room --styles all [--moods M01_dusk] [--limit N]
비교표는 run_comfy_looks.py --sheet 출력폴더 로 만든다(파일 이름 규칙이 같음).
"""
import argparse
import json
import time
from pathlib import Path

import torch
from diffusers import ControlNetModel, LCMScheduler, StableDiffusionControlNetPipeline
from PIL import Image

HERE = Path(__file__).resolve().parent
W, H = 768, 448


def main() -> None:
	ap = argparse.ArgumentParser()
	ap.add_argument("out")
	ap.add_argument("--spaces", default="corridor")
	ap.add_argument("--styles", default="all")
	ap.add_argument("--moods", default="")
	ap.add_argument("--steps", type=int, default=5)
	ap.add_argument("--seed", type=int, default=20261127)
	ap.add_argument("--limit", type=int, default=0)
	a = ap.parse_args()
	cfg = json.loads((HERE / "looks.json").read_text(encoding="utf-8"))
	out = Path(a.out)
	out.mkdir(parents=True, exist_ok=True)
	torch.set_num_threads(max(1, torch.get_num_threads()))
	cn = [ControlNetModel.from_pretrained("lllyasviel/control_v11f1p_sd15_depth", torch_dtype=torch.float32),
		ControlNetModel.from_pretrained("lllyasviel/control_v11p_sd15_lineart", torch_dtype=torch.float32)]
	pipe = StableDiffusionControlNetPipeline.from_pretrained("stable-diffusion-v1-5/stable-diffusion-v1-5", controlnet=cn,
		torch_dtype=torch.float32, safety_checker=None, requires_safety_checker=False)
	pipe.load_lora_weights("latent-consistency/lcm-lora-sdv1-5")
	pipe.fuse_lora()
	pipe.scheduler = LCMScheduler.from_config(pipe.scheduler.config)
	pipe.set_progress_bar_config(disable=True)
	styles = [s for s in cfg["styles"] if a.styles == "all" or s["id"] in a.styles.split(",")]
	moods = [None] if not a.moods else [m for m in cfg["moods"] if a.moods == "all" or m["id"] in a.moods.split(",")]
	n = 0
	for sp in a.spaces.split(","):
		d = Image.open(HERE / "guides" / f"{sp}_depth.png").convert("RGB").resize((W, H))
		l = Image.open(HERE / "guides" / f"{sp}_lines.png").convert("RGB").resize((W, H))
		for i, st in enumerate(styles):
			for m in moods:
				name = f"{sp}_{st['id']}_{m['id'] if m else 'M00'}_s0_00001_.png"
				if (out / name).exists():
					continue
				# SD 1.5 글자 한도(77토큰) 때문에 화풍을 앞에, 공간은 짧은 설명으로
				prompt = f"{st['prompt']}, {cfg['spaces_short'][sp]}" + (f", {m['prompt']}" if m else "")
				t = time.time()
				img = pipe(prompt, image=[d, l], negative_prompt=cfg["negative"], num_inference_steps=a.steps, guidance_scale=1.5,
					controlnet_conditioning_scale=[0.75, 0.45], control_guidance_end=[0.8, 0.6], width=W, height=H,
					generator=torch.Generator().manual_seed(a.seed + i)).images[0]
				img.save(out / name)
				n += 1
				print(f"{name}  {time.time() - t:.0f}s", flush=True)
				if a.limit and n >= a.limit:
					return


if __name__ == "__main__":
	main()
