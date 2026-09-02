"""整章/逐页重试失败的章节（复用 factory 的 build_hd_pdf / opts / assemble）。
用法: python _ocr_liang_retry_pages.py <book> <ch>  [max_tries]   (整章提交重试)
      python _ocr_liang_retry_pages.py --page <book> <ch>          (逐页提交)
"""
import asyncio, importlib.util, io, os, sys, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
F2 = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_ocr_liang_factory2.py")
spec = importlib.util.spec_from_file_location("fac", F2)
fac = importlib.util.module_from_spec(spec)
# 避免 import 时重复 wrap stdout / sys.path（factory 顶部用了 TextIOWrapper）
import _crop_liang_pdfs as C

class _C:
    PDF = C.PDF
    BASIC_CHS = C.BASIC_CHS
    STRONG_CHS = C.STRONG_CHS
    NO_HEADER_PAGES = C.NO_HEADER_PAGES
    HEADER_CUT_FRAC = C.HEADER_CUT_FRAC
    FOOTER_FALLBACK = C.FOOTER_FALLBACK
    FOOTER_GAP = C.FOOTER_GAP
    def __getattr__(self, n):
        return getattr(C, n)

def make_opts(max_new=8192):
    from paddleocr import PaddleOCRVLOptions
    return PaddleOCRVLOptions(
        use_doc_orientation_classify=True, use_doc_unwarping=True,
        use_layout_detection=True, use_ocr_for_image_block=True,
        max_pixels=16*1024*1024, max_new_tokens=max_new, temperature=0.0,
        prettify_markdown=True, relevel_titles=True,
    )

def load_token():
    import io as _io
    envf = os.path.join(ROOT, "_vlm", ".env")
    if os.path.exists(envf):
        for line in open(envf, encoding="utf-8"):
            if line.startswith("PADDLEOCR_AISTUDIO_TOKEN="):
                return line.strip().split("=", 1)[1]
    return os.environ.get("PADDLEOCR_AISTUDIO_TOKEN", "")
TOKEN = load_token()
STAGE = os.path.join(ROOT, "_vlm", "ocr_stage", "liang_glt_hd")

def build_hd_pdf(p_start, p_end, out_pdf):
    """复用 factory2 的 build_hd_pdf（纯净重实现，避免 import 坏 stdout）。"""
    import fitz, io as _io, tempfile
    from PIL import Image
    doc = fitz.open(C.PDF)
    tmpdir = os.path.join(tempfile.gettempdir(), "liang_hd_tmp")
    os.makedirs(tmpdir, exist_ok=True)
    pages = []
    for p0 in range(p_start - 1, p_end):
        top_f, bot_f = crop_fracs(p0)
        imgs = doc[p0].get_images(full=True)
        if imgs:
            info = doc.extract_image(imgs[0][0])
            img = Image.open(_io.BytesIO(info["image"])).convert("RGB")
        else:
            pix = doc[p0].get_pixmap(matrix=fitz.Matrix(3.0, 3.0))
            img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
        W, H = img.size
        img2 = img.crop((0, int(H*top_f), W, int(H*bot_f)))
        tmp = os.path.join(tmpdir, "p%04d.jpg" % (p0+1))
        img2.save(tmp, quality=92)
        pages.append(tmp)
    pdf = fitz.open()
    for t in pages:
        r = fitz.open(t)
        page = pdf.new_page(width=r[0].rect.width, height=r[0].rect.height)
        page.insert_image(page.rect, filename=t)
        r.close()
        os.remove(t)
    pdf.save(out_pdf)
    pdf.close()
    doc.close()
    return len(pages)

def crop_fracs(p0):
    import fitz
    if (p0 + 1) in C.NO_HEADER_PAGES:
        top = 0.004
    else:
        top = C.HEADER_CUT_FRAC
    doc = fitz.open(C.PDF)
    pn_top, _ = C.locate_pageno_top(doc, p0)
    doc.close()
    bottom = C.FOOTER_FALLBACK
    if pn_top is not None:
        cand = pn_top - C.FOOTER_GAP
        if 0.895 <= cand <= 0.985:
            bottom = cand
    return top, bottom

async def main():
    from paddleocr import AsyncPaddleOCRClient
    args = sys.argv[1:]
    page_mode = args and args[0] == "--page"
    rng = None
    if "--range" in args:
        i = args.index("--range")
        rng = args[i+1]
        args = args[:i]
    if page_mode:
        book, ch = args[1], args[2]
    else:
        book, ch = args[0], args[1]
        max_tries = int(args[2]) if len(args) > 2 else 3
    chs = C.BASIC_CHS if book == "基础" else C.STRONG_CHS
    s = e = None
    for name, ss, ee in chs:
        if name == ch:
            s, e = ss, ee
    if rng:
        aa, bb = rng.split("-")
        s, e = int(aa), int(bb)
    dir0 = os.path.join(STAGE, book, ch)
    os.makedirs(os.path.join(dir0, "pages"), exist_ok=True)
    hd_pdf = os.path.join(dir0, f"_{ch}_hd.pdf")
    print("[%s] %s/%s 合成高清PDF..." % (time.strftime("%H:%M:%S"), book, ch), flush=True)
    t0 = time.time()
    n = build_hd_pdf(s, e, hd_pdf)
    print("  高清PDF %d页 %.0fs" % (n, time.time()-t0), flush=True)
    req_params = dict(model="PaddleOCR-VL-1.6", file_path=hd_pdf, options=make_opts())
    if page_mode:
        req_params["page_ranges"] = None
    async with AsyncPaddleOCRClient(token=TOKEN, request_timeout=600, poll_timeout=3600) as client:
        if page_mode:
            for p in range(s, e + 1):
                t0 = time.time()
                try:
                    r = await client.parse_document(model="PaddleOCR-VL-1.6", file_path=hd_pdf,
                                                    page_ranges=str(p), options=make_opts())
                    with open(os.path.join(dir0, "pages", f"p{p}.md"), "w", encoding="utf-8") as f:
                        f.write(r.pages[0].markdown_text)
                    print("p%d OK %.0fs" % (p, time.time()-t0), flush=True)
                except Exception as ex:
                    print("p%d FAIL %s" % (p, str(ex)[:110]), flush=True)
        else:
            failed = True
            # --range 指定 → page_ranges 提交子集；否则全章提交
            pr = None
            full_s = full_e = s
            for name2, ss2, ee2 in chs:
                if name2 == ch:
                    full_s, full_e = ss2, ee2
            if rng is not None:
                pr = "%d-%d" % (s, e)
            for k in range(max_tries):
                try:
                    kw = dict(model="PaddleOCR-VL-1.6", file_path=hd_pdf, options=make_opts())
                    if pr:
                        kw["page_ranges"] = pr
                    r = await client.parse_document(**kw)
                    ok = len(r.pages)
                    base = s if pr else full_s
                    for i, pg in enumerate(r.pages):
                        pno = base + i
                        with open(os.path.join(dir0, "pages", f"p{pno}.md"), "w", encoding="utf-8") as f:
                            f.write(pg.markdown_text)
                    print("成功 %d页(%s) 尝试%d %.0fs" % (ok, pr or "全章", k+1, time.time()-t0), flush=True)
                    failed = False
                    break
                except Exception as ex:
                    print("第%d次失败: %s" % (k+1, str(ex)[:110]), flush=True)
                    if k + 1 < max_tries: time.sleep(20)
            if failed:
                print("全部 %d 次失败，可换 --page 逐页定位" % max_tries, flush=True)
    print("DONE", flush=True)

if __name__ == "__main__":
    asyncio.run(main())