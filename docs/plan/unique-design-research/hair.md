# 머리 모양·머리 색 조사 — 인외 미소녀 36명용

_조사일: 2026-11-24 · 담당: 아트 조사 · 목적: "흔한 AI 그림"(갈색 머리·그냥 긴 머리·그냥 단발)에서 벗어날 방법 찾기_

> **우리는 방법만 배운다.** 아래 캐릭터 이름은 "이런 방법을 쓴 예"로만 적었다. 이름·디자인·옷을 그대로 가져오지 않는다. 프롬프트에 캐릭터 이름 태그도 넣지 않는다.

## 0. 한 줄 결론

- 서브컬처에서 기억에 남는 머리는 **① 멀리서도 이름 붙일 수 있는 바깥 모양 하나 + ② 정해진 자리에 넣은 두 번째 색 하나 + ③ 진짜 머리로는 불가능한 것 하나**로 되어 있다.
- 인외 캐릭터는 여기에 **"머리가 그 종족의 몸이 된다"**(촉수·뱀·깃털·덩굴·불·물·수정)를 더하면 된다. 단보루에 이 태그들이 다 있다(`tentacle_hair`, `snake_hair`, `feather_hair`, `plant_hair`, `fiery_hair`, `liquid_hair`, `crystal_hair` …).
- 모델은 "여러 색 머리"라고만 하면 평균(갈색·회색)으로 뭉갠다. **종류 태그 + 각 색 태그 + 색 이름이 붙은 태그**(예: `streaked_hair, white_hair, red_streaks`)를 같이 써야 붙는다.

### 표시 규칙
- **✓** = 단보루에서 직접 확인함(태그 목록 API·위키·"같이 붙는 태그" 기록, 2026-11-24). 괄호 안 숫자 = 그 태그가 붙은 그림 수.
- **(미확인)** = 태그가 있는지 확인 못 함 / 없음. 쓰지 말거나 비슷한 확인 태그로 바꾼다.
- **(0 → ○○)** = 이름은 있지만 다른 태그로 넘겨지는 이름(별칭). 진짜 태그를 써야 한다.
- 캐릭터 예시 뒤 **✓** = 단보루 기록에서 그 캐릭터에 그 태그가 자주 붙는 것을 확인. ✓ 없는 예시는 조사자 기억 기반(다시 확인 안 함).

---

## 1. 머리 모양(색 말고 모양) 카탈로그

### 1-A. 바깥 덩어리 모양 — 멀리서 실루엣이 정해지는 것

| 유형 | 한 줄 설명 | 예시 캐릭터 | 왜 눈에 띄나 | 태그 |
|---|---|---|---|---|
| 드릴 머리 | 끝이 용수철처럼 꼬인 굵은 다발 | 토모에 마미(마도카) ✓ · 카사네 테토(UTAU) ✓ · 셀레스티아 루덴베르크(단간론파) ✓ · 브로냐 자이칙(붕괴3rd) ✓ · 요리가미 조온(동방) ✓ | 원기둥 + 나선 = 사람 머리에 없는 기계 같은 모양. 아주 작게 봐도 보임 | `drill_hair` ✓(136k) · `twin_drills` ✓(75k) · `single_drill` ✓(1.1k) · `tri_drills` ✓(164) · `quad_drills` ✓(1k) · `drill_sidelocks` ✓(10.6k) · `ringlets` ✓(9k, 가는 곱슬 다발) |
| 히메컷 | 앞머리 일자 + 귀옆 머리 일자 + 뒷머리 길게, 세 단 | 호라이산 카구야(동방) | 칼로 자른 듯한 직선이 얼굴을 액자처럼 감쌈. 공포물과 잘 어울림 | `hime_cut` ✓(33k) · `blunt_bangs` ✓(445k) · `blunt_ends` ✓(56k) |
| 해파리 컷 | 위는 둥근 짧은 층, 아래는 긴 층 — 해파리 모양 | 오로 크로니(hololive) ✓ · 카츠라기 이즈미 ✓ · 오사와 루리노 ✓ | 머리 한 덩이에 "짧음+긺" 두 실루엣. 해파리·버섯 계열 인외에 딱 | `jellyfish_cut` ✓(2.6k) |
| 울프컷·멀릿 | 위는 들쭉날쭉 층, 목뒤만 길게 | 여러 ZZZ·BA 캐릭터 | 끝이 뾰족한 가시 덩어리 → 짐승·야생 느낌 | `wolf_cut` ✓(9.5k) · `mullet` ✓(2.4k) · `choppy_bangs` ✓(11k) |
| 터무니없이 긴 머리 | 발끝보다 길어 바닥에 퍼짐 | 하츠네 미쿠 ✓ · 텐도 아리스(BA) · 테레사(붕괴3rd) · 라푼젤(NIKKE) | 머리가 "옷"이나 "배경"이 됨. 바닥에 고이게 하면 공포감 | `absurdly_long_hair` ✓(31k) · `very_long_hair` ✓(1.47m) · `hair_spread_out` ✓(50k) · `floating_hair` ✓(202k) |
| 큰 머리 | 부피가 아주 큰 머리 | — | 몸보다 머리가 큰 실루엣 = 만화적 과장 | `big_hair` ✓(14k) · `afro` ✓ · `huge_afro` ✓(46) · `beehive_hairdo` ✓(941) · `pompadour` ✓ · `fluffy_hair` ✓(6.5k) |
| 가늘고 납작한 가닥 여러 개 | 칼국수 면처럼 얇고 납작한 가닥 다발 | — | 끈·띠·지느러미 같은 질감. 해초·리본 인외에 | `kishimen_hair` ✓(2k) |
| 단발 변형 | 뒤는 짧고 앞이 긴 역단발 / 바가지 / 아주 짧은 컷 | — | 평범한 단발을 피하는 방법 | `inverted_bob` ✓(8k) · `bowl_cut` ✓(4.8k) · `pixie_cut` ✓(1.9k) · `short_hair_with_long_locks` ✓(72k, 짧은 머리 + 앞 가닥만 길게) |

### 1-B. 묶은 모양 — 묶음이 "물건·동물 부위"처럼 보이는 것

