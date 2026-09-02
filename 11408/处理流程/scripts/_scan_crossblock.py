# -*- coding: utf-8 -*-
# 扫描"行内 $ 开头但实际是跨行块"的公式：$ 后跟 \left{ 或 \begin{（非 $$）
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
md = sys.argv[1]
lines = open(md, encoding="utf-8").read().split("\n")
cnt = 0
for i, l in enumerate(lines, 1):
    s = l.strip()
    if s.startswith("$") and not s.startswith("$$"):
        if ("\\left{" in s) or ("\\begin{" in s):
            cnt += 1
            if cnt <= 40:
                print(f"L{i}: {s[:70]}")
print(f"共 {cnt} 个")
