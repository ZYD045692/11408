# -*- coding: utf-8 -*-
# 把 公式待修清单.md 映射到 origin 行号，生成 origin 定位版
# 定位策略：
#   1. 每个拆分稿文件用"首个非空行"(章节标题)在 origin 中定位 → 得到该文件相对 origin 的行偏移
#   2. 条目 origin 行号 = 拆分行号 + 偏移，校验内容归一化后包含关系；失败则回退全文搜索
import io, sys, os, re, glob
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

SPLIT_ROOTS = {
    "30讲-高数": "11408/拆分稿/数学/30讲-高数",
    "30讲-线代": "11408/拆分稿/数学/30讲-线代",
}
ORIGIN = {
    "30讲-高数": "11408/origin/27张宇基础30讲（高数）/27张宇基础30讲（高数）.md",
    "30讲-线代": "11408/origin/27张宇基础30讲线代/27张宇基础30讲线代.md",
}

def norm(s):
    return re.sub(r"\s+", "", s)

# ---- 解析清单 ----
entries = []  # (book, split_file, line_no, snippet)
book = None
for line in open("11408/公式待修清单.md", encoding="utf-8").read().split("\n"):
    if line.startswith("## "):
        book = line[3:].strip()
    elif line.startswith("- ") and book:
        m = re.match(r"-\s*(.+\.md)\s*L(\d+)\s*INLINE:\s*(.*)$", line)
        if m:
            entries.append((book, m.group(1), int(m.group(2)), m.group(3)))

# ---- 预载 origin 行 + 计算每个拆分稿的偏移 ----
odata = {}
offsets = {}
for book, root in SPLIT_ROOTS.items():
    olines = open(ORIGIN[book], encoding="utf-8").read().split("\n")
    odata[book] = olines
    for f in sorted(os.listdir(root)):
        if not f.endswith(".md"):
            continue
        slines = open(os.path.join(root, f), encoding="utf-8").read().split("\n")
        # 找拆分稿首个非空行
        off = None
        for i, l in enumerate(slines):
            if l.strip():
                target = norm(l)
                for j, ol in enumerate(olines):
                    if target and norm(ol) == target:
                        off = (j + 1) - (i + 1)
                        break
                break
        offsets[(book, f)] = off

def locate(book, sfile, sln, snip):
    olines = odata[book]
    spath = os.path.join(SPLIT_ROOTS[book], sfile)
    slines = open(spath, encoding="utf-8").read().split("\n")
    split_line = slines[sln - 1] if 0 < sln <= len(slines) else ""
    sn = norm(split_line)
    off = offsets.get((book, sfile))
    if off is not None and sn:
        cand = sln + off
        if 1 <= cand <= len(olines):
            on = norm(olines[cand - 1])
            if on == sn or (sn and sn in on):
                return cand, olines[cand - 1]
    # 回退：全文搜索（只允许 sn 在 on 中，杜绝空串误匹配）
    if sn:
        for j in range(len(olines)):
            on = norm(olines[j])
            if on and (on == sn or sn in on):
                return j + 1, olines[j]
    if snip:
        sn2 = norm(snip)
        for j in range(len(olines)):
            on = norm(olines[j])
            if on and sn2 and sn2 in on:
                return j + 1, olines[j]
    return None, None

out = ["# 公式缺失/损坏清单（origin 定位版）", "",
       "> 用法：在 Obsidian 中打开对应 origin 文件，按 **L 行号** 跳转，对照原书补全公式。", ""]
cur = None
for book, sfile, sln, snip in entries:
    if book != cur:
        out.append(f"## {book}")
        out.append("")
        cur = book
    olno, oline = locate(book, sfile, sln, snip)
    if olno:
        out.append(f"- **{sfile} 拆分L{sln}** → origin **L{olno}**：`{oline[:70]}`")
    else:
        out.append(f"- **{sfile} 拆分L{sln}** → ⚠️ 未在 origin 定位：`{snip[:40]}`")

out.append("")
open("11408/公式待修清单-origin定位.md", "w", encoding="utf-8").write("\n".join(out))
print("\n".join(out))
