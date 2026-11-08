#!/usr/bin/env python3
"""Превью канала 1280x720 (thumbnails/<slug>.jpg): градиент цвета канала, значок, английское название, LIVE, korea-tv.uk.
Та же раскладка, что у остальных превью сайта. Нужен Pillow; шрифты — системные macOS.
Usage: python3 -I make_thumbnails.py <out dir> <slug> <icon> "<English name>" <#color> [<slug> <icon> "<name>" <#color> ...]
Пример: python3 -I tools/make_thumbnails.py thumbnails tvchosun-live TVC "TV Chosun" '#d84315'"""
import os, sys
from PIL import Image, ImageDraw, ImageFont
OUT, args = sys.argv[1], sys.argv[2:]
assert args and len(args) % 4 == 0, __doc__
CH = [tuple(args[i:i + 4]) for i in range(0, len(args), 4)]
W, H = 1280, 720
BOLD = '/System/Library/Fonts/Supplemental/Arial Bold.ttf'
KR = '/System/Library/Fonts/AppleSDGothicNeo.ttc'
F_ICON, F_NAME, F_BADGE = ImageFont.truetype(BOLD, 150), ImageFont.truetype(BOLD, 64), ImageFont.truetype(BOLD, 30)
F_BRAND = ImageFont.truetype(KR, 34, index=6)
def rgb(h): h = h.lstrip('#'); return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
def lighten(c, a): return tuple(int(x + (255 - x) * a) for x in c)
def darken(c, a): return tuple(int(x * (1 - a)) for x in c)
def centered(d, text, font, cy, fill):
    b = d.textbbox((0, 0), text, font=font); d.text((W/2 - (b[2]-b[0])/2, cy - (b[3]-b[1])/2 - b[1]), text, font=font, fill=fill)
for slug, icon, name, color in CH:
    base = rgb(color); top, bot = lighten(base, .12), darken(base, .55)
    img = Image.new('RGB', (W, H)); d = ImageDraw.Draw(img)
    for y in range(H):
        t = y / H; d.line([(0, y), (W, y)], fill=tuple(int(top[i] + (bot[i]-top[i]) * t) for i in range(3)))
    d.ellipse((W/2-140, 150, W/2+140, 430), fill=darken(base, .25))
    centered(d, icon, F_ICON, 290, (255, 255, 255))
    centered(d, name, F_NAME, 500, (255, 255, 255))
    bw, bh, bx, by = 150, 52, W/2-75, 570
    d.rounded_rectangle((bx, by, bx+bw, by+bh), radius=26, fill=(229, 57, 53))
    d.ellipse((bx+18, by+18, bx+34, by+34), fill=(255, 255, 255))
    d.text((bx+44, by+11), 'LIVE', font=F_BADGE, fill=(255, 255, 255))
    centered(d, '한국 · TV  korea-tv.uk', F_BRAND, 668, (255, 255, 255))
    img.save(os.path.join(OUT, slug + '.jpg'), quality=85)
print('ok', len(CH))
