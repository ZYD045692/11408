# -*- coding: utf-8 -*-
"""把 PDF 连续页渲染成缩略图拼成一张联系表（列x行），用 luma 一次定位章节页。
用法: python _pdf_sheet.py <pdf> <start> <end> <cols>
输出: _pdf_sheet_p<start>-<end>.png，每格左上角标页码
"""
import io, sys, fitz
from PIL import Image, ImageDraw
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

pdf = sys.argv[1]
p1, p2 = int(sys.argv[2]), int(sys.argv[3])
cols = int(sys.argv[4]) if len(sys.argv) > 4 else 4
doc = fitz.open(pdf)

THUMB_W = int(sys.argv[5]) if len(sys.argv) > 5 else 300
pages = list(range(p1, p2 + 1))
rows = (len(pages) + cols - 1) // cols
THUMB_H = int(THUMB_W * 1.35)
pad = 6
W = cols * THUMB_W + (cols + 1) * pad
H = rows * THUMB_H + (rows + 1) * pad
sheet = Image.new("RGB", (W, H), "white")
draw = ImageDraw.Draw(sheet)

for k, p in enumerate(pages):
    page = doc[p - 1]
    pix = page.get_pixmap(matrix=fitz.Matrix(THUMB_W / page.rect.width, THUMB_W / page.rect.width))
    img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
    img.thumbnail((THUMB_W, THUMB_H))
    r, c = divmod(k, cols)
    x = pad + c * (THUMB_W + pad)
    y = pad + r * (THUMB_H + pad)
    sheet.paste(img, (x, y))
    draw.text((x + 4, y + 4), "p%d" % p, fill=(255, 0, 0))

fn = "_pdf_sheet_p%d-%d.png" % (p1, p2)
sheet.save(fn)
print(fn)
