# -*- coding: utf-8 -*-
"""数学 PDF 页眉索引：Umi-OCR 识别每页顶部 12% 条，提取"第N讲/第N章"，建 讲/章→页范围 索引。
输出 _vlm/pages/ocr_index/<book>.jsonl（每页一行，断点续跑）。
用法: python _vlm_math_index.py [书名...]（缺省全部三本）"""
import os, re, sys, io, json, base64, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fitz
import requests
import _vlm_lib as V

UMI = "http://127.0.0.1:1224/api/ocr"
MATH_PDFS = {
    "30讲-高数": "11408/pdf/27张宇基础30讲（高数）.pdf",
    "30讲-线代": "11408/pdf/27张宇基础30讲线代.pdf",
    "1000题-解析册": "11408/pdf/27张宇1000题数一【解析册】.pdf",
}
IDX_DIR = os.path.join(V.VLM, "pages", "ocr_index")
os.makedirs(IDX_DIR, exist_ok=True)

PAT = re.compile(r"第\s*(\d{1,2})\s*([讲章])")

def ocr_strip(png_bytes):
    try:
        r = requests.post(UMI, json={"base64": base64.b64encode(png_bytes).decode(), "options": {}}, timeout=60)
        j = r.json()
        if j.get("code") != 100:
            return ""
        return " ".join(x.get("text", "") for x in j.get("data", []))
    except Exception:
        return ""

def run(books):
    for book in books:
        pdf = os.path.join(V.ROOT, MATH_PDFS[book])
        out_path = os.path.join(IDX_DIR, f"{book}.jsonl")
        done = V.load_done(out_path, "page")
        doc = fitz.open(pdf)
        n_pages = doc.page_count
        n_new = 0
        t0 = time.time()
        for pno in range(n_pages):
            if str(pno) in done:
                continue
            pg = doc[pno]
            r = pg.rect
            clip = fitz.Rect(r.x0, r.y0, r.x1, r.y0 + r.height * 0.12)
            pix = pg.get_pixmap(dpi=110, clip=clip)
            txt = ocr_strip(pix.tobytes("png"))
            m = PAT.search(txt)
            row = {"page": pno, "head": txt[:120]}
            if m:
                row["unit"], row["kind"] = int(m.group(1)), m.group(2)
            V.append_jsonl(out_path, row)
            n_new += 1
            if n_new % 50 == 0:
                V.log(f"[mathidx] {book}: {n_new} 页 ({(time.time()-t0)/n_new:.2f}s/页)")
        doc.close()
        V.log(f"[mathidx] {book}: 完成 新增{n_new} 页, 共{n_pages}页, 耗时{time.time()-t0:.0f}s")

def summarize(book):
    """读索引，打印 讲/章 → 页范围。"""
    rows = [json.loads(l) for l in open(os.path.join(IDX_DIR, f"{book}.jsonl"), encoding="utf-8")]
    units = {}
    for r in rows:
        if "unit" in r:
            units.setdefault((r["kind"], r["unit"]), []).append(r["page"])
    for (kind, u), pages in sorted(units.items(), key=lambda x: (x[0][1])):
        print(f"  第{u}{kind}: p{min(pages)+1}~p{max(pages)+1} ({len(pages)}页命中)")

if __name__ == "__main__":
    books = sys.argv[1:] or list(MATH_PDFS)
    if "--summary" in sys.argv:
        for b in books:
            if b.startswith("--"):
                continue
            print(f"== {b} ==")
            summarize(b)
    else:
        run([b for b in books if not b.startswith("--")])
