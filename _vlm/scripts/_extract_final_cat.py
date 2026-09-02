# -*- coding: utf-8 -*-
"""从手动校正后的 task4 报告 .md 提取最终 cat，与 JSONL 对比；输出 cat=D 清单。
行格式: | img_NN.jpg | ![[...\|80]] | t1 | cat | sub | 描述 | 上下文 | raw |"""
import os, re, json, glob
BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results", "task4_images_context")
ROW = re.compile(r"^\|\s*(img_\d+\.jpg)\s*\|.*?\]\]\s*\|\s*([A-D]?)\s*\|\s*([A-D]?)\s*\|")
out = {}
for fn in sorted(glob.glob(os.path.join(BASE, "*.md"))):
    book = os.path.basename(fn)[:-3]
    md_cat = {}
    for line in open(fn, encoding="utf-8"):
        m = ROW.match(line)
        if m:
            md_cat[m.group(1)] = (m.group(2), m.group(3))
    jl = {}
    jf = os.path.join(BASE, book + ".jsonl")
    for line in open(jf, encoding="utf-8"):
        r = json.loads(line)
        jl[r["img"]] = r.get("cat")
    changed = {i: (jl.get(i), c[1]) for i, c in md_cat.items() if jl.get(i) != c[1]}
    nD = sum(1 for c in md_cat.values() if c[1] == "D")
    out[book] = {i: c[1] for i, c in md_cat.items()}
    print(f"{book}: md行数={len(md_cat)} jsonl行数={len(jl)} 人工改判={len(changed)} 其中D={nD}")
    for i, (old, new) in sorted(changed.items()):
        print(f"   {i}: {old} -> {new}")
dst = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "repair", "task4_final_cat.json")
json.dump(out, open(dst, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("写出", os.path.normpath(dst))
