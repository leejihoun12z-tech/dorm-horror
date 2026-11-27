# 새 채팅 시작 안내 — 기숙사 공포 미연시 (2026-11-27)

_사용자: "신문사랑 미연시 공포 나누고, 미연시 공포 내용들 새 채팅에서 다시 시작하자. PC 연결해서."_
이 게임(기숙사 공포 미연시)은 이제 **PC에서 연 Claude Code 세션**에서 이어 간다. 클라우드 세션은 그래픽카드·ComfyUI·Blender·크롬에 닿지 않아 시안이 막혔다(11-27).
"마지막 신문사"(판타지 뉴스 기자 게임)는 별개 — 이 저장소에 섞지 않는다.

## 1. 새 채팅 여는 법 (PC)
1. PC에 저장소가 없으면: `git clone https://github.com/leejihoun12z-tech/dorm-horror.git` (있으면 `git pull`)
2. Claude 데스크톱 앱 → Claude Code → **새 세션** → 폴더로 `dorm-horror` 선택 (또는 터미널에서 그 폴더로 가서 `claude`)
3. 아래 첫 메시지를 붙여 넣는다. CLAUDE.md·STATUS.md는 자동으로 읽힌다.

```
기숙사 공포 미연시 새 채팅이야. docs/new-chat-start.md 를 읽고 이어서 해.
첫 작업: 룩 탐색을 이 PC ComfyUI로 돌려 줘 (docs/plan/look-exploration-20261127.md §4·§6).
보기는 corridor, room, stairs, laundry, lounge 5곳, 화풍은 전부. 모델 받기·설치는 먼저 물어보고 해.
```

## 2. 지금까지 정해진 것 (한 장 요약)
| 항목 | 상태 |
|---|---|
| 엔진 | Godot 4.7, GDScript, 1인칭 3D [확정] |
| 장르·설정 | 대학 여자 기숙사(인외+사람), 주인공 = 사감, 하루 = 아침 업무 → 낮 수리·민원 → 22:30 점호 → 심야 순찰 → 일지·회귀 [확정] (`docs/plan/dorm-horror-plan.md` §3) |
| 수위 | 피·고어 거의 없음, 점프스케어 적게, 공포 중심 = 불쾌한 골짜기, 강도 상한 3 [확정] |
| 캐릭터 표현 | **종이인형극 빌보드** [확정 방향] — 평소 앞·뒤 그림 + 연출 컷 풀일러 몇 장 + 특이사항 때만 빌보드 애니(사용자 생각, 확정 아님). 노드 `game/characters/paper_puppet.gd` (tech-plan §5-5-5) |
| 캐릭터 그림체 | ComfyUI L5 계열(아트 채팅), 명단 27명 후보 — 메인 고르기 대기 |
| **배경 룩** | **미정 — 사용자 감으로 고름.** 인형의 집도 확정 아님. 원하는 것: 바이럴급 퀄리티 + 우리만의 기발한 콘셉트 + 분위기 있는·특색 있는 조명 + 2.5D 이질감 연출 |
| 탐색 자료 | 감 잡기 보드 `docs/plan/vibe-board-20261127.md`(배경 콘셉트·2.5D·제4의 벽·시스템·2D 공포·조명, 참고 게임 89개 목록) · 룩 탐색 꾸러미 `docs/plan/look-exploration-20261127.md` |
| 3D 캐릭터(마네킹) | 종이인형 방향이라 중단 후보 — 사용자 확인 대기 |

## 3. 사용자가 원한 순서 (11-27)
1. **룩 정하기** — 우리 기숙사 공간 그림 위에 화풍 여러 개(룩 탐색) → 감 오는 2~3개 고르기
2. 고른 룩으로 밤 판·조명 섞기·종이인형 합성
3. 그다음에 배경 모델링 방식·낮밤 조명 방식 정하기 → 복도 한 칸 실제 품질 시험
4. 캐릭터는 그사이 1명 그림 묶음(앞·뒤·풀일러)부터
- 하지 말 것: 회색 상자 복도에 스타일 입혀 보는 렌더 시안(사용자: 차이를 못 느낌), 남의 스크린샷을 저장소에 넣기.

## 4. 룩 탐색 실행 메모 (PC)
- 필요: `sd_xl_base_1.0.safetensors`(checkpoints) · `controlnet-union-sdxl-1.0-promax.safetensors`(controlnet, xinsir의 `diffusion_pytorch_model_promax.safetensors` 이름 바꿈) · 있는 `animagine-xl-4.0-opt`
- 실행: `python tools/look/run_comfy_looks.py --spaces corridor,room,stairs,laundry,lounge --out "<ComfyUI>/output/dorm_look"` (220장, 장당 약 25초 가정)
- 처음 실행이라 노드 이름 오류가 나면 ComfyUI 업데이트 또는 스크립트 고침. 결과 비교표 `_sheet_style_*.jpg`를 사용자에게 보여 주고 고르게 한다.
- 클라우드 CPU 저화질 도구 `tools/look/run_cpu_looks.py`도 있음(장당 약 80초, 품질 낮음 — 비상용).

## 5. 작업 규칙 요약
- 한국어·결론부터·짧은 문장. 보고 = 처리한 내용 / 확인할 내용과 추천 / 다음 작업.
- 상태 태그 지키기, 작업값을 확정으로 올리지 않기, 사람 플레이 전엔 재미·무서움 완료라 하지 않기.
- 결제·외부 공개·되돌리기 어려운 삭제·설치는 먼저 묻기. 비상업 모델·Hunyuan3D·Fab NoAI 금지.
- 끝날 때 STATUS 갱신(최근 완료 10줄) → 커밋 → push.
