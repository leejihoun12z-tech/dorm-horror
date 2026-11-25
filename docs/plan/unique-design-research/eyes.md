# 눈 디자인 조사 — 동공·홍채·흰자·눈 주변 표식

_2026-11-24 · 인외 미소녀 36명용 조사 · 방법만 배움(캐릭터를 베끼지 않음)_

## 0. 결론 먼저

- **우리 그림이 "AI 같은" 이유**: 동그란 동공 + 흰 흰자 + 맨살 눈가. 서브컬처 게임은 이 셋 중 **최소 하나를 바꾼다**.
- 바꾸는 방법은 세 갈래: ① **동공 모양**(기호·세로·가로·고리) ② **흰자 색**(검정·노랑·짝짝이) ③ **눈 주변**(표식·아이라인·속눈썹 색·셋째 눈).
- 한 캐릭터에 **한 가지 강한 것 + 한 가지 보조**까지만. 다 넣으면 오히려 흐려진다.
- 모델(Anima)은 **전신 1024×1536에서 얼굴이 작으면 기호 동공을 못 그린다**. 흰자 색·아이라인·얼굴 표식처럼 **면적이 큰 것**이 전신에서 살아남는다. 기호 동공은 얼굴 고쳐 그리기(FaceDetailer/인페인트)로 넣는 게 기본.

> 근거: Danbooru 눈 태그 묶음(tag_group:eyes_tags) 전수, 태그별 글 수(post_count), 태그별 "같이 많이 붙는 캐릭터" 순위(related_tag). 캐릭터 예시는 그 순위에서 뽑았고, 순위에 없는 것은 (미확인).

---

## 1. 동공·홍채 종류 카탈로그

표의 "글 수"는 Danbooru에 그 태그가 붙은 그림 수(2026-11-24). **글 수가 많을수록 모델이 잘 안다** — 대략 1만 이상이면 믿을 만, 1천 아래면 잘 안 나옴.

### 1-1. 기호 모양 동공 (symbol-shaped pupils)

동공 자체가 기호. 위 묶음 태그는 `symbol-shaped_pupils`(하위 태그가 자동으로 포함).

