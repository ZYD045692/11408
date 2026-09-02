# -*- coding: utf-8 -*-
"""逐页精确计算页码位置（tesseract）+ 覆盖率报告。
用法: python _calc_pageno_pos.py [p1] [p2]  （默认 10~128 基础篇）
输出: 每页 预期书页码 / tesseract 定位页码 & top y / root /. 无页码页标注。
"""
import subprocess, os, tempfile, io, sys
import fitz
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
from PIL import Image

TESS = r"C:\Users\Surperman\scoop\apps\tesseract\current\tesseract.exe"
TD = r"C:\Users\Surperman\scoop\persist\tesseract\tessdata"
PDF = r"d:\obsidian'srepository\my\11408\pdf\数学\27李良概统辅导-基础&强化.pdf"
NO_PAGENO = {10, 30, 51, 77, 96, 101, 116, 128, 129, 139, 144, 163, 191, 213, 219, 233}

def locate_pageno(p0, rs=2.0):
    """返回 (页码数字, top_y_frac, height_px) 或 None。已验证配置：psm11 + 全宽 + y55%~99%。"""
    doc = fitz.open(PDF)
    pix = doc[p0].get_pixmap(matrix=fitz.Matrix(rs, rs))
    doc.close()
    img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
    H = img.height
    # 全宽、y 80%~99%：页码以孤立数字串出现在底部
    band = img.crop((0, int(H*0.80), img.width, int(H*0.99)))
    tmp = os.path.join(tempfile.gettempdir(), "tess_pn.png")
    band.save(tmp)
    r = subprocess.run([TESS, tmp, "stdout", "--tessdata-dir", TD, "-l", "chi_sim", "--psm", "11", "tsv"],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    best = None   # (text, top_frac, height_px, x_center_frac, conf)
    ybase = int(H*0.80)
    for ln in r.stdout.split("\n")[1:]:
        c = ln.split("\t")
        if len(c) < 12: continue
        text = c[11].strip()
        try: conf = float(c[10])
        except: continue
        if not text.isdigit(): continue
        if len(text) not in (2, 3): continue          # 页码 2-3 位
        x, y, w, h = int(c[6]), int(c[7]), int(c[8]), int(c[9])
        abs_y = ybase + y
        top_frac = abs_y / H
        xc = (x + w/2) / img.width
        if not (0.90 <= top_frac <= 0.985): continue  # 页码应在 90%-98.5%
        if not (0.55 <= xc <= 0.97): continue         # 右下/中右
        if best is None or (conf, len(text)) > (best[4], len(best[0])):
            best = (text, round(top_frac,4), h, round(xc,2), conf)
    if best is None:
        return None
    return (best[0], best[1], best[2])

def main():
    p1 = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    p2 = int(sys.argv[2]) if len(sys.argv) > 2 else 127
    ok, no, mis = [], [], []
    for p0 in range(p1-1, p2):
        pno = p0 + 1
        src = locate_pageno(p0)
        if pno in NO_PAGENO:
            st = "无页码页"
            if src:
                st += " 但识别到 %r@%.1f%%" % (src[0], src[1]*100)
                mis.append((pno, st))
            else:
                no.append(pno)
        else:
            book_no = p0 - 6   # p10(1-based)=书003 -> PDF页 = 书页码+7, 0-based p0 -> book = p0+1-7 = p0-6
            exp = "%03d" % book_no
            if src and src[0] == exp:
                ok.append((pno, src[1]*100))
            else:
                mis.append((pno, "识别到 %r (预期%s)@%.1f%%" % (src and src[0], exp, src and src[1]*100) if src else "未识别到(预期%s)" % exp))
    print("基础篇 %d~%d:" % (p1, p2))
    print("  页码匹配 %d 页, 无页码页 %d 页, 异常 %d 页" % (len(ok), len(no), len(mis)))
    print("  页码top_y分布:", sorted(set(round(y,2) for _, y in ok)))
    print("  异常页:", mis[:12])
    print("  前10页:", ok[:10])

if __name__ == "__main__":
    main()