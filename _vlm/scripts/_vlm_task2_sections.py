# -*- coding: utf-8 -*-
"""任务2：小节级全书对照（内容型小节）。单元=### X.Y.Z 内容节，页范围=书签±1页。
结果写 _vlm/results/task2_sections/<书>.jsonl。
用法: python _vlm_task2_sections.py [书名号...] [--dry-run] [--limit N]"""
import os, sys, json
from concurrent.futures import ThreadPoolExecutor
import _vlm_lib as V

PROMPT_TMPL = """这是考研书《{book}》一节（节号 {sec}，节名「{name}」）的 OCR 文本和对应的书页扫描图。
书页已按顺序给出，红字标注 PDF 页码；其中 {core} 是本节正文页，其余为上下文参考页（属其他节内容，不要报告）。
OCR 文本经过清洗，措辞/标点/排版与书上略有出入**不算问题**；广告、二维码、公众号、页眉页脚是**故意删除**的，也不算缺失。你只负责观察事实，不要推断原因、不要下结论。

== 本节的 OCR markdown 全文（<img> 是图片占位符）==
{text}
== 结束 ==

请按书上顺序列出本节的**内容块**，逐块观察：
- i: 块序号（从1开始）
- type: 正文 | 例题 | 图表 | 公式块 | 广告页眉 | 其他
- in_md: 该块内容在 OCR 文本中是否存在（有 | 部分 | 无）
- evidence: 引用书页上该块开头的一句原文
- note: 具体差异说明（OCR 缺失了哪部分；没有写空串）

严格只输出 JSON 数组，不要输出任何其他文字。"""

def run(books=None, dry_run=False, limit=None):
    books = books or ["数据结构"]
    outdir = os.path.join(V.VLM, "results", "task2_sections")
    os.makedirs(outdir, exist_ok=True)
    for book in books:
        md, pdf = V.BOOKS[book]
        toc, _ = V.pdf_toc(pdf)
        sections = V.split_sections(md, "content")
        out_path = os.path.join(outdir, f"{book}.jsonl")
        done = V.load_done(out_path, "sec")
        V.log(f"[task2] {book}: {len(sections)} 内容节, 已完成{len(done)}")
        todo = []
        for sec in sections:
            if sec["sec"] in done:
                continue
            pages = V.sec_pages(toc, sec["sec"])
            if pages is None:
                V.append_jsonl(out_path, {"book": book, "sec": sec["sec"], "cat": "NO_BOOKMARK"})
                continue
            todo.append((sec, pages))
            if limit and len(todo) >= limit:
                break
        if dry_run:
            for sec, pages in todo:
                start, end = pages
                end = end if end is not None else start
                page_nos = list(range(max(0, start - 1), end + 2))
                print(f"  {book} {sec['sec']} {sec['name'][:20]}: 页{page_nos[0]+1}-{page_nos[-1]+1} (核心p{start+1}~p{end+1}) md{len(sec['text'])}字")
            V.log(f"[task2] {book}: dry-run {len(todo)} 节")
            continue

        def work(item):
            sec, pages = item
            start, end = pages
            end = end if end is not None else start
            page_nos = list(range(max(0, start - 1), end + 2))
            core = f"p{start+1}~p{end+1}"
            imgs = V.render_pages(pdf, page_nos, os.path.join(V.VLM, "pages", book), tag=f"{book[:2]}")
            prompt = PROMPT_TMPL.format(book=book, sec=sec["sec"], name=sec["name"],
                                        core=core, text=sec["text"][:7000])
            try:
                text, usage = V.chat(prompt, images=imgs, max_tokens=4000,
                                     tag=f"t2:{book}:{sec['sec']}")
                j = V.parse_json(text)
                if not isinstance(j, list):
                    j = []
                for row in j:
                    if isinstance(row, dict):
                        row.update({"book": book, "sec": sec["sec"]})
                        V.append_jsonl(out_path, row)
                V.append_jsonl(out_path, {"book": book, "sec": sec["sec"], "cat": "META",
                                          "n_rows": len(j), "pages": f"{page_nos[0]+1}-{page_nos[-1]+1}",
                                          "usage": usage, "raw": text})   # 原始返回全文留档
            except Exception as e:
                V.append_jsonl(out_path, {"book": book, "sec": sec["sec"],
                                          "cat": "CALL_FAIL", "error": str(e)[:200]})

        with ThreadPoolExecutor(V.cfg()["threads"]) as ex:
            list(ex.map(work, todo))
        V.log(f"[task2] {book}: 本轮跑 {len(todo)} 节")

if __name__ == "__main__":
    argv = sys.argv[1:]
    limit = None
    if "--limit" in argv:
        i = argv.index("--limit")
        limit = int(argv[i + 1])
        argv = argv[:i] + argv[i + 2:]
    args = [a for a in argv if not a.startswith("--")]
    run(books=args or None,
        dry_run="--dry-run" in argv,
        limit=limit)