| 유형 | 한 줄 설명 | 예시 | 왜 눈에 띄나 | 태그 |
|---|---|---|---|---|
| 머리로 만든 동물 귀 | 묶음·삐침이 고양이·여우 귀처럼 섬 | 각청(원신) ✓ · 감우(원신) ✓ · 데히야(원신) ✓ · 토요사토미미노 미코(동방) ✓ · 타카오(벽람항로) ✓ | 진짜 귀 없이 "귀 실루엣"을 만듦. 인외 귀와 겹치면 귀가 4개처럼 보여 기묘함 | `hair_ears` ✓(6.9k) · `cone_hair_bun` ✓(22k) · `pointy_hair` ✓(9k) |
| 머리로 만든 뿔 | 꽉 묶은 원뿔 묶음이 뿔처럼 섬 | 한주리·춘리(스트리트 파이터) ✓ · 미오다 이부키(단간론파) ✓ · 엔텔레키아(명일방주) ✓ | 진짜 뿔이 있는 종족에 "가짜 뿔"을 더하면 뿔 개수로 장난 가능 | `hair_horns` ✓(7.7k) · `double_bun` ✓(186k) · `bun_cover` ✓(25k) |
| 머리로 만든 날개 | 옆머리가 날개처럼 펼쳐짐 | 하츠네 미쿠 ✓ · 타카네 루이(hololive) ✓ · 엘리라 펜도라(니지산지) ✓ · 미오·헬라구르(명일방주) ✓ | 머리 옆 실루엣이 가로로 넓어짐. 박쥐·새 인외에 | `hair_wings` ✓(1.4k) · 진짜 날개는 `head_wings` ✓(98k) |
| 고리 머리 | 묶은 머리를 고리(동그라미)로 말아 올림 | 곽청아(동방) ✓(`hair_rings` + `hair_stick`) | 속이 빈 고리 = 실루엣에 "구멍"이 생겨 멀리서도 보임 | `hair_rings` ✓(74k) · `braided_hair_rings` ✓(17k) · `single_hair_ring` ✓(7.7k) · `tri_hair_rings` ✓(25) · `quad_hair_rings` ✓(138) |
| 물건 모양 묶음 | 리본·하트·별·꽃·도넛 모양으로 묶음 | 산고노미야 코코미(원신) ✓(`bow-shaped_hair`) | "머리로 만든 장신구" — 불가능해서 기억됨 | `bow-shaped_hair` ✓(12k) · `heart_hair_bun` ✓(645) · `donut_hair_bun` ✓(4k) · `star-shaped_hair` ✓(103) · `flower-shaped_hair` ✓(614) · `triple_bun` ✓(141) |
| 꼬리 여러 개 | 묶음 3개·4개·5개 | — | 트윈테일보다 한 단계 더. 꼬리 많은 종족(여우·구미호) 암시 | `tri_tails` ✓(2.8k) · `quad_tails` ✓(8k) · `quin_tails` ✓(39) · `multi-tied_hair` ✓(12k, 한 가닥을 마디마디 묶음) |
| 앞으로 내린 묶음 | 꼬리머리를 가슴 앞으로 | 카기야마 히나(동방) | 뒤에 있어야 할 것이 앞에 → 낯섦 | `front_ponytail` ✓(9.5k) · `front_braid` ✓(232) |
| 갈라진·접힌 꼬리 | 꼬리 끝이 두 갈래 / 위로 접혀 올라감 | — | 뱀 혀·물고기 꼬리 같은 끝 모양 | `split_ponytail` ✓(3.5k) · `folded_ponytail` ✓(26k) |
| 머리 관 땋기 | 머리 둘레를 땋아 왕관처럼 | — | 위쪽 실루엣이 평평한 고리 | `crown_braid` ✓(38k) · `half_crown_braid`(미확인) |
| 짝짝이 트윈테일 | 양쪽 길이·높이가 다름 | — | 대칭을 깨서 눈이 감 | `uneven_twintails` ✓(2k) |

### 1-C. 머리 위 작은 장치 — 상반신 컷에서 잘 보이는 것

| 유형 | 한 줄 설명 | 예시 | 왜 눈에 띄나 | 태그 |
|---|---|---|---|---|
| 바보털(삐침) | 정수리에서 튀어나온 한 가닥 | 푸리나(원신) ✓ · 츠노마키 와타메(hololive) ✓ · 타카나시 호시노(BA) | 머리 꼭대기 실루엣. 하트·초승달 모양으로 바꾸면 기호가 됨 | `ahoge` ✓(1m) · `huge_ahoge` ✓(25k) · `heart_ahoge` ✓(19k) · `ahoge_wag` ✓(1.5k, 흔들림) · `star_ahoge` ✓(75, 약함) |
| 더듬이 머리 | 두 가닥이 곤충 더듬이처럼 | 프린츠 오이겐(벽람항로) ✓ | 벌레·나방 인외에 그대로 연결 | `antenna_hair` ✓(134k) · `heart_antenna_hair` ✓(655) |
| 위로 솟은 앞머리 두 덩이 | 정수리 앞쪽 양옆이 숟가락처럼 솟음 | 반딧불이(스타레일) ✓ · 브레머튼(벽람항로) ✓ | 위쪽 실루엣에 귀 같은 두 혹 | `hair_intakes` ✓(287k) · `single_hair_intake` ✓(16k) |
| 옆으로 뻗친 털 뭉치 | 머리 옆에서 삐져나온 뭉치(표정 따라 움직이기 좋음) | 코세키 비주(hololive) ✓ | 감정 표현용 "제3의 귀" | `hair_flaps` ✓(58k) · `expressive_hair` ✓(3.3k) |
| 앞머리 모양 바꾸기 | 송곳니처럼 뾰족 / 가운데 한 가닥 / 엇갈림 / 사선 / 아치 | — | 얼굴 바로 위라 가장 많이 보이는 곳. 36명 앞머리를 다 다르게 | `fanged_bangs` ✓(2.6k) · `center-flap_bangs` ✓(13k) · `crossed_bangs` ✓(114k) · `diagonal_bangs` ✓(9.7k) · `arched_bangs` ✓(5.9k) · `asymmetrical_bangs` ✓(50k) · `braided_bangs` ✓(19k) · `curtained_hair` ✓(56k) · `wispy_bangs` ✓(11k) |
| 귀옆 머리 | 얼굴 양옆에 길게 늘어진 가닥 | — | 얼굴 테두리 강조. 묶거나 고리를 달면 장치가 됨 | `sidelocks` ✓ · `long_sidelocks` ✓(40k) · `very_long_sidelocks` ✓(2k) · `low-tied_sidelocks` ✓(8.3k) · `asymmetrical_sidelocks` ✓(5.2k) · `single_sidelock` ✓(19k) · `sidelocks_tied_back` ✓(1.6k) |
| 목뒤 한 가닥 | 뒷목에만 길게 남긴 한 가닥 | — | 뒷모습 실루엣의 꼬리 | `lone_nape_hair` ✓(2.9k) |

### 1-D. 비대칭 — 한쪽만 다르게

| 유형 | 한 줄 설명 | 예시 | 왜 눈에 띄나 | 태그 |
|---|---|---|---|---|
| 한쪽 눈 가림 | 앞머리가 한쪽 눈을 덮음 | 아케론(스타레일) ✓ | 얼굴 절반이 숨겨짐 → 비밀·공포 | `hair_over_one_eye` ✓(388k) · 두 눈 다 = `hair_over_eyes` ✓(33k) |
| 한쪽만 묶음 / 옆 꼬리 | 한쪽만 올려 묶음 | 나히다(원신) | 좌우 실루엣이 달라짐 | `one_side_up` ✓(157k) · `side_ponytail` ✓(242k) · `high_side_ponytail` ✓(6.2k) |
| 한쪽 밀기 | 한쪽 옆을 짧게 밈 | — | 미소녀에 드문 거친 요소 | `sidecut` ✓(3.2k) · `undercut` ✓(24k) |
| 비대칭 머리 전체 | 좌우 길이가 크게 다름 | — | — | `asymmetrical_hair` ✓(38k) |

