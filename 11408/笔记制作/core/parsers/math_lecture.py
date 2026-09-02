# -*- coding: utf-8 -*-
"""数学讲级 Parser：单段或多段（chunk→synth）JSON → 讲级模板（一句话/核心考点/易错/闪卡/复习清单）。"""
import re
from .base import Parser, fmt_cards, fmt_points, fmt_confusions, preserve_fm, extract_examples, collect_cards


class MathLectureParser(Parser):
    type = "math_lecture"

    def _collect(self, stages):
        """stages → (one_liner, points_md, point_count, confusions_md, cards)"""
        synth = next((d for st, d in stages if st == "synth" and d), None)
        chunks = [d for st, d in stages if st != "synth" and d]

        if synth and synth.get("points"):
            points, n = fmt_points(synth.get("points"))
            return (synth.get("one_liner", ""), points, n,
                    fmt_confusions(synth.get("confusions")),
                    fmt_cards(collect_cards(synth.get("points"))))
        if len(stages) == 1 and stages[0][1] is not None:
            d = stages[0][1]
            points, n = fmt_points(d.get("points"))
            return (d.get("one_liner", ""), points, n,
                    fmt_confusions(d.get("confusions")),
                    fmt_cards(collect_cards(d.get("points"))))
        # synth 失败 → 退回拼接各块要点
        flat = []
        for d in chunks:
            for p in d.get("points") or []:
                flat.append({"name": p.get("name", ""), "conclusion": p.get("conclusion", ""),
                             "content": p.get("content", ""), "exam_tip": p.get("exam_tip", "")})
        points, n = fmt_points(flat)
        return ("", points, n, "",
                fmt_cards([c for d in chunks for c in collect_cards(d.get("points"))]))

    def render(self, task, stages, gen_line):
        one, points, n, confusions, cards = self._collect(stages)
        meta = task.meta
        name = meta["name"]

        old = open(task.note_path, encoding="utf-8").read()
        fm = preserve_fm(old, gen_line)

        src = open(task.source_path, encoding="utf-8").read()
        exs = extract_examples(src)

        out = [fm + "---", "", f"# {task.title}", "",
               "> [!abstract] 一句话总结",
               "> " + (one or "（待补）").replace("\\n", "\n").replace("\n", "\n> "), ""]
        out.append("## 核心考点")
        out.append(points or "- （待补）")
        out.append("")
        out.append("## 易错点")
        out.append(confusions or "- （待补）")
        out.append("")
        out.append("## 闪卡（Spaced Repetition）")
        out.append("#card")
        out.extend(cards or ["- （待补）"])
        out.append("")
        out.append("## 复习清单")
        out.append(f"- [ ] 通读原文 [[{name}]]（拆分稿）")
        if exs:
            out.append(f"- [ ] 重做例题：{'、'.join('例' + e for e in exs[:20])}")
        out.append("- [ ] 1000题 对应章节")
        out.append("")
        out.append("## 关联")
        out.append(f"- 原文：[[{name}]]（拆分稿）")
        out.append("")
        return "\n".join(out), len(cards)