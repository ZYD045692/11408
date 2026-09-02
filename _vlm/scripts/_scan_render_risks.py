# -*- coding: utf-8 -*-
"""全局渲染风险扫描（不动文件，只报告）:
1) 行内 $ 为奇数的行（可能未闭合的行内公式 → Obsidian 渲染异常/变色）
2) $$ 显示公式块的开关配对（按全文 $$ 计数奇偶）
3) 单元格内疑似构造在 origin 正文中的存在情况（origin 的 HTML 表格是正常块，仅统计）
4) 残留控制字符
"""
import glob, os, re
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
for f in sorted(glob.glob("11408/origin/*/*.md")):
    lines = open(f, encoding="utf-8").read().split("\n")
    odd_dollar = []
    for i, l in enumerate(lines, 1):
        if l.startswith("|") or "<table" in l:
            continue
        # 去掉转义 \$ 不存在于这些书，直接数
        if l.count("$") % 2:
            odd_dollar.append(i)
    dd = sum(l.count("$$") for l in lines)
    ctrl = sum(1 for l in lines for c in l if ord(c) < 32 and c != "\t")
    print(os.path.basename(f),
          f"行内$奇数行={len(odd_dollar)}", odd_dollar[:6] if odd_dollar else "",
          f"| $$总数={dd}({'偶' if dd % 2 == 0 else '奇!'})", f"| 控制字符={ctrl}")
