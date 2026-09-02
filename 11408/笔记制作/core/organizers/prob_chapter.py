# -*- coding: utf-8 -*-
"""概统章级 Organizer：李良概统-基础 每章一个章级总览笔记。

- 输入：拆分稿/数学/概统-基础/第N章-章名.md（整章一个文件）
- 输出：笔记/数学/概统-基础/第N章-章名.md（章级总览，无小节拆分，用户确认）
- 概统-强化 不做（用户确认）
"""
import glob, os, re
from .base import Organizer, ensure_stub, denoise, truncated
from ..config import BASE_SPLIT, BASE_NOTE, cfg
from ..task import Task, Job

BOOK = "概统-基础"
SPLIT_DIR = os.path.join(BASE_SPLIT, "数学", BOOK)

P_PROB_CH_JSON = r"""你是考研数学笔记整理助手。下面是《概率论与数理统计》{book}分册「{chapter}」的完整原文（OCR 稿，可能含图片引用和排版噪声）。
把这一整章整理成一份**章级总览笔记**。核心要求：**深度优先、结论忠于原文**——读者只看这份章级总览就能把握本章脉络、应付本章大部分题目；关键定义、定理、公式必须保留（LaTeX 行内 $...$、独立 $$...$$，定界符务必配对）。

约束：
- 把本章整理成 5~10 个"章级考点"（概念定义/公式定理/题型方法分类），每个考点结论必须能在原文找到依据，禁止编造；conclusion 必须是完整句子。
- 每个考点必须自带 2~5 张闪卡：定义、公式、易错点、典型用法各出一张，问题自包含，答案 40 字内。闪卡用于复习（Obsidian 重复间隔），答案要可独立记忆。
- confusions 覆盖章内易混概念（如"互不相容 vs 对立""不相关 vs 独立"），1~5 条，适合用 markdown 表格。
- 不要输出"本章核心是…"式目录句；JSON 字符串值内不要换行；LaTeX 命令完整（\frac、\mid、\leq、\chi、\overline 等）。

严格只输出一个 JSON 对象（不要代码栅栏，不要其他文字）。JSON 结构：
{{
  "one_liner": "用一句话点透整章本质",
  "points": [
    {{
      "name": "考点名",
      "conclusion": "核心结论一句话",
      "content": "关键公式(LaTeX)/定义/方法 1~3 行",
      "exam_tip": "考试怎么用/易错提醒",
      "cards": [
        {{"q": "具体自包含的问题", "a": "40字内一句话/公式"}}
      ]
    }}
  ],
  "confusions": [
    {{"title": "易混点", "body": "对比说明(markdown表格)"}}
  ]
}}
要求：points 5~10 个，每个考点 2~5 张闪卡；confusions 1~5 条。

原文：
{src}"""


CN_NUM = {"一": 1, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9, "十": 10}

def _chapter_no(name):
    m = re.search(r"第([一二三四五六七八九十]+)章", name)
    if not m:
        return 0
    s = m.group(1)
    if s in CN_NUM:
        return CN_NUM[s]
    # 十/十几/二十几 处理
    if s.startswith("十"):
        return 10 + CN_NUM.get(s[1:], 0)
    if "十" in s:
        a, b = s.split("十")
        return CN_NUM.get(a, 1) * 10 + CN_NUM.get(b, 0)
    return 0


def _chapter_title(name):
    # 第N章-章名 → 章名（空格分隔）
    return re.sub(r"第[一二三四五六七八九十]+章-", "", name) if "-" in name else name


def _stub_body(name, title, no):
    return f"""---
type: 笔记
course: 数学
book: {BOOK}
chapter_no: {no}
topic: "{title}"
status: 未开始
mastery: 0
tags:
  - 考研数学/概率论
  - 笔记
source: "[[11408/拆分稿/数学/{BOOK}/{name}]]"
---

# {title}

> [!abstract] 一句话总结
>

## 本章脉络

## 核心考点

## 易混与对比
-

## 闪卡（Spaced Repetition）
#card
-

## 复习清单
- [ ] 通读原文 [[11408/拆分稿/数学/{BOOK}/{name}|{name}]]（拆分稿）

## 关联
- 原文：[[11408/拆分稿/数学/{BOOK}/{name}|{name}]]（拆分稿）
"""


class ProbChapterOrganizer(Organizer):
    type = "prob_chapter"

    def scan(self, only=None):
        tasks = []
        for f in sorted(glob.glob(os.path.join(SPLIT_DIR, "*.md"))):
            name = os.path.basename(f)[:-3]
            no = _chapter_no(name)
            title = _chapter_title(name)
            note_dir = os.path.join(BASE_NOTE, "数学", BOOK)
            note = os.path.join(note_dir, name + ".md")
            if not os.path.exists(note):
                os.makedirs(note_dir, exist_ok=True)
                ensure_stub(note, _stub_body(name, title, no))
            tasks.append(Task(
                type=self.type, note_path=note, source_path=f,
                tag=f"{BOOK}:{name}", title=title,
                meta={"book": BOOK, "name": name, "no": no, "title": title,
                      "raw_sub": "概率论"}))
        return tasks

    def jobs(self, task):
        src = denoise(open(task.source_path, encoding="utf-8").read())
        src = truncated(src, max_src=cfg().get("max_src", 160000))
        prompt = (P_PROB_CH_JSON
                  .replace("{book}", task.meta["book"])
                  .replace("{chapter}", task.meta["title"])
                  .replace("{src}", src))
        return [Job(prompt, stage="main")]