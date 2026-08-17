# -*- coding: utf-8 -*-
"""全量：含公式的 HTML 多列表格 → Markdown 管道表格。
跳过 colspan/rowspan 表格（Markdown 无法表达）。每表报告转换结果与列数校验。
"""
import io, sys, re, glob
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

DRY_RUN = False  # True=只报告不写入
total_conv = 0
total_skip = 0
for f in sorted(glob.glob("11408/origin/*/*.md")):
    lines = open(f, encoding="utf-8").read().split("\n")
    changed = 0
    skipped = 0
    i = 0
    while i < len(lines):
        if "<table" in lines[i]:
            s = i
            buf = []
            while i < len(lines) and "</table>" not in lines[i]:
                buf.append(lines[i]); i += 1
            if i < len(lines):
                buf.append(lines[i])
            e = i  # 含 </table> 的行
            block = "\n".join(buf)
            if "$" not in block:
                i += 1
                continue
            if re.search(r"colspan|rowspan", block, re.I):
                skipped += 1
                i += 1
                continue
            # 解析
            rows = []
            for r in re.findall(r"<tr[^>]*>(.*?)</tr>", block, re.S):
                cells = re.findall(r"<td[^>]*>(.*?)</td>", r, re.S)
                if cells:
                    rows.append([clean_cell(c) for c in cells])
            md = to_markdown(rows)
            if not md:
                i += 1
                continue
            # 校验列数一致
            cols = [len(x) for x in rows]
            if max(cols) != min(cols):
                skipped += 1
                i += 1
                continue
            lines[s:e + 1] = md.split("\n")
            changed += 1
        i += 1
    if changed or skipped:
        print(f"== {f.split('/')[-2]}: 转换{changed} 跳过{skipped}")
        if not DRY_RUN:
            open(f, "w", encoding="utf-8").write("\n".join(lines))
        total_conv += changed
        total_skip += skipped
print(f"总计：转换 {total_conv}，跳过(colspan/rowspan/列不一致) {total_skip}")
