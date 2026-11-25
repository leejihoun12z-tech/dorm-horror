"""마네킹 얼굴 텍스처(그린 얼굴) 0~3단계를 만든다. 사용: python3 tools/char/make_mannequin_face.py
Family Time 방식: 얼굴은 3D가 아니라 텍스처에 그린 선·색. 피부는 투명(몸 셰이더의 흰 플라스틱이 비침).
단계: 0 화장한 얼굴 · 1 눈 하이라이트 없음 · 2 한쪽 눈이 '그려 넣은 눈' + 얼굴 관절선 · 3 역안(흰자 검게·점 동공) + 굳은 입 (강도 상한 3)
"""
from PIL import Image, ImageDraw, ImageFilter
import os, math

S = 1024
OUT = os.path.join(os.path.dirname(__file__), '..', '..', 'assets', 'characters', 'mannequin')
INK = (36, 22, 28, 255)
RED = (196, 24, 44, 255)
RED_D = (120, 10, 26, 255)
EYE_RED = (214, 40, 60, 255)


def almond(cx, cy, w, h, tilt=0.0):
    pts = []
    for i in range(48):
        t = i / 48 * 2 * math.pi
        x = math.cos(t) * w / 2
        y = math.sin(t) * h / 2 * (0.75 if math.sin(t) > 0 else 1.0)
        x2 = x * math.cos(tilt) - y * math.sin(tilt)
        y2 = x * math.sin(tilt) + y * math.cos(tilt)
        pts.append((cx + x2, cy + y2))
    return pts


def eye(d, cx, cy, side, stage, painted=False):
    w, h = 236, 168
    tilt = 0.10 * side
    shape = almond(cx, cy, w, h, tilt)
    if painted:
        # 그려 넣은 눈: 평면 빨강 + 붓 자국, 깊이 없음
        d.polygon(shape, fill=(230, 210, 205, 255))
        d.ellipse([cx - 52, cy - 50, cx + 52, cy + 46], fill=(205, 30, 50, 255))
        for k in range(5):
            d.line([(cx - 90 + k * 36, cy - 70), (cx - 70 + k * 36, cy + 70)], fill=(205, 30, 50, 120), width=6)
        d.line(shape + [shape[0]], fill=INK, width=7)
        return
    inverted = stage >= 3
    d.polygon(shape, fill=(18, 12, 16, 255) if inverted else (250, 246, 246, 255))
    # 홍채
    ir = (232, 226, 226, 255) if inverted else EYE_RED
    d.ellipse([cx - 70, cy - 74, cx + 70, cy + 70], fill=ir)
    if inverted:
        d.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], fill=(10, 6, 8, 255))
    else:
        d.ellipse([cx - 42, cy - 46, cx + 42, cy + 40], fill=(120, 6, 24, 255))
        d.ellipse([cx - 70, cy - 74, cx + 70, cy + 70], outline=RED_D, width=7)
        if stage == 0:
            d.ellipse([cx - 38 + 12 * side, cy - 52, cx - 8 + 12 * side, cy - 22], fill=(255, 255, 255, 255))
            d.ellipse([cx + 14, cy + 14, cx + 26, cy + 26], fill=(255, 235, 235, 255))
    # 윗눈꺼풀 굵은 선 + 속눈썹
    top = [p for p in shape if p[1] <= cy + 4]
    top.sort()
    d.line(top, fill=INK, width=16, joint='curve')
    ox = cx + side * w / 2
    for k in range(3):
        d.line([(ox - side * 14 * k, cy - 14 - 6 * k), (ox + side * (22 - 6 * k), cy - 40 - 12 * k)], fill=INK, width=9)
    low = [p for p in shape if p[1] > cy + 10]
    low.sort()
    d.line(low, fill=(90, 60, 66, 255), width=4)


def make(stage):
    img = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    ey = 500
    # 볼 붓 자국 (화장)
    blush = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    bd = ImageDraw.Draw(blush)
    if stage <= 1:
        for side in (-1, 1):
            cx = 512 + side * 250
            for k in range(4):
                bd.line([(cx - 60, 600 + k * 14), (cx + 60, 585 + k * 14)], fill=(235, 110, 130, 110), width=12)
        img = Image.alpha_composite(img, blush.filter(ImageFilter.GaussianBlur(4)))
        d = ImageDraw.Draw(img)
    # 눈썹 (그려 넣은 화장 눈썹)
    for side in (-1, 1):
        cx = 512 + side * 190
        d.line([(cx - 85 * side * -1 if False else cx - 80, ey - 165 + (8 if side < 0 else 0)), (cx + 80, ey - 165 + (0 if side < 0 else 8))], fill=(70, 50, 52, 255), width=9)
    # 눈
    eye(d, 512 - 190, ey, -1, stage, painted=(stage == 2))
    eye(d, 512 + 190, ey, 1, stage)
    # 입술
    my = 745
    if stage >= 3:
        d.line([(452, my), (572, my)], fill=RED, width=16)
    else:
        d.pieslice([452, my - 40, 572, my + 36], 0, 180, fill=RED)
        d.polygon([(452, my - 2), (512, my - 26), (572, my - 2)], fill=RED)
        d.line([(458, my), (566, my)], fill=RED_D, width=5)
        d.ellipse([486, my + 6, 508, my + 16], fill=(255, 200, 205, 255))
    # 얼굴 관절선 (2단계부터)
    if stage >= 2:
        pts = [(512 + 300, 120), (512 + 280, 400), (512 + 300, 700), (512 + 250, 960)]
        d.line(pts, fill=(120, 116, 122, 255), width=6, joint='curve')
    img.save(os.path.join(OUT, f'face_s{stage}.png'))


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    for st in range(4):
        make(st)
    print('ok', OUT)
