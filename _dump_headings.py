# -*- coding: utf-8 -*-
# 导出指定文件所有标题序列（带行号），用于人工观察层级
import io, sys, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

md = sys.argv[1]
start = int(sys.argv[2]) if len(sys.argv) > 2 else 1
end = int(sys.argv[3]) if len(sys.argv) > 3 else 10**9
HEAD = re.compile(r'^(#{1,6})\s+(.*)$')
lines = open(md, encoding="utf-8").read().split("\n")
for i, l in enumerate(lines, 1):
    if i < start or i > end:
        continue
    m = HEAD.match(l)
    if m:
        print(f"L{i}: {'#'*len(m.group(1))} {m.group(2).strip()}")
