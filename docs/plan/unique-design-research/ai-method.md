# 「AI 평균 얼굴」에서 벗어나는 방법 — Anima·태그 모델 기술 조사

_작성: 2026-11-24 · 조사만, 아무것도 생성·설치하지 않음_
_대상: 몬스터 소녀 약 36명 디자인 · ComfyUI · anima_aestheticV11 + 스타일 LoRA · 1024×1536 · 30 steps · cfg 4 · er_sde · 흰 배경 전신_

---

## 0. 결론 먼저

1. **원인은 세 가지가 겹친 것**이다. ① 학습 그림에 많은 것(갈색 머리 216만 장, 긴 머리 644만 장)으로 끌려감 ② 우리가 쓰는 **Aesthetic 판은 「일관된 기본 화풍」으로 다듬은 판**이라 원래부터 다양성이 줄어 있음 ③ 옷 설명 문장이 길어지면 앞쪽 몸·종족 정보가 묽어짐.
2. **프롬프트에서 할 일**: 문장 대신 **실제 있는 Danbooru 태그**(글 수 많은 것)로 · **종족·몸·피부를 맨 앞** · 색은 **물건마다 붙여서**(`black jacket`) · 옷은 **실루엣 하나 + 디테일 하나 + 소품 하나**만 · 전체 200토큰 안 · 부정 프롬프트에 **나온 기본값만 골라 넣기**(`brown hair` 등).
3. **작업 순서에서 할 일**: 전신을 바로 뽑지 말고 **상반신으로 디자인을 먼저 정함** → 머리·눈 색은 **부분 고쳐 그리기(inpaint)** → **우리가 고른 그림을 img2img·LLLite로 이어 받아** 전신 → 얼굴·눈 **다시 그리기(FaceDetailer 등)** → Aesthetic로 낮은 세기 마무리.
4. **Anima가 되는 것**: img2img·inpaint·LoRA(기본 ComfyUI) · ControlNet 대신 **LLLite**(우리 PC에 any-test-like-v2 있음) · 포즈 전용 어댑터(실험판) · 지역 나눠 프롬프트(전용 노드 3종) · IP-Adapter(노드는 있으나 가중치 파일 공개 상태가 불분명 → 사실상 아직 못 씀). **SDXL용 ControlNet·IP-Adapter·BREAK는 그대로 안 됨.**

---

## 1. 왜 평균으로 돌아가나

| 원인 | 설명 | 근거 |
|---|---|---|
| **태그 빈도** | 모델은 학습 그림에 많이 나온 모습을 「안전한 답」으로 본다. Danbooru 글 수: `long hair` 6,436,636 · `brown hair` 2,158,548 · `black hair` 2,282,038 ↔ `colored skin` 223,119 · `lamia` 6,524 · `arachne` 1,413 · `jellyfish girl` 459. 몬스터 쪽 태그는 수십~수백 배 적다. | Danbooru 태그 API (아래 표) |
| **모르는·약한 태그는 사실상 무시** | 글 수가 아주 적은 태그(수백~수천)는 모델이 잘 모른다. `pink inner hair`, `translucent hair`, `character sheet`, `insect girl`은 **Danbooru 태그가 아님**(글 수 0). 이런 말은 글 인코더(Qwen)가 문장으로 읽어 「대충」 반영할 뿐이다. | Danbooru API · bextoper 가이드(「태그는 꼭 Booru에서 확인」, 작가 태그는 100장 이상) |
| **긴 문장이 묽어짐** | 한 커뮤니티 글은 Anima에서 **300토큰을 넘으면 뒤쪽이 잘리고 전체가 평균처럼 된다**, 200토큰 안을 권장. 같은 개념을 여러 줄 반복하면 다른 디테일이 무너진다고 함. 다른 가이드는 「45~70 태그면 충분」. 옷 문장이 길수록 종족·피부 같은 앞쪽 정보의 몫이 줄어든다. | Civitai 31399 · 37140 (300토큰 「잘림」은 글쓴이 주장, (미확인)) |
| **Aesthetic 판 자체** | 공식 카드: Aesthetic = 「일관성과 더 좋은 기본 화풍」으로 미세조정. Base = 「가장 다양하고 유연」. Turbo는 다양성이 줄어든다고 명시. 즉 **우리가 쓰는 판이 기본값으로 당기는 힘이 가장 센 쪽**이다. 스타일 LoRA도 그 LoRA 학습 그림의 평균 쪽으로 당긴다. | Anima 공식 README · Civitai 35368 |
| **색 번짐** | 색 낱말이 여러 개면 서로 섞인다(머리색이 옷으로, 옷색이 피부로). Anima는 예전 모델보다 머리·눈 색 바뀜이 줄었지만 「개념·화풍 번짐」은 여전하다는 보고. | Anima 토론 #76 · Civitai 32568 요약 |
| **전신에서 얼굴이 작음** | 1024×1536 전신이면 얼굴이 대략 120~180px(어림, (미확인)). 이 크기에서는 눈동자 모양(세로 동공·십자 동공)·색 눈흰자 같은 작은 특징이 뭉개져 「둥근 눈동자」로 돌아간다. | FaceDetailer 설명(작은 얼굴을 잘라 크게 다시 그림) |
| **점수·품질 태그 과다** | Aesthetic에 `score_*`를 양쪽(긍정·부정)에 다 넣으면 「너무 밀어서 뻔한 그림(slop)」이 된다고 공식 카드가 경고. | Anima 공식 README |

