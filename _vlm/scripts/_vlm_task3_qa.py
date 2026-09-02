# -*- coding: utf-8 -*-
"""任务3：408 题目/答案完整性观察（Q/A 两个独立 Pass）。
单元=习题/答案节，页范围=PDF书签±1页(灰标)。结果写 _vlm/results/task3{q,a}/<书>.jsonl。
用法: python _vlm_task3_qa.py Q|A [书名号...] [--dry-run] [--limit N]"""
import os, sys, json
from concurrent.futures import ThreadPoolExecutor
import _vlm_lib as V

def build_prompt(sec, probs, pre, core_labels, pass_type):
    plist = "、".join(sorted(probs, key=lambda x: int(x)))
    head = f"""这是考研书《{sec['name']}》一节（节号 {sec['sec']}）的 OCR 文本和对应的书页扫描图。
书页已按顺序给出，红字标注 PDF 页码；其中 {core_labels} 是本节正文页，其余为上下文参考页（上面有其他节内容，属正常，不要报告）。
OCR 文本经过清洗，措辞/标点可能与书上略有出入，这不算问题。你只负责**观察事实**，不要推断原因、不要下结论。

== 本节的 OCR markdown 全文（<img> 是图片占位符）==
{sec['text'][:6000]}
== 结束 ==

本节共有这些题号：{plist}（另有小节前言，不用管）。"""

    if pass_type == "Q":
        head += """
对**每一个题号**，逐项观察 **OCR 文本**（以书页为基准对照）。注意：present/stem_complete/options_complete/subq_complete/figure_ok **只能填 true 或 false**（不适用的填 null），不要填其他内容：
- present: 这道题在 OCR 文本中是否存在
- stem_complete: OCR 题干与书页相比是否完整（有开头句、有结尾，未被截断）
- options_complete: OCR 的选项与书页相比是否齐全（书上有 A B C D 而 OCR 缺了任何一个就是 false；非选择题填 null）
- subq_complete: 书页上有 1）2）3）等子问时，OCR 是否齐全；书上无子问填 null
- figure_ok: 题干提到"如图/如右图"时，OCR 对应位置是否有 <img> 占位；无图题填 null
- evidence: 引用书页上该题开头的一句原文作为证据（找不到就写空串）
- note: OCR 与书页的具体差异（没有就写空串）

严格只输出 JSON 数组（每题一个对象，键名如上，外加 "num"），不要输出任何其他文字。"""
    else:
        head += """
对**每一个题号**，逐项观察 **OCR 文本**中的**答案与解析**（以书页为基准对照）。注意：present/letter_exists/analysis_complete **只能填 true 或 false**，不要填其他内容：
- present: 该题的答案在 OCR 文本中是否存在
- letter_exists: **先看 OCR 文本**，逐题检查：该题题号下是否出现了答案字母或答案内容（如单独的 "C"、“【答案】C”、“答案：C”）。只要 OCR 文本里看不到该题的答案字母/答案内容，就填 false——即使书页上有。典型 false 场景：OCR 中该题题号下直接就是解析文字，没有任何答案字母。
- analysis_complete: OCR 的解析与书页相比是否完整——重点看：①解析是否被并进上一题（OCR 本题只剩字母或什么都没有）②解析是否在中间断掉、句子不完整（true=完整/false=有缺）
- evidence: 引用书页上该题答案开头的一句原文（找不到写空串）
- note: OCR 与书页的具体差异（没有写空串）

严格只输出 JSON 数组（每题一个对象，键名如上，外加 "num"），不要输出任何其他文字。"""
    return head

def run(pass_type, books=None, dry_run=False, limit=None):
    assert pass_type in ("Q", "A")
    books = books or list(V.BOOKS)
    outdir = os.path.join(V.VLM, "results", "task3" + pass_type.lower())
    os.makedirs(outdir, exist_ok=True)
    for book in books:
        md, pdf = V.BOOKS[book]
        toc, _ = V.pdf_toc(pdf)
        sections = [s for s in V.split_sections(md, "exercise") if s["kind"] == pass_type]
        out_path = os.path.join(outdir, f"{book}.jsonl")
        done = V.load_done(out_path, "sec")
        V.log(f"[task3{pass_type}] {book}: {len(sections)} 节, 已完成{len(done)}")
        todo = []
        for sec in sections:
            if sec["sec"] in done:
                continue
            probs, pre = V.split_problems(sec["text"])
            pages = V.sec_pages(toc, sec["sec"])
            if not probs:
                V.append_jsonl(out_path, {"book": book, "sec": sec["sec"], "kind": pass_type,
                                          "cat": "SKIP", "note": "无#####题号"})
                continue
            if pages is None:
                V.append_jsonl(out_path, {"book": book, "sec": sec["sec"], "kind": pass_type,
                                          "cat": "NO_BOOKMARK", "n_probs": len(probs)})
                continue
            todo.append((sec, probs, pre, pages))
            if limit and len(todo) >= limit:
                break
        n_run = 0
        for sec, probs, pre, pages in todo:
            start, end = pages
            end = end if end is not None else start
            page_nos = list(range(max(0, start - 1), end + 2))
            core = f"p{start+1}~p{end+1}"
            if dry_run:
                print(f"  {book} {sec['sec']} {pass_type}: 题{len(probs)} 页{page_nos[0]+1}-{page_nos[-1]+1} (核心{core})")
                n_run += 1
                continue
        if dry_run:
            V.log(f"[task3{pass_type}] {book}: dry-run {n_run} 节")
            continue

        def work(item):
            sec, probs, pre, pages = item
            start, end = pages
            end = end if end is not None else start
            page_nos = list(range(max(0, start - 1), end + 2))
            core = f"p{start+1}~p{end+1}"
            imgs = V.render_pages(pdf, page_nos, os.path.join(V.VLM, "pages", book), tag=f"{book[:2]}")
            prompt = build_prompt(sec, probs, pre, core, pass_type)
            max_tok = min(12000, max(4000, len(probs) * 120))
            try:
                text, usage = V.chat(prompt, images=imgs, max_tokens=max_tok,
                                     tag=f"t3{pass_type}:{book}:{sec['sec']}")
                j = V.parse_json(text)
                if not isinstance(j, list):
                    j = []
                for row in j:
                    if isinstance(row, dict):
                        row.update({"book": book, "sec": sec["sec"], "kind": pass_type})
                        V.append_jsonl(out_path, row)
                V.append_jsonl(out_path, {"book": book, "sec": sec["sec"], "kind": pass_type,
                                          "cat": "META", "n_probs": len(probs), "n_rows": len(j),
                                          "pages": f"{page_nos[0]+1}-{page_nos[-1]+1}", "usage": usage,
                                          "raw": text})   # 原始返回全文留档
            except Exception as e:
                V.append_jsonl(out_path, {"book": book, "sec": sec["sec"], "kind": pass_type,
                                          "cat": "CALL_FAIL", "error": str(e)[:200]})

        with ThreadPoolExecutor(V.cfg()["threads"]) as ex:
            list(ex.map(work, todo))
        V.log(f"[task3{pass_type}] {book}: 本轮跑 {len(todo)} 节")

if __name__ == "__main__":
    argv = sys.argv[1:]
    limit = None
    if "--limit" in argv:
        i = argv.index("--limit")
        limit = int(argv[i + 1])
        argv = argv[:i] + argv[i + 2:]
    args = [a for a in argv if not a.startswith("--")]
    run(args[0], books=args[1:] or None,
        dry_run="--dry-run" in argv,
        limit=limit)
