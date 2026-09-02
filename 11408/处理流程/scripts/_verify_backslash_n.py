# -*- coding: utf-8 -*-
"""验证：代码块外、非 \\neq/\\nu 前缀的字面 \\n 残留"""
import io, sys, re, glob
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

REAL_N = re.compile(r"\\n(?![eun])")  # 字面 \n 后不跟 e/u/n（排除 \neq \nu \ne 前缀误报）
total = 0
for f in sorted(glob.glob("11408/origin/*/*.md")):
    in_code = False
    hits = []
    for i, l in enumerate(open(f, encoding="utf-8"), 1):
        s = l.strip()
        if s.startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        if REAL_N.search(l):
            hits.append((i, l[max(0, l.index("\\n") - 18):l.index("\\n") + 10]))
    if hits:
        print(f"== {f.split('/')[-2]}: {len(hits)} 处")
        for i, t in hits[:10]:
            print(f"  L{i}: ...{t}...")
        total += len(hits)
print("总计字面\\n残留:", total)
