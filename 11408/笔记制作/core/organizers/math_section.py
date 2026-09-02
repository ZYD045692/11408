# -*- coding: utf-8 -*-
"""数学小节 Organizer：从讲级拆分稿切小节（#### N 标题），每个小节一张 JSON 填充任务。

拆分规则（沿用旧 _math_sections.py）：拆分稿 ### 基础内容精讲 与 ### 基础习题精练 之间，
每个 #### N 标题视为一个小节；编号 x.y（讲号.节序）。
目标路径按讲分目录：笔记/数学/{高数,线代}/第N讲/x.y-标题.md（对齐 30讲-* 树按讲结构）。
"""
import glob, os, re
from .base import Organizer, ensure_stub, denoise, truncated
from ..config import BASE_SPLIT, BASE_NOTE, cfg
from ..task import Task, Job

BOOKS = [("30讲-高数", "高数")]   # 只有高数切小节；线代只出讲级笔记

P_SEC_JSON = r"""你是考研数学笔记整理助手。下面是《{book}》{lecture} 中"{sec} {title}"一节的教材原文（OCR 稿，可能含图片引用和排版噪声）。
把这一节整理成复习笔记。核心要求：**深度优先、结论忠于原文**——读者只看笔记就能应付本节大部分题目；允许达到原文一半长度；不照抄原文段落，但关键定义、定理、公式必须保留（LaTeX 行内 $...$、独立 $$...$$，定界符务必配对）。

约束：
- 每个考点的结论必须能在原文中找到依据，禁止编造定理、公式或解题步骤；conclusion 必须是完整句子，禁止残句或混入其他考点内容。
- 每个考点必须自带 2~5 张闪卡。数学考的是"对具体函数执行计算/判定"，闪卡按四类出：
  1. 工具卡：本节用到的公式/等价无穷小/泰勒展开/基本极限，要求精确背诵（如"$x\to0$ 时 $1-\cos x\sim$？"→"$\frac12x^2$"）；
  2. 触发卡：题型形态→方法（如"$1^\infty$ 型未定式怎么处理？"→"$e^{\lim v(u-1)}$"）；
  3. 判据卡：分类决策树的节点（如"间断点分类第一步看什么？"→"左右极限是否存在"）；
  4. 陷阱卡：定理/公式的失效条件（如"等价无穷小能否用于加减项？"→"不能，只适用乘除因子"）。
  问题自包含，不依赖具体例题编号；答案 40 字以内，一个公式、一句话或一组关键词。
- 不要输出"本节核心是…"式目录句。
- JSON 字符串值内不要换行（所有内容写在一行）；LaTeX 公式内部不要出现 \n，命令必须完整（如 \frac、\mid、\leq、\subseteq、\to）。

严格只输出一个 JSON 对象（不要代码栅栏，不要其他任何文字）。JSON 结构：
{{
  "one_liner": "用一句话点透本节知识点的本质（禁止'本节核心是…'式罗列）",
  "points": [
    {{
      "name": "考点名",
      "conclusion": "核心结论一句话",
      "content": "关键公式/定理(LaTeX)/解题步骤模板，如 $g(D)\subseteq D_1$、$|f(x)|\le M$",
      "exam_tip": "考试怎么用/易错提醒",
      "cards": [
        {{"q": "具体场景/条件下的问题", "a": "40字以内的一句话或公式"}}
      ]
    }}
  ],
  "confusions": [
    {{"title": "易混点", "body": "对比说明，适合的用 markdown 表格"}}
  ]
}}
要求：points 按原文标题子目逐个覆盖——每个子目至少 1 个考点；子目内含多个独立判定/特性/公式的（如"四种特性"），每个单独成点。一般 3~10 个，禁止为凑数拆分，更禁止为压数量合并掉整块内容。confusions 1~5 条。

原文：
{src}"""