### 참고: 우리가 쓸 만한 태그 글 수 (2026-11-24 Danbooru)

| 분류 | 태그 (글 수) |
|---|---|
| 피부 | `colored skin` 223,119 · `blue skin` 42,539 · `green skin` 32,674 · `grey skin` 24,842 · `red skin` 20,336 · `purple skin` 19,214 · `black skin` 15,458 · `pink skin` 14,482 · `yellow skin` 8,641 · `orange skin` 4,049 · `aqua skin` 2,231 · `multicolored skin` 25,221 · `two-tone skin` 19,432 · `colored extremities` 19,667 · `body markings` 17,637 · `scales` 29,914 |
| 머리 모양 | `bob cut` 144,350 · `drill hair` 136,471 · `asymmetrical hair` 38,205 · `hime cut` 32,764 · `wolf cut` 9,542 · `tentacle hair` 42,686 · `fiery hair` 4,796 · `liquid hair` 2,441 · `crystal hair` 2,249 · `snake hair` 2,819 · `glowing hair` 2,500 |
| 머리 색 나눔 | `multicolored hair` 1,248,548 · `streaked hair` 462,464 · `two-tone hair` 419,709 · `gradient hair` 234,289 · `colored inner hair` 171,016 · `split-color hair` 33,123 · `colored tips` 28,200 · `white streaks` 32,634 · `red streaks` 29,170 · `pink streaks` 15,604 |
| 눈 | `symbol-shaped pupils` 262,888 · `heart-shaped pupils` 124,678 · `slit pupils` 95,938 · `colored sclera` 80,958 · `multicolored eyes` 70,164 · `glowing eyes` 64,409 · `empty eyes` 52,408 · `ringed eyes` 42,927 · `black sclera` 39,296 · `star-shaped pupils` 35,306 · `no pupils` 23,865 · `constricted pupils` 21,189 · `cross-shaped pupils` 20,128 · `yellow sclera` 19,139 · `gradient eyes` 14,110 · `third eye` 13,898 · `red sclera` 10,760 · `horizontal pupils` 7,531 · `heterochromia` 180,650 |
| 몸·종족 | `horns` 719,770 · `pointy ears` 629,504 · `cat girl` 179,056 · `fox girl` 157,195 · `feathered wings` 114,426 · `claws` 85,125 · `monster girl` 83,036 · `dragon horns` 81,519 · `dragon girl` 68,130 · `fins` 53,979 · `dragon tail` 51,023 · `personification` 48,397 · `fish tail` 30,321 · `head fins` 20,908 · `stitches` 20,199 · `extra arms` 16,494 · `mermaid` 16,517 · `insect wings` 15,328 · `extra eyes` 14,877 · `mechanical wings` 9,194 · `taur` 8,466 · `harpy` 6,871 · `lamia` 6,524 · `slime girl` 5,750 · `digitigrade` 4,187 · `plant girl` 3,516 · `spider girl` 3,446 · `centaur` 3,139 · `gills` 2,199 · `arachne` 1,413 · `bee girl` 1,206 · `jellyfish girl` 459 |
| 구도 | `full body` 1,339,481 · `multiple views` 285,287 · `reference sheet` 23,606 · `turnaround` 5,117 · (`character sheet`는 태그 아님) |

