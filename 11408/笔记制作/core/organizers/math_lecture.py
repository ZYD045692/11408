# -*- coding: utf-8 -*-
"""数学讲级 Organizer：整讲笔记。长讲分块提炼 → 合成；短讲一次生成。"""
import glob, os, re
from .base import Organizer, ensure_stub, denoise, chunk_source, truncated
from ..config import BASE_SPLIT, BASE_NOTE, cfg
from .math_section import split_lecture, BOOKS as SECTION_BOOKS
from ..task import Task, Job

BOOKS = [("30讲-高数", "高数"), ("30讲-线代", "线代")]
MAX_SYNTH_SRC = 9000     # 合成阶段要点汇总输入上限

P_MATH_ONE_JSON = r"""你是考研数学笔记整理助手。下面是《{book}》{lecture} 的原文（OCR 稿，可能含图片引用和排版噪声）。
把这一讲整理成复习笔记。核心要求：**深度优先、结论忠于原文**——读者只看笔记就能应付本讲大部分题目；允许达到原文一半长度；不照抄原文段落，但关键定义、定理、公式必须保留（LaTeX 行内 $...$、独立 $$...$$，定界符务必配对）。

约束：
- 每个考点的结论必须能在原文中找到依据，禁止编造定理、公式或解题步骤；conclusion 必须是完整句子，禁止残句或混入其他考点内容。
- 每个考点必须自带 2~5 张闪卡，按"工具卡/触发卡/判据卡/陷阱卡"四类出（详见 math_section 中的说明）；问题自包含，不依赖具体例题；答案 40 字以内。
- JSON 字符串值内不要换行（所有内容写在一行）；LaTeX 公式内部不要出现 \n，命令必须完整（如 \frac、\mid、\leq、\subseteq、\to）。

严格只输出一个 JSON 对象（不要代码栅栏，不要其他任何文字）。JSON 结构：
{{
  "one_liner": "用一句话点透本讲本质或核心思想（禁止'本讲核心是…'式罗列）",
  "points": [
    {{
      "name": "考点名",
      "conclusion": "核心结论一句话",
      "content": "关键公式/定理(LaTeX)/解题步骤模板，如 $g(D)\subseteq D_1$、$|f(x)|\le M$",
      "exam_tip": "考试怎么用/易错提醒",
      "cards": [
        {{"q": "问题(具体自包含)", "a": "答案(一个公式或一句话，简短唯一)"}}
      ]
    }}
  ],
  "confusions": [
    {{"title": "易混点", "body": "对比说明，适合的用 markdown 表格"}}
  ]
}}
要求：points 5~12 个考点，每个考点 2~5 张闪卡；confusions 1~5 条。

原文：
{src}"""

P_MATH_CHUNK_JSON = r"""你是考研数学笔记整理助手。下面是《{book}》{lecture} 的部分原文（第 {i}/{n} 块，OCR 稿）。
提炼这一块的核心考点与记忆卡片。要求**深度优先、结论忠于原文**：关键定义、定理、公式必须保留（LaTeX 行内 $...$、独立 $$...$$，定界符务必配对）；可把原文例题的通用解题步骤提炼成 1~3 行模板，但不要保留具体例题的数值或特定方程。JSON 字符串值内不要换行，LaTeX 公式内部不要出现 \n，命令必须完整（如 \frac、\mid、\leq、\subseteq、\to）。闪卡问题抽象通用（问定义、定理、公式、通用方法），不针对具体例题或数值，答案是可直接记忆的结论。

严格只输出一个 JSON 对象（不要代码栅栏，不要其他任何文字）。JSON 结构：
{{
  "points": [
    {{
      "name": "考点名",
      "conclusion": "核心结论一句话",
      "content": "关键公式(LaTeX)/解题步骤模板 1~3 行，如 $g(D)\subseteq D_1$",
      "exam_tip": "考试怎么用/易错提醒",
      "cards": [
        {{"q": "问题(具体自包含)", "a": "答案(一个公式或一句话，简短唯一)"}}
      ]
    }}
  ]
}}
要求：points 3~8 个考点，每个考点 2~5 张闪卡，覆盖定义、公式、易错点、典型用法等不同侧面，不要凑数。

原文块：
{src}"""