| 모양 | 태그 | 글 수 | 예시 캐릭터 | 캐릭터 모티프와 연결 |
|---|---|---|---|---|
| 하트 | `heart-shaped_pupils` | 124,678 | (특정 캐릭터보다 표정용으로 많이 씀) | 매혹·홀림. 서큐버스·사랑 계열. 표정(홀림)과 섞이므로 "평소 눈"으로 쓰려면 다른 장치와 같이 |
| 별 | `star-shaped_pupils` | 35,306 | 호시노 아이(최애의 아이), 아이메스(명조), 나히다(원신), 호두(원신), 아이리스(홀로라이브), 키아나(붕괴3rd), 아리아(젠레스) | 아이돌·별·하늘. "빛나는 사람"이라는 성격을 눈으로 |
| 십자 | `cross-shaped_pupils` | 20,128 | 나히다(원신), 파워(체인소 맨), 방랑자(원신), 트리비(스타레일), 루나(퍼니싱), W(명일방주), 엘리라(니지산지) | 신성·종교·과녁. 나히다는 잎/풀 문양처럼 보이게 씀 |
| 마름모(다이아) | `diamond-shaped_pupils` | 18,259 | 엘리시아(붕괴3rd), 키레네(스타레일), 각청(원신), 종려(원신), 프리스티스·안젤리나·길베르타(명일방주), 아케론(스타레일), 크레이지 올리(홀로라이브) | 보석·결정·고귀함. 엘리시아는 요정·사랑, 키레네는 그 계승 |
| 꽃 | `flower-shaped_pupils` | 12,997 | 호두(원신, 매화), 하루우라라(우마무스메, 벚꽃), 스파클(스타레일), 카멜리아·금희(명조), 푸리나(원신) | 이름·고향 꽃을 눈에 새김. 호두 = 매화 = 저승 장례 |
| X | `x-shaped_pupils` | 9,269 | 아를레키노(원신), 크레이지 올리(홀로라이브), 에인·소프·말쿠트(블루 아카이브), 푸리나·콜롬비나·산드로네(원신), 라파엘로(벽람항로) | 금지·봉인·죽음·표식. 아를레키노 = "X 문양" 집행관 |
| 물방울 | `drop-shaped_pupils` | 4,414 | 푸리나·포칼로스·느비예트(원신, 물의 나라), 나비아·클로린드(원신) | 물 속성 캐릭터에게 물방울. 같은 나라 캐릭터끼리 공유 = 지역 표식 |
| 나비 | `butterfly-shaped_pupils` | 2,004 | 스파클·스파시(스타레일), 베아트리스(리제로), 우루하 루시아(홀로라이브) | 가면극·변덕·영혼. 스파클은 눈 아래 나비 무늬로도 반복 |
| 토끼 | `rabbit-shaped_pupils` | 3,326 | 우사다 페코라(홀로라이브) | 토끼 캐릭터 = 토끼 얼굴 동공. 종족을 눈에 그대로 |
| 전원 버튼 | `power_symbol-shaped_pupils` | 2,958 | 퍼플 하트 등 여신 변신(넵튠 시리즈), 젠트레야(VTuber) | "변신·기계 켜짐". 변신 후에만 나타나는 눈 |
| 시계 | `clock-shaped_pupils` | 1,333 | 토키사키 쿠루미(데이트 어 라이브) | 시간 능력. **한쪽 눈만** 시계 = 비대칭 |
| 조준선 | `crosshair_pupils` | 1,200 | 하츠메 메이(히로아카), 부트힐(스타레일), 아르젠티(스타레일), 순나(젠레스), 타카네 루이(홀로라이브) | 총잡이·사냥꾼·기계 눈 |
| 삼각 | `triangle-shaped_pupils` | 1,236 | 파루잔·라일라·시틀랄리·나히다(원신), 카사네 테토 | 기하·학자·마법진 |
| 해골 | `skull-shaped_pupils` | 152 | (미확인) | 죽음·사신 — 글 수 적어 잘 안 나옴 |
| 클로버 | `clover-shaped_pupils` | 353 | (미확인) | 행운·도박 |
| 눈송이 | `snowflake_pupils` | 304 | (미확인) | 얼음·설녀 |
| 초승달 | `crescent-shaped_pupils` | 87 | (미확인) | 달·밤. **거의 안 나옴** |
| 톱니 | `gear-shaped_pupils` | 52 | (미확인) | 기계·태엽. **거의 안 나옴** |
| 그 외 | `paw-shaped_pupils` 528 · `fish-shaped_pupils` 305 · `keyhole-shaped_pupils` 95 · `money-shaped_pupils` 92 · `musical_note-shaped_pupils` 106 · `lightning_bolt-shaped_pupils` 161 · `bone-shaped_pupils` 38 · `crown-shaped_pupils` 21 · `black_hole-shaped_pupils` 75 · `radiation_symbol-shaped_pupils` 59 | — | — | 글 수 적음 → 프롬프트만으론 거의 실패, 인페인트·손 수정 전제 |

**주의**: `moon-shaped_pupils`(2)는 사실상 없는 태그 → `crescent-shaped_pupils` 사용. `spiral_eyes`는 0 → 소용돌이 눈은 `@_@`(59,149, 어지러움 표정) 또는 `spiral-only_eyes`(1,057).

**비슷하지만 다른 태그**: `symbol_in_eye`(36,746) = 동공은 그대로 두고 **홍채 안에 기호가 떠 있음**(하이라이트 자리에 별 등). 예: 호시마치 스이세이(홀로라이브, 별), 하루우라라(우마무스메), 마비카(원신), 코메이지 코이시(동방). 하위로 `star_in_eye`(14,196), `heart_in_eye`(16,051), `flower_in_eye`(3,336), `cross_in_eye`(147).
→ 동공 모양 바꾸기보다 **모델이 덜 망가뜨림**(동공은 둥근 채로 남기 때문).

### 1-2. 동물·인외 동공