**읽는 법**: 수천 이하(`jellyfish girl`, `bee girl`, `arachne`)는 그 태그 하나로 기대하지 말고, **더 큰 태그 몇 개로 쪼개서** 쓴다. 예: `jellyfish girl` → `monster girl, translucent, tentacles, colored skin, blue skin` + 짧은 문장 한 줄. 몬스터 소녀 대부분이 이 경우다.

---

## 2. 프롬프트 기술

### 2-1. 문장보다 「진짜 태그」
- Anima는 태그·문장·섞은 것 모두 학습했다(공식). 한 가이드의 정리: **「정확한 겉모습은 태그, 관계·배치·장면 논리는 문장」**, 태그 묶음 뒤에 문장 1~2줄이 가장 안정적.
- 그러니 **외형 특징은 글 수 많은 태그로 박고**, 태그가 없는 것(「뱀 꼬리 배 쪽만 금색 비늘」)만 문장으로 짧게 쓴다.
- 태그 표기: 소문자, 밑줄 대신 띄어쓰기(`slit pupils`). `score_*`만 밑줄. 괄호가 든 태그는 `\(` 로 감싼다(`slime \(substance\)`).
- 공식 카드: 문장만 쓸 때는 **두 문장 이상**(너무 짧으면 엉뚱한 그림).

### 2-2. 순서
- 공식 순서: `[품질·메타·연도·안전] [1girl 등] [캐릭터] [작품] [작가] [일반 태그]`. 원작 캐릭터·작가 태그를 안 쓰는 우리는 사실상 `품질 → 1girl, solo → 일반 태그`.
- **일반 태그 안에서는 앞쪽이 더 세다**는 것이 SDXL 계열 공통 경험(Illustrious 가이드 「뒤로 갈수록 묽어짐」). Anima는 공식 카드가 「섹션 안 순서는 상관없음」이라고 해서 **Anima에서는 효과가 약할 수 있음 (미확인)**. 그래도 손해는 없으니 **종족·몸 → 피부 → 머리 → 눈 → 옷** 순으로 둔다.
- 서로 부딪히는 태그를 넣지 않는다(`short hair` + `very long hair`, `extreme close-up` + `full body`).

### 2-3. 세기(가중치)
- 공식 카드: 가중치는 되지만 **SDXL보다 큰 값이 필요**(예 `(chibi:2)`).
- 반대 주장: 한 Civitai 글은 「Qwen이 `(tag:1.3)`을 글자 그대로 읽어 망가진다」고 함. 이 글은 Forge 계열 기준일 수 있어 **ComfyUI에서는 (미확인)**.
- 권장: 같은 seed로 `(slit pupils:1.6)` 있음/없음 A/B 1회 비교 후 결정. 세기를 쓰더라도 **한 캐릭터에 1~2곳**(가장 약한 몬스터 부위)만.

### 2-4. 물건마다 색 붙이기
- 색은 **반드시 물건 낱말 바로 앞**: `black jacket`, `white dress`, `gold trim` — 이런 「색+물건」 태그는 Danbooru에 실제로 많다(`black jacket` 409,624).
- 맨 색 낱말만 떼어 쓰면(`pink, black`) 아무 데나 번진다.
- 머리 두 색은 태그 조합으로: `black hair, colored inner hair, pink hair` 또는 `black hair, pink streaks`. `pink inner hair`는 태그가 아니어서(0건) 문장 인코더 해석에 맡기는 셈 — Anima는 글 인코더가 문장을 읽으므로 될 수도 있음 (미확인), A/B 비교.
- **색 가짓수 줄이기**: 한 캐릭터 프롬프트에 색 낱말 4~5개 이하. 많을수록 섞인다.