### 1-E. 머리가 종족의 몸이 되는 것 ★ 인외 핵심

| 유형 | 한 줄 설명 | 예시 | 왜 눈에 띄나 | 태그 |
|---|---|---|---|---|
| 촉수 머리 | 머리 가닥(특히 귀옆 머리)이 촉수 | 니노마에 이나니스(hololive) ✓ · 칼리·잉클링(스플래툰) | 끝이 둥근 빨판 가닥 = 문어·오징어 인외 바로 읽힘 | `tentacle_hair` ✓(43k) · 스스로 움직임 `prehensile_hair` ✓(3.4k) |
| 뱀 머리 | 머리카락 일부/전부가 뱀 | 메두사(Fate) ✓ · 아자미(BA) ✓ | 머리 끝에 "얼굴"이 생김 = 가장 강한 공포 장치 | `snake_hair` ✓(2.8k) |
| 깃털 머리 | 머리카락 사이에 깃털이 자람 | 사일런스·라 플루마·피아메타(명일방주) ✓ · 장리·양양(명조) ✓ · 도키버드(VTuber) ✓ | 끝 모양이 깃털 → 새·하피 인외 | `feather_hair` ✓(8.4k) · 날개처럼 펴면 `hair_wings` ✓ |
| 식물 머리 | 잎·덩굴로 된 머리 / 머리에 덩굴 | 키이(몬무스) — 단보루 `plant_hair` 위키의 관련 항목 ✓ · 카멜리아(명조) ✓(`hair_vines`) | 머리카락 대신 잎 = 드라이어드·알라우네 | `plant_hair` ✓(1.3k) · `hair_vines` ✓(2.2k) · `hair_flower` ✓ · `flower_on_head` ✓(2.9k) · `mushroom_on_head` ✓(820) |
| 불꽃 머리 | 머리가 불로 되어 있음 | 마비카(원신) ✓ · 세나·브리기드(제노블레이드) ✓ · 미즈 하데스 ✓ | 끝이 타오르는 실루엣 + 빛 | `fiery_hair` ✓(4.8k) (불이 "붙은" 머리는 `burning_hair` ✓(96)) |
| 물·액체 머리 | 머리가 액체로 흐름 | 보틀 미쿠 ✓ · 코보 카나에루(hololive) ✓ | 끝이 물방울·튀는 물 | `liquid_hair` ✓(2.4k) · `slime_hair` ✓(435) |
| 수정 머리 | 보석·결정으로 된 머리 | 포스포필라이트(보석의 나라) ✓ · 쿠쿨칸(Fate) ✓ | 단단하고 각진 머리 = 불가능 그 자체 | `crystal_hair` ✓(2.2k) · `ice_hair` ✓(84, 약함) |
| 구름·연기 머리 | 구름 덩어리 머리 | — | 유령·안개 인외 | `cloud_hair` ✓(357, 약함) |
| 기계·전선 머리 | 케이블·기계 부품 머리 | — | 인형·안드로이드 인외 | `cable_hair` ✓(437) · `mechanical_hair` ✓(724) |
| 비치는 머리 | 머리카락 덩어리 너머가 비쳐 보임 | — | 유령 인외에 최적. 단보루 위키: 가닥 사이 틈이 아니라 덩어리 자체가 비칠 때 | `see-through_hair` ✓(818) (`transparent_hair`는 0 → 쓰지 않음) |
| 현실 불가능 머리 | 진짜 머리로 못 하는 모양 전체 | — | 보조 태그로 같이 넣으면 과장이 세짐 | `impossible_hair` ✓(927) · `living_hair` ✓(777) |

### 1-F. 머리와 장신구가 한 몸인 것

| 유형 | 한 줄 설명 | 예시 | 왜 눈에 띄나 | 태그 |
|---|---|---|---|---|
| 비녀가 고리를 꿰뚫음 | 비녀·막대가 묶음을 관통 | 곽청아(동방) ✓ | 장신구가 머리 구조를 "잡아 주는" 것으로 보임 | `hair_stick` ✓(30k) · `kanzashi` ✓(6.6k) |
| 뿔 사이·뿔 따라 머리 | 머리가 뿔 사이로 흐르거나 뿔에 감김 | — | 종족 부위와 머리가 엮임 | `hair_between_horns` ✓(1.5k) · `horn_ornament` ✓(21k) · `hair_through_headwear` ✓(3.6k) |
| 종족 모티프 머리 장식 | 상어·박쥐·뼈·해골·물고기 모양 핀 | 가우르 구라(hololive) ✓(`shark_hair_ornament`) · 사카마타 클로에 ✓(`x_hair_ornament`) | 핀 하나로 종족을 말함. 작지만 반복되면 기호 | `shark_hair_ornament` ✓(6.6k) · `bat_hair_ornament` ✓(6.4k) · `bone_hair_ornament` ✓(7.8k) · `skull_hair_ornament` ✓(13k) · `fish_hair_ornament` ✓(5.6k) · `jellyfish_hair_ornament` ✓(265) · `feather_hair_ornament` ✓(28k) · `x_hair_ornament` ✓(124k) · `cross_hair_ornament` ✓(19k) · `crescent_hair_ornament` ✓(19k) |
| 묶음을 덮는 덮개 | 경단 머리에 천·금속 덮개 | — | 묶음을 "부품"처럼 보이게 | `bun_cover` ✓(25k) |
| 머리띠 모양 | 다이아·무지개 머리띠 | 텐큐 치마타(동방) ✓(`rainbow_hairband`) · 이나니스 ✓(`diamond_hairband`) | 머리 위 선 하나로 색 포인트 | `hairband` ✓ · `diamond_hairband` ✓(6.4k) |
| 구슬·방울 | 머리 끝에 방울·구슬 | — | 끝을 무겁게 → 흔들림 | `hair_bell` ✓(32k) · `hair_beads` ✓(10k) · `hair_bobbles` ✓(70k) · `hair_tubes` ✓(108k) |

---

## 2. 머리 색 처리 카탈로그

단보루 "머리 색" 묶음(tag group:hair color)에 있는 여러 색 처리: `multicolored_hair`(큰 묶음) 아래 `two-tone_hair`, `split-color_hair`, `colored_inner_hair`, `colored_tips`, `gradient_hair`, `streaked_hair`, `striped_hair`, `spotted_hair`, `patterned_hair`, `rainbow_hair`, `roots_(hair)`, 그리고 `see-through_hair`.

