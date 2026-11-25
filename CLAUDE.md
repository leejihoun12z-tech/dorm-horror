# 기숙사 공포 미연시 (가제 미정) — Claude 작업 가이드

Godot 4.7 (GDScript) 1인칭 3D 공포 미연시예요. 던전 게임(MyGodotGame)과 **별개 프로젝트**예요.

## 현재 상태 (세션 시작 시 자동 로드)
@docs/STATUS.md

## 시작할 때
1. `git pull`로 최신을 받는다. 충돌이 나면 멈추고 사용자에게 알린다.
2. STATUS.md를 보고 이번 요청에 맞는 문서만 더 읽는다.

| 작업 | 먼저 읽을 문서 |
|---|---|
| 기획·흐름·시스템 | `docs/plan/dorm-horror-plan.md` (하루 흐름 §3) |
| 구현 방식·구조 | `docs/plan/tech-plan.md` |
| 세계·설정 | `docs/plan/setting-bible.md` (다 정하지 않는 원칙 §4) |
| 컨셉·공포 연출 | `docs/plan/dorm-horror-concept.md` |
| 아트·캐릭터 | `docs/plan/art-bible.md` |
| 3D 캐릭터 시험 | `docs/plan/char3d-test-plan.md` |

3. 문서와 요청이 부딪치면 작업 전에 사용자에게 확인한다. "문서 읽었어요" 같은 보고는 하지 않는다.

## 끝날 때 (의미 있는 변경이 있었을 때만)
- `docs/STATUS.md`의 "최근 완료"(10줄 이내)와 "다음 할 일"을 갱신한다.
- 결정은 해당 문서에 이유 한 줄과 함께 적는다. 구조 결정은 `docs/plan/tech-plan.md` 결정 기록에.
- 커밋하고 현재 브랜치에 `git push`까지 묻지 않고 한다.

## 사용자 작업 방식
- 한국어, 결론부터, 짧은 문장. 보고 = **처리한 내용 / 확인할 내용과 추천 / 다음 작업**.
- 상태 태그 [확정]/[작업값]/[후보]/[보류]/[폐기·대체]/[확인 필요]를 지킨다. 작업값을 확정으로 올리지 않는다. 이미 확정한 것은 다시 묻지 않는다.
- 값 정하기: 임시값 → (가능하면) 시뮬레이션 → 사용자 플레이로 고침. 사람 플레이 전에는 재미·조작감·무서움을 완료라고 하지 않는다.
- 누가 봐도 이상한 시각 결함(부유·관통·잘림)은 먼저 고치고, 사용자에게는 취향만 묻는다.
- 결제·외부 공개·되돌리기 어려운 삭제는 사용자 승인 없이 하지 않는다.
- 설정·미스터리는 다 정하지 않는다. 게임에서는 조각만 보여 준다(setting-bible §4).

## 엔진·코드 규칙
- Godot 4.7.x, Forward+, GDScript만. Godot 4 문법만(`@onready`, `@export`, `await`, `CharacterBody3D`).
- 탭 들여쓰기, snake_case 함수·변수, PascalCase 클래스, CONSTANT_CASE 상수. 정적 타입을 늘 쓴다.
- 씬과 스크립트는 기능별 폴더에 같이 둔다: `game/player/`, `game/world/`, `game/day/`, `game/dialogue/`. 데이터 표는 `data/`.
- 입력은 InputMap 액션으로만 받는다(`project.godot` [input]). 키 코드를 코드에 직접 쓰지 않는다.
- 씬 간 통신은 시그널, 전역 상태는 Autoload.
- 내용(기숙생·이상현상·수칙·업무·대사)은 코드가 아니라 데이터 표로 넣는다(tech-plan §3).

## 실행·확인
- 에디터 F5 = 시험 복도(`game/world/test_corridor.tscn`).
- 오류 검사: `godot --headless --path . --quit-after 120`
- 입력 확인: `godot --headless --path . -s res://tools/dev/check_input.gd`
- 화면 한 장: `godot --path . -s res://tools/dev/screenshot.gd -- --out=절대경로.png [--door] [--crouch]` (리눅스 서버는 `xvfb-run -a`로 감싸고 `--rendering-driver opengl3`). `--headless`로 찍으면 빈 화면.
- 정지 화면 확인은 "관찰"이다. 조작감은 사용자가 직접 해 봐야 한다.

## 아트 자료
- 캐릭터 그림 원본은 크기가 커서(약 1.6GB) 아직 **MyGodotGame 저장소** `assets/art_src/dorm/`에 있다. 쓸 그림만 골라 `assets/`로 옮긴다.
- 권리 규칙: Fab "NoAI" 상품을 AI 입력에 넣지 않음, Hunyuan3D 안 씀, Tripo 무료판 결과물은 상업 불가(시험용만). 자세히 `docs/plan/art-bible.md` §5.
