# -*- coding: utf-8 -*-
# 检查 markdown 表格行内 $..$ 中是否还有裸 |（应已转 \lvert）
import io, sys, re, glob
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
LV = "\\lvert"
RV = "\\rvert"
VE = "\\vert"
for f in sorted(glob.glob("11408/origin/*/*.md")):
    lines = open(f, encoding="utf-8").read().split("\n")
    bad = []
    for i, l in enumerate(lines, 1):
        if not l.startswith("|"):
            continue
        for m in re.finditer(r"\$([^$]+)\$", l):
            inner = m.group(1)
            stripped = inner.replace(LV, "").replace(RV, "").replace(VE, "")
            if "|" in stripped:
                bad.append((i, inner[:60]))
    if bad:
        print(f"== {f.split('/')[-2]}: {len(bad)} 处数学含裸管道")
        for i, m in bad[:8]:
            print(f"   L{i}: {m}")
