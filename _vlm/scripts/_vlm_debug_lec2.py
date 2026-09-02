# -*- coding: utf-8 -*-
"""调试2：每讲的 习题/解答 页范围 + 题号定位命中率。"""
import sys, io, re, os
if sys.stdout is not None and hasattr(sys.stdout, "buffer") and (sys.stdout.encoding or "").lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _vlm_task3_math as M

full = M.load_full("30讲-高数")
units = M.parse_30jiang(M.MATH["30讲-高数"][0])
units = M.locate_30jiang("30讲-高数", units, full)
for u in units:
    loc_q = sum(1 for n in u["q"] if u.get("pp_q", {}).get(n) is not None)
    loc_a = sum(1 for n in u["a"] if u.get("pp_a", {}).get(n) is not None)
    pq = u.get("pages_q"); pa = u.get("pages_a")
    f = lambda r: f"p{r[0]+1}~p{r[1]}" if r else "None"
    print(f"第{u['lec']:>2}讲: Q题{len(u['q'])}(定位{loc_q}) {f(pq)} | A题{len(u['a'])}(定位{loc_a}) {f(pa)}")
