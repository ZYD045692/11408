# -*- coding: utf-8 -*-
"""修复未闭合 <div style="text-align: center;">：
- 首个非空内容为 <img> → 在 img 后补 </div>（保留居中）
- 其余（文本/表格/其它div/标题）→ 删除孤儿 div 行（OCR 容器残留，内容正常渲染）
改后 div 收支必须为 0。
"""
import io, sys, re, glob
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BOOKS = sorted(glob.glob("11408/origin/*/*.md"))
DIV = re.compile(r'^<div style="text-align: center;">\s*$', re.I)

for f in BOOKS:
    lines = open(f, encoding="utf-8").read().split("\n")
    n = len(lines)
    # 1) 找未闭合的 <div> 开标签（行索引 0-based）
    stack = []
    for i, l in enumerate(lines):
        opens = len(re.findall(r"<div\b", l, re.I))
        closes = len(re.findall(r"</div>", l, re.I))
        for _ in range(opens):
            stack.append(i)
        for _ in range(closes):
            if stack:
                stack.pop()
    unclosed = stack  # 0-based 索引，全部为未闭合 <div style="text-align: center;">
    if not unclosed:
        continue
    del_set = set()
    insert_at = set()  # 在此索引前插入 </div>
    for i in unclosed:
        # 找首个非空内容行
        j = i + 1
        while j < n and not lines[j].strip():
            j += 1
        if j >= n:
            del_set.add(i)
            continue
        content = lines[j].strip()
        if content.startswith("<img"):
            # img 后补 </div>：找 img 后的首个非空行，在其前插
            k = j + 1
            while k < n and not lines[k].strip():
                k += 1
            insert_at.add(k if k < n else n)
        else:
            del_set.add(i)
    # 2) 重建
    new = []
    for idx, l in enumerate(lines):
        if idx in del_set:
            continue
        if idx in insert_at:
            new.append("</div>")
        new.append(l)
    if n in insert_at:
        new.append("</div>")
    open(f, "w", encoding="utf-8").write("\n".join(new))
    # 3) 验证
    bal = 0
    for l in new:
        bal += len(re.findall(r"<div\b", l, re.I)) - len(re.findall(r"</div>", l, re.I))
    print(f"{f.split('/')[-2]}: 删 {len(del_set)} 处, 补 </div> {len(insert_at)} 处, 修复后 div 收支 {bal}")
