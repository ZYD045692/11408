# -*- coding: utf-8 -*-
"""一次性补跑：试题册Q 综合篇/测试卷二/二、填空题（题11-16，页184-187）。
前三次模型陷入下划线死循环截断，本次 prompt 加“禁止连续下划线”约束。"""
import os, sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _vlm_lib as V
import _vlm_task3_math as M

book = "1000题-试题册"
md, pdf = M.MATH[book]
units = M.split_1000_q(md)
u = [x for x in units if x["unit"] == "综合篇/测试卷二/二、 填空题"][0]
full = M.load_full(book)
units2 = M.locate_1000q(book, units, full)
u = [x for x in units2 if x["unit"] == u["unit"]][0]
nums = ["11", "12", "13", "14", "15", "16"]
p0, p1 = u["pages_q"]
page_nos = list(range(max(0, p0 - 1), p1 + 2))
uc = u["unit"]
prompt = M.build_prompt(book, uc, u["probs"], nums, p0, p1, "Q")
prompt += "\n额外要求：evidence 里禁止连续输出 4 个以上下划线；遇到填空长横线用“___”三个下划线表示即可。每条 evidence 不超过 40 字。"
imgs = V.render_pages(pdf, page_nos, os.path.join(V.VLM, "pages", book), tag=book[:2])
out_path = os.path.join(V.VLM, "results", "task3q", f"{book}.jsonl")
text, usage = V.chat(prompt, images=imgs, max_tokens=8000, tag=f"t3patch:{uc}")
j = V.parse_json(text)
if not isinstance(j, list):
    import re as _re
    t = _re.sub(r"^```(json)?|```$", "", text.strip(), flags=_re.M)
    i = t.find("[")
    BAD = _re.compile(r'(\\\\)|\\u(?![0-9a-fA-F]{4})|\\(?![\\"/bfnrtu])')
    t = BAD.sub(lambda m: m.group(1) if m.group(1) else "\\\\" + m.group(0)[1:], t[i:])
    cut = t.rfind("},")
    j = json.loads(t[:cut + 1] + "]") if cut > 0 else []
n0 = 0
for row in j:
    if isinstance(row, dict) and str(row.get("num")) in nums:
        row.update({"book": book, "sec": uc, "uc": uc, "kind": "Q", "fill": True})
        V.append_jsonl(out_path, row)
        n0 += 1
V.append_jsonl(out_path, {"book": book, "sec": uc, "uc": uc, "kind": "Q", "cat": "META_FILL",
                          "n_probs": 6, "n_rows": n0, "pages": f"{page_nos[0]+1}-{page_nos[-1]+1}",
                          "usage": usage, "raw": text})
print(f"补跑完成: {n0}/6 行")
