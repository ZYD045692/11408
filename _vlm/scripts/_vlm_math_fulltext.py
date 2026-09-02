# -*- coding: utf-8 -*-
"""数学 PDF 全页 OCR 全文索引（Umi-OCR 本地，http://127.0.0.1:1224）。
输出 _vlm/pages/ocr_full/<book>.jsonl（每页一行 {page, text}，断点续跑）。
用法: python _vlm_math_fulltext.py [书名...]"""
import os, sys, io, json, base64, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fitz
import requests
import _vlm_lib as V

UMI = "http://127.0.0.1:1224/api/ocr"
MATH_PDFS = {
    "30讲-高数": "11408/pdf/27张宇基础30讲（高数）.pdf",
    "30讲-线代": "11408/pdf/27张宇基础30讲线代.pdf",
    "1000题-试题册": "11408/pdf/27张宇1000题数一【试题册】.pdf",
    "1000题-解析册": "11408/pdf/27张宇1000题数一【解析册】.pdf",
}
OUT_DIR = os.path.join(V.VLM, "pages", "ocr_full")
os.makedirs(OUT_DIR, exist_ok=True)

def ocr_page(png_bytes, retries=3):
    for i in range(retries):
        try:
            r = requests.post(UMI, json={"base64": base64.b64encode(png_bytes).decode(), "options": {}}, timeout=90)
            j = r.json()
            if j.get("code") == 100:
                return "\n".join(x.get("text", "") for x in j.get("data", []))
        except Exception:
            pass
        time.sleep(2 * (i + 1))
    return ""

def run(books):
    for book in books:
        pdf = os.path.join(V.ROOT, MATH_PDFS[book])
        out_path = os.path.join(OUT_DIR, f"{book}.jsonl")
        done = V.load_done(out_path, "page")
        doc = fitz.open(pdf)
        n_pages = doc.page_count
        n_new = 0
        t0 = time.time()
        for pno in range(n_pages):
            if str(pno) in done:
                continue
            pix = doc[pno].get_pixmap(dpi=110)
            txt = ocr_page(pix.tobytes("png"))
            V.append_jsonl(out_path, {"page": pno, "text": txt})
            n_new += 1
            if n_new % 25 == 0:
                V.log(f"[ocrfull] {book}: {n_new} 页 ({(time.time()-t0)/n_new:.2f}s/页, 共{n_pages})")
        doc.close()
        V.log(f"[ocrfull] {book}: 完成 新增{n_new}, 共{n_pages}页")

if __name__ == "__main__":
    run(sys.argv[1:] or list(MATH_PDFS))
