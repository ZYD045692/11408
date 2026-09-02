# -*- coding: utf-8 -*-
"""扫「被当成标题的正文」：标题行含句末标点/过长/像句子"""
import io, sys, re, glob
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

HEAD = re.compile(r"^(#{1,6})\s+(.*)$")
SUS = re.compile(r"[。？；！]$|。.*。|，.{20,}，")  # 句末标点或长句

for f in sorted(glob.glob("11408/origin/*/*.md")):
    hits = []
    for i, l in enumerate(open(f, encoding="utf-8"), 1):
        m = HEAD.match(l)
        if not m:
            continue
        t = m.group(2).strip()
        # 排除已知结构标题
        if re.match(r"^(第\s*\d+\s*[章讲部分]|\d+\.\d+|\d+\.\d+\.\d+|\d+\.\d+\.\d+\.\d+|[一二三四五六七八九十]、|考点追踪|【|本节|答案|一、|二、|三、|\d+\s*[\\]?\.\s*[A-Z]|\d{1,3}\s+[A-Z]|例\s*\d|解\s|注\s)", t):
            continue
        if len(t) > 25 and SUS.search(t):
            hits.append((len(m.group(1)), i, t[:70]))
    if hits:
        print(f"== {f.split('/')[-2]}: {len(hits)}")
        for lv, i, t in hits[:15]:
            print(f"  H{lv} L{i}: {t}")
