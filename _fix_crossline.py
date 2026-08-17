# -*- coding: utf-8 -*-
# 修复跨行矩阵：$\begin{env}$ ... $\end{env}$（跨行）→ $$\begin{env} ... \end{env}$$
import io, sys, os, re, glob
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

ENVS = ["matrix", "vmatrix", "bmatrix", "pmatrix", "cases", "array"]


def fix_book(book):
    md = glob.glob(f"11408/origin/{book}/*.md")[0]
    text = open(md, encoding="utf-8").read()
    lines = text.split("\n")

    # 找所有 begin/end env 的位置（行号、类型、匹配的 $ 包裹）
    markers = []  # (line_idx, kind, env)
    for i, l in enumerate(lines):
        for m in re.finditer(r"\\(begin|end)\{(matrix|vmatrix|bmatrix|pmatrix|cases|array)\}", l):
            markers.append((i, m.group(1), m.group(2), m.start()))

    # 栈配对
    stack = []
    pairs = []
    for mk in markers:
        i, kind, env, pos = mk
        if kind == "begin":
            stack.append((i, env))
        else:
            if stack and stack[-1][1] == env:
                bi, benv = stack.pop()
                if bi != i:  # 跨行
                    pairs.append((bi, i, env))
            else:
                stack = [(bi, env) for bi, env in stack if not (env == env and False)]
                # 不匹配，清栈继续

    n = 0
    for bi, ei, env in pairs:
        bl = lines[bi]
        el = lines[ei]
        # begin 行：$\begin{env}$ → $$\begin{env}
        nb = re.sub(r"\$\\begin\{" + env + r"\}\$", r"$$\\begin{" + env + "}", bl, count=1)
        if nb == bl:  # 可能形态：$\begin{env}（开$在行首）
            nb = re.sub(r"^(\s*)\$\\begin\{" + env + r"\}", r"\1$$\\begin{" + env + "}", bl)
        # end 行：$\end{env}$ → \end{env}$$
        ne = re.sub(r"\$\\end\{" + env + r"\}\$", r"\\end{" + env + "}$$", el, count=1)
        if ne == el:
            ne = re.sub(r"\\end\{" + env + r"\}(\s*)\$$", r"\\end{" + env + "}$$", el)
        if nb != bl:
            lines[bi] = nb
            n += 1
        if ne != el:
            lines[ei] = ne
            n += 1

    open(md, "w", encoding="utf-8").write("\n".join(lines))
    return n, len(pairs)


if __name__ == "__main__":
    only = sys.argv[1] if len(sys.argv) > 1 else None
    books = ["2027数据结构", "2027操作系统", "2027计算机组成原理", "2027计算机网络",
             "27张宇基础30讲（高数）", "27张宇基础30讲线代",
             "27张宇1000题数一【试题册】", "27张宇1000题数一【解析册】"]
    for b in books:
        if only and only not in b:
            continue
        n, p = fix_book(b)
        print(f"{b}: 跨行矩阵 {p} 对, 修改 {n} 行")
