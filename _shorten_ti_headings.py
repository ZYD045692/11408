# -*- coding: utf-8 -*-
"""高数 origin:把上一轮生成的题目标题截短为纯编号,题干挪回正文行。
  ###### ★ 例 1.2 设函数...   →  ###### ★ 例1.2  +  正文行: 设函数...
  ##### 1.1 若 $\\lim...$       →  ##### 1.1       +  正文行: 若 $\\lim...$
  ##### 1.1 (B) 解 因为...      →  ##### 1.1       +  正文行: (B) 解 因为...
题号后允许跟 空白 或 全角（ 。一次性,可删。"""
import io, sys, re, shutil
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

path = "11408/origin/27张宇基础30讲（高数）/27张宇基础30讲（高数）.md"
shutil.copy(path, "_backup_round2/高数_before_shorten.md")
lines = open(path, encoding="utf-8").read().split("\n")

sec = None
in_code = in_math = False
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
    if s.startswith("### 基础内容精讲"): sec = "精讲"; out.append(s); continue
    if s.startswith("#### 习题"): sec = "习题"; out.append(s); continue
    if s.startswith("#### 解答"): sec = "解答"; out.append(s); continue
    if re.match(r"^## 第|^### ", s): sec = None

    if sec == "精讲":
        m = re.match(r"^(#{4,6})\s+(★*)\s*例\s*(\d+\.\d+)(?=\s|（)\s*(.*)$", s)
        if m:
            hashes, stars, num, body = m.groups()
            head = f"{hashes} {stars + ' ' if stars else ''}例{num}"
            out.append(head)
            if body.strip():
                out.append(body.strip())
            n_li += 1
            continue
    if sec in ("习题", "解答"):
        m = re.match(r"^(#{4,6})\s+(\d+\.\d+)(?=\s|（)\s*(.*)$", s)
        if m:
            hashes, num, body = m.groups()
            out.append(f"{hashes} {num}")
            if body.strip():
                out.append(body.strip())
            if sec == "习题": n_ti += 1
            else: n_jie += 1
            continue
    out.append(s)

print(f"例截短 {n_li} (预期344) | 习题 {n_ti} (预期185) | 解答 {n_jie} (预期183)")
assert n_li == 344 and n_ti == 185 and n_jie == 183, "数量不符,不写盘!"
open(path, "w", encoding="utf-8", newline="\n").write("\n".join(out))
print("已写盘")