### 2-5. 피부색
- `colored skin` + 구체 색(`blue skin`)을 같이. 위키: 구체 색 태그가 `colored skin`을 포함하는 관계.
- 손발만 색이 다르면 `colored extremities`, 여러 색이면 `multicolored skin` / `two-tone skin`, 무늬는 `body markings`.

### 2-6. 기본값을 밀어내는 부정 프롬프트
- 부정 프롬프트는 cfg가 1보다 클 때만 힘이 있다(cfg 4면 됨, Turbo cfg 1이면 거의 무력 — Civitai 35368).
- 원칙(여러 가이드 공통): **처음엔 짧게, 실제로 나온 실패만 추가**. 「SDXL에서 물려받은 100개짜리 부정」으로 시작하지 말 것.
- 캐릭터마다 **그 캐릭터에 안 맞는 기본값만** 넣는다: 머리색이 정해진 캐릭터면 `brown hair`, 동공이 특이하면 `round pupils`는 태그가 아니므로 대신 `brown eyes` 등 실제로 나온 색, 피부가 색이면 부정에 사람 피부 낱말 — 다만 「사람 피부」에 해당하는 Danbooru 태그는 없음. `pale skin`(77,274)은 원하는 색 피부까지 밀 수 있어 **넣지 않는 편이 안전** (미확인, A/B).
- 반대로 **원하는 것을 부정에 넣지 않기**(흰 배경을 원하면 `simple background`를 부정에 넣지 않음).

### 2-7. 품질·화풍 태그 (Anima 전용)
- 공식 기본 앞머리: `masterpiece, best quality, score_7, safe,` (Aesthetic은 품질 태그가 꼭 필요하지 않음, `masterpiece, best quality,`는 안전).
- **Aesthetic에서는 `score_*`를 긍정·부정 양쪽에 다 넣지 말 것**(공식 경고).
- 공식 부정: `worst quality, low quality, score_1, score_2, score_3, artist name, blurry, jpeg artifacts, chromatic aberration`.
- 연도 태그(`year 2025`, `newest`)는 「사실이 아니라 그림 느낌 조절」(Civitai 35368). 최신 서브컬처 게임 느낌 쪽으로 당길 때 시험해 볼 만함.
- 작가 태그는 `@이름` 형식이어야 힘이 있음(공식). **우리는 살아 있는 작가 이름을 쓰지 않으므로 해당 없음.** 대신 화풍은 ① 우리 스타일 LoRA ② 화풍 낱말(`flat color`, `cel shading`, `thick outlines` 등)로 정한다.

