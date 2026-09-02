# -*- coding: utf-8 -*-
# 聚焦"破坏拆分边界"的结构异常：
#   1) 章标题不是标准 # 第N章（408）/ 1000题章标题
#   2) 节标题被脚注污染：### $^{...}$N.M 或 ### N.M$...$
#   3) 习题区/答案区标题不是 #### 开头
import io, sys, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BOOKS = [
    ("2027数据结构", "2027数据结构/2027数据结构.md"),
    ("2027操作系统", "2027操作系统/2027操作系统.md"),
    ("2027计算机组成原理", "2027计算机组成原理/2027计算机组成原理.md"),
    ("2027计算机网络", "2027计算机网络/2027计算机网络.md"),
    ("30讲-高数", "27张宇基础30讲（高数）/27张宇基础30讲（高数）.md"),
    ("30讲-线代", "27张宇基础30讲线代/27张宇基础30讲线代.md"),
    ("1000题-试题册", "27张宇1000题数一【试题册】/27张宇1000题数一【试题册】.md"),
    ("1000题-解析册", "27张宇1000题数一【解析册】/27张宇1000题数一【解析册】.md"),
]

# 章节标题（各种级别），带行号
for name, origin in BOOKS:
    lines = open("11408/origin/" + origin, encoding="utf-8").read().split("\n")
    ch_bad, sec_bad, ex_bad = [], [], []
    for i, l in enumerate(lines):
        s = l.strip()
        if not s or not s.startswith("#"):
            continue
        # --- 章标题检查 ---
        # 含"第N章"的标题行
        m = re.search(r"第\s*(\d+)\s*章", s)
        if m and s.startswith("#"):
            if not (s.startswith("# 第") and not s.startswith("##")):
                # 不是 "# 第N章"（一个井号）
                ch_bad.append((i + 1, s[:70]))
            continue
        if re.search(r"第\s*\d+\s*讲", s) and re.match(r"^#{3,}", s):
            ch_bad.append((i + 1, s[:70] + "  <讲用了###+"))
            continue
        if name.startswith("1000题") and re.search(r"基础篇|强化篇|综合篇|测试卷", s) and re.match(r"^#{2,}", s):
            ch_bad.append((i + 1, s[:70] + "  <篇/卷用了##+"))
            continue
        # --- 408 节标题被脚注污染 ---
        if name.startswith("2027"):
            if s.startswith("### "):
                # 节标题应有 ### N.M 开头；若被 $..$ 污染则异常
                if re.match(r"^###\s+\$", s) and re.search(r"\d+\.\d+", s):
                    sec_bad.append((i + 1, s[:70]))
            # --- 习题区/答案区标题不是 #### ---
            if re.search(r"本节(试题|习题)精选|答案与解析", s) and not s.startswith("####"):
                ex_bad.append((i + 1, s[:70]))

    print(f"\n===== {name} =====")
    if ch_bad:
        print("  [章标题格式异常]")
        for ln, t in ch_bad:
            print(f"    L{ln}: {t}")
    if sec_bad:
        print("  [节标题被脚注污染]")
        for ln, t in sec_bad:
            print(f"    L{ln}: {t}")
    if ex_bad:
        print("  [习题区标题非####]")
        for ln, t in ex_bad:
            print(f"    L{ln}: {t}")
    if not ch_bad and not sec_bad and not ex_bad:
        print("  ✓ 无破坏性结构异常")