P_MATH_SYNTH_JSON = r"""下面是《{book}》{lecture} 各原文块提炼出的要点汇总（有重复、粒度太细）。
请合并压缩成本讲的最终笔记要点。要求**深度优先、结论忠于原文**：读者只看这份笔记就能应付本讲大部分题目；压缩的是重复和废话，不是信息量。

约束：
- 合并后的每个考点结论必须忠于原文，禁止编造；只提炼原文例题中的通用方法模板，不保留具体数值或特定方程。
- 每个考点必须自带 2~5 张闪卡，覆盖本考点的定义、判别法/公式、易错点、典型用法等不同侧面；问题抽象通用（问定义、定理、公式、通用方法），不针对具体例题或数值，答案是可直接记忆的结论。
- JSON 字符串值内不要换行（所有内容写在一行）；LaTeX 公式内部不要出现 \n，命令必须完整（如 \frac、\mid、\leq、\subseteq、\to）。

严格只输出一个 JSON 对象（不要代码栅栏，不要其他任何文字）。JSON 结构：
{{
  "one_liner": "用一句话点透本讲本质，追求'记住这一句就抓住本讲灵魂'的效果（禁止目录式罗列）",
  "points": [
    {{
      "name": "考点名",
      "conclusion": "核心结论一句话",
      "content": "关键公式/定理(LaTeX)/解题步骤模板，如 $g(D)\subseteq D_1$、$|f(x)|\le M$",
      "exam_tip": "考试怎么用/易错提醒",
      "cards": [
        {{"q": "问题(具体自包含)", "a": "答案(一个公式或一句话，简短唯一)"}}
      ]
    }}
  ],
  "confusions": [
    {{"title": "易混点", "body": "对比说明，适合的用 markdown 表格"}}
  ]
}}
要求：合并为 points 5~12 个考点，每个考点 2~5 张闪卡；confusions 1~5 条；重复内容只留一次。

要点汇总：
{CHUNKS}"""


def lecno(path):
    m = re.search(r"第(\d+)讲", os.path.basename(path))
    return int(m.group(1)) if m else 0

def iter_lecture_files(book):
    for f in sorted(glob.glob(os.path.join(BASE_SPLIT, "数学", book, "*.md")),
                    key=lecno):
        name = os.path.basename(f)[:-3]
        yield name, f

def _stub_body(name, book, sub, topic, has_sections=False):
    n = int(re.search(r"第(\d+)讲", name).group(1)) if re.search(r"第(\d+)讲", name) else 0
    return f"""---
type: 笔记
course: 数学
book: {book}
lecture: {n}
topic: "{topic}"
status: 未开始
mastery: 0
tags:
  - 考研数学/{sub}
  - 笔记
source: "[[11408/拆分稿/数学/{book}/{name}]]"
---

# {name.replace('-', ' ')}

> [!abstract] 一句话总结
>

## 核心考点

## 易错点

## 闪卡（Spaced Repetition）
#card
-

## 复习清单
- [ ] 通读原文 [[11408/拆分稿/数学/{book}/{name}|{name}]]（拆分稿）
- [ ] 1000题 对应章节

## 关联
- 原文：[[11408/拆分稿/数学/{book}/{name}|{name}]]（拆分稿）
"""


def lecture_note_path(book, sub, name, has_sections):
    """讲级笔记落盘路径：有小节的（高数）放讲目录内与小节同层；无小节的（线代）直接放书目录下。"""
    if has_sections:
        return os.path.join(BASE_NOTE, "数学", book, name, name + ".md")
    return os.path.join(BASE_NOTE, "数学", book, name + ".md")


class MathLectureOrganizer(Organizer):
    type = "math_lecture"

    def scan(self, only=None):
        tasks = []
        for book, sub in BOOKS:
            bfs = [(n, f) for n, f in iter_lecture_files(book) if "第0讲" not in n]
            if only and only not in (book, sub) and not any(n == only for n, _ in bfs):
                continue
            for name, f in bfs:
                has_sections = any(book == b for b, _ in SECTION_BOOKS) and bool(split_lecture(f)[1])
                note = lecture_note_path(book, sub, name, has_sections)
                if only and only != name and only not in (book, sub):
                    continue
                if not os.path.exists(note):
                    topic = name.split("-", 1)[1] if "-" in name else name
                    ensure_stub(note, _stub_body(name, book, sub, topic, has_sections))
                tasks.append(Task(type=self.type, note_path=note, source_path=f,
                                  tag=f"{book}:{name}", title=name.replace("-", " "),
                                  meta={"book": book, "sub": sub, "name": name,
                                        "raw_sub": book}))
        return tasks

    def synth_source(self, stage_results):
        """把已成功的各块要点拼成 synth 阶段的输入（截断防 prompt 过长）"""
        lines = []
        for st, data in stage_results:
            if st == "synth" or data is None:
                continue
            for p in data.get("points") or []:
                lines.append("### " + str(p.get("name", ""))[:60])
                lines.append(str(p.get("conclusion", "")))
                lines.append(str(p.get("content", "")))
        return ("\n".join(lines)).strip()[:MAX_SYNTH_SRC]

    def jobs(self, task):
        src = denoise(open(task.source_path, encoding="utf-8").read())
        lecture = task.title
        groups = chunk_source(src, cfg().get("max_src", 12000))
        book = task.meta["book"]
        if len(groups) == 1:
            prompt = (P_MATH_ONE_JSON
                      .replace("{book}", book).replace("{lecture}", lecture)
                      .replace("{src}", groups[0]))
            return [Job(prompt, stage="one")]
        out = []
        for i, g in enumerate(groups, 1):
            prompt = (P_MATH_CHUNK_JSON
                      .replace("{book}", book).replace("{lecture}", lecture)
                      .replace("{i}", str(i)).replace("{n}", str(len(groups)))
                      .replace("{src}", g))
            out.append(Job(prompt, stage=f"c{i}"))
        prompt = (P_MATH_SYNTH_JSON
                  .replace("{book}", book).replace("{lecture}", lecture))
        out.append(Job(prompt, stage="synth", is_synth=True))
        return out