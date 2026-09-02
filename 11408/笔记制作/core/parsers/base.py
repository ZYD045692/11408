# -*- coding: utf-8 -*-
"""Parser 基类 + 公共工具：容错 JSON 提取、$ 配平、闪卡规范化、frontmatter 保留 + gen 写入。"""
import json, os, re
from ..config import cfg
from .normalize import (
    preprocess_json_escapes,
    protect_latex,
    normalize_newlines,
    normalize_table_cells,
    dollar_balanced,
    fix_math_backslash_decay,
    fix_dollar_misplace,
)


def extract_json(text):
    """容错提取首个 {...}（剥 ```json 外壳，截取 { ... } 区间，修 LaTeX 转义）"""
    text = text.strip()
    text = re.sub(r"^```(json)?|```$", "", text, flags=re.M).strip()
    text = preprocess_json_escapes(text)
    text = protect_latex(text)
    for i, ch in enumerate(text):
        if ch in "{[":
            for end in range(len(text), i, -1):
                try:
                    return json.loads(text[i:end])
                except Exception:
                    continue
            break
    return None


def math_balanced(text):
    """LaTeX 定界符 $ / $$ 配平校验"""
    return dollar_balanced(text)


def fmt_cards(cards, cap=None):
    """ [{q,a}] → ['- q::a'] 列表。按问题去重（剥 $ 与空白），封顶 cap 张。"""
    if cap is None:
        cap = cfg().get("max_cards", 10)
    out, seen = [], set()
    for c in cards or []:
        if isinstance(c, dict):
            q = normalize_newlines(c.get("q", ""))
            a = normalize_newlines(c.get("a", ""), allow_nl=False)
        else:
            m = re.match(r"-?\s*(.*?)::(.*)", str(c).strip())
            if not m:
                continue
            q, a = m.group(1).strip(), m.group(2).strip()
            q = normalize_newlines(q)
            a = normalize_newlines(a)
        if not q:
            continue
        k = re.sub(r"[\s$]", "", q)
        if k in seen:
            continue
        seen.add(k)
        out.append(f"- {q}::{a}")
        if cap and len(out) >= cap:
            break
    return out


def fmt_points(points):
    """points → markdown。输出 (text, n_counter)"""
    lines = []
    n = 0
    for p in points or []:
        name = re.sub(r"^考点\s*\d*[：:]\s*", "", str(p.get("name", "")).strip())
        conclusion = normalize_newlines(p.get("conclusion", ""))
        content = normalize_newlines(p.get("content", ""), allow_nl=True)
        tip = normalize_newlines(p.get("exam_tip", ""), allow_nl=True)
        n += 1
        lines.append(f"### 考点{n}：{name}")
        if conclusion:
            lines.append(f"**{conclusion}**")
        if content:
            lines.append(content)
        if tip:
            lines += ["", "> [!tip] 考试怎么用", f"> {tip.replace(chr(10), chr(10) + '> ')}"]
        lines.append("")
    return ("\n".join(lines)).strip(), n


def collect_cards(points):
    """从 points[].cards 聚合闪卡列表。"""
    cards = []
    for p in points or []:
        for c in p.get("cards") or []:
            if isinstance(c, dict) and c.get("q"):
                cards.append(c)
    return cards


def fmt_confusions(confusions):
    lines = []
    for c in confusions or []:
        t = str(c.get("title", "")).strip()
        b = str(c.get("body", "")).strip()
        if not t and not b:
            continue
        # 若 body 是表格，则标题独占一行，表格作为独立块（不能缩进）
        first_line = b.split("\n")[0].strip() if b else ""
        is_table = first_line.startswith("|") and "|" in first_line[1:]
        if is_table:
            b = normalize_table_cells(b)
            if t:
                lines.append(f"**{t}**")
                lines.append("")
            lines.extend(b.split("\n"))
            lines.append("")
        else:
            b = normalize_newlines(b, allow_nl=True)
            if t and b:
                body_lines = b.split("\n")
                first = body_lines[0]
                rest = [("  " + ln) if ln.strip() else "" for ln in body_lines[1:]]
                lines.append(f"- **{t}**：{first}")
                lines.extend(rest)
            elif b:
                lines.append(b)
            elif t:
                lines.append(f"- **{t}**")
    return "\n".join(lines).strip()


def extract_examples(src):
    return sorted(set(re.findall(r"例\s*(\d+\.\d+)", src)),
                  key=lambda s: [int(x) for x in s.split(".")])


def preserve_fm(old_text, gen_line):
    """保留原 frontmatter（服务 stub/人工修改的 status 等），剥旧 gen:，追加新 gen:。
    无 frontmatter 时建最小 frontmatter。返回不含结尾 --- 的 frontmatter 块。"""
    m = re.match(r"(?s)^(---\n.*?\n)---", old_text)
    if not m:
        return f"---\n{gen_line}\n"
    fm = m.group(1)
    fm = re.sub(r"(?m)^gen:.*\n", "", fm)
    return fm + f"gen: {gen_line}\n"


def already_gen(note_path):
    if not os.path.exists(note_path):
        return False
    return "gen:" in open(note_path, encoding="utf-8").read()[:600]


class Parser:
    """解析工具：模型 JSON → 校验 → 渲染笔记模板落盘。"""

    type = ""

    def parse(self, raw):
        return extract_json(raw)

    def validate(self, data):
        """结构校验：must have 必需键"""
        return isinstance(data, dict) and bool(data.get("points"))

    def raw_ok(self, raw):
        return math_balanced(raw)

    def render(self, task, stages, gen_line):
        """stages: [(stage, data|None), ...] 按执行序。返回完整笔记文本。"""
        raise NotImplementedError
