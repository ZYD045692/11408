# -*- coding: utf-8 -*-
"""任务4：非A图片带上下文二次判定。
对任务1判为 B/C/D 的图片，从 origin md 中定位 <img src="imgs/img_NN.jpg"> 的引用位置，
抽取上下文（前后若干行 + 所属小节标题）一并给模型，重新判定 A/B/C/D。
输出 _vlm/results/task4_images_context/<书>.jsonl（按 img 续跑）。
用法: python _vlm_task4_images.py [书名号...]（缺省全部8本）"""
import os, sys, re, json, glob
from concurrent.futures import ThreadPoolExecutor
import _vlm_lib as V
import _vlm_task3_math as M
from _vlm_task1_images import IMG_BOOKS, SUBJECT

RES = os.path.join(V.VLM, "results", "task4_images_context")
CTX_LINES = 6   # img 引用行前后各取的行数

PROMPT = """你是图片审查员，审查一张来自《{book}》（{subject}）OCR 工程的扫描图片。
最终目标：把"不属于书本正文"的图片筛出来（判 D），宁可多问"这张图删了读者会损失知识吗"。

这次附带该图在 markdown 里的**上下文**（图片引用行前后文字、小节标题、图注），请结合上下文判断：

```
{context}
```

第一步（必做）：用一句中文客观描述图片里是什么内容。
第二步：判断大类（四选一）：
  A = 正文插图：承载本科目知识内容的图，如函数/坐标图、几何图形、结构示意图、流程图、
      思维导图、知识相关的实物照片等。判断标准：删掉它，读者会损失本科目的知识信息。
      注意：仅仅"画得像一张插图"不算 A，必须真的承载本科目知识内容。
      上下文若表明它是某道题/某个知识点的配图（如图注"图X-X"、正文"如图所示"），倾向 A。
  B = 内容型图片：本该排版为文字/公式的正文内容被截成了图片
      （公式、表格、代码、文字段落、题目、整页书页等）。内容必须与本科目知识相关。
  C = 无法判断。
  D = 非正文图片：与本科目知识无关的装饰性/功能性图片。典型例子：
      小图标（笔、书本、放大镜、灯泡等）、警示/提示三角标志、二维码、条形码、Logo、
      水印、广告、封面元素、页眉页脚装饰、与知识无关的卡通/手绘插画、纯装饰花纹、空白或严重损坏。
第三步：给出细分类（仅对应大类填，否则填 null）：
  B 的细类：文字段落 / 公式 / 表格 / 目录页 / 整页书页 / 图文混合 / 二维码或广告 / 空白或损坏 / 其他
  D 的细类：图标 / 警示标志 / 二维码或广告 / 装饰插画 / Logo或水印 / 封面元素 / 空白或损坏 / 其他

严格只输出一行 JSON，不要输出任何其他文字：
{{"desc": "一句描述", "cat": "A|B|C|D", "sub": "细类或null"}}"""

_md_cache = {}

def md_lines(book):
    if book not in _md_cache:
        md = (V.BOOKS.get(book) or M.MATH[book])[0]
        _md_cache[book] = open(md, encoding="utf-8").read().split("\n")
    return _md_cache[book]

def get_context(book, img_name):
    """定位 img 引用行，抽取 ±CTX_LINES 行 + 最近的上级标题。"""
    lines = md_lines(book)
    hits = [i for i, l in enumerate(lines) if img_name in l]
    if not hits:
        return None
    i = hits[0]
    lo, hi = max(0, i - CTX_LINES), min(len(lines), i + CTX_LINES + 1)
    head = ""
    for j in range(i - 1, max(-1, i - 400), -1):
        m = re.match(r"^(#{1,5})\s+(.*)", lines[j])
        if m:
            head = f"{'#' * len(m.group(1))} {m.group(2).strip()[:60]}"
            break
    ctx = "\n".join(l for l in lines[lo:hi] if l.strip())
    ctx = re.sub(r"<img[^>]*>", f"[图片:{img_name}]", ctx)
    ctx = re.sub(r"<div[^>]*>|</div>", "", ctx)
    ctx = ctx[:1500]
    return (f"【所属小节】{head}\n" if head else "") + ctx

def work(book, img_name, old_cat, out_path):
    img_path = os.path.join(IMG_BOOKS[book], img_name)
    ctx = get_context(book, img_name)
    no_ref = ctx is None
    if no_ref:
        ctx = "（该图未被 markdown 正文引用，存在于 imgs 目录但没有对应 <img> 标签——多为未采用的页面装饰或冗余扫描件）"
    try:
        text, usage = V.chat(PROMPT.format(book=book, subject=SUBJECT[book], context=ctx),
                             images=[img_path], max_tokens=300, tag=f"t4:{book}:{img_name}")
        j = V.parse_json(text)
        if not isinstance(j, dict) or "cat" not in j:
            j = {"desc": "", "cat": "PARSE_FAIL", "sub": None}
        j["raw"] = text
        j["book"], j["img"], j["t1cat"], j["context"] = book, img_name, old_cat, ctx
        if no_ref:
            j["no_ref"] = True
        V.append_jsonl(out_path, j)
        return True
    except Exception as e:
        V.append_jsonl(out_path, {"book": book, "img": img_name, "t1cat": old_cat,
                                  "cat": "CALL_FAIL", "error": str(e)[:200]})
        return False

def run(books=None):
    books = books or list(IMG_BOOKS)
    for book in books:
        t1_path = os.path.join(V.VLM, "results", "task1_images", f"{book}.jsonl")
        if not os.path.exists(t1_path):
            continue
        seen, non_a = set(), []
        for line in open(t1_path, encoding="utf-8"):
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
            except Exception:
                continue
            img = r.get("img")
            if not img or img in seen:
                continue
            seen.add(img)
            if r.get("cat") in ("B", "C", "D"):
                non_a.append((img, r["cat"]))
        non_a.sort(key=lambda x: int(re.search(r"(\d+)", x[0]).group(1)))
        out_path = os.path.join(RES, f"{book}.jsonl")
        os.makedirs(RES, exist_ok=True)
        done = V.load_done(out_path, "img")
        todo = [(im, c) for im, c in non_a if im not in done]
        V.log(f"[task4] {book}: 非A共{len(non_a)} 已完成{len(done)} 待跑{len(todo)}")
        if not todo:
            continue
        ok = 0
        with ThreadPoolExecutor(V.cfg()["threads"]) as ex:
            for r in ex.map(lambda t: work(book, t[0], t[1], out_path), todo):
                ok += r
        V.log(f"[task4] {book}: 完成 ok={ok} fail={len(todo)-ok}")

if __name__ == "__main__":
    run(books=sys.argv[1:] or None)