| 처리 | 한 줄 설명 | 예시 | 왜 눈에 띄나 | 태그 |
|---|---|---|---|---|
| 두 색 머리(묶음) | 뚜렷한 두 색. 아래 종류와 같이 씀 | — | — | `two-tone_hair` ✓(420k) · `multicolored_hair` ✓(1.25m) |
| 좌우 반반 | 정수리에서 세로로 두 색 갈림 | 시오리 노벨라(hololive) ✓ · 쿠레이지 올리 ✓ · 네리사 레이븐크로프트 ✓ · 로잔나(NIKKE) ✓ · 다이얼린(ZZZ) ✓ · 우시자키 우루미(동방) ✓ · 나우(포켓몬) ✓ · 우타(원피스) ✓ | 얼굴 정면에서 바로 보임. 가장 "강한" 두 색. 흑백 갈림이면 범고래·판다 같은 동물 무늬로 읽힘 | `split-color_hair` ✓(33k) |
| 안쪽 색 | 겉은 한 색, 안쪽 층은 다른 색 | 엘렌 조(ZZZ, 검정+빨강) ✓ · 카즈사·플라나·아로나·사오리(BA) ✓ · 미나토 아쿠아·아마네 카나타·토코야미 토와·AZKi(hololive) ✓ · 리제 헬레스타(니지산지) ✓ · 스타킹(PSG) ✓ | 평소엔 차분, 움직이거나 머리를 넘길 때 색이 "번쩍". 공포물에서 정체 드러낼 때 쓰기 좋음 | `colored_inner_hair` ✓(171k) |
| 앞머리만 다른 색 | 앞머리 전체가 다른 색 | — | 얼굴 바로 위 색 = 상반신 컷에서 가장 잘 보임 | `colored_bangs` ✓(6.6k) |
| 줄(가닥) | 기본 한 색 + 몇 가닥만 다른 색 | 니엔(명일방주, 흰+빨강) ✓ · 프린츠 오이겐(흰+빨강) ✓ · 가우르 구라(회백+파랑) ✓ · 사카마타 클로에(회색+검정) ✓ · 아를레키노(원신, 흑백) ✓ · 브레머튼(분홍+회색) ✓ · 귀인 정사(동방, 검정+빨강·흰) ✓ · M4A1(소녀전선, 갈색·검정+초록) ✓ · 푸리나(흰+파랑) ✓ | 적은 양으로 큰 효과. 소녀전선 AR소대처럼 **팀·종족을 줄 색으로 구분**하는 데 씀 | `streaked_hair` ✓(462k) + 색 붙은 태그 `red_streaks` ✓(29k) · `blue_streaks` ✓(26k) · `white_streaks` ✓(33k) · `black_streaks` ✓(18k) · `pink_streaks` ✓(16k) · `purple_streaks` ✓(10k) · `blonde_streaks` ✓(5.9k) · `green_streaks` ✓(3.4k) · `aqua_streaks` ✓(3k) · `grey_streaks` ✓(2.7k) · `orange_streaks` ✓(2k) · 한 가닥만 `single_hair_streak` ✓ (`yellow_streaks`·`white_streak` 단수형은 없음/0) |
| 줄무늬 | 줄이 규칙적인 무늬(호랑이·얼룩말) | 의현(ZZZ) ✓ · 인드라(명일방주) ✓ · 호랑이·얼룩말(케모노 프렌즈) ✓ | 단보루 위키: 줄(streak)과 다름. 동물 털 무늬 | `striped_hair` ✓(2k) |
| 점무늬 | 둥근 점 무늬(표범·서벌) | 재규어·서벌(케모노 프렌즈) ✓ · 칼리(스플래툰) ✓ | 털 무늬를 머리로 옮김 | `spotted_hair` ✓(549, 약함) |
| 무늬 머리 | 별·하트 등 그림이 머리에 "찍힌" 것 | 사토노 다이아몬드·키타산 블랙(우마무스메) ✓ | 단보루 위키: 진짜 머리로 못 하는 무늬. 불가능 요소 | `patterned_hair` ✓(3.6k) |
| 별 머리 | 머리 안쪽에 별이 박힘(밤하늘) | 무나 호시노바(hololive) ✓ — 단보루 위키 대표 예 | 머리 안쪽이 우주. 불가능 요소 + 빛 | `starry_hair` ✓(1.8k) |
| 서서히 변함 | 한 색에서 다른 색으로 부드럽게 | 히지리 뱌쿠렌(동방, 보라→금) ✓ · 니노마에 이나니스(보라→주황) ✓ · 타카나시 키아라(주황→초록) ✓ · 반딧불이(스타레일) ✓ · 나키리 아야메·모모스즈 네네(hololive) ✓ | 실루엣 끝을 다른 색으로 "닫음" | `gradient_hair` ✓(234k) — 단보루 위키: 들어간 색을 전부 태그할 것 |
| 끝만 다른 색 | 끝이 뚝 끊기듯 다른 색(물에 담근 것처럼) | 유키하나 라미·하코스 벨즈(hololive) ✓ · 코코미(분홍+파랑) ✓ · 나히다(흰+초록) ✓ · 후 타오 ✓ · 훙·스즈란(명일방주) ✓ | 끝 색 = 종족 색(불꽃 끝, 독 끝, 피 끝) 넣기 좋음 | `colored_tips` ✓(28k) (`red_tips` 같은 색 붙은 형은 0 → 없음) |
| 뿌리만 다른 색 | 정수리 쪽만 다른 색 | — | 염색이 자란 느낌. 현실감 + 불량 느낌 | `roots_(hair)` ✓(8k) (`roots`는 0 → 별칭) |
| 무지개 | 여러 색 | — | 과하면 촌스러움. 한 부분(안쪽·끝)에만 | `rainbow_hair` ✓(2.6k) · `rainbow_gradient` ✓(3k) |
| 빛나는 머리 | 머리에서 빛이 나 얼굴·주변을 밝힘 | — | 어두운 기숙사 배경에서 광원이 됨 | `glowing_hair` ✓(2.5k) |
| 비치는 머리 | 머리 덩어리 너머가 비침 | — | 유령 | `see-through_hair` ✓(818) |
| 다른 판 머리 색 | 같은 캐릭터의 다른 색 판 | — | 변신·폭주 장면 차분에 | `alternate_hair_color` ✓(18k) |

### 2-1. 자주 보이는 기억에 남는 색 조합 (위 확인 결과에서)

| 조합 | 예 | 메모 |
|---|---|---|
| **흰·회색 + 원색 한 가닥(빨강/파랑)** | 니엔, 프린츠 오이겐, 구라, 푸리나 | 가장 흔한 "성공 공식". 흰 바탕이라 줄 색이 아주 잘 보임 |
| **검정 + 강한 안쪽 색(빨강·분홍)** | 엘렌 조, 카즈사 | 겉은 얌전, 안은 위험 — 이중성 캐릭터 |
| **흑백(검정+흰·회색) 갈림 / 줄** | 시오리, 클로에, 아를레키노 | 동물 무늬(범고래·판다) 또는 "두 얼굴" |
| **보라 → 따뜻한 색(주황·금) 그러데이션** | 이나니스, 뱌쿠렌 | 차가운 위 + 따뜻한 끝 = 신비 |
| **분홍 + 파랑·민트 끝** | 코코미 | 바다·해파리 계열 |
| **주황 + 초록 끝** | 키아라 | 보색에 가까운 강한 대비 |
| **분홍 + 회색 줄** | 브레머튼 | 단 색에 차가운 줄 = 세련 |
| **흰 + 초록 끝** | 나히다 | 식물 인외에 바로 응용 가능 |

공통점: **바탕은 흰·회색·검정처럼 무채색이거나 한 색이고, 두 번째 색은 채도 높은 원색 하나**. 두 색 다 중간색(갈색+베이지)인 경우는 거의 없다.

