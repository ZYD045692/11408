# -*- coding: utf-8 -*-
"""408 考点 Parser：JSON → 408 笔记模板（一句话/核心要点/易混/真题/关联/闪卡）。"""
import os, re
from .base import Parser, fmt_cards, fmt_points, fmt_confusions, preserve_fm, collect_cards


class K408Parser(Parser):
    type = "408"

    def render(self, task, stages, gen_line):
        data = stages[0][1]
        if data is None:
            data = {}
        points, n = fmt_points(data.get("points"))
        confusions = fmt_confusions(data.get("confusions"))
        cards = fmt_cards(collect_cards(data.get("points")))
        meta = task.meta

        old = open(task.note_path, encoding="utf-8").read()
        fm = preserve_fm(old, gen_line)

        out = [fm + "---", "", f"# {task.title}", "",
               "> [!abstract] 一句话总结",
               "> " + (data.get("one_liner") or "（待补）").replace("\\n", "\n").replace("\n", "\n> "), ""]
        out.append("## 核心要点")
        out.append(points or "- （待补）")
        out.append("")
        out.append("## 易混与对比")
        out.append(confusions or "- （待补）")
        out.append("")
        out.append("## 真题与错题")
        out.append(f"- 习题原文：{meta['exlink'] or '（无）'}")
        if meta.get("years"):
            out.append(f"- 本节统考真题年份：{meta['years']}")
        out.append("")
        out.append("## 关联考点")
        out.append(f"- 前置：[[{meta['prev']}]]" if meta.get("prev") else "- 前置：（本章首节）")
        out.append(f"- 后续：[[{meta['next']}]]" if meta.get("next") else "- 后续：（本章末节）")
        out.append("")
        out.append("## 闪卡")
        out.append("#card")
        out.extend(cards or ["- （待补）"])
        out.append("")
        return "\n".join(out), len(cards)