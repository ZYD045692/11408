# -*- coding: utf-8 -*-
"""配对法清理公式边界空格：$ x $ → $x$，$$ x $$ → $$x$$。

只删「开 $ 后紧跟的空格」和「闭 $ 前紧跟的空格」，不碰公式内部空格
（如 `x $y$ z` 中 `$` 前的空格是文本分隔，保留）。反斜杠转义符号原样。
支持 $...$ 与 $$...$$ 两种边界。逐行处理（不跨行）。
"""
import glob, io, os, sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
BS = chr(92)

def clean_line(ln):
    out = []
    i, n = 0, len(ln)
    while i < n:
        if ln[i] == "$":
            # 判断是否 \$
            if i > 0 and ln[i-1] == BS:
                out.append("$"); i += 1; continue
            is_dd = i + 1 < n and ln[i+1] == "$"
            delim = 2 if is_dd else 1
            # 找配对闭合 $
            j = ln.find("$", i + delim)
            if j == -1:
                out.append(ln[i:]); break
            # 边界空格：开 $ 后紧跟空格 → 删（保留 $ 本身）
            out.append(ln[i:i+delim])
            k = i + delim
            while k < n and ln[k] == " ":
                k += 1
            if k >= n:
                # 后续全空格：异常，原样
                out.append(ln[i+delim:j]); break
            out.append(ln[k:j].rstrip(" "))
            out.append("$" * delim)
            i = j + delim
        else:
            out.append(ln[i]); i += 1
    return "".join(out)

def main():
    total = 0
    for book in ["27李良概统基础", "27李良概统强化"]:
        for md in sorted(glob.glob(os.path.join(r"d:\obsidian'srepository\my\11408\origin", book, "*.md"))):
            lines = open(md, encoding="utf-8").read().split("\n")
            changed = 0
            for i, ln in enumerate(lines):
                cl = clean_line(ln)
                if cl != ln:
                    lines[i] = cl
                    changed += 1
            if changed:
                open(md, "w", encoding="utf-8", newline="\n").write("\n".join(lines))
                print("✓ %-24s 清理 %d 行" % (os.path.basename(md)[:24], changed))
                total += changed
    print("共清理行数:", total)

if __name__ == "__main__":
    main()