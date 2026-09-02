# -*- coding: utf-8 -*-
# 修复 $ 错位：\left{$ → $\left{，$\right. → \right.$（全 8 本）
import io, sys, os, re, glob
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

PAIRS = [
    (r"\\left\{\$", r"$\\left\\{"),
    (r"\\left\(\$", r"$\\left("),
    (r"\\left\[\$", r"$\\left["),
    (r"\\left\|\$", r"$\\left|"),
    (r"\$\\right\.", r"\\right.$"),
    (r"\$\\right\)", r"\\right)$"),
    (r"\$\\right\]", r"\\right]$"),
    (r"\$\\right\}", r"\\right}$"),
    (r"\$\\right\|", r"\\right|$"),
]

books = ["2027数据结构", "2027操作系统", "2027计算机组成原理", "2027计算机网络",
         "27张宇基础30讲（高数）", "27张宇基础30讲线代",
         "27张宇1000题数一【试题册】", "27张宇1000题数一【解析册】"]
for b in books:
    md = glob.glob(f"11408/origin/{b}/*.md")[0]
    txt = open(md, encoding="utf-8").read()
    n = 0
    for pat, rep in PAIRS:
        c = len(re.findall(pat, txt))
        if c:
            txt = re.sub(pat, lambda m: rep, txt)
            n += c
    if n:
        open(md, "w", encoding="utf-8").write(txt)
        print(f"{b}: 修复 {n} 处")
