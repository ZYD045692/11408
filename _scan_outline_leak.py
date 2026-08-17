# -*- coding: utf-8 -*-
"""扫大纲泄漏：
1. Setext 标题：非空正文行 紧跟 一行 --- / ===（Obsidian 会当 H2/H1）
2. HTML 标题标签 <h1>~<h6>
"""
import io, sys, re, glob
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

for f in sorted(glob.glob("11408/origin/*/*.md")):
    lines = open(f, encoding="utf-8").read().split("\n")
    setext = []
    html_h = []
    for i, l in enumerate(lines):
        s = l.strip()
        if re.fullmatch(r"-{3,}", s) or re.fullmatch(r"={3,}", s):
            # 前一行（非空）是什么
            j = i - 1
            while j >= 0 and not lines[j].strip():
                j -= 1
            prev = lines[j].strip() if j >= 0 else ""
            if prev and not prev.startswith("#") and not prev.startswith("<"):
                setext.append((i + 1, prev[:50], s[:5]))
        if re.search(r"<h[1-6][ >]", l, re.I) or re.search(r"</h[1-6]>", l, re.I):
            html_h.append((i + 1, l.strip()[:60]))
    if setext or html_h:
        print(f"== {f.split('/')[-2]}")
        if setext:
            print(f"  Setext标题风险 {len(setext)}")
            for i, prev, sep in setext[:12]:
                print(f"    L{i} [前一行]: {prev}")
        if html_h:
            print(f"  HTML标题标签 {len(html_h)}")
            for i, t in html_h[:12]:
                print(f"    L{i}: {t}")
