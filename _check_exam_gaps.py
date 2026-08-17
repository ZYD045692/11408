# -*- coding: utf-8 -*-
# 对比 408 四本：origin 习题区节号 vs 拆分稿习题文件节号
# 找出：1) 有习题区但无习题文件 2) 习题文件为空/无题号
import io, sys, os, re, glob
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BOOKS = {
    "数据结构": "2027数据结构/2027数据结构.md",
    "操作系统": "2027操作系统/2027操作系统.md",
    "计算机组成原理": "2027计算机组成原理/2027计算机组成原理.md",
    "计算机网络": "2027计算机网络/2027计算机网络.md",
}

EX = re.compile(r"^####\s*([\d.]*)\s*(本节(?:试题|习题)精选|答案与解析)\s*$")

for b, origin in BOOKS.items():
    print(f"\n===== {b} =====")
    lines = open("11408/origin/" + origin, encoding="utf-8").read().split("\n")
    # 收集所有节 (N.M) 及其习题区
    secs_with_exam = set()
    sec_names = {}
    cur = None
    for l in lines:
        m = re.match(r"^### (\d+)\.(\d+)\s+(.*)$", l.strip())
        if m:
            cur = (int(m.group(1)), int(m.group(2)))
            sec_names[cur] = m.group(3)
            continue
        m = EX.match(l.strip())
        if m and cur:
            secs_with_exam.add(cur)
    # 拆分稿习题文件节号
    root = f"11408/拆分稿/{b}"
    files = [p for p in glob.glob(root + "/**/*.md", recursive=True) if "习题" in p]
    got = set()
    for p in files:
        base = os.path.basename(p)
        m = re.match(r"(\d+)\.(\d+)-", base)
        if m:
            got.add((int(m.group(1)), int(m.group(2))))
    # 差集
    missing = sorted(secs_with_exam - got)
    if missing:
        for (a, c) in missing:
            print(f"  ⚠ 缺失习题区: 第{a}章 {a}.{c} {sec_names.get((a,c),'')}")
    else:
        print("  ✓ 所有习题区都有对应习题文件")
    # 检查习题文件是否过小（可能为空）
    small = []
    for p in files:
        sz = os.path.getsize(p)
        if sz < 200:  # 小于200字节可能只有frontmatter
            small.append((os.path.relpath(p, root), sz))
    if small:
        for rp, sz in small:
            print(f"  ⚠ 过小文件({sz}B): {rp}")
    else:
        print("  ✓ 无过小习题文件")
