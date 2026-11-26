# 3D 캐릭터 만드는 법 — 최신 자료 조사·검증 (2026-11-26)

_사용자 지시: "허깅페이스·깃허브·SNS 커뮤니티 최신 자료·스킬 찾아보고 작업 방식 피드백 검증". 조사 3갈래(오픈 모델·도구 / 서비스·커뮤니티 후기 / Godot) + 핵심 주장 2개는 원문 다시 확인. 상태: 전체 [후보]_

## 1. 결론
- **"그림에서 출발 → AI 3D"는 맞다. 다만 AI 3D는 '바탕 모양'까지만이다.** 커뮤니티·업체 도움말·참고 게임 모두 같은 말: 얼굴·질감·관절은 사람이(우리는 스크립트로) 다시 만든다.
- **Family Time도 AI 메시는 시험용이었다.** Steam 공개 문구: AI는 컨셉아트·임시 질감·"quick mesh tests"에만, 결국 손으로 만든 모델로 바꾼다(원문 확인 2026-11-26). → 우리 기준 그림의 깔끔함은 손 모델링에서 나온 것이다.
- **얼굴을 비우고 따로 그리는 계획은 맞다.** Tripo 공식 도움말도 "전신에서 얼굴은 작아서 흐려짐 → 머리는 따로, 눈은 따로 그려 바꿔라". 커뮤니티 조언도 "AI 얼굴은 움직이지 말고 표정 그림을 바꿔 끼워라".
- **마네킹은 AI 리깅·AI 부위 나누기가 필요 없다.** 딱딱한 부품 = 관절이라 Blender에서 잘라 붙이는 게 가장 확실하다.
- **무료 Tripo로는 시험이 금방 막힐 수 있다.** 무료 = 상업 불가·공개, 최신 P2.0은 무료에서 내려받기가 안 된다는 후기가 있음. → **로컬 무료 모델(TripoSG, MIT)을 같이 시험**한다.

## 2. 쓸 만한 것 (이 프로젝트 기준)
| 단계 | 도구 | 라이선스 | 이 PC(RTX 5060 8GB) | 근거 |
|---|---|---|---|---|
| 데포르메 전신 그림 | ChatGPT 이미지 편집 | 서비스 약관 | 웹 | 디자인 유지가 가장 쉬움 |
| 옆·뒷모습 | **Qwen-Image-Edit-2511 + Multiple-Angles LoRA** | Apache-2.0 | GGUF 양자화면 될 것 [확인 필요] | HF 2025-12, 각도 지정(0°·90°·180°) |
| 그림 → 3D 모양 | **TripoSG** | **MIT** | **8GB 공식** (README 확인) | 모양만 나옴 = 색은 어차피 우리가 칠함 |
| 그림 → 3D (비교) | Tripo 웹 P2.0 / P1.0(로우폴리) | 무료 = 상업 불가 | 웹 | P2.0(2026-09) 사각면·부위 분리·4방향 입력 |
| 그림 → 3D (대안) | ComfyUI-Trellis2 / Pixal3D | MIT | 저VRAM 모드 [확인 필요] | 2026-09·05 |
| 애니 전용 분리 생성 | StdGEN (몸·옷·머리 따로) | Apache-2.0 | `--low_vram` [확인 필요] | VRoid 학습 |
| 자르기·칠하기·내보내기 | Blender 스크립트 (+ mcp-for-blender) | MIT | 설치됨 | 손으로 깎는 일만 못 함 |
| 로우폴리 정리 | Decimate / QRemeshify 애드온 | GPL 애드온(결과물은 자유) | 설치 필요 | |

## 3. 안 맞는 것
| 도구 | 이유 |
|---|---|
| Hunyuan3D 전 계열 | 라이선스가 한국 제외 (2026년에도 그대로) |
| PartPacker·PartField·OmniPart | NVIDIA 비상업 코드 |
| MeshAnything V2·FastMesh | 비상업 라이선스 |
| Step1X-3D·TRELLIS.2 원본·Direct3D-S2 1024 | 24GB 이상 |
| Era3D | AGPL, 오래됨 |
| 자동 리깅(UniRig 등) | 딱딱한 부품 인형에는 쓸 데가 없음. 애니 캐릭터 검증 자료도 없음 |

