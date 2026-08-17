# -*- coding: utf-8 -*-
"""导出 PDF 书签目录（标题+页码）"""
import io, sys, fitz
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

pdf = sys.argv[1]
doc = fitz.open(pdf)
toc = doc.get_toc()

def walk(items, depth=0):
    for lvl, title, page in items:
        if depth < lvl:
            print("%s%s  p%d" % ("  " * (lvl - 1), title, page))

walk(toc)
print("\n总页数:", doc.page_count)
