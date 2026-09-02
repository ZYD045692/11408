# -*- coding: utf-8 -*-
"""精确统计：div 失衡 / 行尾反斜杠 / 连续重复行 / 失衡 == 样本"""
import io, sys, re, glob
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

for f in sorted(glob.glob("11408/origin/*/*.md")):
    lines = open(f, encoding="utf-8").read().split("\n")
    bal = 0
    first_unclosed = None
    for i, l in enumerate(lines, 1):
        d = len(re.findall(r"<div\b", l, re.I)) - len(re.findall(r"</div>", l, re.I))
        if d and first_unclosed is None and bal + d > 1:
            first_unclosed = (i, l.strip()[:60])
        bal += d
    trailing = [(i, l.strip()[:70]) for i, l in enumerate(lines, 1)
                if l.rstrip().endswith("\\") and not l.lstrip().startswith("```")]
    prev = None
    dups = []
    for i, l in enumerate(lines, 1):
        s = l.strip()
        if s and s == prev and len(s) > 5:
            dups.append((i, s[:60]))
        prev = s
    hl = []
    for i, l in enumerate(lines, 1):
        if "```" in l or "$" in l:
            continue
        if l.count("==") % 2 == 1:
            hl.append((i, l.strip()[:70]))
    probs = []
    if bal: probs.append(f"div 失衡 {bal:+d}")
    if trailing: probs.append(f"行尾反斜杠 {len(trailing)}")
    if dups: probs.append(f"连续重复 {len(dups)}")
    if hl: probs.append(f"失衡== {len(hl)}")
    if probs:
        print(f"{f.split('/')[-2]}: " + "; ".join(probs))
        if first_unclosed: print(f"   首个未闭合div L{first_unclosed[0]}: {first_unclosed[1]}")
        for i, t in (trailing + dups + hl)[:5]:
            print(f"   L{i}: {t}")
