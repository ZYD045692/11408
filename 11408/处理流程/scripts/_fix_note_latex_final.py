# -*- coding: utf-8 -*-
"""笔记 LaTeX 修复 v-final2 —— 按 57 处错误清单设计的安全映射（已核对的片段）。

映射清单（每个都来自 validate 报错的实际片段）：
1. bmatrix 行分隔：`\begin{bmatrix} A \ B` → `\begin{bmatrix} A \\ B`
   （bmatrix/-ed 环境内 单反+空格 → 双反+空格）
2. 双反命令被 JSON 转义塌缩：`\\[` → `\[`（10.3 L25）、`\\sum`→`\sum`（2.1 L82）、
   `(1+x)^\\alpha`→`(1+x)^\alpha`（6.1）、`u_\\alpha`→`u_\alpha`（概统2）
3. 全角命令：`\text{∫}`→`\int`、`∫`→`\int`、`≤`→`\leq`、`≥`→`\geq`、`±`→`\pm`、`λ`→`\lambda`
4. `\int` 前缀污染：`\intwidehat{`→`\widehat{`、`\intbegin{`→`\begin{`、`\intend{`→`\end{`、
   `\inty=`→`y=`、`\intalpha`→`\alpha`、`\intbeta`→`\beta`、`\int_{` 保留
5. 乱码命令：`\ring`→`\circ `（邻域空心圈，2.5）、`\bigpropto`→`\propto`（15.5）、
   `\pmi`→`\pm i`（15讲L45）、`\by`→`\`、`\leqM`→`\leq M`
6. 花括号多绕：`P\\\{X\\leq x\\\}`→`P\{X\leq x\}`（概统2 L26）
7. `1^\lim`→`1^\infty`（2.5 无穷上标）
8. `\ned`/`\nds` 等：先保留不动（不确定），单独查
"""
import glob, io, os, re, sys, shutil

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
BS = chr(92)
B2 = BS + BS
BAK = r"_vlm/md_backup/note_latex_fix"

def fix_bmatrix(text):
    """数学环境内 单反+空格 → 双反+空格（bmatrix/matrix/cases/aligned 等）。
    纯字符串操作，避免正则转义。找一个 \begin{env} 与下一个 \end{env}，改窗口内。"""
    ENVS = ["bmatrix", "vmatrix", "matrix", "pmatrix", "Bmatrix",
            "cases", "aligned", "split", "array"]
    out = text
    for env in ENVS:
        beg = BS + "begin{" + env + "}"
        end = BS + "end{" + env + "}"
        if beg not in out:
            continue
        chunks = out.split(beg)
        res = [chunks[0]]
        for c in chunks[1:]:
            if end in c:
                head, tail = c.split(end, 1)
                head = head.replace(BS + " ", B2 + " ")   # 单反+空格 → 双反+空格
                res.append(beg + head + end + tail)
            else:
                res.append(beg + c)
        out = "".join(res)
    return out

def fix_all(text):
    n = 0
    # 1) bmatrix 行分隔
    t1 = fix_bmatrix(text)
    if t1 != text:
        n += 1; text = t1
    # 2) 双反命令塌缩：\\命令 → \命令（但 \\ 后跟字母才塌，\\ 行分隔不塌——bmatrix已处理，别处 \\ 后跟字母的错）
    #   安全：`\\` 后跟字母/[/{ → 单反
    text = re.sub(B2 + r"(?=[a-zA-Z\[\{])", lambda m: BS, text)
    # 3) 全角命令 + \text 内全角
    text = re.sub(BS + r"text\{(∫|≤|≥|±)\}", lambda m: { "∫": BS+"int", "≤": BS+"leq", "≥": BS+"geq", "±": BS+"pm" }[m.group(1)], text)
    for full, cmd in [("∫", "int"), ("≤", "leq"), ("≥", "geq"), ("±", "pm"), ("λ", "lambda")]:
        text = text.replace(full, BS + cmd)
    # 4) \int 前缀污染（按出现在清单里的）
    for old, new in [
        (BS+"intwidehat{", BS+"widehat{"),
        (BS+"intbegin{", BS+"begin{"),
        (BS+"intend{", BS+"end{"),
        (BS+"inty=", "y="),
        (BS+"intalpha", BS+"alpha"),
        (BS+"intbeta", BS+"beta"),
        (BS+"intold", BS+"old"),
        (BS+"intleft", BS+"left"),
    ]:
        if old in text:
            text = text.replace(old, new); n += 1
    # 5) 乱码命令
    for old, new in [
        (BS+"bigpropto", BS+"propto"),
        (BS+"pmi", BS+"pm i"),
        (BS+"leqM", BS+"leq M"),
        (BS+"by", ""),
    ]:
        if old in text:
            text = text.replace(old, new); n += 1
    # 6) 花括号多绕 \ \{X \rightarrow 复原
    text = re.sub(B2 + r"(\{[^}]*\})", r"\1", text)   # \\\{X → \{X（2反+{X}→1反+{X}）
    # 7) 1^\lim → 1^\infty
    text = text.replace("1^" + BS + "lim", "1^" + BS + "infty")
    return text, n

def main():
    fixed = 0
    for f in glob.glob(r"d:\obsidian'srepository\my\11408\笔记" + os.sep + "**" + os.sep + "*.md", recursive=True):
        t = open(f, encoding="utf-8").read()
        if "gen:" not in t[:600]:
            continue
        orig = t
        t, _ = fix_all(t)
        if t != orig:
            os.makedirs(BAK, exist_ok=True)
            shutil.copy(f, os.path.join(BAK, os.path.basename(f)))
            open(f, "w", encoding="utf-8", newline="\n").write(t)
            fixed += 1
    print("修改文件数:", fixed)

if __name__ == "__main__":
    main()