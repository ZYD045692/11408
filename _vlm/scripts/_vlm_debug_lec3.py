# -*- coding: utf-8 -*-
"""调试3：看第2讲答案页 OCR 原文里题号长什么样。"""
import sys, io, os, re, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _vlm_task3_math as M

full = M.load_full("30讲-高数")
units = M.parse_30jiang(M.MATH["30讲-高数"][0])
u2 = [u for u in units if u["lec"] == 2][0]
print("第2讲 A 题号:", sorted(u2["a"], key=lambda x: float(x)))
for p in range(102, 106):
    t = full.get(p, "")
    hits = re.findall(r"2\s*[.．、]\s*\d{1,2}", t)
    print(f"--- p{p+1} 含2.x串: {hits}")
    print(t[:400].replace("\n", "⏎"))
    print()