def clean_title(t):
    t = re.sub(r"\$[^$]*\$", "", t)           # 去行内公式
    t = t.split("“")[0]                        # OCR 引号垃圾（公式残骸）一律截断
    t = re.sub(r"[（(]仅数学.*$", "", t)       # 去范围标注
    t = re.sub(r"[（(]数.*$", "", t)           # 去截断的残缺标注
    t = re.sub(r"[/\\:*?\"<>|#^\[\]]", "", t)  # 文件名非法字符
    t = re.sub(r"\s{2,}", " ", t)
    return t.strip(" 、。；;")[:30]

def split_lecture(path):
    """返回 (lec_no, [(sec_idx, title, body)])；body 为该节原文"""
    t = open(path, encoding="utf-8").read()
    lec = int(re.search(r"第(\d+)讲", os.path.basename(path)).group(1))
    m1 = re.search(r"(?m)^### 基础内容精讲", t)
    m2 = re.search(r"(?m)^### 基础习题精练", t)
    if not m1:
        return lec, []
    seg = t[m1.start(): m2.start() if m2 else len(t)]
    parts = re.split(r"(?m)^#### ([一二三四五六七八九十]+|\d+)[ 、\s](.+)$", seg)
    secs = []
    for i in range(1, len(parts) - 2, 3):
        title = clean_title(parts[i + 1])
        body = parts[i + 2].strip()
        if title and body:
            secs.append((len(secs) + 1, title, body))
    return lec, secs

STUB = """---
type: 小节
course: 数学
book: {book}
lecture: {lec}
section: "{sec}"
point_title: "{sec} {title}"
status: 未开始
mastery: 0
tags:
  - 考研数学/{sub}
  - 小节
source: "[[11408/拆分稿/数学/{book}/{lec_name}]]"
---

# {sec} {title}

> [!abstract] 一句话总结
>

## 核心要点
-

## 易混与对比
-

## 关联
- 所属讲：[[{lec_name}|{lec_name}]]
- 原文：[[11408/拆分稿/数学/{book}/{lec_name}|{lec_name}]]（拆分稿）

## 闪卡
#card
-
"""


class MathSectionOrganizer(Organizer):
    type = "math_section"

    def scan(self, only=None):
        tasks = []
        for book, sub in BOOKS:
            files = sorted(glob.glob(os.path.join(BASE_SPLIT, "数学", book, "*.md")),
                           key=lambda p: int(re.search(r"第(\d+)讲", p).group(1)))
            if only and only not in (book, sub) and not any(
                    only == os.path.basename(f)[:-3] for f in files):
                continue
            for f in files:
                name = os.path.basename(f)[:-3]
                if "第0讲" in name:
                    continue
                if only and only not in (book, sub, name):
                    continue
                lec, secs = split_lecture(f)
                for idx, title, body in secs:
                    sec = f"{lec}.{idx}"
                    note = os.path.join(BASE_NOTE, "数学", book, name, f"{sec}-{title}.md")
                    if not os.path.exists(note):
                        ensure_stub(note, STUB.format(book=book, lec=lec, sec=sec, title=title,
                                                      sub=sub, lec_name=name))
                    tasks.append(Task(type=self.type, note_path=note, source_path=f,
                                      tag=f"{sub}:{sec}", title=f"{sec} {title}",
                                      meta={"book": book, "sub": sub, "lec_name": name,
                                            "sec": sec, "body": body, "raw_sub": "小节"}))
        return tasks

    def jobs(self, task):
        src = denoise(task.meta["body"])
        src = truncated(src, max_src=cfg().get("max_src", 12000))
        title = task.title.split(" ", 1)[-1]
        prompt = (P_SEC_JSON
                  .replace("{book}", task.meta["book"])
                  .replace("{lecture}", task.meta["lec_name"])
                  .replace("{sec}", task.meta["sec"])
                  .replace("{title}", title)
                  .replace("{src}", src))
        return [Job(prompt, stage="main")]