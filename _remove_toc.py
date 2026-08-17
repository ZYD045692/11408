# -*- coding: utf-8 -*-
"""移除 8 本 origin 文件头部的 📑 快速跳转 目录块（到第一个 --- 分隔行）。
拆分脚本 find_body 本来就跳过该块，删除对拆分零影响。"""
import io, sys, re, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BOOKS = [
    "11408/origin/2027操作系统/2027操作系统.md",
    "11408/origin/2027数据结构/2027数据结构.md",
    "11408/origin/2027计算机组成原理/2027计算机组成原理.md",
    "11408/origin/2027计算机网络/2027计算机网络.md",
    "11408/origin/27张宇基础30讲（高数）/27张宇基础30讲（高数）.md",
    "11408/origin/27张宇基础30讲线代/27张宇基础30讲线代.md",
    "11408/origin/27张宇1000题数一【试题册】/27张宇1000题数一【试题册】.md",
    "11408/origin/27张宇1000题数一【解析册】/27张宇1000题数一【解析册】.md",
]

for md in BOOKS:
    lines = open(md, encoding="utf-8").read().split("\n")
    # 找到第一个 "## 📑 快速跳转"
    start = None
    for i, l in enumerate(lines):
        if l.strip() == "## 📑 快速跳转":
            start = i
            break
    if start is None:
        print(f"{os.path.basename(md)}: 无快速跳转，跳过")
        continue
    # 找到其后第一个 --- 分隔行
    end = None
    for j in range(start, len(lines)):
        if lines[j].strip() == "---":
            end = j
            break
    if end is None:
        end = len(lines)
    removed = lines[start:end + 1]
    new = lines[:start] + lines[end + 1:]
    # 清理开头多余空行
    while new and not new[0].strip():
        new.pop(0)
    open(md, "w", encoding="utf-8").write("\n".join(new).rstrip("\n") + "\n")
    print(f"{os.path.basename(md)}: 删 {len(removed)} 行（{len(removed)} 行 TOC 块）")
