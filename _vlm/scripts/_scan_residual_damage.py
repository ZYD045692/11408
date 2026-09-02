# -*- coding: utf-8 -*-
"""全局残留腐蚀扫描：控制字符 / 行首碎片(ight|eq开头) / 字面\n \\ 不进字母的命令"""
import os, sys, glob, re, collections
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
BS = chr(92)
for f in sorted(glob.glob("11408/origin/*/*.md")):
    t = open(f, encoding="utf-8").read()
    lines = t.split("\n")
    issues = []
    cc = collections.Counter(ord(c) for c in t if ord(c) < 32 and c != "\n")
    if cc:
        issues.append(f"控制字符 {dict(cc)}")
    frag = [i + 1 for i, l in enumerate(lines) if re.match(r"^(ight|eq[$\s},.]|\bnx_|[a-z]x_)", l)]
    if frag:
        issues.append(f"行首碎片 {len(frag)} 行: {frag[:8]}")
    lit = [i + 1 for i, l in enumerate(lines) if BS + "n" in l and not re.search(r"\\n[a-z]", l)]
    if lit:
        issues.append(f"字面\\n {len(lit)} 行: {lit[:8]}")
    print(os.path.basename(f), "->", "; ".join(issues) if issues else "干净")
