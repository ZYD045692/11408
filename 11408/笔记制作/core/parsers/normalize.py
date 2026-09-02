# -*- coding: utf-8 -*-
"""Markdown / LaTeX 输出归一化公共库。

把处理流程（OCR 清洗）和笔记制作（LLM 生成）中反复出现的转义/换行/LaTeX 问题
集中处理，避免各脚本各自造轮子。

复用来源：
- _vlm/scripts/_fix_escape_damage.py（字面 \\n、数学环境内 \\ 衰减）
- 11408/处理流程/scripts/_verify_backslash_n.py（\\n 与 LaTeX 命令区分）
- 11408/处理流程/scripts/_fix_dollar_misplace.py（$ 错位）
- 11408/处理流程/scripts/_fix_table_backslash_n.py（表格内 \\n）
"""
import re

# 字面 \\n，但后面紧跟字母时视为 LaTeX 命令（\\neq、\\ni、\\nabla...）保留
LITERAL_N_RE = re.compile(r"(?<!\\)\\n(?![a-zA-Z])")

# 数学环境内：单反斜杠后跟数字 / - / =  / 空格，通常是衰减的行分隔 \\
DECAYED_BS_RE = re.compile(r"(?<!\\)\\(?=[0-9\-= ])")

# $ 错位：\\left{ 后紧跟 $，或 $ 在 \\right. 前
DOLLAR_MISPLACE_RE = re.compile(r"(?P<cmd>\\(?:left|right)(?:\{|\(|\[|\||\.|\)|\]|\}))(?P<dollar>\$)")
DOLLAR_MISPLACE_MAP = {
    r"\left{": r"$\left\{",
    r"\left(": r"$\left(",
    r"\left[": r"$\left[",
    r"\left|": r"$\left|",
    r"\right.": r"\right.$",
    r"\right)": r"\right)$",
    r"\right]": r"\right]$",
    r"\right}": r"\right}$",
    r"\right|": r"\right|$",
}

def fix_literal_newlines(text, replacement=" "):
    """把 OCR/LLM 残留的字面 \\n 替换成 replacement，但保留 \\neq、\\ni 等命令。"""
    return LITERAL_N_RE.sub(replacement, text)

def fix_dots_escape(text):
    """修复模型把 \\dots 错误写成 \\\\(\\dots 或 \\\\dots 的问题（反斜杠重复）。

    模型在 JSON 中有时写单反斜杠命令（\\alpha），有时写双反斜杠命令（\\\\alpha），
    两种情况都要处理，避免 \\\\(\\cdots\\\\) 这类残留破坏 LaTeX 渲染。
    """
    bs = chr(92)

    def _repl_dots(m):
        return bs + "dots"

    def _repl_cdots(m):
        return bs + "cdots"

    # 双反斜杠形式：\\(\\cdots\\)、\\(\\dots\\)、\\(\\cdots、\\(\\dots、\\\\dots
    text = re.sub(re.escape(bs + bs + "(") + re.escape(bs + bs) + "cdots" + re.escape(bs + bs + ")"), _repl_cdots, text)
    text = re.sub(re.escape(bs + bs + "(") + re.escape(bs + bs) + "dots" + re.escape(bs + bs + ")"), _repl_dots, text)
    text = re.sub(re.escape(bs + bs + "(") + re.escape(bs + bs) + "cdots", _repl_cdots, text)
    text = re.sub(re.escape(bs + bs + "(") + re.escape(bs + bs) + "dots", _repl_dots, text)
    text = re.sub(re.escape(bs + bs) + "dots", _repl_dots, text)
    # 单反斜杠形式（兜底）
    text = re.sub(re.escape(bs + "(") + re.escape(bs) + "cdots" + re.escape(bs + ")"), _repl_cdots, text)
    text = re.sub(re.escape(bs + "(") + re.escape(bs) + "dots" + re.escape(bs + ")"), _repl_dots, text)
    text = re.sub(re.escape(bs + "(") + re.escape(bs) + "cdots", _repl_cdots, text)
    text = re.sub(re.escape(bs + "(") + re.escape(bs) + "dots", _repl_dots, text)
    return text

def collapse_whitespace(text):
    """把连续空格/制表符压成一个空格，并去掉首尾空白。"""
    return re.sub(r"[ \t]+", " ", text).strip()

