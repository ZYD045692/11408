# -*- coding: utf-8 -*-
"""把 PDF 指定页渲染为 PNG（1页1图），供 Read/luma 查看。
用法: python _pdf_page.py <pdf> <p1> [p2]  （页码从1开始；1页或区间）
"""
import io, sys, fitz
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

pdf = sys.argv[1]
p1 = int(sys.argv[2])
p2 = int(sys.argv[3]) if len(sys.argv) > 3 else p1
doc = fitz.open(pdf)
out = []
for p in range(p1, p2 + 1):
    page = doc[p - 1]
    mat = fitz.Matrix(2.0, 2.0)  # 2x 放大
    pix = page.get_pixmap(matrix=mat)
    fn = "_pdf_page_%d.png" % p
    pix.save(fn)
    out.append(fn)
    print(fn)
print("done", doc.page_count)