### 2-2. 조사한 게임별 경향 (짧게)
- **hololive·니지산지 VTuber**: 색 처리가 가장 과감. 반반·안쪽 색·별 머리·액체 머리가 흔함(작은 화면에서 알아봐야 해서).
- **원신·스타레일**: 그러데이션·끝 색 + 바보털·`hair_intakes` 조합이 많음.
- **명일방주·벽람항로**: 흰·회색 바탕 + 원색 줄. 동물 귀·뿔과 머리를 엮음.
- **블루아카이브**: 안쪽 색이 특히 많음(카즈사·아로나·플라나·사오리 ✓). 머리 위 헤일로가 실루엣을 대신함.
- **ZZZ**: 안쪽 색·줄무늬(동물 무늬) — 짐승 인외 참고에 좋음.
- **동방**: 모양 자체가 특이(고리 머리·귀 모양 머리·앞으로 내린 묶음·히메컷)하고 색은 단순한 편.
- **몬스터 소녀 전통(몬무스·몬스터걸 백과 등)**: 종족 부위를 머리로 바꾸는 방식(식물·슬라임·뱀·깃털)이 중심.
- 리버스: 1999·림버스 컴퍼니·퍼니싱·소녀전선2·NIKKE: 이번에는 확인된 예가 적음. 이 게임들은 머리보다 옷·실루엣 소품으로 개성을 내는 편으로 보임(조사자 인상, 확인 안 함).

---

## 3. 태그 한눈에 (확인된 것만, 그림 수 = 모델이 얼마나 잘 아는지 짐작용)

**아주 잘 앎(10만 이상)** — 그냥 써도 붙음
`multicolored_hair` · `two-tone_hair` · `streaked_hair` · `gradient_hair` · `colored_inner_hair` · `drill_hair` · `hair_intakes` · `hair_over_one_eye` · `double_bun` · `antenna_hair` · `hair_rings`(7.4만) · `twin_drills`(7.5만) · `floating_hair` · `crossed_bangs` · `blunt_bangs` · `side_ponytail` · `one_side_up`

**잘 앎(1만~10만)** — 대체로 붙음
`split-color_hair` · `colored_tips` · `red_streaks` · `blue_streaks` · `white_streaks` · `black_streaks` · `pink_streaks` · `hime_cut` · `absurdly_long_hair` · `tentacle_hair` · `cone_hair_bun` · `huge_ahoge` · `heart_ahoge` · `crown_braid` · `braided_hair_rings` · `bow-shaped_hair` · `big_hair` · `center-flap_bangs` · `bun_cover` · `hair_flaps` · `dragon_horns` 등

**조금 앎(1천~1만)** — 가중치(1.1~1.3) + 비슷한 태그를 같이
`hair_ears` · `hair_horns` · `feather_hair` · `fiery_hair` · `snake_hair` · `liquid_hair` · `crystal_hair` · `plant_hair` · `hair_vines` · `jellyfish_cut` · `wolf_cut` · `quad_tails` · `tri_tails` · `patterned_hair` · `striped_hair` · `starry_hair` · `glowing_hair` · `rainbow_gradient` · `colored_bangs` · `kishimen_hair` · `hair_wings` · `fanged_bangs` · `sidecut` · `prehensile_hair` · `expressive_hair` · `roots_(hair)`

**거의 모름(1천 미만)** — 혼자 쓰면 무시될 가능성 큼. 위 단계 태그로 받치기
`see-through_hair`(818) · `living_hair`(777) · `impossible_hair`(927) · `heart_hair_bun`(645) · `flower-shaped_hair`(614) · `spotted_hair`(549) · `slime_hair`(435) · `cable_hair`(437) · `cloud_hair`(357) · `star-shaped_hair`(103) · `ice_hair`(84) · `star_ahoge`(75) · `quin_tails`(39)

**없음 / 별칭이라 쓰면 안 되는 이름**
`silver_hair`(→ `grey_hair` 또는 `white_hair`) · `transparent_hair`(→ `see-through_hair`) · `hair_over_both_eyes`(→ `hair_over_eyes`) · `french_braid`(0) · `roots`(→ `roots_(hair)`) · `red_tips`·`blue_tips` 등 색 붙은 끝(없음 → `colored_tips` + 색) · `pink_inner_hair` 등 색 붙은 안쪽(없음 → `colored_inner_hair` + 색) · `white_streak`(단수, 0 → `white_streaks`) · `yellow_streaks`(0 → `blonde_streaks`) · `animal_ear_hair`(0 → `hair_ears`) · `hair_tentacles`·`hair_on_fire`·`water_hair`·`leaf_hair`·`hairpin`(0) · `galaxy_hair`·`gem_hair`·`pastel_hair`·`smoke_hair`·`mushroom_hair`·`cat_ear_hair`(없음)

---

## 4. 기억에 남는 머리 vs AI 평균 머리 — 규칙 12개

1. **멀리서 실루엣 하나.** 썸네일 크기·흑백으로 줄여도 "드릴", "고리", "뿔 묶음", "날개 머리"처럼 이름 붙일 바깥 모양이 하나 있어야 한다. 그냥 긴 머리·그냥 단발은 실루엣이 0개다.
2. **불가능한 것 딱 하나.** 별 박힌 머리, 무늬 찍힌 머리, 빛나는 끝, 촉수 가닥, 비치는 머리처럼 진짜 머리로 못 하는 요소를 하나 넣는다. 두 개 이상이면 시끄러워진다.
3. **인외는 "머리 = 몸"으로.** 종족 부위를 따로 붙이지 말고 머리에서 이어지게 한다(문어 → 촉수 귀옆머리, 하피 → 깃털 끝, 드라이어드 → 잎 머리, 유령 → 비치는 끝).
4. **두 번째 색은 자리 하나만.** 안쪽 / 끝 / 줄 / 앞머리 / 좌우 반반 중 하나만 고른다. 둘 이상 섞으면 모델이 평균색으로 뭉갠다.
5. **바탕은 무채색이나 한 색, 포인트는 원색.** 성공 예 대부분이 흰·회색·검정 바탕 + 빨강·파랑·분홍 같은 강한 한 색이다. 갈색+베이지처럼 둘 다 흐린 조합은 피한다.
6. **포인트 색은 몸·옷에 한 번 더.** 머리 줄 색 = 눈 색이나 옷 포인트 색. 반대로 머리 바탕색은 옷 주색과 다르게 해서 머리와 옷이 붙어 보이지 않게 한다.
7. **장신구는 모양 안에 녹인다.** 비녀가 고리를 꿰뚫고, 머리가 뿔 사이로 흐르고, 핀 모양이 종족을 말한다. 아무 리본이나 붙이는 건 개성이 아니다.
8. **비대칭 한 군데.** 한쪽 눈 가림·한쪽 묶음·한쪽 귀옆 머리만 길게. 완전 대칭 얼굴+머리는 평균으로 보인다.
9. **앞머리를 36명 모두 다르게.** 상반신 컷에서 가장 많이 보이는 곳이 앞머리다. 일자·송곳니·가운데 한 가닥·엇갈림·사선·땋은 앞머리를 돌려 쓴다.
10. **갈색 단색 금지(쓰려면 장치 2개).** 갈색·검정 단색은 모델 기본값과 같다. 꼭 써야 하면 강한 모양 1 + 불가능 요소 1을 같이.
11. **36명 겹침 표를 먼저.** 실루엣 6갈래(1-A~1-F) × 색 처리 6가지(반반·안쪽·줄·그러데이션·끝·무늬/별)로 칸을 만들고 한 칸에 한 명만. 같은 칸이 생기면 하나를 바꾼다.
12. **공포 쪽 장치를 머리로.** 이 게임은 기숙사 공포물이라 머리를 무섭게 쓸 수 있다: 바닥에 고인 터무니없이 긴 머리, 스스로 움직이는 머리, 눈을 다 가린 앞머리, 평소엔 숨어 있다 드러나는 안쪽 색, 끝에 얼굴이 있는 뱀 머리.

