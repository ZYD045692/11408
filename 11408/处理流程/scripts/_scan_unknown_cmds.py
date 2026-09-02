# -*- coding: utf-8 -*-
# 精准检查：1) 未知 LaTeX 命令（OCR 截断残留） 2) 每行 $ 成对性 3) 反斜杠+全角空格
import io, sys, os, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BOOKS = [
    "11408/origin/2027数据结构/2027数据结构.md",
    "11408/origin/2027操作系统/2027操作系统.md",
    "11408/origin/2027计算机组成原理/2027计算机组成原理.md",
    "11408/origin/2027计算机网络/2027计算机网络.md",
    "11408/origin/27张宇基础30讲（高数）/27张宇基础30讲（高数）.md",
    "11408/origin/27张宇基础30讲线代/27张宇基础30讲线代.md",
    "11408/origin/27张宇1000题数一【试题册】/27张宇1000题数一【试题册】.md",
    "11408/origin/27张宇1000题数一【解析册】/27张宇1000题数一【解析册】.md",
]

# 合法 LaTeX 命令白名单（数学书常用）
WHITELIST = set("""
begin end text frac sqrt int iint oint sum prod lim left right mathbf boldsymbol
displaystyle quad qquad times cdot leq geq partial mathrm overrightarrow underline
matrix cases pmatrix bmatrix dfrac tfrac limits choose atop longrightarrow rightarrow
Rightarrow Leftrightarrow sim approx neq equiv infty pi alpha beta gamma lambda sigma
mu theta Omega Phi Sigma Gamma Delta varepsilon varphi ldots cdots dots cdotp tan sin
cos log ln max min exp det to star circ bullet vert Vert mid wedge vee oplus otimes pm
mp ne ge le gg ll propto simeq cong subset supset subseteq supseteq notin cup cap
setminus bigcup bigcap emptyset varnothing forall exists nabla top bot angle perp
parallel lfloor rfloor lceil rceil lbrace rbrace langle rangle big Big Bigg bigg
overbrace underbrace odot ominus dx dy dz da db dc dd e mu nu xi rho eta omega zeta
varphi vartheta upsilon tau chi psi Phi Psi Omega Delta Theta Lambda Xi Pi Sigma
Upsilon Phi Psi Omega Gamma sqrt hline hspace vspace mbox hbox operatorname mod bmod
pmod arg coth tanh sinh cosh sech csc sec cot arcsin arccos arctan lg lg ln log
max min sup inf limsup liminf longleftarrow Leftarrow longleftrightarrow hookrightarrow
mapsto mid nmid triangle leftrightarrow vdash dashv models simeq leqslant geqslant
smallsetminus prec succ preceq succeq subset approx sim cong asymp dot ddot dddot
check hat vec bar acute grave breve widetilde widehat mathring tag not
""".split())

# 已知 OCR 损坏的命令（应修，不算未知但重点）
KNOWN_BROKEN = {"qua", "cd", "te", "p", "lef", "righ", "be", "en", "fr", "sqr", "li", "in", "cdo", "ac"}

for md in BOOKS:
    lines = open(md, encoding="utf-8").read().split("\n")
    unknown = {}   # cmd -> [(line, context)]
    odd_dollar = []
    bs_zenkaku = []
    for i, l in enumerate(lines, 1):
        # $ 成对性（含 $$ 块）
        n_doll = l.count("$")
        n_blocks = l.count("$$")
        if (n_doll - 2 * n_blocks) % 2 != 0:
            odd_dollar.append((i, l[:60]))
        # 未知命令
        for m in re.finditer(r"\\([a-zA-Z]+)", l):
            cmd = m.group(1)
            if cmd not in WHITELIST:
                unknown.setdefault(cmd, []).append((i, l[max(0, m.start()-18):m.end()+18]))
        # 反斜杠+全角空格
        for m in re.finditer(r"\\[　]", l):
            bs_zenkaku.append((i, l[max(0, m.start()-15):m.end()+15]))
    print(f"\n===== {os.path.basename(md.split('/')[-2])} =====")
    if odd_dollar:
        print(f"  [$成对性奇数] {len(odd_dollar)} 行")
        for ln, s in odd_dollar[:5]:
            print(f"    L{ln}: {s}")
    else:
        print("  [$成对] ✓ 全部偶数")
    if bs_zenkaku:
        print(f"  [\\+全角空格] {len(bs_zenkaku)} 处")
        for ln, s in bs_zenkaku[:5]:
            print(f"    L{ln}: ...{s}...")
    if unknown:
        # 按频次排序，只显示可疑的（非单词的截断）
        print(f"  [未知命令] {len(unknown)} 种")
        for cmd, lst in sorted(unknown.items(), key=lambda x: -len(x[1])):
            print(f"    \\{cmd} x{len(lst)}  L{lst[0][0]}: ...{lst[0][1]}...")
    else:
        print("  [未知命令] ✓ 无")
