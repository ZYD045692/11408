# -*- coding: utf-8 -*-
"""补跑 task2 数据结构 8.5.3（书签缺失，用相邻书签界定 p380~382）。
先剔除 jsonl 里的 NO_BOOKMARK 行，再追加正常结果。"""
import os, sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _vlm_lib as V
import _vlm_task2_sections as T

book = "数据结构"
md, pdf = V.BOOKS[book]
out_path = os.path.join(V.VLM, "results", "task2_sections", f"{book}.jsonl")

# 1) 剔除 8.5.3 的 NO_BOOKMARK 行
rows = [l for l in open(out_path, encoding="utf-8") if l.strip()]
keep = [l for l in rows if not (json.loads(l).get("sec") == "8.5.3" and json.loads(l).get("cat") == "NO_BOOKMARK")]
with open(out_path, "w", encoding="utf-8") as f:
    f.writelines(keep)
print(f"剔除 NO_BOOKMARK 行 {len(rows)-len(keep)} 条")

# 2) 正常流程补跑（pages 由相邻书签 8.5.2@p380 / 8.5.4@p382 界定，0-based 379~381）
sec = [s for s in V.split_sections(md, "content") if s["sec"] == "8.5.3"][0]
start, end = 379, 381
page_nos = list(range(max(0, start - 1), end + 2))
core = f"p{start+1}~p{end+1}（由相邻书签 8.5.2/8.5.4 界定）"
imgs = V.render_pages(pdf, page_nos, os.path.join(V.VLM, "pages", book), tag=book[:2])
prompt = T.PROMPT_TMPL.format(book=book, sec=sec["sec"], name=sec["name"],
                              core=core, text=sec["text"][:7000])
text, usage = V.chat(prompt, images=imgs, max_tokens=4000, tag=f"t2patch:{book}:8.5.3")
j = V.parse_json(text)
if not isinstance(j, list):
    j = []
for row in j:
    if isinstance(row, dict):
        row.update({"book": book, "sec": sec["sec"]})
        V.append_jsonl(out_path, row)
V.append_jsonl(out_path, {"book": book, "sec": sec["sec"], "cat": "META",
                          "n_rows": len(j), "pages": f"{page_nos[0]+1}-{page_nos[-1]+1}",
                          "usage": usage, "raw": text})
print(f"补跑完成: {len(j)} 块")
