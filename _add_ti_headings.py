# -*- coding: utf-8 -*-
"""高数 origin:例题/课后习题/解答 行转标题(父级+1),让题目进 Obsidian 大纲。
规则: 精讲区 `例N.M ...` → 父标题+1 级; 习题/解答区 `N.M ...` → H5。
题号后允许跟 空白 或 全角（ (如 7.4（仅数学三）)。
若目标行前行以 < 开头(HTML行),先插空行防标题被吞。一次性,可删。"""
import io, sys, re, shutil
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

path = "11408/origin/27张宇基础30讲（高数）/27张宇基础30讲（高数）.md"
shutil.copy(path, "_backup_round2/高数_before_tiheadings.md")
lines = open(path, encoding="utf-8").read().split("\n")

# 先修 OCR 粘连: 13.60.4 → 13.6 0.4
for i, s in enumerate(lines):
    if s.startswith("13.60.4 解"):
        lines[i] = s.replace("13.60.4 解", "13.6 0.4 解", 1)
        print(f"OK L{i+1}: 13.60.4 -> 13.6 0.4")
        break

sec = None      # 精讲 / 习题 / 解答
lvl = 0         # 最近标题级别
in_code = in_math = False
n_li = n_ti = n_jie = n_blank = 0
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

    target = None
    if sec == "精讲" and re.match(r"^★*\s*例\s*\d+\.\d+(?=\s|（)", s):
        target = "例"
    elif sec in ("习题", "解答") and re.match(r"^\d+\.\d+(?=\s|（)", s):
        target = sec
    if target and 2 <= lvl <= 5:
        prev = out[-1] if out else ""
        if prev.strip().startswith("<"):
            out.append("")  # 防 HTML 块吞标题
            n_blank += 1
        out.append("#" * (lvl + 1) + " " + s)
        if target == "例": n_li += 1
        elif target == "习题": n_ti += 1
        else: n_jie += 1
        continue
    out.append(s)

print(f"例→标题 {n_li} (预期344) | 习题→标题 {n_ti} (预期185) | 解答→标题 {n_jie} (预期183) | 插空行 {n_blank}")
assert n_li == 344 and n_ti == 185 and n_jie == 183, "数量不符,不写盘!"
open(path, "w", encoding="utf-8", newline="\n").write("\n".join(out))
print("已写盘")