| 종류 | 태그 | 글 수 | 예시 | 모티프 |
|---|---|---|---|---|
| 세로 동공(고양이·뱀·용) | `slit_pupils` | 95,938 | 미아(몬무스, 라미아), 엘런 조(젠레스, 상어 — 미확인), 각종 용·뱀 캐릭터 | 포식자. **가장 잘 나오는 인외 표시** |
| 가로 동공(염소·양·개구리·말) | `horizontal_pupils` | 7,531 | 모리야 스와코(동방, 개구리), 토우테츠 유우마(동방, 도철/양), 쿠로코마 사키(동방, 말), 야사카 카나코(동방), 카야(블루 아카이브), 컬트 오브 더 램의 양 | 초식·악마(염소). **악마=염소 눈**이 고전 공식 |
| 사각 동공 | `rectangular_pupils` | 757 | (미확인) | 문어·염소 변형 |
| 두족류 눈 | `cephalopod_eyes` | 2,651 | 스플래툰 계열 | 문어·오징어 — W자 모양 |
| 겹눈 | `compound_eyes` | 3,216 | (미확인) | 벌레·거미 |
| 동공 여러 개 | `extra_pupils` | 1,348 | (미확인) | 한 눈에 동공 2개 = 이형 |
| 동공 없음 | `no_pupils` | 23,865 | 수(몬무스, 슬라임) | 슬라임·유령·정령 |
| 단색 눈(흰자까지 한 색) | `solid_eyes` | 4,166 | (미확인) | 기계·빙의·괴물 |
| 수축/확장 동공 | `constricted_pupils` 21,189 · `dilated_pupils` 1,130 | — | — | 공포·광기 연출(표정) |
| 단추 눈 | `button_eyes` | 2,928 | 인형 캐릭터 | 인형·저주 인형 |
| 픽셀 눈 | `pixel_eyes` | 281 | — | 디지털 존재 |
| 기계 눈 | `mechanical_eyes` 3,255 · `single_mechanical_eye` 1,316 · `lens_eye`(미확인 수) | — | 아리아(젠레스, 로봇형) | 사이보그·인형 |

### 1-3. 고리·무늬 홍채

| 종류 | 태그 | 글 수 | 예시 | 모티프 |
|---|---|---|---|---|
| 동심원 고리 눈 | `ringed_eyes` | 42,927 | 마키마(체인소 맨), 케이·리오·아리스(블루 아카이브), 요루·나유타(체인소 맨), 프란체스카(Fate) | 지배·비인간·인공. 마키마 = "지배의 악마" |
| 소용돌이 | `@_@` 59,149 · `spiral-only_eyes` 1,057 | — | 표정용(어지러움) | 최면·광기 — 평소 눈으로 쓰려면 인페인트 |
| 점선 홍채 | `dashed_eyes` | 2,668 | — | 기계·몽롱 |
| 물결 | `squiggle_eyes` | 449 | — | 광기 |
| 홍채 안 글자 | `text_in_eyes` | 658 | — | 저주·계약 |
| 눈 반사 | `eye_reflection` | 1,744 | — | 연출용 |

### 1-4. 색으로 바꾸기

| 종류 | 태그 | 글 수 | 예시 | 모티프 |
|---|---|---|---|---|
| 짝짝이 눈 | `heterochromia` | 180,650 | 호시노(블루 아카이브), 미나토 아쿠아·호쇼 마린(홀로라이브), 아이리스(홀로라이브), 크레이지 올리(홀로라이브) | 두 정체성·반신(半身)·저주 받은 쪽 |
| 여러 색 홍채 | `multicolored_eyes` | 70,164 | 반딧불이·삼월칠(스타레일), 어벤츄린(스타레일), 세이아(블루 아카이브), 감우·라이덴 쇼군·유라·신학(원신), 앙쥬 카트리나(니지산지), 키류 코코(홀로라이브) | 색 두세 개 = 속성 두 개 |
| 그러데이션 | `gradient_eyes` | 14,110 | 반딧불이(스타레일), 세이아·미카(블루 아카이브), 감우·신학·코코미(원신), 아마네 카나타·하쿠이 코요리(홀로라이브), 야쿠모 유카리(동방) | 위→아래 색 바뀜. 머리 끝 색과 이어짐 |
| 두 톤 | `two-tone_eyes` | 20,971 | — | 그러데이션보다 경계 뚜렷 |
| 무지개 | `rainbow_eyes` | 771 | — | 요정·환상 — 글 수 적음 |
| 동공만 다른 색 | `mismatched_pupils` 14,798 · `white_pupils` 130,742 · `red_pupils` 24,017 · `pink_pupils` 13,783 · `yellow_pupils` 10,632 | — | — | **흰 동공**이 의외로 강력·잘 나옴 → 유령·눈먼 무녀 |
| 홍채 모양 짝짝이 | `mismatched_irises` | 236 | — | 글 수 적음 |

### 1-5. 빛·텅 빈 눈

