# -*- coding: utf-8 -*-
"""HTML表格→Markdown 转换器（试运行：打印预览，不写文件）"""
import io, sys, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

def clean_cell(html):
    # 去 td 外层，转换内联标签
    html = html.strip()
    html = re.sub(r"<br\s*/?>", " ", html, flags=re.I)
    html = re.sub(r"</?p[^>]*>", " ", html, flags=re.I)
    html = re.sub(r"<b[^>]*>(.*?)</b>", r"**\1**", html, flags=re.S | re.I)
    html = re.sub(r"<strong[^>]*>(.*?)</strong>", r"**\1**", html, flags=re.S | re.I)
    html = re.sub(r"<i[^>]*>(.*?)</i>", r"*\1*", html, flags=re.S | re.I)
    html = re.sub(r"<sup[^>]*>(.*?)</sup>", r"^\1", html, flags=re.S | re.I)
    html = re.sub(r"<sub[^>]*>(.*?)</sub>", r"_\1", html, flags=re.S | re.I)
    html = re.sub(r"<[^>]+>", "", html)  # 其余标签剥掉
    html = re.sub(r"[ \t]+", " ", html)
    return html.strip()

def escape_pipes_in_math(text):
    # 在 $...$ 内把 |X| 换成 \lvert X \rvert
    def repl_inline(m):
        inner = m.group(1)
        inner = re.sub(r"\|([^|]*)\|", r"\\lvert\1\\rvert", inner)
        return "$" + inner + "$"
    # 处理行内 $...$（不含 $$）
    out = re.sub(r"\$([^$]+)\$", repl_inline, text)
    return out

def extract_table(block):
    rows = []
    for r in re.findall(r"<tr[^>]*>(.*?)</tr>", block, re.S):
        cells = re.findall(r"<td[^>]*>(.*?)</td>", r, re.S)
        if cells:
            rows.append([clean_cell(c) for c in cells])
    return rows

def to_markdown(rows):
    if not rows:
        return None
    ncol = max(len(r) for r in rows)
    # 补齐每行列数
    norm = [r + [""] * (ncol - len(r)) for r in rows]
    # 转义单元格里的 |（数学中的管道已处理，正文中的裸 | 也转义）
    esc = []
    for r in norm:
        esc.append([c.replace("|", "\\|") for c in r])
    lines = []
    header = esc[0]
    lines.append("| " + " | ".join(header) + " |")
    lines.append("|" + "---|" * ncol)
    for r in esc[1:]:
        lines.append("| " + " | ".join(r) + " |")
    return "\n".join(lines)

# 测试用例
samples = [
    ("高数 L10525", "11408/origin/27张宇基础30讲（高数）/27张宇基础30讲（高数）.md", 10525),
    ("数据结构 L5430", "11408/origin/2027数据结构/2027数据结构.md", 5430),
    ("计组 L4080", "11408/origin/2027计算机组成原理/2027计算机组成原理.md", 4080),
]
for name, path, ln in samples:
    lines = open(path, encoding="utf-8").read().split("\n")
    # 找包含该行的表格块
    block = None
    for i in range(len(lines)):
        if i + 1 == ln:
            # 向上找 <table
            s = i
            while s >= 0 and "<table" not in lines[s]:
                s -= 1
            e = i
            while e < len(lines) and "</table>" not in lines[e]:
                e += 1
            block = "\n".join(lines[s:e + 1])
            break
    if block:
        rows = extract_table(block)
        md = to_markdown(rows)
        print("=" * 20, name, f"({len(rows)}行)")
        print(md)
        print()
    else:
        print("未找到", name)