---

## 5. 모델이 무시하거나 뭉개는 것과 붙게 쓰는 법

| 문제 | 왜 생기나 | 이렇게 쓴다 |
|---|---|---|
| "여러 색 머리"가 갈색·회색으로 나옴 | `multicolored_hair`만 있으면 어느 색인지 모름 → 평균 | **종류 태그 + 각 색 태그 + 색 붙은 태그**를 같이: `multicolored_hair, white_hair, streaked_hair, red_streaks` / `two-tone_hair, black_hair, colored_inner_hair, red_hair` |
| 그러데이션이 한 색으로 끝남 | 색이 하나만 적힘 | 단보루 위키 규칙대로 **들어간 색을 전부** 적는다: `gradient_hair, purple_hair, orange_hair` |
| 안쪽 색이 안 보임 | 정면·차렷 자세에선 안쪽 층이 가려짐 | 안쪽이 드러나는 태그를 같이: `hair_flaps`, `floating_hair`, `wind`, `hair_spread_out`, 옆모습 `from_side`(같은 계열) |
| 색이 눈·옷으로 번짐 | 색 단어가 근처 물건에 붙음 | 눈·옷 색을 **따로 분명히** 적는다(`blue_eyes`, `black_dress` 등). 머리 포인트 색과 같은 색 옷은 꼭 필요할 때만 |
| "불꽃 같은 머리" 같은 말이 안 먹음 | 문장 설명은 태그보다 약함 | 문장 대신 **정확한 태그 이름**: `fiery_hair`, `tentacle_hair`, `hair_ears`, `hair_horns` |
| 드문 태그가 무시됨 | 그림 수 1천 미만이면 모델이 거의 모름(3장 표) | 가중치 `(tag:1.2)` 정도 + **잘 아는 이웃 태그로 받치기**: `see-through_hair` → `+ ghost, transparent` 계열 / `spotted_hair` → `+ leopard_print` 계열 / `cloud_hair` → `+ big_hair, fluffy_hair` |
| 그냥 긴 머리로 나옴 | `long_hair`만 쓰면 모델 기본 모양 | 길이 태그 하나 + **모양 태그 하나 + 앞머리 태그 하나**를 항상 같이: `very_long_hair, twin_drills, center-flap_bangs` |
| 모양 태그끼리 싸움 | `hime_cut` + `twin_drills` + `jellyfish_cut` 같이 서로 다른 실루엣을 동시에 | 실루엣 태그는 **하나만**. 작은 장치(바보털·더듬이)는 하나 더 괜찮음 |
| 별칭 이름을 씀 | `silver_hair`, `transparent_hair`처럼 0개짜리 이름은 학습 이름이 아님 | 3장 "없음/별칭" 목록에서 진짜 태그로 바꿈 |
| 갈색 머리가 계속 나옴 | 모델 기본값 | 머리 색을 프롬프트 **앞쪽**에 두고, 원하지 않으면 부정 프롬프트에 `brown_hair` |
| 특정 유명 캐릭터처럼 나옴 | 태그 조합이 그 캐릭터 그림과 똑같으면 모델이 그 캐릭터를 떠올림(예: `tentacle_hair` + 보라→주황 그러데이션) | **색 하나를 바꾸거나 모양 하나를 바꿔** 유명 조합을 피한다. 캐릭터 이름 태그는 절대 안 넣음 |
| 머리 "무늬"가 옷 무늬로 감 | `striped`, `star` 같은 단어가 옷에 붙음 | 머리 전용 태그(`striped_hair`, `starry_hair`, `patterned_hair`)를 쓰고, 옷은 민무늬로 적어 둔다 |

> 위 가중치·받치기 방법은 단보루 태그 그림 수를 근거로 한 **짐작**이다. 실제 Anima에서 몇 번 뽑아 붙는지 확인해야 한다. (시험 전)

---

## 6. 36명에 바로 쓰는 배분 틀 (제안)

실루엣 6갈래 × 색 처리 6가지 = 36칸. 한 칸에 한 명.

| | 좌우 반반 | 안쪽 색 | 줄(가닥) | 그러데이션 | 끝 색 | 무늬·별·빛 |
|---|---|---|---|---|---|---|
| A 바깥 덩어리(드릴·히메·해파리·울프·초장발·큰 머리) | | | | | | |
| B 묶음 모양(귀·뿔·날개·고리·물건 모양·여러 꼬리) | | | | | | |
| C 머리 위 장치(바보털·더듬이·hair_intakes·hair_flaps) | | | | | | |
| D 비대칭(눈 가림·한쪽 묶음·한쪽 밀기) | | | | | | |
| E 머리 = 몸(촉수·뱀·깃털·잎·불·물·수정·구름·전선·비침) | | | | | | |
| F 머리+장신구 한 몸(비녀·뿔 사이·종족 핀·덮개) | | | | | | |

- 종족별로 E줄을 먼저 채우고(인외 정체성), 나머지를 A~D·F로 나눈다.
- 같은 열(색 처리) 안에서도 바탕색·포인트색이 겹치지 않게 색 조합 칸을 따로 적는다.

---

## 7. 조사에 쓴 캐릭터 목록 (방법 참고용 · 130명)

✓ = 단보루 기록으로 그 머리 태그 확인. 나머지는 기억 기반.

