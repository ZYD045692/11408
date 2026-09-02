# -*- coding: utf-8 -*-
"""把 results/*.jsonl 转成给人看的 Markdown 观察表（每任务每书一个 .md，与 JSONL 同目录）。
随时可重跑，全量重建。用法: python _vlm_report.py"""
import os, re, json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import _vlm_lib as V
from _vlm_task1_images import IMG_BOOKS

RES = os.path.join(V.VLM, "results")

def rows(path):
    out = []
    if os.path.exists(path):
        for line in open(path, encoding="utf-8"):
            line = line.strip()
            if line:
                try:
                    out.append(json.loads(line))
                except Exception:
                    pass
    return out

# 单元格内容里长得像 HTML 标签的 <（未闭合的 <table> 会提前终结外层 markdown 表格）
_HTML_TAG = re.compile(r"<(?=/?(?:table|thead|tbody|tfoot|tr|td|th|caption|colgroup|col|div|span|img|br|p|a|b|i|em|strong|font|center|sup|sub|u|s|del|ins|mark|small|figure|figcaption|section|article|header|footer|hr|ul|ol|li|dl|dt|dd)\b)", re.I)

def esc(s, n=90):
    if s is None or s == "null":
        s = ""
    s = str(s).replace("|", "\\|").replace("\n", " ").replace("\r", " ")
    s = s.replace("```", "'''")   # 防 Obsidian 把表格单元格里的代码栅栏当成代码块起点
    s = _HTML_TAG.sub("&lt;", s)  # 防原始 HTML 标签终结外层表格
    # 内嵌序列化表格的 --- 分隔行会伪装成外层表格分隔行 → 核心表格解析器 undefined.cells 崩溃
    s = s.replace("\\|---", "\\|―――").replace("---\\|", "―――\\|")
    return s[:n] + ("…" if len(s) > n else "")

def flag(v):
    if v is True:  return "✅"
    if v is False: return "❌"
    return "·"   # null/缺失

def img_sort_key(name):
    m = re.search(r"(\d+)", name)
    return int(m.group(1)) if m else 0

def report_task1():
    for book, dirp in IMG_BOOKS.items():
        rel = os.path.relpath(dirp, V.ROOT).replace("\\", "/")   # Obsidian 嵌入要 vault 相对路径 + 正斜杠
        rs = rows(os.path.join(RES, "task1_images", f"{book}.jsonl"))
        if not rs:
            continue
        rs.sort(key=lambda r: img_sort_key(r.get("img", "")))
        L = [f"# 任务1 插图鉴定观察表 — {book}（{len(rs)} 条）", "",
             "A=正文插图 B=内容型图片 C=无法判断 D=非正文(装饰/图标/二维码等)；最后一列 raw=模型原始返回", "",
             "| 图 | 缩略 | cat | sub | 描述 | raw |", "|---|---|---|---|---|---|"]
        for r in rs:
            img = r.get("img", "")
            thumb = f"![[{rel}/{img}\\|80]]" if r.get("cat") in ("A", "B", "C", "D") else ""
            L.append(f"| {img} | {thumb} | {r.get('cat','')} | {esc(r.get('sub'),12) or '·'} | {esc(r.get('desc'))} | {esc(r.get('raw'),300)} |")
        open(os.path.join(RES, "task1_images", f"{book}.md"), "w", encoding="utf-8", newline="\n").write("\n".join(L))

QFLAGS = ["present", "stem_complete", "options_complete", "subq_complete", "figure_ok"]
AFLAGS = ["present", "letter_exists", "analysis_complete"]

def _books_with_data(outdir):
    """按 outdir 里实际存在的 jsonl 决定出哪些书的表（408 在前，数学在后）。"""
    order = list(V.BOOKS) + ["30讲-高数", "30讲-线代", "1000题-试题册", "1000题-解析册"]
    have = {f[:-6] for f in os.listdir(outdir) if f.endswith(".jsonl")}
    return [b for b in order if b in have] + sorted(have - set(order))