### 2-8. 지역 나눠 프롬프트(색 번짐 막기)
- **BREAK**: 한 Civitai 글은 Anima에서 「BREAK만 제대로 되는 구분자」라고 하지만 근거는 글쓴이 한 명. **ComfyUI 기본 `CLIPTextEncode`는 BREAK를 특별히 처리하지 않는 것으로 알려짐 (미확인)** — Forge/A1111 Regional Prompter는 Anima를 Latent·Attention 모드로 지원.
- ComfyUI 기본 `Conditioning (Set Area)` + `Combine`은 Anima에서 **오류 보고**, `Conditioning (Set Mask)`는 됐다는 보고(Anima 토론 #76).
- Anima 전용 노드:
  - `Comfyui-Anima-Regional-Conditioning` (Sen-sou) — 마스크별 프롬프트, 실험판, Anima 전용.
  - `ComfyUI-MoonNodes`의 `Moon Anima Regional Patcher` — BREAK로 나눈 프롬프트 + 마스크 목록. 끝 지점 0.6~0.8 권장(경계선 줄임).
  - toyxyz `Anima_ControlNet-LLLite`의 **regional** 어댑터 — 색 칠한 영역 지도로 배치.
- **우리 경우(한 명 전신)**: 머리 영역/몸 영역을 마스크로 나누는 건 손이 많이 간다. 그보다 **① 색 가짓수 줄이기 → ② 나온 그림에서 머리·눈만 inpaint로 색 고치기**가 현실적. 지역 프롬프트는 「인간 상반신 + 거대한 하반신(라미아·아라크네)」처럼 위아래가 확실히 다른 캐릭터에만 시험.

---

## 3. 작업 순서 기술

| 기술 | 무엇을 해결 | Anima에서 | 메모 |
|---|---|---|---|
| **상반신 먼저, 전신은 나중** | 얼굴·눈·머리 디자인이 작은 크기에서 뭉개지는 것 | 됨(그냥 구도 태그) | `upper body` / `cowboy shot`으로 4~8 seed → 고른 것 기준으로 전신 |
| **Base로 탐색, Aesthetic로 마무리** | Aesthetic 판의 평균 당김 | 됨(모델 파일 바꿈) | 공식: Base = 가장 다양. 탐색은 Base(또는 다른 Anima 미세조정판), 마무리 img2img만 Aesthetic 0.3~0.4. (실제 효과는 우리 PC에서 A/B 필요, (미확인)) |
| **FaceDetailer / ADetailer** | 전신에서 작은 얼굴·눈 | 됨(모델과 무관하게 잘라서 다시 샘플링) | **우리 ComfyUI에 Impact Pack 없음** → 설치 필요. 한 Anima 가이드 기본값: 얼굴 denoise 0.26 · 눈 0.24 · 손 0.40. 눈만 다시 그릴 땐 프롬프트에 눈 태그만. |
| **inpaint로 머리·눈 고치기** | 색 번짐·평범한 머리 | 됨(기본 노드) | 가이드 값: 작은 수정 0.4 · 기본 0.6 · 큰 변경 0.75. **마스크 안에 들어갈 것만** 프롬프트에 씀(`pink streaks, black hair`). |
| **우리 그림에서 img2img** | 다시 뽑으면 평범해지는 것(강도 유지) | 됨 | 가이드 값: 다듬기 0.3 · 기본 0.5 · 많이 바꿈 0.7. 약 1메가픽셀 유지(너무 크면 늘어남·겹침). 고른 상반신을 「색·덩어리 밑그림」으로 써서 전신 구도로 다시 그리는 식. |
| **LLLite (ControlNet 대신)** | 포즈 바꾸기 · 우리 스케치/선화로 실루엣 고정 | **됨, 단 전용 노드** | 우리 PC에 `anima-lllite-any-test-like-v2` 있음(controlnet·model_patches 두 곳). any-test = 대충 그린 스케치·선화로 구도 유도 + 흑백 그림 색칠. Comfy-Org 저장소에 scribble 모델도 있음. `v2`만 Base 1.0용, 나머지는 옛 Preview3용. toyxyz판 = 영역 지도·3D 포즈(뼈대 그림 아님, 모양 있는 3D 인형 그림). |
| **포즈 전용 어댑터** | 서 있는 자세만 나오는 것 | 실험판 | Claquasse `Anima-Control-Pose` Preview-2: DWPose 뼈대 그림 입력, 세기 0~2. 비상업 라이선스. |
| **IP-Adapter (우리 그림을 참고로)** | 같은 캐릭터 유지 | **노드만 있음** | `comfyui-anima-ipadapter`(Wenaka2004, SigLIP2 사용). README에 가중치 파일 링크 없음, v1·v2 파일은 안 맞음 → **지금 바로 쓸 수 있다고 보기 어려움 (미확인)**. Claquasse 쪽 IP-Adapter·얼굴 유지 모듈은 「예정」. SDXL용 IPAdapter_plus는 구조가 달라 안 됨. |
| **디자인 시트 구도** | 정면 전신 + 얼굴 크게를 한 장에 | 됨(태그) | `reference sheet`(23,606) · `multiple views`(285,287) · `turnaround`(5,117). 한 장에 여러 뷰가 들어가면 각 얼굴이 더 작아지는 단점 — **얼굴 크게 뷰는 따로 생성 후 붙이는 편이 깨끗** (경험칙, (미확인)). |
| **색 보정 단계** | 마지막에 채도가 평범해짐 | 모델 밖 | 그림 편집기에서 색상·채도 조정 또는 우리 팔레트로 맞춤 → 그 그림으로 낮은 img2img(0.2~0.3)로 다시 정리. |
| **여러 seed 비교** | 한 장 보고 판단 | — | 가이드: 프롬프트 판단 전 **최소 4 seed**. 배치 1로 여러 번 돌려 seed를 다르게. |
| **와일드카드(무작위 줄)** | 사람이 짜도 평균으로 모이는 것 | 됨(노드에 따라) | `__name__` 형식. 「머리 모양」「동공」「피부 무늬」 목록에서 강제로 하나씩 뽑아 조합을 넓힘. |

### 우리 PC 상황 (2026-11-24 확인)
- diffusion_models: `anima_aestheticV11` · `anima_turbo` · `Nya-Iris_Anima_Base1-V2.0` · `WAI-ANIMA1` (**순수 Anima Base는 없음** — Base 계열 다양성을 쓰려면 받거나, Nya-Iris(Base1 기반 미세조정, 성격 (미확인))로 시험).
- LLLite: `anima-lllite-any-test-like-v2` 있음. `ComfyUI-Anima-LLLite` 노드 설치 여부는 custom_nodes 목록에 안 보임 → (미확인, 기본 노드로 되는지 확인 필요).
- custom_nodes: AdvancedLivePortrait · GGUF · KJNodes · PixelSmile · See-through · controlnet_aux. **Impact Pack(FaceDetailer) 없음.**

---

## 4. Anima가 무엇이고 무엇이 되나

| 항목 | 내용 |
|---|---|
| 정체 | CircleStone Labs + Comfy Org의 **2B 애니 모델**. NVIDIA **Cosmos-Predict2-2B** 기반(DiT 계열) — **SDXL 계열이 아님**. 글 인코더 = **Qwen3 0.6B**, VAE = Qwen-Image VAE. |
| 판 | Base(가장 다양, LoRA 학습용) · Aesthetic(일관된 고품질 기본 화풍, 우리는 v1.1) · Turbo(cfg 1·8~12 steps, 다양성 ↓) |
| 권장 값 | 512²~1536² · 30~50 steps · cfg 4~5(가이드는 3~6) · er_sde = 평평한 색·또렷한 선 · euler = 조금 더 창의적 · dpmpp_2m_sde = 더 다양(지나칠 수 있음) |
| 프롬프트 | 태그·문장·섞기 · 소문자·띄어쓰기 · 작가 `@` · 가중치는 SDXL보다 크게(공식) · 문장만이면 2문장 이상 |
| 약점 | 실사 약함(의도) · 긴 글자 · 손(특히 작가 태그와 함께, 프리뷰 시절 리뷰) · 글 인코더가 작아 복잡한 자세·구도 문장은 약함(리뷰 주장) · SDXL보다 느림 |
| 라이선스 | 모델·파생·LoRA는 비상업. **생성한 그림은 상업 사용 가능**(공식). |
| ComfyUI 지원 | 기본 지원(diffusion_models / text_encoders / vae 폴더). txt2img · img2img · inpaint · LoRA = 기본 노드로 가능(모델 종류와 무관한 기능). |
| ControlNet | SDXL ControlNet ✕. **LLLite**(Comfy-Org: any-test-like-v2·scribble / toyxyz: regional·3D pose·3D pose+outline, Base 1.0 학습) ○. 포즈 어댑터(Claquasse, 실험) ○ |
| IP-Adapter | SDXL용 ✕. Anima용 노드 있음, 공개 가중치 불분명 → △ (미확인) |
| 지역 프롬프트 | 기본 Set Area+Combine 오류 보고 · Set Mask 됨 보고 · 전용 노드 2종 + LLLite regional ○ |

---

## 5. 우리 경우 추천 순서

> 원칙: **한 번에 전신 완성 X → 디자인(상반신) 확정 → 전신으로 옮기기 → 작은 부위 다시 그리기 → 마무리.** 각 단계에서 「평균으로 돌아간 부분」만 고친다.

1. **디자인 한 줄 정하기 (사람)** — 캐릭터마다 「눈에 박히는 3가지」(예: 파란 피부 · 세로 동공 노란 눈흰자 · 비대칭 촉수 머리)를 먼저 적는다. 프롬프트는 이 3가지를 **맨 앞에, 실제 태그로**.
2. **탐색 (상반신, 빠르게)** — 1024×1024(또는 832×1216) · `upper body` 또는 `cowboy shot` · 태그 40~60개 · 200토큰 안 · **8 seed**. 모델은 Aesthetic와 Base 계열(또는 Turbo로 빠르게)을 같은 seed로 A/B. sampler는 er_sde 기본, 너무 평범하면 euler / dpmpp_2m_sde 시험.
3. **고르고 고치기** — 가장 센 1장을 고름. 평범해진 곳만 inpaint: 머리 색·모양(0.6), 눈(0.4~0.6, 눈 태그만). 필요하면 그림 편집기로 색 보정.
4. **전신으로 옮기기** — 두 가지 중 하나:
   - (가) 같은 프롬프트에 `full body` + 고른 상반신 색을 살린 **img2img 0.5~0.65**(캔버스 1024×1536에 상반신을 위에 놓고 아래는 대충 칠한 밑그림).
   - (나) 우리가 대충 그린 전신 실루엣·선화 → **LLLite any-test-like-v2**로 구도 고정 + 같은 프롬프트. 꼬리·다리 개수 같은 몬스터 몸 구조를 지키기 좋음.
5. **작은 부위 다시 그리기** — 얼굴 FaceDetailer(0.26 안팎) · 눈 0.24 안팎 · 손 0.40 · 몬스터 부위(뿔·지느러미·꼬리 끝)는 마스크 inpaint. (Impact Pack 설치 필요)
6. **마무리** — Aesthetic v1.1 + 스타일 LoRA로 **img2img 0.3~0.4**(화풍만 통일, 디자인은 안 바뀌는 세기). 끝나면 1단계의 「3가지」가 살아 있는지 확인, 하나라도 평균으로 돌아갔으면 5단계로.
7. **기록** — 캐릭터마다 seed·프롬프트·denoise를 남김. 다음 캐릭터에서 잘 된 태그·실패한 태그 목록을 키움.

### 프롬프트 뼈대 (긍정)

```
masterpiece, best quality, safe,
1girl, solo,
[종족·몸] monster girl, lamia, scales, fins,
[피부] colored skin, blue skin, body markings,
[머리 모양] asymmetrical hair, tentacle hair,
[머리 색] black hair, colored inner hair, pink hair,
[눈] yellow eyes, slit pupils, black sclera,
[옷 실루엣 한 개] black bodysuit,
[디테일 한 개] gold trim,
[소품 한 개] choker,
[팔레트] limited palette, high contrast,
[화풍] flat color, cel shading,
[자세·배경] standing, full body, white background, simple background,
Her lower body is a long black snake tail with gold belly scales. Her hair ends in pink tentacles.
```

- 각 칸은 **1~3개**. 옷은 실루엣 1 + 디테일 1 + 소품 1을 넘기지 않음(옷 말이 늘수록 몸 쪽이 약해짐).
- 색 낱말 4~5개 이하, 모두 물건에 붙여서.
- 마지막 문장 1~2줄 = 태그가 없는 관계만(몸 구조·어디에 무엇이).
- `limited palette`·`high contrast`·`flat color`·`cel shading`은 Danbooru 태그 여부와 효과 (미확인) — A/B로 남길지 정함.
- 가장 약한 몬스터 부위 하나만 세기 올림 시험: `(slit pupils:1.6)` (ComfyUI에서 가중치 효과 (미확인)).

### 부정 뼈대

```
worst quality, low quality, artist name, blurry, jpeg artifacts, chromatic aberration,
[이 캐릭터에 실제로 나온 기본값만] brown hair, brown eyes,
[필요할 때만] multiple views, (전신 한 장일 때) / text, watermark
```

- Aesthetic에서는 `score_1, score_2, score_3`를 넣을지 말지 하나로 정함(긍정에 score를 안 쓰면 부정에만 두는 건 괜찮다는 해석 — 공식 문구는 「양쪽 다」 금지).
- 부정은 **실패를 본 뒤 하나씩** 추가. 원하는 것(흰 배경 등)과 겹치지 않게.
- 피부: 「사람 피부」에 해당하는 태그가 없으므로 부정이 아니라 **긍정 쪽 `colored skin` + 색 태그 + inpaint**로 해결.

---

## 6. 정리 — 효과 순으로 먼저 해 볼 것

1. 탐색을 **상반신·Base 계열**로 바꿔 Aesthetic와 같은 seed A/B (모델 다양성 확인).
2. 프롬프트를 **태그 40~60개·200토큰 안**으로 줄이고 종족·피부·눈을 앞에.
3. 머리·눈은 **inpaint로 따로** — 한 번에 맞추려 하지 않기.
4. Impact Pack 설치 → **FaceDetailer** 눈 다시 그리기.
5. 전신은 **우리 그림 img2img 또는 LLLite any-test**로 이어 받기.
6. 부정에 **보인 기본값만**(`brown hair` 등).
7. 지역 프롬프트·포즈 어댑터·IP-Adapter는 위가 다 된 뒤 필요한 캐릭터에만.

---

## 출처

- Anima 공식 README (CircleStone Labs): https://huggingface.co/circlestone-labs/Anima/blob/main/README.md
- Anima 공식 카드 미러(같은 내용 확인): https://huggingface.co/tanochwale/Anima
- Anima 토론 #76 — 지역 프롬프트 오류·해결: https://huggingface.co/circlestone-labs/Anima/discussions/76
- ComfyUI Anima 사용법(파일·LLLite): https://comfyui.nomadoor.net/en/basic-workflows/anima/
- Anima 프리뷰 실사용 리뷰(약점): https://lilting.ch/en/articles/anima-2b-anime-image-generation
- Civitai 35368 Anima 판·설정 가이드 (civarchive 사본): https://civarchive.com/articles/35368
- Civitai 31399 「프롬프트가 Anima를 망치는 법」(토큰·BREAK·가중치 주장): https://civarchive.com/articles/31399
- Civitai 37140 「Anima Made Easy」(denoise 기본값): https://civarchive.com/articles/37140
- Civitai 32568 Anima 지역 샘플러(검색 요약만): https://civitai.com/articles/32568/anima-crossover-couple-generation-using-regional-sampler
- Comfy-Org Anima-LLLite: https://huggingface.co/Comfy-Org/Anima-LLLite
- toyxyz Anima ControlNet-LLLite(영역·3D 포즈): https://huggingface.co/toyxyz/Anima_ControlNet-LLLite
- Claquasse Anima-Control-Pose: https://huggingface.co/Claquasse/Anima-Control-Pose
- Anima IP-Adapter 노드 설명: https://comfy.icu/node/AnimaIPAdapterApply · 저장소 https://github.com/Wenaka2004/comfyui-anima-ipadapter
- Anima 지역 조건 노드: https://www.localainews.co/news/comfyui/comfyui-anima-regional-conditioning-paints-prompts-in-bounded-regions/ · https://github.com/Sen-sou/Comfyui-Anima-Regional-Conditioning
- Moon Anima Regional Patcher: https://comfy.icu/node/MoonAnimaRegionalPatcher
- Regional Prompter(Forge, Anima 지원 표): https://github.com/hako-mikan/sd-webui-regional-prompter
- Illustrious 프롬프트 가이드(태그 확인·부정은 실패 뒤): https://bextoper.github.io/bex-s-Stable-Diffusion-and-Illustrious-Guide/illustrious_guide
- Illustrious 간단 가이드(색은 구체 색+물건): https://civitai.com/articles/23210
- Danbooru 위키 colored skin: https://danbooru.donmai.us/wiki_pages/colored_skin
- Danbooru 태그 글 수 API(2026-11-24 조회): https://danbooru.donmai.us/tags.json
- FaceDetailer 원리: https://stable-diffusion-art.com/inpaint-comfyui/
- SDXL 계열 FaceDetailer·Hires 템플릿(Animagine): https://github.com/answerbattery/comfy-workflows