## 4. 커뮤니티에서 확인된 실패·요령 (2026 레딧·업체 도움말)
- 실패: 얼굴 뭉개짐, 손가락 6개, 머리카락이 몸에 붙음, 통통한 비율에서 자동 리깅 깨짐, 한 덩어리 메시라 셰이더 작업이 어려움, 질감 흐림.
- 요령: 4방향(정면·옆·뒤) A/T포즈 입력 · 머리카락은 큰 덩어리·얇은 장식 빼기 · 머리는 따로 생성 · AI 질감 버리고 단색으로 다시 칠하기 · 메시 나누기 → UV 정리 → 재질 교체.
- 정리 시간: 캐릭터 하나 **몇 시간~하루**(업체의 "30분"은 믿지 않음). "로우폴리로 바로 뽑으면 모양도 질감도 별로, 고밀도로 뽑아 줄이는 게 낫다"는 후기도 있음.

## 5. Godot 쪽 확인
- **마네킹(부품 고정)은 지금 얼굴 투사 방식 그대로 쓰면 된다.** 부품은 휘지 않아 셰이더의 로컬 좌표가 고정된다.
- **나중에 피부처럼 휘는(스키닝) 캐릭터는 지금 방식이 안 된다**: Godot 4의 `vertex()` 위치는 이미 휜 뒤 값이라 얼굴 그림이 미끄러짐(Godot 포럼 2026-02). → Blender에서 얼굴 면만 정면 투사해 **UV2로 굽고**, 셰이더는 UV2 + instance uniform으로 표정 칸을 고른다.
- 쓸 수 있는 기능(4.4~4.6에 들어옴): SpringBoneSimulator3D(머리카락·치마 흔들림), LookAtModifier3D(시선), SkeletonModifier3D(꺾인 자세 덮어쓰기), IK 노드.
- 외곽선: 뒤집은 껍질은 각진 로우폴리에서 모서리가 갈라짐 → 매끈한 법선을 구워 쓰거나 후처리 외곽선.
- 걷기 동작: Quaternius Universal Animation Library = CC0, 무료판은 일부·전체는 유료($9.99~).

## 6. 출처 (주요)
- Family Time Steam AI 공개 문구: https://store.steampowered.com/app/5072600/Family_Time/ (원문 확인 2026-11-26)
- TripoSG: https://github.com/VAST-AI-Research/TripoSG (MIT, 8GB, 원문 확인 2026-11-26)
- Tripo 얼굴 도움말: https://www.tripo3d.ai/help/features/how-to-fix-ai-character-face-textures-with-tripo-ai
- Tripo P2.0 시험기: https://digitalproduction.com/2026/09/29/tripo-p2-0-put-quad-mesh-generation-to-the-test/
- 레딧 r/aigamedev 스냅샷(2026-10-02): https://reddit.sentinel-team.org/posts/1wsbnia/snapshots/2026-10-02T23%3A10%3A08.729506Z
- Qwen-Image-Edit-2511: https://huggingface.co/Qwen/Qwen-Image-Edit-2511 · 각도 LoRA: https://huggingface.co/fal/Qwen-Image-Edit-2511-Multiple-Angles-LoRA
- StdGEN: https://github.com/hyz317/StdGEN · ComfyUI-Trellis2: https://github.com/visualbruno/ComfyUI-Trellis2
- Hunyuan3D 라이선스: https://huggingface.co/tencent/Hunyuan3D-2/blob/main/LICENSE
- Godot 스키닝 전 위치 없음: https://forum.godotengine.org/t/getting-local-vertex-position-before-skinning-deformation/133883
- Quaternius UAL: https://quaternius.com/packs/universalanimationlibrary.html
- 확인 못 한 것: Family Time Patreon 글(접속 막힘), Tripo 가격 페이지(접속 막힘 → 제3자 자료), Qwen·StdGEN의 8GB 실제 동작.
