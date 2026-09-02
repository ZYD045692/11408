# -*- coding: utf-8 -*-
"""测试：高数 PDF 页眉条是否含"第N讲"——Umi-OCR 识别顶部条。"""
import os, sys, io, json, base64, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import fitz
import requests

Umi = "http://127.0.0.1:1224/api/ocr"

def ocr_img(png_bytes):
    r = requests.post(Umi, json={"base64": base64.b64encode(png_bytes).decode(), "options": {}}, timeout=60)
    j = r.json()
    if j.get("code") != 100:
        return f"<ERR {j.get('code')}>"
    return " ".join(x.get("text", "") for x in j.get("data", []))

doc = fitz.open("11408/pdf/27张宇基础30讲（高数）.pdf")
for pno in [10, 30, 60, 100, 200, 300, 400, 500]:
    pg = doc[pno]
    r = pg.rect
    clip = fitz.Rect(r.x0, r.y0, r.x1, r.y0 + r.height * 0.12)   # 顶部12%
    pix = pg.get_pixmap(dpi=110, clip=clip)
    t0 = time.time()
    txt = ocr_img(pix.tobytes("png"))
    print(f"p{pno+1} 顶条 ({time.time()-t0:.1f}s): {txt[:80]}")
doc.close()
