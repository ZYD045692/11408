# -*- coding: utf-8 -*-
"""概统章级 Parser：JSON → 章级总览模板（一句话/脉络/核心考点/易混/闪卡）。"""
import os, re
from .base import Parser, fmt_cards, fmt_points, fmt_confusions, preserve_fm, collect_cards


class ProbChapterParser(Parser):
    type = "prob_chapter"

    def render(self, task, stages, gen_line):
        data = stages[0][1] if stages else None
        data = data or {}
        points, n = fmt_points(data.get("points"))
        confusions = fmt_confusions(data.get("confusions"))
        cards = fmt_cards(collect_cards(data.get("points")))
        meta = task.meta

        old = open(task.note_path, encoding="utf-8").read()
        fm = preserve_fm(old, gen_line)

        out = [fm + "---", "", f"# {task.title}", "",
               "> [!abstract] 一句话总结",
               "> " + (data.get("one_liner") or "（待补）").replace("\\n", "\n").replace("\n", "\n> "), ""]
        out.append("## 本章脉络")
        out.append((data.get("outline") or "（待补）"))
        out.append("")
        out.append("## 核心考点")
        out.append(points or "- （待补）")
        out.append("")
        out.append("## 易混与对比")
        out.append(confusions or "- （待补）")
        out.append("")
        out.append("## 闪卡（Spaced Repetition）")
        out.append("#card")
        out.extend(cards or ["- （待补）"])
        out.append("")
        return "\n".join(out), len(cards)