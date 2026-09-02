# -*- coding: utf-8 -*-
"""任务1：插图鉴定。逐张分类+描述，结果写 _vlm/results/task1_images/<书>.jsonl。
用法: python _vlm_task1_images.py [书名号...]（缺省全部8本）"""
import os, sys, glob, json
from concurrent.futures import ThreadPoolExecutor
import _vlm_lib as V

IMG_BOOKS = {
    "数据结构": "11408/origin/2027数据结构/imgs",
    "操作系统": "11408/origin/2027操作系统/imgs",
    "计算机组成原理": "11408/origin/2027计算机组成原理/imgs",
    "计算机网络": "11408/origin/2027计算机网络/imgs",
    "30讲-高数": "11408/origin/27张宇基础30讲（高数）/imgs",
    "30讲-线代": "11408/origin/27张宇基础30讲线代/imgs",
    "1000题-试题册": "11408/origin/27张宇1000题数一【试题册】/imgs",
    "1000题-解析册": "11408/origin/27张宇1000题数一【解析册】/imgs",
}
IMG_BOOKS = {k: os.path.join(V.ROOT, v) for k, v in IMG_BOOKS.items()}

SUBJECT = {
    "数据结构": "考研计算机(408)·数据结构",
    "操作系统": "考研计算机(408)·操作系统",
    "计算机组成原理": "考研计算机(408)·计算机组成原理",
    "计算机网络": "考研计算机(408)·计算机网络",
    "30讲-高数": "考研数学·高等数学",
    "30讲-线代": "考研数学·线性代数",
    "1000题-试题册": "考研数学·习题(试题册)",
    "1000题-解析册": "考研数学·习题解析(解析册)",
}

PROMPT = """你是图片审查员，审查一张来自《{book}》（{subject}）OCR 工程的扫描图片。
最终目标：把"不属于书本正文"的图片筛出来（判 D），宁可多问"这张图删了读者会损失知识吗"。

第一步（必做）：用一句中文客观描述图片里是什么内容。
第二步：判断大类（四选一）：
  A = 正文插图：承载本科目知识内容的图，如函数/坐标图、几何图形、结构示意图、流程图、
      思维导图、知识相关的实物照片等。判断标准：删掉它，读者会损失本科目的知识信息。
      注意：仅仅"画得像一张插图"不算 A，必须真的承载本科目知识内容。
  B = 内容型图片：本该排版为文字/公式的正文内容被截成了图片
      （公式、表格、代码、文字段落、题目、整页书页等）。内容必须与本科目知识相关。
  C = 无法判断。
  D = 非正文图片：与本科目知识无关的装饰性/功能性图片。典型例子：
      小图标（笔、书本、放大镜、灯泡等）、警示/提示三角标志、二维码、条形码、Logo、
      水印、广告、封面元素、页眉页脚装饰、与知识无关的卡通/手绘插画
      （如搬东西的小人、食物图案等）、纯装饰花纹、空白或严重损坏。
第三步：给出细分类（仅对应大类填，否则填 null）：
  B 的细类：文字段落 / 公式 / 表格 / 目录页 / 整页书页 / 图文混合 / 二维码或广告 / 空白或损坏 / 其他
  D 的细类：图标 / 警示标志 / 二维码或广告 / 装饰插画 / Logo或水印 / 封面元素 / 空白或损坏 / 其他

严格只输出一行 JSON，不要输出任何其他文字：
{{"desc": "一句描述", "cat": "A|B|C|D", "sub": "细类或null"}}"""

def work(book, img_path, out_path):
    name = os.path.basename(img_path)
    try:
        text, usage = V.chat(PROMPT.format(book=book, subject=SUBJECT[book]),
                             images=[img_path], max_tokens=300, tag=f"t1:{book}:{name}")
        j = V.parse_json(text)
        if not isinstance(j, dict) or "cat" not in j:
            j = {"desc": "", "cat": "PARSE_FAIL", "sub": None}
        j["raw"] = text   # 原始返回全文留档，便于追溯/二次处理
        j["book"], j["img"] = book, name
        V.append_jsonl(out_path, j)
        return True
    except Exception as e:
        V.append_jsonl(out_path, {"book": book, "img": name, "cat": "CALL_FAIL", "error": str(e)[:200]})
        return False

def run(books=None, limit=None):
    books = books or list(IMG_BOOKS)
    for book in books:
        imgs = sorted(glob.glob(os.path.join(IMG_BOOKS[book], "*.*")))
        if limit:
            imgs = imgs[:limit]
        out_path = os.path.join(V.VLM, "results", "task1_images", f"{book}.jsonl")
        done = V.load_done(out_path, "img")
        todo = [p for p in imgs if os.path.basename(p) not in done]
        V.log(f"[task1] {book}: 共{len(imgs)} 已完成{len(done)} 待跑{len(todo)}")
        if not todo:
            continue
        ok = 0
        with ThreadPoolExecutor(V.cfg()["threads"]) as ex:
            for r in ex.map(lambda p: work(book, p, out_path), todo):
                ok += r
        V.log(f"[task1] {book}: 完成 ok={ok} fail={len(todo)-ok}")

if __name__ == "__main__":
    run(books=sys.argv[1:] or None)