| 종류 | 태그 | 글 수 | 예시 | 모티프 |
|---|---|---|---|---|
| 빛나는 눈(두 눈) | `glowing_eyes` | 64,409 | 각종 변신·각성 | 마력·인외. 어두운 장면에서 특히 강함 |
| 한쪽만 빛남 | `glowing_eye` | 16,037 | — | 봉인된 눈·각성 반쪽 |
| 빛 꼬리 | `eye_trail` | 4,575 | — | 움직이는 귀신불 느낌. 공포물에 좋음 |
| 불타는 눈 | `flaming_eyes` | 926 | — | 화염 계열 |
| 전기 눈 | `electric_eyes` | 139 | — | 글 수 적음 |
| 텅 빈 눈(빛 없음) | `empty_eyes` | 52,408 | — | 조종당함·죽은 자. **기숙사 공포에 핵심** |
| 흐릿한 흰 눈 | `blank_eyes` | 19,707 | — | 빙의·최면 |
| 퀭한 눈 | `hollow_eyes` | 3,803 | — | 시체·좀비 |
| 반짝이는 눈 | `sparkling_eyes` | 19,614 | — | 순진·아이돌 — 공포와 대비용 |

---

## 2. 흰자와 눈 주변

### 2-1. 흰자(sclera)

| 종류 | 태그 | 글 수 | 예시 | 쓰임 |
|---|---|---|---|---|
| 색 흰자(묶음) | `colored_sclera` | 80,958 | 아리아(젠레스), 레베카(사이버펑크), 미드나(젤다), 가디안(포켓몬) | 인외 표시의 왕. **전신에서도 보임** |
| 검은 흰자 | `black_sclera` | 39,296 | 아시도 미나(히로아카), 안드로이드 21(드래곤볼), 헬하운드(마물낭 도감), X(리버스: 1999), 아스타로트(신라만상) | 악마·심연·괴물. 가장 확실하게 "사람 아님" |
| 노란 흰자 | `yellow_sclera` | 19,139 | — | 짐승·병든 느낌 |
| 빨간 흰자 | `red_sclera` | 10,760 | — | 흡혈·광기 |
| 파랑/초록/분홍/보라/주황 | `blue_sclera` 4,293 · `green_sclera` 2,635 · `pink_sclera` 1,422 · `purple_sclera` 1,254 · `orange_sclera` 1,157 | — | — | 속성 색 맞추기 |
| 짝짝이 흰자 | `mismatched_sclera` | 2,503 | X·레굴루스·버틴·애플(리버스: 1999), 멜리노에·자그레우스·타나토스(하데스), 카네키(도쿄 구울), 로랑(퍼니싱) | **한쪽만 괴물** = 반쯤 변한 존재. 공포물에 딱 |
| 흰자 없음 | `no_sclera` | 4,699 | — | 눈 전체가 홍채 = 짐승·외계 |
| 핏발 | `bloodshot_eyes` | 2,081 | — | 광기·불면 |

### 2-2. 눈 주변 표식·화장

| 종류 | 태그 | 글 수 | 예시 | 쓰임 |
|---|---|---|---|---|
| 빨간 아이라인 | `red_eyeliner` | 21,695 | 스카라무슈/방랑자·라이덴 쇼군·나히다·종려·소(원신), 단항·음월(스타레일), 푸화(붕괴3rd), 루시(사이버펑크), 제로투(달링 인 더 프랑키스) | 동양풍·요괴·신. **눈꼬리 빨강 = 가장 싸고 효과 큼** |
| 아이라인 일반·색 | `eyeliner` 48,203 · `black_eyeliner` 2,624 · `purple_eyeliner` 521 | — | — | — |
| 아이섀도 | `eyeshadow` 76,348 · `red_eyeshadow` 22,287 · `pink_eyeshadow` 6,915 · `blue_eyeshadow` 6,304 · `purple_eyeshadow` 6,211 · `black_eyeshadow` 3,123 · `gold_eyeshadow` 132 | — | — | 색으로 속성 표시 |
| 눈 밑 섀도 | `eyeshadow_under_eye` | 300 | — | 퀭함 |
| 스모키 | `smokey_eyeshadow` | 94 | — | 글 수 적음 |
| 눈 밑 표식(한쪽) | `mark_under_eye` | 3,332 | — | 눈물점보다 큰 상징 |
| 눈 밑 표식(양쪽) | `mark_under_both_eyes` | 3,291 | — | — |
| 눈물 모양 표식 | `teardrop_facial_mark` | 6,609 | — | 광대·슬픔·저주 |
| 별 표식 | `star_facial_mark` | 5,112 | — | 아이돌·광대 |
| 마름모 표식 | `diamond_facial_mark` | 1,357 | — | 광대·카드 |
| 그 외 모양 표식 | `heart_facial_mark` · `crescent_facial_mark` · `cross_facial_mark` · `butterfly_facial_mark` · `sparkle_facial_mark` · `x_facial_mark` 등 (위키 확인, 글 수 미확인) | — | 스파클(스타레일)은 눈 아래 나비 | 동공 기호와 **같은 모양 반복** |
| 이마 표식 | `forehead_mark` | 40,263 | — | 셋째 눈 대용·종교 |
| 미간 표식 | `mark_between_eyes` | 20 | — | 거의 없음 → `forehead_mark` 사용 |
| 얼굴 문신(복잡) | `facial_tattoo` | 23,885 | — | 부족·저주 문양 |
| 빛나는 무늬 | `glowing_markings` 1,056 · `glowing_tattoo` 2,259 | — | — | 마력 회로. 어두운 곳에서 강함 |
| 페이스페인트 | `facepaint` | 18,786 | — | 전사·의식 |
| 수염 무늬 | `whisker_markings` | 20,945 | — | 고양이·여우 |
| 얼굴 보석 | `face_jewel` 726 · `bindi` 2,118 | — | — | 보석·이국 |
| 금 간 피부 | `cracked_skin` | 7,917 | — | 인형·석상·깨지는 존재 |
| 호루스의 눈 | `eye_of_horus` | 1,953 | — | 이집트·저주 |

