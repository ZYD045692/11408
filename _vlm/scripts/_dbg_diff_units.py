# -*- coding: utf-8 -*-
"""对比 备份 vs 当前 解析册/试题册 各单元题号集合差异"""
import os, sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _vlm_lib as V
import _vlm_task3_math as M

for book, splitter in (("1000题-解析册", M.split_1000_a), ("1000题-试题册", M.split_1000_q)):
    cur = splitter(M.MATH[book][0])
    old = splitter(os.path.join(V.VLM, "md_backup", f"{book}.md"))
    cu = {u["unit"]: set(u["probs"]) for u in cur}
    ou = {u["unit"]: set(u["probs"]) for u in old}
    print(f"== {book} 单元数 {len(ou)}→{len(cu)}")
    for unit in sorted(set(cu) | set(ou)):
        c, o = cu.get(unit, set()), ou.get(unit, set())
        if c != o:
            print(f"  {unit}: +{sorted(c - o, key=lambda x: int(x) if x.isdigit() else 0)} -{sorted(o - c, key=lambda x: int(x) if x.isdigit() else 0)}")
