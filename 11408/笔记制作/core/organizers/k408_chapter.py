# -*- coding: utf-8 -*-
"""408 章级总览 Organizer：每章一个总览笔记（N-章名/N-章名.md）。

- 输入：拆分稿 408 章目录全部内容（导读 + 各考点）
- 输出：章级总览笔记（one_liner + 章内关键考点 + 易混 + 闪卡）
- 命名：章目录与总览同名 `N-章名/N-章名.md`（用户确认的命名规范）
- 与现有 408 考点笔记（小节级）互补：章级总览管"整章全景"，考点笔记管"每节深入"
"""
import glob, os, re
from .base import Organizer, ensure_stub, denoise, truncated
from ..config import BASE_SPLIT, BASE_NOTE, cfg
from ..task import Task, Job

COURSES = ["数据结构", "操作系统", "计算机组成原理", "计算机网络"]

P_408_CH_JSON = r"""你是考研 408 笔记整理助手。下面是《{course}》第{cno}章「{ctitle}」的完整教材原文（OCR 稿，含导读与各节考点，可能含图片引用和排版噪声）。
把这一整章整理成一份**章级总览笔记**。核心要求：**深度优先、结论忠于原文**——读者只看这份章级总览就能把握本章脉络、应付本章大部分题目；允许达到原文 1/3 长度；关键定义、定理、公式、典型算法框架必须保留（LaTeX 行内 $...$、独立 $$...$$，定界符务必配对）。

约束：
- 把本章内容整理成 5~10 个"章级考点"（如进程状态机、内存管理策略、路由协议分类），每个考点结论必须能在原文找到依据，禁止编造；conclusion 必须是完整句子。
- 每个考点必须自带 2~5 张闪卡：先识别本考点的核心结构（状态机/分类体系/对比/流程），用闪卡把结构枚举完整（节点、转换边、类别判据各一张）；问题自包含，答案 40 字内。
- confusions 覆盖章内易混概念（1~5 条，适合用 markdown 表格）。
- 不要输出"本章核心是…"式目录句；JSON 字符串值内不要换行；LaTeX 命令完整（\frac、\mid、\leq 等）。

严格只输出一个 JSON 对象（不要代码栅栏，不要其他文字）。JSON 结构：
{{
  "one_liner": "用一句话点透整章本质或核心矛盾",
  "points": [
    {{
      "name": "考点名",
      "conclusion": "核心结论一句话",
      "content": "关键公式(LaTeX)/算法框架/分类 1~3 行",
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


def vault_abs(abs_path):
    """绝对路径 → 相对 vault 根（无 .md 扩展），用于 wikilink。BASE_NOTE=vault/11408/笔记 → vault=笔记/../.."""
    vault_root = os.path.normpath(os.path.join(BASE_NOTE, "..", ".."))
    return os.path.relpath(abs_path, vault_root).replace("\\", "/")[:-3]


def chapter_title(ch_name):
    """N-章名 → 章名（显示用）；如 1-计算机系统概述 → 计算机系统概述"""
    m = re.match(r"(?:\d+-)?(.+)", ch_name)
    return m.group(1)


def chapter_no(ch_name):
    m = re.match(r"(\d+)-", ch_name)
    return int(m.group(1)) if m else 0


def chapter_src(ch_dir):
    """整章原文：导读 + 考点文件按名排序拼接（去习题区，习题不进章级总览）"""
    parts = []
    guide = glob.glob(os.path.join(ch_dir, "*-导读.md"))
    if guide:
        parts.append(open(guide[0], encoding="utf-8").read())
    for kf in sorted(glob.glob(os.path.join(ch_dir, "考点", "*.md"))):
        parts.append(open(kf, encoding="utf-8").read())
    return "\n\n".join(parts)


def _stub_body(ch_name, ctitle, course, cno, src_rel):
    return f"""---
type: 章
course: {course}
chapter_no: {cno}
chapter_title: "{ctitle}"
status: 未开始
mastery: 0
tags:
  - 408/{course}
  - 章级总览
source: "[[{src_rel}]]"
---

# {ctitle}

> [!abstract] 一句话总结
>

## 本章脉络

## 核心考点

## 易混与对比
-

## 闪卡
#card
-
"""


class K408ChapterOrganizer(Organizer):
    type = "k408_chapter"

    def scan(self, only=None):
        tasks = []
        for course in COURSES:
            if only and only != course:
                continue
            for ch_dir in sorted(glob.glob(os.path.join(BASE_SPLIT, course, "*/"))):
                ch_name = os.path.basename(os.path.normpath(ch_dir))
                if not re.match(r"\d+-", ch_name):
                    continue
                cno = chapter_no(ch_name)
                ctitle = chapter_title(ch_name)
                note_dir = os.path.join(BASE_NOTE, "408", course, ch_name)
                note = os.path.join(note_dir, ch_name + ".md")
                src_rel = vault_abs(ch_dir.rstrip("/\\") + "/" + ch_name + "-导读.md")
                if not os.path.exists(note):
                    ensure_stub(note, _stub_body(ch_name, ctitle, course, cno, src_rel))
                tasks.append(Task(
                    type=self.type, note_path=note, source_path=os.path.join(ch_dir, "考点"),
                    tag=f"{course}章{cno}",
                    title=ctitle,
                    meta={"course": course, "ch_dir": ch_dir, "ch_name": ch_name,
                          "cno": cno, "ctitle": ctitle, "raw_sub": course}))
        return tasks

    def jobs(self, task):
        src = denoise(chapter_src(task.meta["ch_dir"]))
        src = truncated(src, max_src=cfg().get("max_src", 160000))
        prompt = (P_408_CH_JSON
                  .replace("{course}", task.meta["course"])
                  .replace("{cno}", str(task.meta["cno"]))
                  .replace("{ctitle}", task.meta["ctitle"])
                  .replace("{src}", src))
        return [Job(prompt, stage="main")]