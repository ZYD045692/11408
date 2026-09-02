# -*- coding: utf-8 -*-
"""查计组 7.1 附近书签 + 8.5 附近书签（数据结构）"""
import os, sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _vlm_lib as V

for book, prefix in (("计算机组成原理", "7."), ("数据结构", "8.")):
    toc, _ = V.pdf_toc(V.BOOKS[book][1])
    hits = [(l, t, p) for l, t, p in toc if t.strip().startswith(prefix)]
    print(f"== {book} 以 {prefix} 开头的书签 ==")
    for h in hits:
        print(" ", h)
