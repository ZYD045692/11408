# -*- coding: utf-8 -*-
"""李良概统 PDF 批量 OCR 工厂：分批提交 AI Studio，逐页落盘 markdown + 插图。

用法:
  python _ocr_liang_factory.py <start_page> <end_page> [pages_per_batch] [--stage <dir>]

落盘:
  <stage>/pages/p{页}.md        每页 OCR markdown（连续页组装用）
  <stage>/imgs/p{页}/box_*.jpg  该页 markdown_images 下载的插图（原名取自 URL 文件名）
  <stage>/_meta.json            页→(md_len, n_img) 摘要

断点续跑：pages/p{end_page}.md 已存在则整批跳过（按批粒度）。
"""
import asyncio, io, json, os, re, sys, time, urllib.request

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))

PDF = r"d:\obsidian'srepository\my\11408\pdf\数学\27李良概统辅导-基础&强化.pdf"

def load_token():
    envf = os.path.join(ROOT, "_vlm", ".env")
    if os.path.exists(envf):
        for line in open(envf, encoding="utf-8"):
            if line.startswith("PADDLEOCR_AISTUDIO_TOKEN="):
                return line.strip().split("=", 1)[1]
    return os.environ.get("PADDLEOCR_AISTUDIO_TOKEN", "")

TOKEN = load_token()
assert TOKEN, "缺少 PADDLEOCR_AISTUDIO_TOKEN"

def download(url, dest):
    if os.path.exists(dest):
        return True
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=120) as r:
            data = r.read()
        with open(dest, "wb") as f:
            f.write(data)
        return True
    except Exception as e:
        print("  [dl fail]", url[-60:], type(e).__name__, e)
        return False

async def run_batch(client, opts, start, end, stage):
    """提交 [start,end]（1-based），落盘后返回 (first_page, last_page, n_img)。"""
    prange = "%d-%d" % (start, end)
    out_dir = os.path.join(stage, "pages"); img_dir = os.path.join(stage, "imgs")
    os.makedirs(out_dir, exist_ok=True); os.makedirs(img_dir, exist_ok=True)
    t0 = time.time()
    result = await client.parse_document(
        model=Model, file_path=PDF, page_ranges=prange, options=opts)
    meta = []
    for i, pg in enumerate(result.pages):
        pno = start + i
        md_fn = os.path.join(out_dir, "p%d.md" % pno)
        with open(md_fn, "w", encoding="utf-8") as f:
            f.write(pg.markdown_text)
        n_img = 0
        # 下载该页标记图到 imgs/p{no}/
        if pg.markdown_images:
            pdir = os.path.join(img_dir, "p%d" % pno)
            os.makedirs(pdir, exist_ok=True)
            for name, url in pg.markdown_images.items():
                base = os.path.basename(name)
                dest = os.path.join(pdir, base)
                if download(url, dest):
                    n_img += 1
        meta.append({"p": pno, "md_len": len(pg.markdown_text), "n_img": n_img,
                     "t": round(time.time() - t0, 1)})
    with open(os.path.join(stage, "meta_batch_%d-%d.json" % (start, end)), "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=1)
    return start + len(result.pages) - 1, sum(m["n_img"] for m in meta)

async def main():
    global Model
    from paddleocr import AsyncPaddleOCRClient, Model as M, PaddleOCRVLOptions as POpts
    Model = M.PADDLE_OCR_VL
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    p1, p2 = int(args[0]), int(args[1])
    batch = int(args[2]) if len(args) > 2 else 15
    stage = None
    for i, a in enumerate(sys.argv[1:]):
        if a == "--stage" and i + 2 < len(sys.argv):
            stage = sys.argv[i + 2]
    stage = stage or r"d:\obsidian'srepository\my\_vlm\ocr_stage\liang_glt"
    os.makedirs(stage, exist_ok=True)

    opts = POpts(use_doc_orientation_classify=True, use_doc_unwarping=True,
                 use_layout_detection=True, use_ocr_for_image_block=True)
    async with AsyncPaddleOCRClient(token=TOKEN, request_timeout=300, poll_timeout=1800) as client:
        ranges = list(range(p1, p2 + 1, batch))
        for k, s in enumerate(ranges):
            e = min(s + batch - 1, p2)
            # 断点：该批末页 md 已存在 → 跳过
            done_md = os.path.join(stage, "pages", "p%d.md" % e)
            if os.path.exists(done_md):
                print("SKIP batch %d-%d (done)" % (s, e), flush=True)
                continue
            print("BATCH %d-%d/%d  (%d/%d) t=%s" % (s, e, p2, k + 1, len(ranges), time.strftime("%H:%M:%S")), flush=True)
            try:
                last, nimg = await run_batch(client, opts, s, e, stage)
                print("  ok -> p%d, imgs=%d, %.0fs" % (last, nimg, time.time()), flush=True)
            except Exception as ex:
                print("  FAIL %d-%d: %s" % (s, e, ex), flush=True)
                print("  retry once after 20s", flush=True)
                time.sleep(20)
                try:
                    last, nimg = await run_batch(client, opts, s, e, stage)
                    print("  retry ok -> p%d, imgs=%d" % (last, nimg), flush=True)
                except Exception as ex2:
                    print("  FAIL2 %d-%d: %s" % (s, e, ex2), flush=True)
    print("ALL DONE", flush=True)

if __name__ == "__main__":
    asyncio.run(main())