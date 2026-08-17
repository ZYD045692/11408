# -*- coding: utf-8 -*-
"""修复 1000题 origin 的公式边界空格（Obsidian MathJax 要求 $ 与内容紧贴）。
只删开 $ 后的空格和闭 $ 前的空格；文本分隔空格（x $y$ 的 $ 前）不动。
块级 $$...$$ 同样处理。
用法: python _fix_spaces_1000.py
"""
import io, sys, os, glob, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

def fix_block(text):
    """$$ x $$ -> $$x$$（内容不含 $ 才处理）"""
    return re.sub(r"\$\$[ \t]+([^$\n]+?)[ \t]+\$\$", r"$$\1$$", text)

def fix_inline(text):
    """行内 $...$ 配对，删边界空格。返回 (新文本, 修复数)"""
    n = len(text)
    dollars = []
    i = 0
    while i < n:
        if text[i] == '$':
            if i + 1 < n and text[i + 1] == '$':
                i += 2
                continue
            dollars.append(i)
            i += 1
        else:
            i += 1
    if len(dollars) % 2 != 0:
        print(f"  WARN: 单$数量为奇数 {len(dollars)}，最后一对不处理")
    chars = list(text)
    fixed = 0
    pairs = list(zip(dollars[0::2], dollars[1::2]))
    for a, b in reversed(pairs):
        # 闭 $ 前的空格（b 位置左侧）
        k = b - 1
        while k >= 0 and chars[k] in ' \t':
            k -= 1
        if k < b - 1:
            del chars[k + 1:b]
            fixed += b - k - 1
            b = k + 1  # 位置更新（向左移）
        # 开 $ 后的空格（a 位置右侧）——注意 a < b 仍成立
        k = a + 1
        while k < len(chars) and chars[k] in ' \t':
            k += 1
        if k > a + 1:
            del chars[a + 1:k]
            fixed += k - a - 1
    return "".join(chars), fixed

for b in ["27张宇1000题数一【试题册】", "27张宇1000题数一【解析册】"]:
    md = glob.glob(f"11408/origin/{b}/*.md")[0]
    txt = open(md, encoding="utf-8").read()
    before = len(txt)
    txt = fix_block(txt)
    txt, n1 = fix_inline(txt)
    # 再跑一遍（块级与行内交错可能有漏）
    txt2, n2 = fix_inline(txt)
    txt2 = fix_block(txt2)
    total = n1 + n2 + (len(txt) - len(txt2) - (n1 + n2))
    open(md, "w", encoding="utf-8").write(txt2)
    removed = before - len(txt2)
    print(f"{b}: 删除边界空格 {removed} 字符（纯空格，无内容改动）")
    # 验证：$ 后空格残留
    resid = len(re.findall(r"\$[ \t][^$\n]", txt2))
    print(f"  残留 '$空格': {resid}")
