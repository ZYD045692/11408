# -*- coding: utf-8 -*-
"""探查数学书 origin 结构与 PDF 书签情况，结果打印到终端。"""
import os, re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import fitz

print("## 11408/pdf")
for f in sorted(os.listdir("11408/pdf")):
    print("  ", f)
print("## 11408/origin")
for f in sorted(os.listdir("11408/origin")):
    print("  ", f)

MATH = {
    "30讲-高数": "11408/origin/27张宇基础30讲（高数）",
    "30讲-线代": "11408/origin/27张宇基础30讲线代",
    "1000题-试题册": "11408/origin/27张宇1000题数一【试题册】",
    "1000题-解析册": "11408/origin/27张宇1000题数一【解析册】",
}
for book, d in MATH.items():
    mds = [f for f in os.listdir(d) if f.endswith(".md")]
    print(f"\n== {book} == mds: {mds}")
    for mdf in mds[:1]:
        path = os.path.join(d, mdf)
        text = open(path, encoding="utf-8").read()
        heads = re.findall(r"(?m)^(#{1,5})\s+(.{0,40})", text)
        lvl = {}
        for h, t in heads:
            lvl.setdefault(len(h), []).append(t)
        for k in sorted(lvl):
            print(f"  {'#'*k} x{len(lvl[k])}: 例: {lvl[k][:6]}")
        # 找题目相关标题
        qa = [t for h, t in heads if re.search(r"习题|试题|答案|解析|题精选", t)]
        print(f"  题/答相关标题 x{len(qa)}: {qa[:10]}")
        # ##### 题号
        nums = re.findall(r"(?m)^#####\s+(.*)$", text)
        print(f"  ##### x{len(nums)}: {nums[:8]}")

print("\n## PDF 书签")
for f in sorted(os.listdir("11408/pdf")):
    if not f.endswith(".pdf"):
        continue
    doc = fitz.open(os.path.join("11408/pdf", f))
    toc = doc.get_toc()
    print(f"  {f}: {doc.page_count}页, 书签{len(toc)}条", toc[:3] if toc else "")
    doc.close()
