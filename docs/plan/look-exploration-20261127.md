# 룩 탐색 — 우리 기숙사 그림 위에 화풍 16가지 (모델링 전)

_작성 2026-11-27 · 사용자: "모델링 전에 레퍼런스 말고 이미지로 기숙사 내부를 구현하고, 거기서 그림체·룩을 다양하게 진행해 보고 싶어" · 도구 = PC ComfyUI(사용자 선택)_
_전부 [후보]. 결과를 보고 사용자가 감 오는 것을 고른다. 고르기 전에는 모델링·조명 방식을 정하지 않는다._

## 1. 방법 — 구도는 고정, 화풍만 바꿈
1. **구도 그림(이 클라우드 채팅, 끝)**: Godot 회색 상자로 공간 4곳을 실제 비율로 짓고 같은 카메라에서 찍음 → `tools/look/guides/`
   - `*_clay.png` 회색 렌더(사람 확인용) · `*_depth.png` 깊이(가까울수록 흰색) · `*_lines.png` 선(흰 선/검은 바탕)
   - 한 장 보기 `tools/look/guides/guides_sheet.jpg`
   - 다시 만들기: `godot ... -s res://tools/look/look_spaces.gd -- --dir=폴더` → `python tools/look/make_guides.py 폴더 tools/look/guides`
2. **화풍 입히기(PC)**: ComfyUI에서 SDXL + ControlNet(깊이 + 선)으로 구도를 붙잡고, 프롬프트로 화풍만 바꿈 → 같은 공간이 16가지로.
3. **비교**: 공간별 16칸 비교표 자동 생성 → 사용자 고르기 → 고른 2~3개만 밤 판·다른 공간·종이인형 합성으로 넓힘.

## 2. 공간 4곳
| 공간 | 들어 있는 것 |
|---|---|
| 복도 corridor | 양쪽 방문·번호판·신발장·소화전함·게시판·형광등·끝의 방화문과 비상구 표시·테라초 바닥 |
| 2인실 room | 창가 침대 2·책상과 선반 2·옷장 2·창문과 커튼·작은 냉장고·러그 |
| 사감실 office | 복도 쪽 창구·책상과 모니터·CCTV 화면 4·열쇠함·화이트보드·서류장·정수기·소파·벽시계 |
| 계단 stairs | ㄷ자 계단·계단참·난간·계단참 창·층 표시·방화문 |

## 3. 화풍 16가지 (`tools/look/looks.json`에서 고치거나 늘림)
S01 사실 사진 · S02 리미널 형광 · S03 인형의 집·미니어처 · S04 연필·볼펜 스케치 · S05 1비트 디더 · S06 애니 배경화(Animagine) · S07 유화 · S08 평면 색·깔끔한 선 · S09 흑백 + 빨강 한 색 · S10 종이·골판지 공예 · S11 옛 홍보 비디오(VHS) · S12 PS1 저해상도 · S13 수묵·먹선 · S14 오려 붙인 콜라주 · S15 연극 무대 세트 · S16 점토 스톱모션
- 프롬프트에 작가·게임 이름은 넣지 않음(화풍을 말로만 설명).

## 4. PC에서 할 일 (RTX 5060 8GB 기준)
1. 받기(한 번만, 합 약 9.4GB) — 사용권 확인함(2026-11-27, Hugging Face):
   - `ComfyUI/models/checkpoints/sd_xl_base_1.0.safetensors` — stabilityai/stable-diffusion-xl-base-1.0 (OpenRAIL++, 상업 사용 가능·사용 제한 조항 있음)
   - `ComfyUI/models/controlnet/controlnet-union-sdxl-1.0-promax.safetensors` — xinsir/controlnet-union-sdxl-1.0의 `diffusion_pytorch_model_promax.safetensors`를 이 이름으로 (Apache-2.0)
   - 애니 배경화(S06)는 이미 있는 `animagine-xl-4.0-opt.safetensors` 사용
2. ComfyUI 켜기 → 저장소 폴더에서
   `python tools/look/run_comfy_looks.py --out "<ComfyUI>/output/dorm_look"`
   (64장 큐 → 끝나면 `_sheet_corridor.jpg` 등 공간별 비교표 4장)
3. 너무 구도에 묶여 화풍이 약하면 `--cn 0.6`, 구도가 무너지면 `--cn 1.3`. 밤 판은 `--night`.
- 확인한 것(클라우드): 스크립트 문법·워크플로 JSON 출력(`--dry-run`)·비교표 함수. **실제 ComfyUI 실행은 PC에서 처음**이라, 노드 이름이 다르다는 오류가 나면 ComfyUI를 최신으로 올리거나 PC 채팅에서 고친다.

## 5. 다음
- 사용자가 비교표에서 감 오는 화풍 2~3개 고르기 → 그 화풍으로 4곳 밤 판 + 종이인형 1장 합성 → 그다음에 모델링·조명 방식 정하기.
