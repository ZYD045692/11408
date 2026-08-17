# -*- coding: utf-8 -*-
"""扫表格内/正文中不在公式里的 LaTeX 命令残留 + 常见乱码签名"""
import io, sys, re, glob
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

# 常见 OCR 截断/乱码签名
SIG = [
    (r"\\cdo", "截断 \\cdot"),
    (r"\\fra", "截断 \\frac"),
    (r"\\sqr", "截断 \\sqrt"),
    (r"\\lef", "截断 \\left"),
    (r"\\righ", "截断 \\right"),
    (r"\\be[gq]", "截断 \\beg"),
    (r"\\en[d]", "截断 \\end"),
    (r"\\al[ph]", "截断 \\alpha"),
    (r"\\be[ta]", "截断 \\beta"),
    (r"\\al[ig]", "截断 \\align"),
    (r"[貼錶謌]", "生僻乱码字"),
    (r"·/td>", "标签乱码"),
]
LATEX_CMD = re.compile(r"\\(?:[a-zA-Z]{2,})\s")

for f in sorted(glob.glob("11408/origin/*/*.md")):
    name = f.split("/")[-2]
    hits = []
    for i, l in enumerate(open(f, encoding="utf-8"), 1):
        # 去掉公式区域后，剩余的 \ 命令（即在表格/正文里的裸 LaTeX）
        t = re.sub(r"\$[^$]*\$", "", l)
        for pat, label in SIG:
            if re.search(pat, t):
                hits.append((i, label, l.strip()[:70]))
                break
        else:
            # 表格行中裸 \ 命令（如 <td>\alpha</td> 缺 $）
            if ("<td" in l or "<tr" in l) and LATEX_CMD.search(t):
                hits.append((i, "表格裸命令", l.strip()[:70]))
    if hits:
        print(f"== {name}: {len(hits)} 处")
        for i, label, t in hits[:15]:
            print(f"  L{i} [{label}]: {t}")
