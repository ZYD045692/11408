# -*- coding: utf-8 -*-
"""找计组 7.2 之前最后一个书签页，界定 7.1 范围"""
import os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _vlm_lib as V

toc, _ = V.pdf_toc(V.BOOKS["计算机组成原理"][1])
idx = [i for i, (l, t, p) in enumerate(toc) if t.strip().startswith("7.2 ")][0]
for l, t, p in toc[max(0, idx - 8):idx + 1]:
    print((l, t, p))
