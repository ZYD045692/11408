# -*- coding: utf-8 -*-
"""扫含 ? 或整句的标题（正文被误当大纲）"""
import io, sys, re, glob
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

HEAD = re.compile(r"^(#{1,6})\s+(.*)$")
for f in sorted(glob.glob("11408/origin/*/*.md")):
    hits = []
    for i, l in enumerate(open(f, encoding="utf-8"), 1):
        m = HEAD.match(l)
        if not m:
            continue
        t = m.group(2).strip()
        if "？" in t or "?" in t:
            hits.append((len(m.group(1)), i, "Q", t[:60]))
        elif len(t) > 20 and re.search(r"[。；：]", t) and re.search(r"[，；。]", t):
            # 长句（有多个逗号/分号，结尾带句读）
            hits.append((len(m.group(1)), i, "S", t[:60]))
    if hits:
        print(f"== {f.split('/')[-2]}: {len(hits)}")
        for lv, i, kind, t in hits[:20]:
            print(f"  H{lv} L{i} [{kind}]: {t}")
