# -*- coding: utf-8 -*-
"""终检2：\\quad\\ 等反斜杠残留 / 行$奇偶 / 连续重复行 / 公式内全角空格 / 失衡 == 高亮 / 孤儿div"""
import io, sys, re, glob
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BOOKS = sorted(glob.glob("11408/origin/*/*.md"))

for f in BOOKS:
    lines = open(f, encoding="utf-8").read().split("\n")
    q_back = []
    odd = []
    dup = []
    fw_space = []
    hl = []
    orphan = []
    prev = None
    for i, l in enumerate(lines, 1):
        s = l.strip()
        if "\\quad\\" in l or re.search(r"\\\s*$", l.strip()):
            q_back.append((i, l.strip()[:70]))
        n = l.count("$")
        if n % 2 == 1 and not s.startswith("```"):
            odd.append((i, l.strip()[:70]))
        if s and s == prev:
            dup.append((i, s[:70]))
        if re.search(r"\$\S*　\S*\$", l):
            fw_space.append((i, l.strip()[:70]))
        # 高亮 == 失衡（非反引号/非公式内）
        if "==" in l and l.count("==") % 2 == 1 and "```" not in l:
            hl.append((i, l.strip()[:70]))
        if re.search(r"<(/?)(table|tr|td|div)\b", l, re.I):
            for m in re.finditer(r"<(/)?(table|tr|td|div)\b", l, re.I):
                pass
        prev = s
    # 标签配对粗略统计
    tags = {"table": 0, "tr": 0, "td": 0, "div": 0}
    for l in lines:
        for t in tags:
            tags[t] += len(re.findall(r"<%s\b" % t, l, re.I)) - len(re.findall(r"</%s>" % t, l, re.I))
    probs = []
    if q_back: probs.append(f"反斜杠残留{len(q_back)}")
    if odd: probs.append(f"行$奇数{len(odd)}")
    if dup: probs.append(f"连续重复行{len(dup)}")
    if fw_space: probs.append(f"公式内全角空格{len(fw_space)}")
    if hl: probs.append(f"失衡=={len(hl)}")
    if any(tags.values()): probs.append(f"标签失衡{ {k:v for k,v in tags.items() if v} }")
    if probs:
        print(f"{f.split('/')[-2]}: " + "; ".join(probs))
        for i, t in (q_back + odd + dup + fw_space + hl)[:6]:
            print(f"    L{i}: {t}")
