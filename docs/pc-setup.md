# PC 세팅 (사용자 컴퓨터, 한 번만)

이 게임은 클라우드 세션만으로는 못 하는 일이 있다: Godot 에디터로 직접 걸어 보기, 크롬으로 Tripo·GPT 웹 쓰기, Blender. 그래서 PC에서 아래를 한 번 해 둔다.

## 1. 받기
```
git clone https://github.com/leejihoun12z-tech/dorm-horror.git
```
- 이미 있는 Godot **4.7.2**로 이 폴더를 열고 F5 → 시험 복도에서 WASD·스페이스·Shift·E·F가 되는지 확인.

## 2. Claude와 연결 (둘 중 하나)
- **A. PC에서 Claude Code 세션 열기 (추천)**: Claude 데스크톱 앱 → Claude Code → 이 폴더를 열고 아래 첫 메시지를 붙여 넣는다. 크롬·Godot·Blender를 바로 쓴다.
- **B. 클라우드 세션이 PC 폴더를 쓰게 하기**: Claude 데스크톱 앱 → 설정 → Claude Code → Remote Control에서 이 폴더를 추가하고 켜 둔다. 그러면 클라우드 세션이 그 폴더를 쓰겠다고 요청할 수 있다(사용자 승인 창이 뜸).

첫 메시지 (A): **`docs/new-chat-start.md` §1을 쓴다** (2026-11-27 갱신 — 예전 「다음 할 일 2번(Family Time 3D)」 메시지는 [폐기·대체]).

## 3. 시험에 필요한 프로그램 (Claude가 설치 전에 물어봄)
| 프로그램 | 쓰는 곳 | 비용 |
|---|---|---|
| Godot 4.7.2 | 게임 | 무료 (이미 있음) |
| Blender 4.x | 로우폴리 몸·머리카락 정리, 리깅 | 무료 |
| Tripo 웹 (무료판) | 로우폴리 초안 (시험용, 상업 불가) | 무료 |
| ComfyUI (이미 있음, MyGodotGame 아트 작업) | 캐릭터 그림 · 배경 룩 탐색(SDXL + ControlNet union, `tools/look/`) | 무료 |
- 결제가 필요한 것(Tripo 유료 등)은 사용자 승인 없이 하지 않는다.
