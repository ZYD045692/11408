# -*- coding: utf-8 -*-
"""探查3：30讲答案结构 / 1000题两篇册结构 / PDF内嵌图与origin imgs哈希匹配测试。"""
import os, re, sys, io, hashlib
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import fitz

print("## 高数 习题节后半段（找答案标题）")
text = open("11408/origin/27张宇基础30讲（高数）/27张宇基础30讲（高数）.md", encoding="utf-8").read()
i = text.find("基础习题精练")
seg = text[i:i+20000]
j = seg.find("#### ", 10)
heads = re.findall(r"(?m)^(####?) +(.{0,30})", seg)
print("  节内####/###标题:", heads[:15])

print("\n## 1000题-试题册 结构（前3章标题树 + ####出现位置）")
t2 = open("11408/origin/27张宇1000题数一【试题册】/27张宇1000题数一【试题册】.md", encoding="utf-8").read()
lines = t2.split("\n")
tree = [(l[:50]) for l in lines if re.match(r"^#{1,4} ", l)][:25]
for l in tree: print("  ", l)
# 一个 ### N. 题的完整内容样本
k = t2.find("### 1.")
print("  样本:", t2[k:k+400].replace("\n", "⏎")[:400])

print("\n## 1000题-解析册 样本")
t3 = open("11408/origin/27张宇1000题数一【解析册】/27张宇1000题数一【解析册】.md", encoding="utf-8").read()
k = t3.find("#### 1.")
print("  ", t3[k:k+400].replace("\n", "⏎")[:400])

print("\n## 图片哈希匹配测试（高数 PDF 前5页内嵌图 vs origin imgs）")
doc = fitz.open("11408/pdf/27张宇基础30讲（高数）.pdf")
img_dir = "11408/origin/27张宇基础30讲（高数）/imgs"
md5_map = {}
for f in os.listdir(img_dir):
    md5_map[hashlib.md5(open(os.path.join(img_dir, f), "rb").read()).hexdigest()] = f
hit = miss = 0
for p in range(5, 15):
    for xref, *_ in doc[p].get_images():
        b = doc.extract_image(xref)["image"]
        h = hashlib.md5(b).hexdigest()
        if h in md5_map:
            hit += 1
            print(f"  PDF p{p+1} 内嵌图 == {md5_map[h]}")
        else:
            miss += 1
doc.close()
print(f"  命中{hit} 未中{miss}（imgs总数{len(md5_map)}）")
