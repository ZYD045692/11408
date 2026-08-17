# -*- coding: utf-8 -*-
"""线代 origin:例题/课后习题/解答 行转标题(父级+1,封顶H6),题干截短为纯编号。
与高数两脚本合并版,一步到位。内容锚定+数量断言。一次性,可删。"""
import io, sys, re, shutil
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

path = "11408/origin/27张宇基础30讲线代/27张宇基础30讲线代.md"
shutil.copy(path, "_backup_round2/线代_before_tiheadings.md")
lines = open(path, encoding="utf-8").read().split("\n")

sec = None; lvl = 0; in_code = in_math = False
n_li = n_ti = n_jie = 0
out = []
for i, s in enumerate(lines):
    t = s.strip()
    if t.startswith("```"):
        in_code = not in_code
        out.append(s); continue
    if in_code:
        out.append(s); continue
    if s.count("$$") % 2 == 1:
        in_math = not in_math
        out.append(s); continue
    if in_math:
        out.append(s); continue
    m = re.match(r"^(#{2,6}) ", s)
    if m:
        lvl = len(m.group(1))
        if s.startswith("### 基础内容精讲"): sec = "精讲"
        elif s.startswith("#### 习题"): sec = "习题"
        elif s.startswith("#### 解答"): sec = "解答"
        elif s.startswith("## 第") or s.startswith("### "): sec = None
        out.append(s); continue

    if sec == "精讲":
        m = re.match(r"^(★*)\s*例\s*(\d+\.\d+)(?=\s|（)\s*(.*)$", s)
        if m and 2 <= lvl <= 6:
            stars, num, body = m.groups()
            hashes = "#" * min(lvl + 1, 6)
            out.append(f"{hashes} {stars + ' ' if stars else ''}例{num}")
            if body.strip():
                out.append("")
                out.append(body.strip())
            n_li += 1
            continue
    if sec in ("习题", "解答"):
        m = re.match(r"^(\d+\.\d+)(?=\s|（)\s*(.*)$", s)
        if m:
            num, body = m.groups()
            out.append(f"##### {num}")
            if body.strip():
                out.append("")
                out.append(body.strip())
            if sec == "习题": n_ti += 1
            else: n_jie += 1
            continue
    out.append(s)

print(f"例→标题 {n_li} (预期92) | 习题 {n_ti} (预期75) | 解答 {n_jie} (预期74)")
assert n_li == 92 and n_ti == 75 and n_jie == 74, "数量不符,不写盘!"
open(path, "w", encoding="utf-8", newline="\n").write("\n".join(out))
print("已写盘")
