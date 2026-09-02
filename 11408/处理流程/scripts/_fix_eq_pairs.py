# -*- coding: utf-8 -*-
"""修复成对 == 触发 Obsidian 黄色高亮：把 C 表达式包进反引号。"""
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

def patch(md, pairs):
    txt = open(md, encoding="utf-8").read()
    ok = 0
    for old, new in pairs:
        if old not in txt:
            print(f"  ⚠ 未找到: {old[:40]!r}")
            continue
        txt = txt.replace(old, new)
        ok += 1
    open(md, "w", encoding="utf-8").write(txt)
    print(f"{md.split('/')[-2]}: 替换 {ok}/{len(pairs)} 组")

patch("11408/origin/2027操作系统/2027操作系统.md", [
    ("if(a==b)", "`if(a==b)`"),
])

patch("11408/origin/2027数据结构/2027数据结构.md", [
    ("if (n==1) return 1;", "`if (n==1) return 1;`"),
    ("head->next==NULL", "`head->next==NULL`"),
    ("head==NULL", "`head==NULL`"),
    ("end1 == end2；", "`end1 == end2`；"),
    ("end1 == (end2+1) mod M", "`end1 == (end2+1) mod M`"),
    ("ST.elem[i]==key", "`ST.elem[i]==key`"),
    ("ST.elem[0]==key", "`ST.elem[0]==key`"),
])