### 2-3. 속눈썹

| 종류 | 태그 | 글 수 | 쓰임 |
|---|---|---|---|
| 색 속눈썹 | `colored_eyelashes` | 62,272 | 머리색과 같은 색 속눈썹 = 인외 느낌이 은근히 남 |
| 흰 속눈썹 | `white_eyelashes` | 9,312 | 설녀·유령·백발 |
| 긴 속눈썹 | `long_eyelashes` | 13,267 | 인형·귀족 |
| 굵은 속눈썹 | `thick_eyelashes` | 7,670 | 강한 인상 |
| 속눈썹 장식 | `eyelash_ornament` | 1,897 | 보석·이국 |

`lower_eyelashes`, `winged_eyeliner`는 Danbooru에 태그가 없음(0) → 쓰지 않음.

### 2-4. 눈 개수·셋째 눈

| 종류 | 태그 | 글 수 | 예시 | 쓰임 |
|---|---|---|---|---|
| 셋째 눈 | `third_eye` | 13,898 | 코메이지 사토리·코이시(동방, 가슴 앞 떠 있는 눈 — 코이시는 닫힘) | 이마·가슴·손 어디든. **닫힌 셋째 눈 = 사연** |
| 눈 여러 개 | `extra_eyes` | 14,877 | 라크네라(몬무스, 거미 6눈), 가저(마물낭 도감, 외눈+촉수 눈), 머펫(언더테일), 모리야 스와코·야사카 카나코(동방), 너깃·직원(프로젝트 문), 빅 버드(프로젝트 문), 호넷(할로우 나이트) | 거미·괴물·환각 |
| 외눈 | `one-eyed` | (위키 확인) | 가저(마물낭 도감) | 사이클롭스 |
| 눈알 장식 | `eyeball_hair_ornament` 1,646 · `eye_print` 2,028 | — | — | 눈을 옷·장신구로 반복 |
| 섭리의 눈 | `eye_of_providence` | 585 | — | 비밀결사 |

### 2-5. 눈 소품

| 소품 | 태그 | 글 수 | 쓰임 |
|---|---|---|---|
| 안대 | `eyepatch` | 108,019 | 가린 쪽에 비밀. 들추면 `eyepatch_lift`(372) |
| 붕대 한쪽 | `bandage_over_one_eye` | 9,283 | 상처·저주 |
| 눈가리개 | `blindfold` | 31,335 | 눈먼 무녀·봉인. 들추면 `blindfold_lift`(549) |
| 가려진 눈 | `covered_eyes` 30,285 · `hair_over_eyes` 32,872 | — | 얼굴을 숨기는 공포 |
| 한쪽 눈 머리로 가림 | `hair_over_one_eye` | 387,626 | 가장 흔함 — 차별점 약함 |
| 외알 안경 | `monocle` | 13,877 | 학자·집사·귀족 |
| 둥근 안경 | `round_eyewear` | 82,331 | — |
| 가면 | `eye_mask` 24,671 · `half_mask` 2,989 | — | 가면극 |
| 베일 | `veil` 103,963 · `mouth_veil` 5,824 | — | 신부·유령 |
| 고글 | `goggles` | 91,113 | — |

