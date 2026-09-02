# -*- coding: utf-8 -*-
"""计组 4.3 综合应用题 题7、题8 整题缺失补齐（复验新发现，备份即缺）。
从 PDF 提取 Q+A，按 `##### 07`/`##### 08` 插入 4.3.5(Q区二) 与 4.3.6(A区二)。
输出 _vlm/repair/zj43.jsonl；--apply 时写回 origin。"""
import os, sys, io, json, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _vlm_lib as V

OUT = os.path.join(V.VLM, "repair", "zj43.jsonl")
BAD_ESC = re.compile(r'(\\\\)|\\u(?![0-9a-fA-F]{4})|\\(?![\\"/bfnrtu])')
BOOK = "计算机组成原理"

PROMPT = """这是考研计算机书《计算机组成原理》4.3 节习题的书页扫描图（红字标注 PDF 页码）。
书页结构：先是"4.3.5 本节习题精选"（内含"一、 单项选择题"和"二、 综合应用题"两部分），后面是"4.3.6 答案与解析"（同样分两部分）。

**注意**：单项选择题的第 7、8 题稿里有，不要提取选择题！
丢失的是**"二、 综合应用题"部分的第 7 题和第 8 题**——它们是排在综合应用题第 6 题和第 9 题之间的两道大题（通常是程序分析/计算/设计类大题，可能含代码、图表）。
答案在"4.3.6 答案与解析"的"二、 综合应用题"部分对应位置。

请完整提取这两道大题：
- question：题干全文（含所有小问、图表说明文字）
- answer：答案与解析全文（代码逐行保留）

严格只输出 JSON 数组：
[{{"num": "7", "question": "题干全文", "answer": "答案解析全文", "confident": true/false}},
 {{"num": "8", "question": "...", "answer": "...", "confident": true/false}}]
某题在书页上找不到时 confident 填 false、对应字段填空串。"""

def parse_arr(text):
    t = re.sub(r"^```(json)?|```$", "", text.strip(), flags=re.M)
    i = t.find("[")
    if i < 0:
        return []
    tt = BAD_ESC.sub(lambda m: m.group(1) if m.group(1) else "\\\\" + m.group(0)[1:], t[i:])
    try:
        return json.loads(tt)
    except Exception:
        cut = tt.rfind("},")
        if cut > 0:
            try:
                return json.loads(tt[:cut + 1] + "]")
            except Exception:
                pass
    return []

def main():
    md, pdf = V.BOOKS[BOOK]
    toc, npg = V.pdf_toc(pdf)
    pq = V.sec_pages(toc, "4.3.5")
    pa = V.sec_pages(toc, "4.3.6")
    V.log(f"[zj43] 4.3.5 页 {pq}  4.3.6 页 {pa}  (PDF 共 {npg} 页)")
    lo = min(pq[0], pa[0]) - 1
    hi = max(pq[1], pa[1]) + 1
    page_nos = list(range(max(0, lo), min(npg, hi + 1)))
    V.log(f"[zj43] 取页 {page_nos[0]+1}~{page_nos[-1]+1} 共 {len(page_nos)} 页")
    imgs = V.render_pages(pdf, page_nos, os.path.join(V.VLM, "pages", BOOK), tag="计组")
    text, usage = V.chat(PROMPT, images=imgs, max_tokens=8000, tag="zj43:4.3:7-8")
    arr = parse_arr(text)
    for it in arr:
        if isinstance(it, dict):
            it["raw"] = text
            V.append_jsonl(OUT, it)
    V.log(f"[zj43] 提取 {len(arr)} 题: {[(a.get('num'), a.get('confident'), len(a.get('question') or ''), len(a.get('answer') or '')) for a in arr if isinstance(a, dict)]}")

if __name__ == "__main__":
    main()
