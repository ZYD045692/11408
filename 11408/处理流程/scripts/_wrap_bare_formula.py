# -*- coding: utf-8 -*-
# 把裸 LaTeX 公式包进 $...$：从裸命令位置向外扩展到公式边界（中文/中文标点处停）
import io, sys, os, re, glob
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BARE = re.compile(r"\\(?:begin|end|frac|sqrt|int|iint|oint|sum|prod|lim|left|right|text|mathbf|boldsymbol|displaystyle|quad|qquad|times|cdot|leq|geq|partial|mathrm|overrightarrow|underline|matrix|cases|pmatrix|bmatrix|dfrac|tfrac|limits|choose|atop|longrightarrow|rightarrow|Rightarrow|Leftrightarrow|sim|approx|neq|equiv|infty|pi|alpha|beta|gamma|lambda|sigma|mu|theta|Omega|Phi|Sigma|Gamma|Delta|varepsilon|varphi|ldots|cdots|dots|cdotp|tan|sin|cos|log|ln|max|min|exp|det|to)\b")

FORMULA_CHARS = set(" \t=+-*/<>()[]{}^_,.;:!?~'\"$0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ\\≤≥≠∞±×÷→←⇒⇔∈∉∑∏∫∂∇√·—")


def is_formula_char(ch):
    if ch in FORMULA_CHARS:
        return True
    if '\u4e00' <= ch <= '\u9fff':
        return False
    if ch in '，。；：？！、':
        return False
    if ch in '（）：；，。！？':
        return False
    return False


def in_math(line):
    ranges = []
    i, n = 0, len(line)
    while i < n:
        if line[i] == '$':
            if i + 1 < n and line[i + 1] == '$':
                j = line.find('$$', i + 2)
                if j != -1:
                    ranges.append((i, j + 2)); i = j + 2; continue
                i += 2; continue
            j = line.find('$', i + 1)
            if j != -1:
                ranges.append((i, j + 1)); i = j + 1; continue
        i += 1
    return ranges


def wrap_line(line):
    ranges = in_math(line)
    bare = [m for m in BARE.finditer(line) if not any(a <= m.start() < b for a, b in ranges)]
    if not bare:
        return line
    start = bare[0].start()
    while start > 0 and is_formula_char(line[start - 1]):
        start -= 1
    end = bare[-1].end()
    while end < len(line) and is_formula_char(line[end]):
        end += 1
    # 去掉边界多余空白
    while start < end and line[start] in ' \t':
        start += 1
    while end > start and line[end - 1] in ' \t':
        end -= 1
    if end <= start:
        return line
    seg = line[start:end]
    # 若已含 $ 或长度异常则跳过
    if '$' in seg:
        return line
    # 包裹
    return line[:start] + '$' + seg + '$' + line[end:]


def fix_book(book):
    md = glob.glob(f"11408/origin/{book}/*.md")[0]
    lines = open(md, encoding="utf-8").read().split("\n")
    n = 0
    for i, l in enumerate(lines):
        new = wrap_line(l)
        if new != l:
            lines[i] = new
            n += 1
    open(md, "w", encoding="utf-8").write("\n".join(lines))
    return n


if __name__ == "__main__":
    only = sys.argv[1] if len(sys.argv) > 1 else None
    books = ["2027数据结构", "2027操作系统", "2027计算机组成原理", "2027计算机网络",
             "27张宇基础30讲（高数）", "27张宇基础30讲线代",
             "27张宇1000题数一【试题册】", "27张宇1000题数一【解析册】"]
    for b in books:
        if only and only not in b:
            continue
        print(f"{b}: 修改 {fix_book(b)} 行")