---

## 3. 게임별로 본 경향 (방법만)

| 게임 | 눈 쓰는 방법 |
|---|---|
| **원신** | 나라마다 동공 기호를 정해 같은 지역끼리 공유(폰타인 = 물방울 `drop-shaped_pupils`, 스네즈나야 집행관 = X `x-shaped_pupils` — 아를레키노·콜롬비나·산드로네·타르탈리아·시뇨라). 신(神)·특별 캐릭터는 기호 동공(나히다 십자·삼각, 호두 매화, 푸리나 물방울). 눈꼬리 빨간 아이라인을 동양풍 캐릭터에 반복(라이덴·스카라무슈·소·종려) |
| **붕괴: 스타레일** | 캐릭터마다 다른 기호: 스파클 나비(+눈 아래 나비), 키레네 마름모, 트리비 십자, 부트힐·아르젠티 조준선. 반딧불이·삼월칠은 그러데이션·여러 색 홍채 |
| **붕괴3rd** | 엘리시아 마름모, 키아나(율자 상태) 별·마름모 — **변신하면 동공이 바뀜** |
| **명조** | 아이메스 별, 카멜리아·금희 꽃, 로치아 X |
| **젠레스 존 제로** | 아리아 = 검은 흰자 + 별/조준선 동공(로봇 몸), 순나 조준선 |
| **블루 아카이브** | 일반 학생은 둥근 눈, **인공 존재만 고리 눈**(케이·리오·아리스 = `ringed_eyes`), 무명 사제(에인·소프·말쿠트) X 동공, 세이아·미카 그러데이션 → "인간/비인간"을 눈으로 나눔 |
| **명일방주** | 대부분 평범한 눈. 특별한 존재만 기호(프리스티스·안젤리나·길베르타 마름모, 리노 별, W 십자). 차별점은 머리 위 고리·뿔·귀로 둠 |
| **리버스: 1999 / 하데스** | **한쪽 흰자만 검게**(`mismatched_sclera`) — 반은 사람, 반은 다른 것 |
| **림버스·프로젝트 문** | 색 흰자·눈 여러 개를 왜곡(괴물화) 단계 표시로 |
| **퍼니싱: 그레이 레이븐** | 루나 십자 동공, 로랑 짝짝이 흰자 |
| **니케 · 벽람항로** | 눈은 대체로 평범하고 몸·옷·무기로 차별 (기호 동공 캐릭터는 확인 못 함 → 미확인). 라파엘로(벽람항로) X 동공 |
| **동방** | 동물 요괴에 가로 동공(스와코 개구리·사키 말·유우마 도철), 사토리 자매 셋째 눈 |
| **홀로라이브·니지산지** | 캐릭터 상징을 눈에 직접: 페코라 토끼 동공, 스이세이 별(홍채 안), 루시아 나비, 올리 X·마름모 + 짝짝이(좀비), 루이 조준선, 엘리라 십자, 카나타·코요리 그러데이션 |
| **몬무스·마물낭 도감** | 종족 그대로: 라미아 세로 동공, 거미 눈 6개, 헬하운드 검은 흰자, 가저 외눈 + 촉수 눈, 슬라임 동공 없음 |

---

## 4. 눈에 정체성을 싣는 규칙 (10개)

