# -*- coding: utf-8 -*-
"""状态机精确扫描公式边界空格：开 $ 后紧跟空格 / 闭 $ 前有空格（跨行，跳过 \\$ 转义与 $$ 块）"""
import io, sys, re, glob
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

for f in sorted(glob.glob("11408/origin/*/*.md")):
    txt = open(f, encoding="utf-8").read()
    n = len(txt)
    inmath = False
    i = 0
    hits = []
    while i < n:
        ch = txt[i]
        if ch == "\\" and i + 1 < n and txt[i + 1] == "$":
            i += 2
            continue
        if ch == "$":
            if txt.startswith("$$", i):
                i += 2
                continue
            if not inmath:
                j = i + 1
                if j < n and txt[j] == " ":
                    line = txt[:i].count("\n") + 1
                    hits.append(("开$后空格", line, txt[max(0, i - 25):i + 40].replace("\n", "⏎")))
                inmath = True
            else:
                if i > 0 and txt[i - 1] == " ":
                    line = txt[:i].count("\n") + 1
                    hits.append(("闭$前空格", line, txt[max(0, i - 45):i + 15].replace("\n", "⏎")))
                inmath = False
        i += 1
    if hits:
        print("=" * 60)
        print(f.split("/")[-2], len(hits), "处")
        for kind, line, ctx in hits[:15]:
            print(f"  L{line} [{kind}]: ...{ctx}...")