| # | 캐릭터 (작품) | 머리 방법 |
|---|---|---|
| 1 | 니엔 (명일방주) ✓ | 흰 머리 + 빨강 줄 |
| 2 | 사일런스 (명일방주) ✓ | 깃털 머리 |
| 3 | 라 플루마 (명일방주) ✓ | 깃털 머리 |
| 4 | 피아메타 (명일방주) ✓ | 깃털 머리 |
| 5 | 미오 (명일방주) ✓ | 날개 머리 |
| 6 | 헬라구르 (명일방주) ✓ | 날개 머리 (남캐, 방법만) |
| 7 | 엔텔레키아 (명일방주) ✓ | 뿔 묶음 |
| 8 | 훙 (명일방주) ✓ | 끝 색 |
| 9 | 스즈란 (명일방주) ✓ | 끝 색 |
| 10 | 인드라 (명일방주) ✓ | 줄무늬 머리 |
| 11 | 이프리트 (명일방주) ✓ | 깃털 머리와 같이 태그됨 |
| 12 | 사리아 (명일방주) ✓ | 깃털 머리와 같이 태그됨 |
| 13 | 파인콘 (명일방주) ✓ | 깃털 머리와 같이 태그됨 |
| 14 | 스카디 (명일방주) | 은백 아주 긴 머리 |
| 15 | 카즈사 (블루아카이브) ✓ | 검정 + 분홍 안쪽 색 |
| 16 | 플라나 (블루아카이브) ✓ | 안쪽 색 |
| 17 | 아로나 (블루아카이브) ✓ | 안쪽 색 |
| 18 | 사오리 (블루아카이브) ✓ | 안쪽 색 |
| 19 | 아자미 (블루아카이브) ✓ | 뱀 머리와 같이 태그됨 |
| 20 | 세리나 (블루아카이브) ✓ | 깃털 머리와 같이 태그됨 |
| 21 | 시미코 (블루아카이브) ✓ | 깃털 머리와 같이 태그됨 |
| 22 | 타카나시 호시노 (블루아카이브) | 큰 바보털 |
| 23 | 소라사키 히나 (블루아카이브) | 아주 긴 흰 머리 + 뿔 |
| 24 | 텐도 아리스 (블루아카이브) | 터무니없이 긴 머리 |
| 25 | 시로미 이오리 (블루아카이브) | 아주 긴 트윈테일 |
| 26 | 푸리나 (원신) ✓ | 흰+파랑 줄 · 바보털 |
| 27 | 각청 (원신) ✓ | 원뿔 경단 = 머리 귀 |
| 28 | 감우 (원신) ✓ | 머리 귀 |
| 29 | 데히야 (원신) ✓ | 머리 귀 |
| 30 | 산고노미야 코코미 (원신) ✓ | 리본 모양 머리 · 분홍+파랑 끝 |
| 31 | 나히다 (원신) ✓ | 흰+초록 끝 · 한쪽 묶음 |
| 32 | 아를레키노 (원신) ✓ | 흑백 줄 · X 동공 |
| 33 | 마비카 (원신) ✓ | 불꽃 머리 |
| 34 | 후 타오 (원신) ✓ | 끝 색 · 그러데이션 |
| 35 | 벤티 (원신) ✓ | 그러데이션 (남캐, 방법만) |
| 36 | 방랑자·스카라무슈 (원신) ✓ | 끝 색 · 해파리 컷 (남캐) |
| 37 | 종려 (원신) ✓ | 그러데이션 (남캐) |
| 38 | 나비아 (원신) | 드릴 |
| 39 | 반딧불이 (스타레일) ✓ | 회색 + 그러데이션 · hair_intakes |
| 40 | 아케론 (스타레일) ✓ | 보라 초장발 · 한쪽 눈 가림 · 줄 |
| 41 | 모데이 (스타레일) ✓ | 그러데이션 (남캐) |
| 42 | 파이논 (스타레일) ✓ | 그러데이션 (남캐) |
| 43 | 로빈 (스타레일) | 머리 날개(진짜 날개) |
| 44 | 브로냐 자이칙 (붕괴3rd) ✓ | 트윈 드릴 |
| 45 | 엘리시아 (붕괴3rd) | 분홍 초장발 |
| 46 | 테레사 (붕괴3rd) | 터무니없이 긴 머리 |
| 47 | 뫼비우스 (붕괴3rd) | 뱀 모티프 |
| 48 | 엘렌 조 (ZZZ) ✓ | 검정 + 빨강 안쪽 색 |
| 49 | 다이얼린 (ZZZ) ✓ | 좌우 반반 |
| 50 | 의현 (ZZZ) ✓ | 줄무늬 머리 |
| 51 | 후 웨이 (ZZZ) ✓ | 줄무늬 머리 |
| 52 | 벨 (ZZZ) ✓ | 줄무늬와 같이 태그됨 |
| 53 | 와이즈 (ZZZ) ✓ | 줄무늬와 같이 태그됨 |
| 54 | 폰 라이칸 (ZZZ) ✓ | 끝 색 (남캐) |
| 55 | 카멜리아 (명조) ✓ | 흰·검정 + 덩굴·꽃 머리 |
| 56 | 칸타렐라 (명조) ✓ | 보라 초장발 + 해파리·꽃 |
| 57 | 장리 (명조) ✓ | 깃털 머리 |
| 58 | 양양 (명조) ✓ | 깃털 머리 |
| 59 | 로잔나 (NIKKE) ✓ | 좌우 반반 |
| 60 | 라푼젤 (NIKKE) | 터무니없이 긴 머리 |
| 61 | 프린츠 오이겐 (벽람항로) ✓ | 흰 + 빨강 줄 · 한 가닥 줄 · 더듬이 |
| 62 | 브레머튼 (벽람항로) ✓ | 분홍 + 회색 줄 · 트윈테일 |
| 63 | 타카오 (벽람항로) ✓ | 머리 귀 |
| 64 | M4A1 (소녀전선) ✓ | 갈색·검정 + 초록 줄 (팀 색 줄) |
| 65 | ST AR-15 (소녀전선) | 분홍 + 파랑 줄 (팀 색 줄) |
| 66 | 히지리 뱌쿠렌 (동방) ✓ | 보라 → 금 그러데이션 |
| 67 | 귀인 정사 (동방) ✓ | 검정 + 빨강·흰 줄 |
| 68 | 토요사토미미노 미코 (동방) ✓ | 뾰족 머리 = 머리 귀 |
| 69 | 곽청아 (동방) ✓ | 고리 머리 + 비녀 |
| 70 | 텐큐 치마타 (동방) ✓ | 무지개 머리띠 |
| 71 | 요리가미 조온 (동방) ✓ | 트윈 드릴 |
| 72 | 우시자키 우루미 (동방) ✓ | 좌우 반반 |
| 73 | 호라이산 카구야 (동방) | 히메컷 |
| 74 | 카기야마 히나 (동방) | 앞으로 내린 묶음 |
| 75 | 가우르 구라 (hololive) ✓ | 회백 + 파랑 줄 · 상어 핀 |
| 76 | 니노마에 이나니스 (hololive) ✓ | 촉수 머리 · 보라→주황 그러데이션 |
| 77 | 타카나시 키아라 (hololive) ✓ | 주황 + 초록 그러데이션 · 액체 머리와 같이 태그됨 |
| 78 | 사카마타 클로에 (hololive) ✓ | 회색 + 검정 줄 · X 핀 |
| 79 | 시오리 노벨라 (hololive) ✓ | 검정·회색 좌우 반반 |
| 80 | 코세키 비주 (hololive) ✓ | 안쪽 색 · hair_flaps |
| 81 | 오로 크로니 (hololive) ✓ | 해파리 컷 · 안쪽 색 |
| 82 | 무나 호시노바 (hololive) ✓ | 별 머리 |
| 83 | 아이라니 이오피프틴 (hololive) ✓ | 별 머리와 같이 태그됨 |
| 84 | 아윤다 리스 (hololive) ✓ | 별 머리와 같이 태그됨 |
| 85 | 우사다 페코라 (hololive) ✓ | 별 머리와 같이 태그됨 |
| 86 | 타카네 루이 (hololive) ✓ | 날개 머리 |
| 87 | 츠노마키 와타메 (hololive) ✓ | 양 뿔 + 바보털 |
| 88 | 미나토 아쿠아 (hololive) ✓ | 안쪽 색 |
| 89 | 아마네 카나타 (hololive) ✓ | 안쪽 색 |
| 90 | 토코야미 토와 (hololive) ✓ | 안쪽 색 |
| 91 | AZKi (hololive) ✓ | 안쪽 색 |
| 92 | 유키하나 라미 (hololive) ✓ | 끝 색 |
| 93 | 하코스 벨즈 (hololive) ✓ | 끝 색 |
| 94 | 네리사 레이븐크로프트 (hololive) ✓ | 좌우 반반 · 안쪽 색 |
| 95 | 쿠레이지 올리 (hololive) ✓ | 좌우 반반 |
| 96 | 코보 카나에루 (hololive) ✓ | 액체 머리 |
| 97 | 모리 칼리오페 (hololive) ✓ | 액체 머리·그러데이션과 같이 태그됨 |
| 98 | 나키리 아야메 (hololive) ✓ | 그러데이션 |
| 99 | 모모스즈 네네 (hololive) ✓ | 그러데이션 |
| 100 | 엘리라 펜도라 (니지산지) ✓ | 날개 머리 |
| 101 | 리제 헬레스타 (니지산지) ✓ | 안쪽 색 |
| 102 | 요루미 레나 (니지산지) ✓ | 좌우 반반 |
| 103 | 도키버드 (VTuber) ✓ | 깃털 머리 |
| 104 | 츠즈리 유기리 (VTuber) ✓ | 안쪽 색 |
| 105 | 키이 (몬무스) ✓ | 식물 머리 (위키 관련 항목) |
| 106 | 스우 (몬무스) | 슬라임 몸 + 더듬이 같은 머리 |
| 107 | 파피 (몬무스) | 하피 — 깃털 |
| 108 | 메두사 (Fate) ✓ | 뱀 머리 |
| 109 | 고르곤 (Fate) ✓ | 뱀 머리 |
| 110 | 센고쿠 나데코 (모노가타리) ✓ | 뱀 머리 |
| 111 | 포스포필라이트 (보석의 나라) ✓ | 수정 머리 |
| 112 | 다이아몬드 (보석의 나라) ✓ | 수정 머리 |
| 113 | 쿠쿨칸 (Fate) ✓ | 수정 머리 |
| 114 | 보틀 미쿠 ✓ | 액체 머리 (위키 예시) |
| 115 | 하츠네 미쿠 ✓ | 초장발 트윈테일 · 날개 머리 |
| 116 | 카사네 테토 ✓ | 트윈 드릴 |
| 117 | 토모에 마미 (마도카) ✓ | 트윈 드릴 |
| 118 | 셀레스티아 루덴베르크 (단간론파) ✓ | 트윈 드릴 |
| 119 | 앤초비 (걸즈 앤 판저) ✓ | 트윈 드릴 |
| 120 | 칸자키 란코 (아이마스) ✓ | 트윈 드릴 |
| 121 | 칼리 (스플래툰) ✓ | 점무늬 · 촉수 같은 머리 |
| 122 | 잉클링 소녀 (스플래툰) ✓ | 점무늬 · 촉수 머리 |
| 123 | 사토노 다이아몬드 (우마무스메) ✓ | 무늬 머리 |
| 124 | 키타산 블랙 (우마무스메) ✓ | 무늬 머리 |
| 125 | 세나 (제노블레이드) ✓ | 불꽃 머리 |
| 126 | 브리기드 (제노블레이드) ✓ | 불꽃 머리 |
| 127 | 재규어·서벌 (케모노 프렌즈) ✓ | 점무늬 |
| 128 | 시베리아호랑이·얼룩말 (케모노 프렌즈) ✓ | 줄무늬 |
| 129 | 나우 (포켓몬) ✓ | 좌우 반반 |
| 130 | 우타 (원피스) ✓ | 좌우 반반 |
| 131 | 스타킹 (PSG) ✓ | 안쪽 색 |
| 132 | 한주리·춘리 (스트리트 파이터) ✓ | 뿔 묶음 |
| 133 | 미오다 이부키 (단간론파) ✓ | 뿔 묶음 |
| 134 | 텐코 시부키 ✓ | 머리 귀 |
| 135 | 카츠라기 이즈미 ✓ | 해파리 컷 |