1. **동그란 동공·흰 흰자·맨 눈가 중 하나는 반드시 바꾼다.** 셋 다 그대로면 "AI 그림"이 된다.
2. **모티프 반복**: 동공 기호 = 얼굴 표식 = 장신구 = 무기 문양. (스파클: 나비 동공 + 눈 아래 나비 / 아를레키노: X 동공 + X 문양) 한 모양이 세 번 나오면 그게 그 캐릭터다.
3. **색 이어 주기**: 홍채 색 = 머리 끝(브리지·안쪽 머리) 색 = 아이라인 색. 그러데이션 눈은 머리 그러데이션 방향과 맞춘다.
4. **비대칭 하나**: 한쪽 눈만 시계·한쪽 흰자만 검정·한쪽만 빛남·한쪽만 안대. 양쪽이 같으면 장식, 다르면 사연.
5. **사람/인외를 눈으로 나눈다**: 같은 학교 안에서 인외만 고리 눈(블루 아카이브 방식). 우리 기숙사 공포에선 "평소 = 사람 눈 / 정체 드러남 = 인외 눈" 두 단계.
6. **종족 그대로 가져오기**: 뱀·용 세로, 염소·양·말·개구리 가로, 거미 여러 눈, 슬라임 동공 없음, 인형 단추·금 간 피부. 종족을 모르는 사람도 눈만 보고 짐작하게.
7. **변신하면 동공이 바뀐다**: 평소엔 둥근 눈 → 각성·광폭 때 기호/빛/검은 흰자. 같은 캐릭터 두 얼굴을 눈으로만 구분(넵튠 전원 기호, 키아나 율자).
8. **집단 표식**: 같은 무리(층·동아리·혈족)는 같은 동공 기호를 공유하고 색만 다르게(원신 폰타인 물방울·집행관 X).
9. **한 캐릭터에 강한 장치는 하나 + 보조 하나까지.** 기호 동공 + 검은 흰자 + 셋째 눈 + 안대는 과하다.
10. **공포물은 '빠진 것'이 무섭다**: 빛 없는 눈(`empty_eyes`), 흰 동공, 동공 없음, 닫힌 셋째 눈, 가린 눈. 많이 더하기보다 하나 빼기.
11. **가리면 궁금해진다**: 안대·눈가리개·머리로 가린 눈 아래에 진짜 눈을 숨겨 두고, 이벤트 그림에서 한 번 보여 준다.
12. **눈 아래는 눈만큼 눈에 띈다**: 눈꼬리 빨간 아이라인·눈물 표식·색 속눈썹은 작은 얼굴에서도 보이는 값싼 차별점.

---

## 5. 그림 만들 때 실전 요령 (Anima · 전신 1024×1536)

### 5-1. 전신에서 잘 나오는 것 / 안 나오는 것

전신 1024×1536이면 얼굴이 대략 100~150px, 눈 하나는 15~25px. 이 크기에선 **동공 안 모양은 거의 안 그려진다.**

| 잘 나옴 (전신 OK) | 반반 (상반신에서는 됨) | 거의 안 나옴 (인페인트 필수) |
|---|---|---|
| `black_sclera`, `colored_sclera`, `glowing_eyes`, `red_eyeliner`, `eyeshadow` 색, `heterochromia`(색 차이 크면), `eyepatch`, `blindfold`, `monocle`, `third_eye`(이마), `facial_tattoo`, `facepaint`, `whisker_markings`, `empty_eyes`, `eye_trail` | `slit_pupils`, `ringed_eyes`, `gradient_eyes`, `multicolored_eyes`, `heart-shaped_pupils`, `star-shaped_pupils`, `symbol_in_eye`, `teardrop_facial_mark`, `star_facial_mark`, `white_pupils`, `mismatched_sclera`, `extra_eyes` | `cross-shaped_pupils`, `diamond-shaped_pupils`, `flower-shaped_pupils`, `x-shaped_pupils`, `butterfly-shaped_pupils`, `crosshair_pupils`, `clock-shaped_pupils`, `horizontal_pupils`, 글 수 1천 아래 기호 전부(톱니·초승달·해골·클로버·눈송이 등) |

(이 표는 태그 글 수와 일반적인 경험을 바탕으로 한 예상. **우리 PC에서 직접 시험 전** — 시험 뒤 고칠 것.)

### 5-2. 고치는 순서

1. **전신은 '면'으로 정체성을 세운다**: 흰자 색·아이라인·얼굴 표식·소품. 이건 전신 첫 그림에서 바로 넣는다.
2. **기호 동공은 얼굴 고쳐 그리기에서 넣는다**: ComfyUI Impact Pack의 FaceDetailer(얼굴을 찾아 크게 잘라 다시 그림)에 **얼굴 전용 프롬프트**를 따로 준다.
   - 얼굴 프롬프트 예: `close-up, face, detailed eyes, star-shaped_pupils, symbol-shaped_pupils, black_sclera, red_eyeliner`
   - denoise 0.35~0.5: 낮으면 기호가 안 생기고, 높으면 얼굴이 바뀐다. 0.4에서 시작.
   - 잘라 내는 크기(guide_size) 512~768 → 눈이 60px 넘게 커져야 기호가 나온다.
