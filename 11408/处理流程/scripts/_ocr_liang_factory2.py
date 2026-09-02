# -*- coding: utf-8 -*-
"""李良概统 高清 OCR 工厂：原图 300dpi + 裁剪页眉页脚 + max_pixels 调大，按章批量生成。

用法:
  python _ocr_liang_factory2.py --book 基础 --ch 第一章        # 单章
  python _ocr_liang_factory2.py --all                          # 全书 14 章

每章处理：
  逐页取原 PDF 内嵌高清图(约 4183px) -> 按裁剪线(页眉7.5%/章首页不裁 + 页码 tesseract 定位)裁掉页眉页脚
  -> 保存高清临时单页 -> 提交 AI Studio PaddleOCR-VL (max_pixels 调大, 保证送入模型分辨率不缩水)
  -> 每页 markdown 落盘 <stage>/<book>/<ch>/p{原pdf页}.md + 图片 imgs/

断点续跑：目标 md 已存在则跳过该页。OCR 结果全部落盘，不做任何清洗（用户有后续要求）。
"""
import argparse, asyncio, io, json, os, re, sys, time, traceback

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _crop_liang_pdfs as C            # 复用 PDF/NO_HEADER_PAGES/BASIC_CHS/STRONG_CHS/locate_pageno_top

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
STAGE = os.path.join(ROOT, "_vlm", "ocr_stage", "liang_glt_hd")
# 最终产出：按 基础/强化 两本 origin
ORIGIN_MAP = {"基础": os.path.join(ROOT, "11408", "origin", "27李良概统基础"),
              "强化": os.path.join(ROOT, "11408", "origin", "27李良概统强化")}
# 章全名（基础/强化 章名一致）
CH_TITLES = {
    "第一章": "随机事件和概率", "第二章": "一维随机变量及其分布",
    "第三章": "多维随机变量及其分布", "第四章": "数字特征",
    "第五章": "大数定律和中心极限定理", "第六章": "数理统计的基本概念",
    "第七章": "参数估计与假设检验",
}

def load_token():
    envf = os.path.join(ROOT, "_vlm", ".env")
    if os.path.exists(envf):
        for line in open(envf, encoding="utf-8"):
            if line.startswith("PADDLEOCR_AISTUDIO_TOKEN="):
                return line.strip().split("=", 1)[1]
    return os.environ.get("PADDLEOCR_AISTUDIO_TOKEN", "")

TOKEN = load_token()
assert TOKEN, "缺少 PADDLEOCR_AISTUDIO_TOKEN"

def crop_fracs(p0):
    """按 _crop_liang_pdfs 的规则返回 (top_frac, bottom_frac)（在页高比例上）。"""
    doc0 = None
    pn_top, _ = C.locate_pageno_top(None, p0) if False else (None, None)
    # 页眉
    if (p0 + 1) in C.NO_HEADER_PAGES:
        top = 0.004
    else:
        top = C.HEADER_CUT_FRAC
    # 页码：逐页 tesseract
    import fitz
    doc = fitz.open(C.PDF)
    pn_top, _ = C.locate_pageno_top(doc, p0)
    doc.close()
    bottom = C.FOOTER_FALLBACK
    if pn_top is not None:
        cand = pn_top - C.FOOTER_GAP
        if 0.895 <= cand <= 0.985:
            bottom = cand
    return top, bottom

def build_hd_pdf(p_start, p_end, out_pdf):
    """从原 PDF 取内嵌高清图 + 裁剪 → 合成一章的临时高清 PDF。返回页数。"""
    import fitz
    from PIL import Image
    import tempfile
    doc = fitz.open(C.PDF)
    pages = []
    tmpdir = os.path.join(tempfile.gettempdir(), "liang_hd_tmp")
    os.makedirs(tmpdir, exist_ok=True)
    for p0 in range(p_start - 1, p_end):
        top_f, bot_f = crop_fracs(p0)
        # 取内嵌整页图
        imgs = doc[p0].get_images(full=True)
        if imgs:
            xref = imgs[0][0]
            info = doc.extract_image(xref)
            img = Image.open(io.BytesIO(info["image"])).convert("RGB")
        else:
            pix = doc[p0].get_pixmap(matrix=fitz.Matrix(3.0, 3.0))
            img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
        W, H = img.size
        img2 = img.crop((0, int(H*top_f), W, int(H*bot_f)))
        tmp = os.path.join(tmpdir, "p%04d.jpg" % (p0+1))
        img2.save(tmp, quality=92)
        pages.append(tmp)
    pdf = fitz.open()
    for i, t in enumerate(pages):
        r = fitz.open(t)
        rect = fitz.Rect(0, 0, 595, 842 * (1.0))
        page = pdf.new_page(width=r[0].rect.width, height=r[0].rect.height)
        page.insert_image(page.rect, filename=t)
        r.close()
        os.remove(t)
    pdf.save(out_pdf)
    pdf.close()
    doc.close()
    return len(pages)