def report_task3(pass_type):
    flags = QFLAGS if pass_type == "Q" else AFLAGS
    outdir = os.path.join(RES, "task3" + pass_type.lower())
    for book in _books_with_data(outdir):
        path = os.path.join(outdir, f"{book}.jsonl")
        rs = rows(path)
        if not rs:
            continue
        data = [r for r in rs if "num" in r]
        meta = [r for r in rs if r.get("cat") == "META"]
        bad = [r for r in rs if r.get("cat") in ("CALL_FAIL", "NO_BOOKMARK", "NO_ANCHOR", "SKIP")]
        hdr = "|".join(f.replace("_complete", "").replace("letter_exists", "letter") for f in flags)
        L = [f"# 任务3{pass_type} 观察表 — {book}（{len(meta)} 节 / {len(data)} 题）", "",
             f"异常行: {len(bad)}（CALL_FAIL/NO_BOOKMARK/NO_ANCHOR/SKIP，详见 JSONL）；raw=该节调用的模型原始返回，标在每节首行", "",
             f"| 节 | 题 | {hdr} | note | evidence | raw |", "|---|---|" + "---|" * (len(flags) + 3)]
        data.sort(key=lambda r: (r.get("sec", ""), tuple(int(x) if x.isdigit() else 0 for x in str(r.get("num", "")).split("."))))
        raw_by_sec = {m.get("sec"): str(m.get("raw", "")) for m in meta}
        seen_sec = set()
        for r in data:
            cells = "|".join(flag(r.get(f)) for f in flags)
            raw_cell = ""
            if r.get("sec") not in seen_sec:
                seen_sec.add(r.get("sec"))
                raw_cell = esc(raw_by_sec.get(r.get("sec"), ""), 400)
            L.append(f"| {r.get('sec','')} | {r.get('num','')} | {cells} | {esc(r.get('note'),60)} | {esc(r.get('evidence'),60)} | {raw_cell} |")
        open(os.path.join(outdir, f"{book}.md"), "w", encoding="utf-8", newline="\n").write("\n".join(L))

def report_task2():
    outdir = os.path.join(RES, "task2_sections")
    for book in _books_with_data(outdir):
        rs = rows(os.path.join(outdir, f"{book}.jsonl"))
        if not rs:
            continue
        data = [r for r in rs if "i" in r]
        meta = [r for r in rs if r.get("cat") == "META"]
        bad = [r for r in rs if r.get("cat") in ("CALL_FAIL", "NO_BOOKMARK")]
        L = [f"# 任务2 小节对照观察表 — {book}（{len(meta)} 节 / {len(data)} 块）", "",
             f"异常行: {len(bad)}（详见 JSONL）；raw=该节调用的模型原始返回，标在每节首行", "",
             "| 节 | 块 | type | in_md | note | evidence | raw |", "|---|---|---|---|---|---|---|"]
        data.sort(key=lambda r: (r.get("sec", ""), r.get("i", 0)))
        raw_by_sec = {m.get("sec"): str(m.get("raw", "")) for m in meta}
        seen_sec = set()
        for r in data:
            im = r.get("in_md", "")
            im = {"有": "✅有", "部分": "🟡部分", "无": "❌无"}.get(im, im)
            raw_cell = ""
            if r.get("sec") not in seen_sec:
                seen_sec.add(r.get("sec"))
                raw_cell = esc(raw_by_sec.get(r.get("sec"), ""), 400)
            L.append(f"| {r.get('sec','')} | {r.get('i','')} | {esc(r.get('type'),8)} | {im} | {esc(r.get('note'),60)} | {esc(r.get('evidence'),60)} | {raw_cell} |")
        open(os.path.join(outdir, f"{book}.md"), "w", encoding="utf-8", newline="\n").write("\n".join(L))

def report_task4():
    outdir = os.path.join(RES, "task4_images_context")
    if not os.path.isdir(outdir):
        return
    for book, dirp in IMG_BOOKS.items():
        path = os.path.join(outdir, f"{book}.jsonl")
        if not os.path.exists(path):
            continue
        rel = os.path.relpath(dirp, V.ROOT).replace("\\", "/")
        rs = rows(path)
        if not rs:
            continue
        rs.sort(key=lambda r: img_sort_key(r.get("img", "")))
        L = [f"# 任务4 非A图片带上下文二次判定 — {book}（{len(rs)} 条）", "",
             "对任务1判为 B/C/D 的图片，嵌入 md 上下文后重判。t1=任务1判定，cat=任务4判定（A=正文插图 B=内容型 C=无法判断 D=非正文）；raw=模型原始返回", "",
             "| 图 | 缩略 | t1 | cat | sub | 描述 | 上下文 | raw |", "|---|---|---|---|---|---|---|---|"]
        for r in rs:
            img = r.get("img", "")
            thumb = f"![[{rel}/{img}\\|80]]" if r.get("cat") in ("A", "B", "C", "D") else ""
            t1 = r.get("t1cat", "")
            cat = r.get("cat", "")
            L.append(f"| {img} | {thumb} | {t1} | {cat} | {esc(r.get('sub'),12) or '·'} | {esc(r.get('desc'))} | {esc(r.get('context'),200)} | {esc(r.get('raw'),300)} |")
        open(os.path.join(outdir, f"{book}.md"), "w", encoding="utf-8", newline="\n").write("\n".join(L))

if __name__ == "__main__":
    report_task1()
    report_task3("Q")
    report_task3("A")
    report_task2()
    report_task4()
    print("reports written")