def normalize_newlines(text, allow_nl=False):
    """对外主入口：归一化字面 \\n + 压缩空白。

    allow_nl=True  -> 把字面 \\n 变成真实换行（适合需要换行的段落）
    allow_nl=False -> 把字面 \\n 变成空格（适合表格单元、结论单行）
    """
    repl = "\n" if allow_nl else " "
    return collapse_whitespace(fix_dots_escape(fix_literal_newlines(text, repl)))

def fix_math_backslash_decay(text):
    """修复数学环境内 \\\\ 衰减成 \\ 的问题（\\1、\\-、\\=、\\ 行分隔）。"""
    def _patch(seg):
        # 先回滚三连反斜杠：\\\1 -> \\\\1
        seg = re.sub(r"\\\\\\(?=[0-9\-= ])", r"\\\\", seg)
        # 再把单反斜杠+数字/-/= / 空格 补成双反斜杠
        seg = DECAYED_BS_RE.sub(r"\\\\", seg)
        return seg

    out, i, n = [], 0, len(text)
    while i < n:
        if text[i] == "$":
            end = text.find("$$" if text.startswith("$$", i) else "$", i + 1)
            if end == -1:
                out.append(text[i:])
                break
            if text.startswith("$$", i):
                seg = text[i:end + 2]
                i = end + 2
            else:
                seg = text[i:end + 1]
                i = end + 1
            out.append(_patch(seg))
        else:
            out.append(text[i])
            i += 1
    return "".join(out)

def fix_dollar_misplace(text):
    """修复 \\left{ 前漏 $、\\right. 后多 $ 等典型 $ 错位。"""
    out = []
    i = 0
    while i < len(text):
        m = DOLLAR_MISPLACE_RE.match(text, i)
        if m:
            cmd = m.group("cmd")
            repl = DOLLAR_MISPLACE_MAP.get(cmd)
            if repl:
                out.append(repl)
                i = m.end()
                continue
        out.append(text[i])
        i += 1
    return "".join(out)

def normalize_table_cells(text):
    """表格单元格内不允许有换行（会破坏表格结构），但保留行边界。
    逐行、逐单元格地把 \\n 和真实换行压成空格。"""
    rows = text.split("\n")
    out_rows = []
    for row in rows:
        if "|" not in row:
            out_rows.append(row)
            continue
        cells = row.split("|")
        # 首尾空字符串是表格边框产生的，保留；中间单元格做归一化
        norm_cells = []
        for idx, cell in enumerate(cells):
            if idx == 0 or idx == len(cells) - 1 or cell.strip():
                norm_cells.append(fix_literal_newlines(cell, " ").replace("\n", " ").strip())
            else:
                norm_cells.append(cell)
        out_rows.append("|".join(norm_cells))
    return "\n".join(out_rows)

def dollar_balanced(text):
    """检查 $ / $$ 是否配平。"""
    t = re.sub(r"\\\$", "", text)
    if t.count("$$") % 2:
        return False
    return t.replace("$$", "").count("$") % 2 == 0

def protect_latex(text):
    """JSON 解析前保护 LaTeX 反斜杠命令，避免 json.loads 把 \\b 当退格、\\u 当 unicode。
    只保护"单个反斜杠+字母"（本会非法）；已是合法 JSON 的 \\n \\t \\r \\b \\f、\\\\（双反斜杠行分隔）、
    \\\\uXXXX 不改动。
    """
    json_escapes = {r"\n", r"\t", r"\r", r"\b", r"\f"}
    unicode_escape = re.compile(r"\\u[0-9a-fA-F]{4}|\\U[0-9a-fA-F]{8}")

    def repl(m):
        s = m.group(0)
        if s in json_escapes or unicode_escape.fullmatch(s):
            return s
        return "\\" + s

    # 只保护：\ 后紧跟字母的 LaTeX 命令，但排除前面已有一个 \（即 \\cmd 不动）
    return re.sub(r"(?<!\\)(\\u[0-9a-fA-F]{4}|\\U[0-9a-fA-F]{8}|(?<!\\)\\[a-zA-Z]+)", repl, text)

def preprocess_json_escapes(text):
    """模型有时把 \\n 写成字面双反斜杠（\\\\n），先还原成 JSON 标准 \\n。"""
    text = re.sub(r"(?<!\\)\\\\n", r"\\n", text)
    text = re.sub(r"(?<!\\)\\\\t", r"\\t", text)
    text = re.sub(r"(?<!\\)\\\\r", r"\\r", text)
    return text
