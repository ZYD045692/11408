# -*- coding: utf-8 -*-
"""数学小节 Parser：JSON → 小节模板（一句话/核心要点/易混/关联/闪卡）。"""
import os
from .base import Parser, fmt_cards, fmt_points, fmt_confusions, preserve_fm, collect_cards


class MathSectionParser(Parser):
    type = "math_section"

    def render(self, task, stages, gen_line):
        data = stages[0][1]
        if data is None:
            data = {}
        points, n = fmt_points(data.get("points"))
        confusions = fmt_confusions(data.get("confusions"))
        cards = fmt_cards(collect_cards(data.get("points")))
        lec_name = task.meta["lec_name"]

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
        out.append("## 关联")
        out.append(f"- 所属讲：[[{lec_name}]]")
        out.append(f"- 原文：[[{lec_name}]]（拆分稿）")
        out.append("")
        out.append("## 闪卡")
        out.append("#card")
        out.extend(cards or ["- （待补）"])
        out.append("")
        return "\n".join(out), len(cards)