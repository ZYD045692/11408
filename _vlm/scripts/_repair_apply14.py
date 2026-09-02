# -*- coding: utf-8 -*-
"""把 missing14 提取的 14 道题插入 1000题-试题册 origin md（数字位置锚定）。
试题册普通章题号是 `### k.`（三级），测试卷是 `#### k.`（四级）。
幂等：md 里已有该章该题的跳过。用法: python _repair_apply14.py [--dry-run]"""
import os, sys, io, json, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _vlm_lib as V
import _vlm_task3_math as M
from _repair_apply import find_block_1000

DRY = "--dry-run" in sys.argv
md = M.MATH["1000题-试题册"][0]
lines = open(md, encoding="utf-8").read().split("\n")

recs = {}
for line in open(os.path.join(V.VLM, "repair", "missing14.jsonl"), encoding="utf-8"):
    line = line.strip()
    if line:
        try:
            r = json.loads(line)
        except Exception:
            continue
        if r.get("content") and r.get("confident"):
            recs[(r["unit"], str(r["num"]))] = r    # retry 在后，覆盖旧的

applied = skipped = 0
for (unit, num), r in sorted(recs.items(), key=lambda kv: (kv[0][0], int(kv[0][1]))):
    h4 = len(unit.split("/")) == 3      # 综合篇/测试卷X/题型 → ####，普通章 → ###
    hprefix = "####" if h4 else "###"
    content = r["content"].strip()
    # 剥掉提取内容自带的标题行，统一重建
    content = re.sub(r"^#{3,4}\s*\d+\s*\\?\s*[.、．]?\s*", "", content).strip()
    blk = f"{hprefix} {num}.\n\n{content}"
    loc = find_block_1000(lines, unit, num)
    if loc is None:
        print(f"✗ {unit} 题{num}: 单元定位失败")
        continue
    if loc[0] != "INSERT":
        skipped += 1
        print(f"· {unit} 题{num}: 块已存在(L{loc[0]})，跳过")
        continue
    ins_at = loc[1]
    if not DRY:
        lines = lines[:ins_at] + [""] + blk.split("\n") + [""] + lines[ins_at:]
    applied += 1
    print(f"✓ {unit} 题{num}: 插入于行{ins_at}（{lines[ins_at][:30] if ins_at < len(lines) else 'EOF'} 之前）")
if not DRY and applied:
    open(md, "w", encoding="utf-8").write("\n".join(lines))
print(f"applied={applied} skipped={skipped} dry={DRY}")