---

## 출처

- Danbooru 태그 묶음: [tag group:hair styles](https://danbooru.donmai.us/wiki_pages/tag_group:hair_styles) · [tag group:hair color](https://danbooru.donmai.us/wiki_pages/tag_group:hair_color)
- Danbooru 태그 위키(정의 확인): [hair_ears](https://danbooru.donmai.us/wiki_pages/hair_ears) · [hair_horns](https://danbooru.donmai.us/wiki_pages/hair_horns) · [hair_wings](https://danbooru.donmai.us/wiki_pages/hair_wings) · [colored_inner_hair](https://danbooru.donmai.us/wiki_pages/colored_inner_hair) · [colored_tips](https://danbooru.donmai.us/wiki_pages/colored_tips) · [streaked_hair](https://danbooru.donmai.us/wiki_pages/streaked_hair) · [split-color_hair](https://danbooru.donmai.us/wiki_pages/split-color_hair) · [gradient_hair](https://danbooru.donmai.us/wiki_pages/gradient_hair) · [patterned_hair](https://danbooru.donmai.us/wiki_pages/patterned_hair) · [starry_hair](https://danbooru.donmai.us/wiki_pages/starry_hair) · [see-through_hair](https://danbooru.donmai.us/wiki_pages/see-through_hair) · [tentacle_hair](https://danbooru.donmai.us/wiki_pages/tentacle_hair) · [liquid_hair](https://danbooru.donmai.us/wiki_pages/liquid_hair) · [jellyfish_cut](https://danbooru.donmai.us/wiki_pages/jellyfish_cut) · [plant_hair](https://danbooru.donmai.us/wiki_pages/plant_hair) · [fiery_hair](https://danbooru.donmai.us/wiki_pages/fiery_hair) · [crystal_hair](https://danbooru.donmai.us/wiki_pages/crystal_hair)
- Danbooru 태그 API(존재·그림 수): `danbooru.donmai.us/tags.json?search[name_comma]=…` · 캐릭터별·태그별 "같이 붙는 태그": `danbooru.donmai.us/related_tag.json?query=…` (2026-11-24 조회)
- 디자인 일반론: [Creative Bloq — 실루엣으로 알아보는 캐릭터](https://www.creativebloq.com/art/character-design/how-to-design-instantly-recognisable-characters-using-strong-silhouettes) · [RocketBrush — 모양 언어와 흑백 가독성](https://rocketbrush.com/blog/shape-language-in-game-character-design-how-to-make-characters-readable-and-consistent) · [Hosted.gg — 가챠 "같은 얼굴" 문제와 실루엣·색](https://hostedgg.com/blog/gacha-same-face-syndrome-culture) · [CLIP STUDIO — 강한 실루엣 디자인](https://www.clipstudio.net/how-to-draw/archives/157653)
