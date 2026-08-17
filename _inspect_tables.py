# -*- coding: utf-8 -*-
"""抽查若干表格的转换质量（含图片保留）"""
import io, sys, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

def clean_cell(html):
    imgs = []
    def keep_img(m):
        imgs.append(m.group(0))
        return "@@IMG%d@@" % (len(imgs) - 1)
    html = re.sub(r"<img[^>]*>", keep_img, html, flags=re.I)
    html = html.strip()
    html = re.sub(r"<br\s*/?>", " ", html, flags=re.I)
    html = re.sub(r"</?p[^>]*>", " ", html, flags=re.I)
    html = re.sub(r"<b[^>]*>(.*?)</b>", r"**\1**", html, flags=re.S | re.I)
    html = re.sub(r"<strong[^>]*>(.*?)</strong>", r"**\1**", html, flags=re.S | re.I)
    html = re.sub(r"<i[^>]*>(.*?)</i>", r"*\1*", html, flags=re.S | re.I)
    html = re.sub(r"<sup[^>]*>(.*?)</sup>", r"^\1", html, flags=re.S | re.I)
    html = re.sub(r"<sub[^>]*>(.*?)</sub>", r"_\1", html, flags=re.S | re.I)
    html = re.sub(r"<[^>]+>", "", html)
    for k, v in enumerate(imgs):
        html = html.replace("@@IMG%d@@" % k, v)
    html = re.sub(r"\s+", " ", html)
    return html.strip()

def escape_math_pipes(text):
    def repl(m):
        inner = m.group(1)
        inner = re.sub(r"\|([^|]*)\|", r"\\lvert \1 \\rvert", inner)
        return "$" + inner + "$"
    return re.sub(r"\$([^$]+)\$", repl, text)

def to_markdown(rows):
    if not rows:
        return None
    ncol = max(len(r) for r in rows)
    norm = [r + [""] * (ncol - len(r)) for r in rows]
    esc = [[escape_math_pipes(c).replace("|", "\\|") for c in r] for r in norm]
    lines = ["| " + " | ".join(esc[0]) + " |"]
    lines.append("|" + "---|" * ncol)
    for r in esc[1:]:
        lines.append("| " + " | ".join(r) + " |")
    return "\n".join(lines)

def table_at(path, target):
    lines = open(path, encoding="utf-8").read().split("\n")
    i = 0
    while i < len(lines):
        if "<table" in lines[i]:
            s = i; buf = []
            while i < len(lines) and "</table>" not in lines[i]:
                buf.append(lines[i]); i += 1
            if i < len(lines): buf.append(lines[i])
            if s + 1 <= target <= i + 1:
                return s, "\n".join(buf)
        i += 1
    return None, None

jobs = [
    ("高数 曲面表", "11408/origin/27张宇基础30讲（高数）/27张宇基础30讲（高数）.md", 20590),
    ("数据结构 邻接表对比", "11408/origin/2027数据结构/2027数据结构.md", 12125),
]
for book, path, ln in jobs:
    s, block = table_at(path, ln)
    if not block:
        print(book, "未找到", ln); continue
    rows = []
    for r in re.findall(r"<tr[^>]*>(.*?)</tr>", block, re.S):
        cells = re.findall(r"<td[^>]*>(.*?)</td>", r, re.S)
        if cells:
            rows.append([clean_cell(c) for c in cells])
    md = to_markdown(rows)
    print("=" * 30, book, f"L{s+1}")
    print(md[:900])
    print("含图片单元格:", md.count("<img"))
    print()