async def ocr_chapter(client, opts, book, ch_name, p_start, p_end, stage):
    """对一章：合成高清 PDF → 提交 → 逐页落盘 md + 图片。返回 (ok, fail) 页数。"""
    os.makedirs(os.path.join(stage, book, ch_name, "pages"), exist_ok=True)
    os.makedirs(os.path.join(stage, book, ch_name, "imgs"), exist_ok=True)
    hd_pdf = os.path.join(stage, book, ch_name, f"_{ch_name}_hd.pdf")
    t0 = time.time()
    print("[%s] %s/%s 组超高清PDF p%d-p%d ..." % (time.strftime("%H:%M:%S"), book, ch_name, p_start, p_end), flush=True)
    n = build_hd_pdf(p_start, p_end, hd_pdf)
    print("  高清PDF建好 %d页 t=%.0fs" % (n, time.time()-t0), flush=True)

    # 断点：跳过已完成的页
    todo = []
    for p in range(p_start, p_end + 1):
        md = os.path.join(stage, book, ch_name, "pages", f"p{p}.md")
        if not os.path.exists(md):
            todo.append(p)
    if not todo:
        print("  全部页已完成，跳过", flush=True)
        return 0, 0

    # 提交全书（page_ranges=章内页已有页号）——直接提交高清PDF整文件，一次解析
    try:
        result = await client.parse_document(
            model="PaddleOCR-VL-1.6", file_path=hd_pdf, options=opts)
    except Exception as e:
        print("  提交失败: %s" % e, flush=True)
        traceback.print_exc()
        return 0, len(todo)
    ok = fail = 0
    for i, pg in enumerate(result.pages):
        pno = p_start + i
        md_fn = os.path.join(stage, book, ch_name, "pages", f"p{pno}.md")
        with open(md_fn, "w", encoding="utf-8") as f:
            f.write(pg.markdown_text)
        # 图片：markdown_images 是 {name:url}，下载到 imgs/
        if pg.markdown_images:
            import urllib.request
            pdir = os.path.join(stage, book, ch_name, "imgs")
            for nm, url in pg.markdown_images.items():
                base = os.path.basename(nm)
                dest = os.path.join(pdir, f"{pno}_{base}")
                if os.path.exists(dest): continue
                try:
                    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
                    with urllib.request.urlopen(req, timeout=120) as r:
                        data = r.read()
                    open(dest, "wb").write(data)
                except Exception:
                    pass
        ok += 1
    print("  OK %d 页, t=%.0fs" % (ok, time.time() - t0), flush=True)
    if ok == n:
        assemble_origin(book, ch_name, p_start, p_end, stage)
    return ok, fail


def assemble_origin(book, ch_name, p_start, p_end, stage):
    """把章内各页 stage md 顺序拼接 → origin/27李良概统{基础,强化}/第N章-章名.md；
    图片复制进 origin 的 imgs/，引用改为相对 origin 文件名。纯拼接不清洗。"""
    origin_dir = ORIGIN_MAP[book]
    os.makedirs(origin_dir, exist_ok=True)
    os.makedirs(os.path.join(origin_dir, "imgs"), exist_ok=True)
    title = "%s-%s" % (ch_name, CH_TITLES[ch_name])
    out_path = os.path.join(origin_dir, title + ".md")
    parts = []
    for p in range(p_start, p_end + 1):
        md = os.path.join(stage, book, ch_name, "pages", f"p{p}.md")
        if os.path.exists(md):
            parts.append(open(md, encoding="utf-8").read().strip())
    text = "\n\n".join(parts)
    # 图片：stage imgs/ 里 `p{no}_box_*.jpg` → origin imgs/ 里 `box_*.jpg`（去页码前缀），
    # md 里 src 本为 `imgs/img_in_image_box_*.jpg`，与复制后名字一致，无需改引用。
    img_src = os.path.join(stage, book, ch_name, "imgs")
    if os.path.isdir(img_src):
        import shutil
        for fn in os.listdir(img_src):
            if not fn.endswith(".jpg"):
                continue
            if "_" not in fn:
                continue
            _pno, box = fn.split("_", 1)
            srcp = os.path.join(img_src, fn)
            dstp = os.path.join(origin_dir, "imgs", box)
            if not os.path.exists(dstp):
                shutil.copy(srcp, dstp)
    with open(out_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    print("  → 已组装 %s 于 %s" % (title + ".md", origin_dir), flush=True)

def opts_max():
    from paddleocr import PaddleOCRVLOptions
    return PaddleOCRVLOptions(
        use_doc_orientation_classify=True,
        use_doc_unwarping=True,
        use_layout_detection=True,
        use_ocr_for_image_block=True,
        max_pixels=16 * 1024 * 1024,       # 16MP（paddle 常见上限）
        max_new_tokens=8192,
        temperature=0.0,
        top_p=1.0,
        repetition_penalty=1.0,
        prettify_markdown=True,
        relevel_titles=True,
    )

async def main():
    from paddleocr import AsyncPaddleOCRClient
    ap = argparse.ArgumentParser()
    ap.add_argument("--book", choices=["基础", "强化"], default=None)
    ap.add_argument("--ch", default=None)
    ap.add_argument("--all", action="store_true")
    a = ap.parse_args()
    opts = opts_max()
    chapters = []
    for book, chs in (("基础", C.BASIC_CHS), ("强化", C.STRONG_CHS)):
        if a.book and a.book != book:
            continue
        for name, s, e in chs:
            if a.ch and a.ch != name:
                continue
            chapters.append((book, name, s, e))
    print("待OCR章节:", [(b, c) for b, c, _, _ in chapters], flush=True)
    async with AsyncPaddleOCRClient(token=TOKEN, request_timeout=600, poll_timeout=3600) as client:
        for book, name, s, e in chapters:
            try:
                await ocr_chapter(client, opts, book, name, s, e, STAGE)
            except Exception as ex:
                print("章节 %s/%s 异常: %s" % (book, name, ex), flush=True)
                traceback.print_exc()
    print("ALL DONE", flush=True)

if __name__ == "__main__":
    asyncio.run(main())