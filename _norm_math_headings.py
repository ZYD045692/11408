# -*- coding: utf-8 -*-
"""30讲高数/线代 origin 标题层级规范化。

规则:
  第N讲 -> H2
  基础知识结构/基础内容精讲/基础习题精练 -> H3
  习题/解答 -> H4
  页码残留(考研数学基础30讲 · XX分册) -> 删除
  解 应选(X) / 注 xxx / 参考例 / 从右往左是展开 等 -> 普通文本
  其余内容标题 -> 由 pass2 按上下文定级(父级+1, 同类连续视为兄弟)
"""
import io, sys, re, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BOOKS = [
    "11408/origin/27张宇基础30讲（高数）/27张宇基础30讲（高数）.md",
    "11408/origin/27张宇基础30讲线代/27张宇基础30讲线代.md",
]

HEAD = re.compile(r'^(#{1,6})\s+(.*)$')
LEC  = re.compile(r'^第\s*\d+\s*讲')
BASE = re.compile(r'^基础知识结构$|^基础内容精讲$|^基础习题精练$')
TXHW = re.compile(r'^(习题|解答)$')
PAGE = re.compile(r'^考研数学基础30讲\s*·\s*(高等数学|线性代数)分册\s*$')
SOLVE = re.compile(r'^解\s*\S|^解$')
NOTE  = re.compile(r'^注\s*\S|^注$')
REF   = re.compile(r'^参考例\s*\d')

def classify(t):
    if LEC.match(t):   return ('keep', 2)
    if BASE.match(t):  return ('keep', 3)
    if TXHW.match(t):  return ('keep', 4)
    if PAGE.match(t):  return ('delete', None)
    if SOLVE.match(t) or NOTE.match(t) or REF.match(t): return ('text', None)
    if t in ("从右往左是展开", "想办法联系起来"): return ('text', None)
    return ('ctx', None)

for md in BOOKS:
    lines = open(md, encoding="utf-8").read().split("\n")
    n_keep = n_text = n_del = n_ctx = 0
    new = []
    for l in lines:
        m = HEAD.match(l)
        if not m:
            new.append(l); continue
        t = m.group(2).strip()
        if t.startswith("📑"):
            new.append(l); continue
        kind, arg = classify(t)
        if kind == 'keep':
            n_keep += 1
            new.append("#" * arg + " " + t)
        elif kind == 'delete':
            n_del += 1
            continue
        elif kind == 'text':
            n_text += 1
            new.append(t)
        else:
            n_ctx += 1
            new.append(l)  # pass2 处理
    open(md, "w", encoding="utf-8").write("\n".join(new))
    print(f"{os.path.basename(md)}: 定级{n_keep} 去#普通{n_text} 删页码{n_del} 待pass2{n_ctx}")
