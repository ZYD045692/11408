# -*- coding: utf-8 -*-
"""408 考点 Organizer：扫拆分稿考点 → 出 JSON 填充任务，并聚合机械信息（真题年份/前后节/习题链接）。"""
import glob, os, re
from .base import Organizer, ensure_stub, denoise, read_fm, truncated
from ..config import BASE_SPLIT, BASE_NOTE, ROOT, cfg
from ..task import Task, Job

COURSES = ["数据结构", "操作系统", "计算机组成原理", "计算机网络"]


def vault_rel(path):
    """把绝对路径转成相对 vault 根的 wikilink 路径（不带 .md 扩展名）。"""
    return os.path.relpath(path, ROOT).replace("\\", "/")[:-3]


P_408_JSON = """你是考研 408 笔记整理助手。下面是《{course}》"{title}"一节的教材原文（OCR 稿，可能含图片引用和排版噪声）。
把这一节整理成复习笔记。核心要求：**深度优先、结论忠于原文**——读者只看笔记就能应付本节大部分题目；允许达到原文一半长度；不照抄原文段落，但关键定义、公式、代码、步骤必须保留（LaTeX 行内 $...$、独立 $$...$$，定界符务必配对）。

约束：
- 每个考点的结论必须能在原文中找到依据，禁止编造定义、公式、代码或解题步骤；conclusion 必须是完整句子，禁止残句或混入其他考点内容。
- 典型代表、实例、优缺点等也必须出自原文，原文没写的不要凭常识补充。
- 每个考点必须自带 2~5 张闪卡。做法：先识别本考点的核心结构（状态机/操作流程/分类体系/对比表），再用闪卡把这个结构枚举完整——每个节点、每条转换边及其触发条件、每个类别及其判据各占一张，不存在的转换（真题常挖的坑）也可以出。
  示例（围绕进程状态机）："进程三态是哪三个？"；"运行态→阻塞态的触发？"；"能否阻塞态→运行态？为什么？"。
  问题自包含，不依赖原文特定比喻或例题；答案 40 字以内，一句话或一组关键词。
- 不要输出"本节核心是…"式目录句。
- JSON 字符串值内不要换行（所有内容写在一行，多行代码用 \\n 表示并放在 ```c 栅栏内）；LaTeX 公式内部不要出现 \\n，命令必须完整（如 \\frac、\\mid、\\leq、\\subseteq、\\to）。

严格只输出一个 JSON 对象（不要代码栅栏，不要其他任何文字）。JSON 结构：
{{
  "one_liner": "一句话点透本节本质或核心矛盾（禁止'本节核心是…'式罗列）",
  "points": [
    {{
      "name": "考点名",
      "conclusion": "核心结论一句话",
      "content": "关键公式(LaTeX)/代码/解题步骤模板 1~3 行",
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
要求：points 按原文标题子目逐个覆盖，一般 3~8 个考点，每个考点 2~5 张闪卡；confusions 1~5 条。

原文：
{src}"""


# ---------- 机械信息（移植自旧 _fill_notes.py） ----------
def zhenti_years(ch_dir, sec):
    """机械提取统考真题年份：习题文件的【20XX 统考真题】 + 考点正文里的 考点追踪（20XX）"""
    years = set()
    ex = glob.glob(os.path.join(ch_dir, "习题", f"{sec}-*.md"))
    if ex:
        t = open(ex[0], encoding="utf-8").read()
        years.update(re.findall(r"【(20\d\d)\s*统考真题】", t))
    kp = glob.glob(os.path.join(ch_dir, "考点", f"{sec}-*.md"))
    if kp:
        t = open(kp[0], encoding="utf-8").read()
        for m in re.findall(r"考点追踪[^\n（）]*（([^）]*)）", t):
            years.update(re.findall(r"20\d\d", m))
    return "、".join(sorted(years, reverse=True))

def section_siblings(ch_dir, sec):
    """同章 考点 目录下按节号排序的前驱/后继"""
    files = sorted(glob.glob(os.path.join(ch_dir, "考点", "*.md")))
    names = [os.path.basename(f)[:-3] for f in files]
    def key(nm):
        m = re.match(r"([\d.]+)-", nm)
        return [int(x) for x in m.group(1).split(".")] if m else [99]
    names.sort(key=key)
    prev_l = next_l = ""
    if sec in [n.split("-")[0] for n in names]:
        idx = [n.split("-")[0] for n in names].index(sec)
        if idx > 0:
            prev_l = names[idx - 1]
        if idx < len(names) - 1:
            next_l = names[idx + 1]
    return prev_l, next_l


def _stub_body(title, exlink, course, cno, ctitle, sec, rel_split):
    return f"""---
type: 考点
course: {course}
chapter_no: {cno}
chapter_title: {ctitle}
section: "{sec}"
point_title: "{title}"
status: 未开始
mastery: 0
tags:
  - 408/{course}
  - 考点
source: "[[{rel_split}]]"
---

# {title}

> [!abstract] 一句话总结
>

## 核心要点
-

## 易混与对比
-

## 真题与错题
- 习题原文：{exlink}

## 关联考点
- 前置：
- 后续/易混：

## 闪卡
#card
-
"""


class K408Organizer(Organizer):
    type = "408"

    def scan(self, only=None):
        tasks = []
        for course in COURSES:
            if only and only != course:
                continue
            for ch_dir in sorted(glob.glob(os.path.join(BASE_SPLIT, course, "*/"))):
                ch_name = os.path.basename(os.path.normpath(ch_dir))     # NN-章名（兼容反斜杠）
                m = re.match(r"(\d+)-(.+)", ch_name)
                cno, ctitle = (int(m.group(1)), m.group(2)) if m else (0, ch_name)
                for kf in sorted(glob.glob(os.path.join(ch_dir, "考点", "*.md"))):
                    base = os.path.basename(kf)[:-3]                     # x.y-节名
                    bm = re.match(r"([\d.]+)-(.+)", base)
                    sec = bm.group(1) if bm else ""
                    title = f"{sec} {bm.group(2)}" if bm else base
                    note = os.path.join(BASE_NOTE, "408", course, ch_name, base + ".md")
                    ex = glob.glob(os.path.join(ch_dir, "习题", f"{sec}-*.md"))
                    exlink = f"[[{vault_rel(ex[0])}|{sec} 本节习题与解析]]" if ex else ""
                    if not os.path.exists(note):
                        ensure_stub(note, _stub_body(title, exlink or "（无）", course, cno, ctitle, sec,
                                                     vault_rel(kf)))
                    tasks.append(Task(
                        type=self.type, note_path=note, source_path=kf,
                        tag=f"{course}:{sec}", title=title,
                        meta={
                            "course": course, "ch_dir": ch_dir, "sec": sec,
                            "exlink": exlink if ex else "",
                            "years": zhenti_years(ch_dir, sec),
                            "prev": section_siblings(ch_dir, sec)[0],
                            "next": section_siblings(ch_dir, sec)[1],
                            "raw_sub": course,
                        }))
        return tasks

    def jobs(self, task):
        src = denoise(open(task.source_path, encoding="utf-8").read())
        src = truncated(src, max_src=cfg().get("max_src", 12000))
        prompt = (P_408_JSON
                  .replace("{course}", task.meta["course"])
                  .replace("{title}", task.title)
                  .replace("{src}", src))
        return [Job(prompt, stage="main")]
