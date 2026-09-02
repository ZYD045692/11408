# -*- coding: utf-8 -*-
"""1) 解析册行对组合二分  2) 坏文件独有 token 集合差分析"""
import os, re, glob
BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results", "task4_images_context")
src = open(os.path.join(BASE, "1000题-解析册.md"), encoding="utf-8").read()
lines = src.split("\n")
head = [l for l in lines if not l.startswith("|")]
tbl = [l for l in lines if l.startswith("|")]
hdr, rows = tbl[:2], tbl[2:]
def w(name, idxs):
    open(os.path.join(BASE, name), "w", encoding="utf-8", newline="\n").write(
        "\n".join(head + hdr + [rows[i] for i in idxs]))
    print("写出", name, "含行", [i + 1 for i in idxs])
w("_ta_行12.md", [0, 1])
w("_tb_行34.md", [2, 3])
w("_tc_行13.md", [0, 2])
w("_td_行14.md", [0, 3])

# 集合差：坏文件里出现、好文件里不出现的 token
bad = {"30讲-高数.md", "操作系统.md", "1000题-解析册.md"}
def toks(t):
    t = re.sub(r"[一-鿿]+", " ", t)          # 去中文
    return set(re.findall(r"[^\s|]+", t))
B, G = set(), set()
for fn in glob.glob(os.path.join(BASE, "*.md")):
    n = os.path.basename(fn)
    if n.startswith("_"):
        continue
    t = toks(open(fn, encoding="utf-8").read())
    (B if n in bad else G).update(t)
uniq = sorted(B - G)
print("\n坏文件独有token(去重后):", len(uniq))
for x in uniq:
    if not re.match(r"^[\w./:-]+$", x) or any(c in x for c in "<>[]{}$\\`'\"=:!?"):
        print("  ", x[:120])