3. **그래도 안 나오면 눈만 인페인트**: 눈 부분만 마스크 → 해상도 올려(only masked, 패딩 32px) `cross-shaped_pupils` 등 한 가지만.
4. **기준 얼굴 그림을 먼저 만든다**: 캐릭터마다 상반신·얼굴 크게 한 장(`portrait`, `upper_body`, `close-up`)으로 눈 디자인을 확정 → 그 그림을 참고(IP-Adapter 등)로 전신을 만든다.
5. **가중치**: 잘 안 나오는 태그는 `(cross-shaped_pupils:1.3)`까지. 1.4 넘으면 눈이 깨지거나 얼굴 전체에 기호가 퍼짐. 대신 상위 태그 `symbol-shaped_pupils`를 같이 넣으면 안정됨.
6. **반대 신호 빼기**: 기호 동공을 넣을 땐 네거티브에 `sparkling_eyes`(별 하이라이트로 대체됨)는 넣지 말고, 하트·별이 표정(홀림)처럼 나오면 네거티브에 `blush, open_mouth` 쪽을 조절.
7. **짝짝이는 '어느 쪽'을 말로 못 고정한다**: `heterochromia, red_eyes, blue_eyes`는 좌우가 랜덤 → 인페인트로 한쪽만 고치거나, 좌우 반전으로 맞춘다. `mismatched_sclera`, 한쪽 `glowing_eye`, 시계 한쪽도 같은 방법.
8. **글 수 적은 태그는 말로 풀어 보조**: 예 `gear-shaped_pupils`(52) → 인페인트 + 직접 그린 작은 톱니를 눈에 얹고 denoise 0.3으로 녹이기. 프롬프트만으로 기대하지 않는다.
9. **확인은 보는 크기로**: 게임에서 보여 줄 크기(대화 화면 상반신)에서 기호가 읽히는지 본다. 확대해서만 보이는 동공은 실제 플레이에선 없는 것과 같다.

### 5-3. 바로 쓰는 조합 예 (새로 짠 것, 특정 캐릭터 아님)

| 컨셉 | 전신용(면) | 얼굴 고쳐 그리기용(선) |
|---|---|---|
| 뱀 소녀 | `colored_sclera, yellow_sclera, eyeshadow, green_eyeshadow(미확인)` | `slit_pupils, yellow_eyes` |
| 거미 소녀 | `extra_eyes, forehead_mark, black_eyeliner` | `red_eyes, constricted_pupils` |
| 염소 악마 | `black_sclera, red_eyeliner` | `horizontal_pupils, yellow_eyes` |
| 유령 | `empty_eyes, white_eyelashes, hollow_eyes` | `white_pupils, blank_eyes` |
| 인형 | `cracked_skin, long_eyelashes, monocle` | `ringed_eyes, button_eyes` |
| 반쯤 변한 괴물 | `mismatched_sclera, bandage_over_one_eye` | `heterochromia, glowing_eye` |
| 무녀·봉인 | `blindfold, red_eyeliner, forehead_mark` | (가린 채 유지, 이벤트 그림만 `blindfold_lift, star-shaped_pupils`) |

---

## 출처

- Danbooru 눈 태그 묶음: https://danbooru.donmai.us/wiki_pages/tag_group:eyes_tags
- Danbooru `symbol-shaped_pupils` 위키(하위 태그·쓰는 법): https://danbooru.donmai.us/wiki_pages/symbol-shaped_pupils
- Danbooru `facial_mark` 위키(표식 모양·자리 태그): https://danbooru.donmai.us/wiki_pages/facial_mark
- Danbooru `makeup` 위키: https://danbooru.donmai.us/wiki_pages/makeup
- 태그별 글 수: https://danbooru.donmai.us/tags.json (name_comma 검색, 2026-11-24)
- 태그별 함께 많이 나오는 캐릭터: https://danbooru.donmai.us/related_tag.json?query=<태그>&category=character (star/cross/flower/diamond/x/drop/butterfly/triangle/power_symbol/rabbit/clock/crosshair-shaped_pupils, ringed_eyes, horizontal_pupils, extra_eyes, black_sclera, colored_sclera, mismatched_sclera, multicolored_eyes, gradient_eyes, symbol_in_eye, red_eyeliner)
- MyAnimeList 스파클 캐릭터 소개(나비 무늬·빨간 아이라인): https://myanimelist.net/character/243878
- 엘런 조 상어 모티프 기사(눈 세부는 미확인): https://nerdbot.com/2025/04/11/why-ellen-joe-became-the-breakout-star-of-zenless-zone-zero

**미확인으로 남긴 것**: 니케·벽람항로 캐릭터별 눈 기호, 엘런 조 동공, 글 수 1천 아래 기호 태그의 실제 렌더 품질, 5-1 표(우리 PC 시험 전).
