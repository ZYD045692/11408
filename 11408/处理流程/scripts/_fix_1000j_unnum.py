# -*- coding: utf-8 -*-
"""解析册：把 $$块首无编号的【解析】标签提为独立行。"""
import io, sys, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

F = "11408/origin/27张宇1000题数一【解析册】/27张宇1000题数一【解析册】.md"
lines = open(F, encoding="utf-8").read().split("\n")

PREFIX = "$$\\begin{aligned}"
targets = []
for i, l in enumerate(lines, 1):
    if l.startswith(PREFIX) and l.find("【解析】") >= 0:
        pos = l.find("【解析】")
        pre = l[len(PREFIX):pos]
        if re.match(r"^\d+\.", pre.strip()):
            continue  # 已处理的带编号
        rest = l[pos + len("【解析】"):]
        targets.append((i, pre, rest))

for ln, pre, rest in sorted(targets, reverse=True):
    # 提取 pre 中的引导文字（若有「原式」「方法一」等）保留到块内；【解析】单独成行
    new_label = "【解析】"
    new_block = PREFIX + rest
    lines[ln - 1] = new_label
    lines[ln:ln] = [new_block]
    print("L%d -> |%s| |%s…|" % (ln, new_label, new_block[:40]))

open(F, "w", encoding="utf-8").write("\n".join(lines))
print("done", [t[0] for t in targets])
