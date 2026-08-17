# -*- coding: utf-8 -*-
"""列出所有未闭合 <div style="text-align: center;"> 及其后续首个非空内容，用于分类决策"""
import io, sys, re, glob
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

for f in sorted(glob.glob("11408/origin/*/*.md")):
    lines = open(f, encoding="utf-8").read().split("\n")
    stack = []
    for i, l in enumerate(lines, 1):
        opens = len(re.findall(r"<div\b", l, re.I))
        closes = len(re.findall(r"</div>", l, re.I))
        for _ in range(opens):
            stack.append(i)
        for _ in range(closes):
            if stack:
                stack.pop()
    if not stack:
        continue
    print("=" * 60)
    print(f.split("/")[-2], f"未闭合 {len(stack)} 处")
    for idx, ln in enumerate(stack):
        # 首个非空内容
        content = None
        for k in range(ln, min(len(lines) + 1, ln + 6)):
            s = lines[k - 1].strip()
            if s and s != '<div style="text-align: center;">':
                content = (k, s[:45])
                break
        if content is None:
            content = ("EOF", "")
        kind = "img" if content[1].startswith("<img") else (
            "div" if content[1].startswith("<div") else (
                "head" if content[1].startswith("#") else "text"))
        print(f"  L{ln} 首内容[{kind}] L{content[0]}: {content[1]}")
