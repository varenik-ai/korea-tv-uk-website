#!/usr/bin/env python3
"""Логотипы для assets/logos/: обрезает пустые поля (прозрачные или белые), уменьшает до 240x120, сохраняет PNG.
Имя файла: <id канала>.<ext> на входе -> <id с '-' вместо '_'>.png на выходе (= slug без -live). Нужен Pillow.
Usage: python3 -I normalize_logos.py <dir with raw logos> <out dir, e.g. assets/logos>"""
import os, sys
from PIL import Image, ImageChops
raw, out = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)
for name in sorted(os.listdir(raw)):
    im = Image.open(os.path.join(raw, name)); im.load(); im = im.convert('RGBA')
    # обрезать пустые поля: прозрачные, а у JPEG без альфы — белый фон
    alpha = im.getchannel('A')
    bbox = alpha.getbbox() if alpha.getextrema()[0] < 250 else ImageChops.difference(im.convert('RGB'), Image.new('RGB', im.size, (255, 255, 255))).getbbox()
    if bbox: im = im.crop(bbox)
    im.thumbnail((240, 120), Image.LANCZOS)
    im.save(os.path.join(out, name.replace('_', '-') + '.png'), optimize=True)
print('ok', len(os.listdir(out)))
