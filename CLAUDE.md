# 기숙사 공포 미연시 (가제 미정) — Claude 작업 가이드

**Unreal Engine 5.8 (C++ 중심)** 1인칭 3D 공포 미연시예요(2026-11-28 Godot에서 바꿈, tech-plan §5-6). 던전 게임(MyGodotGame)과 **별개 프로젝트**예요.

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
| 건물·층·공간 | `docs/plan/building-layout.md` |
| 컨셉·공포 연출 | `docs/plan/dorm-horror-concept.md` |
| 아트·캐릭터 | `docs/plan/art-bible.md` |

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

## 엔진·코드 규칙 (Unreal, [작업값] tech-plan §5-6)
- Unreal Engine 5.8.x, Lumen, Windows. 설치 위치 `C:/Program Files/Epic Games/UE_5.8`.
- 게임 규칙·하루 진행·데이터·저장은 **C++**. 블루프린트는 자산 연결·연출 타이밍만 얇게. 편집기 자동화(레벨 짓기·자산 가져오기·찍기)는 Python(`Scripts/`).
- C++: Unreal 코딩 표준(클래스 접두어 `A`/`U`/`F`/`E`, PascalCase), `UPROPERTY`/`UFUNCTION`으로 편집기에 보이게.
- 입력은 Enhanced Input(Input Action + Mapping Context)으로만. 키를 코드에 직접 쓰지 않는다. 조작은 tech-plan D3 [확정].
- 내용(기숙생·이상현상·수칙·업무·대사)은 코드가 아니라 데이터 표로 넣는다: 원본 `data/*.csv` → DataTable (tech-plan §3).
- `.uasset`·`.umap`·큰 그림·소리는 Git LFS. `Binaries/`·`Intermediate/`·`Saved/`·`DerivedDataCache/`는 git 제외.
- Godot 파일(`project.godot`·`game/`·`addons/`·`tools/dev/*.gd`)은 [폐기·대체] — 회색 상자 판 시작 때 정리. 새 작업에 쓰지 않는다.

## 실행·확인
- 프로젝트: `DormHorror/` (C++ `Source/DormHorror/`, 편집기 Python `Scripts/`, 데이터 원본 `data/*.csv`).
- C++ 빌드(편집기가 닫혀 있어야 함 — 열린 편집기의 Live Coding이 막음): `"C:/Program Files/Epic Games/UE_5.8/Engine/Build/BatchFiles/Build.bat" DormHorrorEditor Win64 Development -Project=<절대경로>/DormHorror.uproject -WaitMutex`
- 회색 상자 다시 짓기(입력 자산·데이터 표·시험 복도, 여러 번 돌려도 됨): `UnrealEditor.exe DormHorror/DormHorror.uproject -ExecutePythonScript=DormHorror/Scripts/build_test_corridor.py -unattended`
- 스스로 플레이·찍기: `-ExecCmds="py DormHorror/Scripts/dev/shoot_play.py"` → `Saved/Screenshots/WindowsEditor/` (`shot showui` = UI 포함, `HighResShot`은 UI 빠짐) + 로그 `[DormShot]`.
- 사용자 걸어 보기: `DormHorror/walk.bat` (편집기 없이 게임 창).
- 소스 파일에 한글이 있으면 UTF-8 BOM으로 저장(MSVC).
- 편집기 Python 실행: `UnrealEditor.exe <uproject> -ExecCmds="py <스크립트> <인자>"` (편집기 열린 채). `-ExecutePythonScript`는 끝나면 편집기를 닫는다.
- 열린 편집기에 명령 보내기: 엔진의 `remote_execution.py` (프로젝트 설정 `bRemoteExecution=True`).
- 화면 한 장: 플레이 중 `HighResShot 1600x900 filename=...` → `Saved/Screenshots/WindowsEditor`.
- Python 이름 함정: Kismet 라이브러리는 접두어가 빠짐(`unreal.MaterialLibrary`), `LevelEditorPlaySettings`는 Python에 없음. 편집기 플레이는 120 fps 상한 — 실제 fps는 패키징 빌드로.
- 엔진 시험 프로젝트(참고): `Projects/dorm-engine-test/DormLookUnreal` · 기록 `docs/plan/engine-test-corridor.md`.
- 정지 화면 확인은 "관찰"이다. 조작감은 사용자가 직접 해 봐야 한다.

## 아트 자료
- 캐릭터 그림 원본은 크기가 커서(약 1.6GB) 아직 **MyGodotGame 저장소** `assets/art_src/dorm/`에 있다. 쓸 그림만 골라 `assets/`로 옮긴다.
- 권리 규칙: Fab "NoAI" 상품을 AI 입력에 넣지 않음, Hunyuan3D 안 씀, Tripo 무료판 결과물은 상업 불가(시험용만). 자세히 `docs/plan/art-bible.md` §5.
