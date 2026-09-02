# -*- coding: utf-8 -*-
"""笔记 LaTeX 精确修正 v6 —— 只处理有 91 处错误的 20 篇，映射来自 validate 报错片段。

安全替换（逐文件按错误行指纹）：
- c1 全角命令 → LaTeX：∫→\\int, μ→\\mu, σ→\\sigma, ε→\\varepsilon, α→\\alpha, β→\\beta,
  Δ→\\Delta, ≥→\\geq, ≤→\\leq, ±→\\pm, ＞→>
- c2 残缺命令补全：\\rac→\\frac, \\rim→\\lim, \\nt→\\int, \\nd→\\mathbf d, \\nds→\\mathbf s? (18.4看原文),
  \\ncdot→\\cdot, \\ntwidehat→\\widehat, \\ntbegin→\\begin, \\ntend→\\end, \\nty→y,
  \\ntalpha→\\alpha, \\ntbeta→\\beta, \\ring→\\circ, \\bigpropto→\\propto
- c3 双反命令塌缩：\\\\(?=[a-zA-Z\\[]) → \\   (\\yes \\alpha → \\alpha)，但保持 bmatrix 行分隔 \\\\ 保留
- c4 特殊: \\text{∫}→\\int, 1^\\lim→1^\\infty, \\varepsilon 修正 \\epsilon

注意：18.4 的 \\nd \\nds 需查原文确认语义，先保守处理。
"""
import glob, io, os, re, sys, shutil

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
BS = chr(92)
B2 = BS + BS

# 全角命令 → LaTeX （安全）
FULLWIDTH = [
    ("∫", BS + "int"), ("μ", BS + "mu"), ("σ", BS + "sigma"),
    ("ε", BS + "varepsilon"), ("α", BS + "alpha"), ("β", BS + "beta"),
    ("Δ", BS + "Delta"), ("≥", BS + "geq"), ("≤", BS + "leq"), ("±", BS + "pm"),
    ("∞", BS + "infty"), ("×", BS + "times"), ("·", "·"),
]
# 残破命令
BROKEN = [
    (BS + "rac", BS + "frac"),
    (BS + "rim", BS + "lim"),
    (BS + "ring", BS + "circ"),
    (BS + "ntwidehat", BS + "widehat"),
    (BS + "ntbegin", BS + "begin"),
    (BS + "ntend", BS + "end"),
    (BS + "ntalpha", BS + "alpha"),
    (BS + "ntbeta", BS + "beta"),
    (BS + "ncdot", BS + "cdot"),
    (BS + "nty", "y"),
    (BS + "nt_", BS + "int_"),
    (BS + "bigpropto", BS + "propto"),
    (BS + "pmi", BS + "pm i"),
    (BS + "//lim", BS + "lim"),     # \//lim
    ("\\\//", B2),                   # \// → 双反  （2.7 里的 \//）
    (BS + "$\\", BS),                # $\ → $ (游离反)
]
# \text 内全角
TEXT_CMD = [
    (BS + r"text\{∫\}", BS + "int"),
    (BS + r"text\{≤\}", BS + "leq"),
    (BS + r"text\{≥\}", BS + "geq"),
    (BS + r"text\{...\}", BS + "cdots"),
]

def fix_line(ln):
    """对单行按安全规则修正（只改明确有错误的模式）"""
    for old, new in FULLWIDTH:
        ln = ln.replace(old, new)
    for old, new in BROKEN:
        ln = ln.replace(old, new)
    for pat, new in TEXT_CMD:
        ln = re.sub(pat, new, ln)
    # 双反+字母命令 → 单反（\\alpha → \alpha；不碰 \\ 行分隔）
    ln = re.sub(B2 + r"(?=[a-zA-Z])", BS, ln)
    return ln

def fix_note(path):
    """读取笔记，逐行过 fix_line，返回 (new_text, changed_lines)"""
    lines = open(path, encoding="utf-8").read().split("\n")
    out, changed = [], 0
    for i, ln in enumerate(lines, 1):
        nl = fix_line(ln)
        if nl != ln:
            out.append(nl)
            changed += 1
        else:
            out.append(ln)
    return "\n".join(out), changed

def main():
    TARGETS = []  # 20 篇错误笔记的绝对路径
    import subprocess
    for f in glob.glob(r"d:\obsidian'srepository\my\11408\笔记" + os.sep + "**" + os.sep + "*.md", recursive=True):
        t = open(f, encoding="utf-8").read()
        if "gen:" not in t[:600]:
            continue
        r = subprocess.run(["node", r"d:\obsidian'srepository\my\11408\处理流程\scripts\_validate_all.cjs", f],
                           capture_output=True, text=True, encoding="utf-8", errors="replace")
        if "parse error" in r.stdout or "metrics" in r.stdout:
            TARGETS.append(f)
    print("目标文件数:", len(TARGETS))
    for f in TARGETS:
        new, changed = fix_note(f)
        if changed:
            open(f, "w", encoding="utf-8", newline="\n").write(new)
            print("  ✓ %s (%d行改)" % (os.path.basename(f), changed))
        else:
            print("  · %s (无变化)" % os.path.basename(f))

if __name__ == "__main__":
    main()