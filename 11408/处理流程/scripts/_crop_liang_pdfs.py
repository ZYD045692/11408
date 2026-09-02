# -*- coding: utf-8 -*-
"""李良概统 PDF 页眉页脚裁剪 + 按 基础/强化→章节 分目录存 PDF。

用法:
  python _crop_liang_pdfs.py --book 基础 --ch 第一章 --pages 10-29 [--out 目录]
  python _crop_liang_pdfs.py --all --book 基础   # 生成基础篇（--book 可留空=全部）

裁剪规则：
- 页眉：有页眉页裁掉顶部 7%（页眉条下沿）；章首页（NO_HEADER_PAGES）不裁顶部。
- 页脚：逐页用 tesseract 定位页码数字带的 top_y（右下区域），裁剪线 = 页码 top - 上偏移量；
  无页码页/定位失败页用固定 93% 兜底。正文/图表延伸到底的页由保护逻辑保留。
- 输出：<out>/基础/第N章.pdf（每章一个 PDF）
"""
import argparse, io, os, subprocess, sys, tempfile
import fitz
from PIL import Image

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

PDF = r"d:\obsidian'srepository\my\11408\pdf\数学\27李良概统辅导-基础&强化.pdf"

TESS = r"C:\Users\Surperman\scoop\apps\tesseract\current\tesseract.exe"
TESSDATA = r"C:\Users\Surperman\scoop\persist\tesseract\tessdata"

# 侦察确认：无页眉页（章首页 + 强化题型起始页）
NO_HEADER_PAGES = {10, 30, 51, 77, 96, 101, 116, 128, 129, 139, 144, 163, 191, 213, 219, 233}

# 章起始页（PDF 1-based），强化篇边界为暂估，跑 --all 前需校准
BASIC_CHS = [("第一章", 10, 29), ("第二章", 30, 50), ("第三章", 51, 76),
             ("第四章", 77, 95), ("第五章", 96, 100), ("第六章", 101, 115),
             ("第七章", 116, 127)]
STRONG_CHS = [("第一章", 129, 143), ("第二章", 144, 162), ("第三章", 163, 190),
              ("第四章", 191, 212), ("第五章", 213, 218), ("第六章", 219, 232),
              ("第七章", 233, 247)]

HEADER_CUT_FRAC = 0.075     # 有页眉页：裁掉顶部 7.5%（页眉条下沿 + 余量）
FOOTER_FALLBACK = 0.93      # 无页码页/定位失败页的底部兜底裁剪线
FOOTER_GAP = 0.003          # 页码 top 上方的安全间隙（页面高度比例，每页精确值，绝不扩大）
RENDER_S = 1.5              # 渲染/裁剪尺寸倍率

# ---------- 页码定位（tesseract） ----------
def locate_pageno_top(doc, p0, rs=2.0):
    """定位页码数字带顶部。返回 (top_frac, 页码文本) 或 (None, 页码文本)。
    书本排版：偶数页页码右下 (x≥55%)、奇数页页码左下 (x≤50%)，y 80%~99%。
    两区各扫一次，取 y 更深（更靠下）的纯数字块为页码。"""
    page = doc[p0]
    pix = page.get_pixmap(matrix=fitz.Matrix(rs, rs))
    img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
    W, H = img.size
    # 右侧区 (x 55%~100%) 与 左侧区 (x 0%~50%)，均 y 85%~99%（聚焦页码带，避免大图漏检）
    regions = [(int(W*0.55), int(H*0.85), "right"),
               (0, int(H*0.85), "left")]
    best = None   # (text, top_frac, xc_abs, conf)
    for X0, Y0, _side in regions:
        band = img.crop((X0, Y0, W if X0 else int(W*0.50), int(H*0.99)))
        tmp = os.path.join(tempfile.gettempdir(), "tess_pn.png")
        band.save(tmp)
        r = subprocess.run([TESS, tmp, "stdout", "--tessdata-dir", TESSDATA,
                            "-l", "chi_sim", "--psm", "11", "tsv"],
                           capture_output=True, text=True, encoding="utf-8", errors="replace")
        for ln in r.stdout.split("\n")[1:]:
            c = ln.split("\t")
            if len(c) < 12: continue
            text = c[11].strip()
            try: conf = float(c[10])
            except: continue
            if not text.isdigit() or len(text) not in (2, 3): continue
            x, y, w = int(c[6]), int(c[7]), int(c[8])
            abs_top = Y0 + y                     # band 内 y + band 起点 → 全页
            top_frac = abs_top / H
            xc_abs = (X0 + x + w/2) / W          # band 内 x + band 起点 → 全页
            if not (0.90 <= top_frac <= 0.985): continue
            if best is None or (conf, len(text)) > (best[3], len(best[0])):
                best = (text, round(top_frac, 4), round(xc_abs, 3), conf)
    if best is None:
        return None, ""
    return best[1], best[0]

def crop_page(doc, p0, render_scale=RENDER_S):
    """p0: 0-based 页码。返回 (裁剪后 PIL Image, (top_frac, bottom_frac))。

    ✨ 高清版：优先取原 PDF 内嵌整页图（~4183px，300dpi 扫描原分辨率），
    按比例裁掉页眉页脚，不重新渲染——保证分章 PDF 与原始扫描逐像素一致。
    """
    # 取内嵌整页图（若存在）
    imgs = doc[p0].get_images(full=True)
    if imgs:
        info = doc.extract_image(imgs[0][0])
        img = Image.open(io.BytesIO(info["image"])).convert("RGB")
    else:
        pix = doc[p0].get_pixmap(matrix=fitz.Matrix(3.0, 3.0))
        img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
    W, H = img.size

    # ---- 顶部 ----
    if (p0 + 1) in NO_HEADER_PAGES:
        top_frac = 4 / H                        # 章首页：仅安全余量
    else:
        top_frac = HEADER_CUT_FRAC              # 页眉条下沿 + 余量（比例）

    # ---- 底部 ----
    bottom_frac = FOOTER_FALLBACK
    pn_top, _ = locate_pageno_top(doc, p0)
    if pn_top is not None:
        cand = pn_top - FOOTER_GAP
        if 0.895 <= cand <= 0.985:
            bottom_frac = cand

    top_cut = max(0, int(H * top_frac) - 2)
    bottom_cut = min(H, int(H * bottom_frac) + 2)
    if bottom_cut - top_cut < int(H * 0.35):
        top_cut, bottom_cut = 0, H
    return img.crop((0, top_cut, W, bottom_cut)), (top_cut / H, bottom_cut / H)


def build_chapter_pdf(out_path, p_start, p_end):
    doc = fitz.open(PDF)
    imgs = []
    fracs_log = []
    for p in range(p_start - 1, p_end):
        img, fracs = crop_page(doc, p)
        imgs.append(img)
        fracs_log.append((p + 1, fracs))
    pdf = fitz.open()
    for i, im in enumerate(imgs):
        tmp = os.path.join(os.path.dirname(out_path), f"._tmp_{i:02d}.jpg")
        im.save(tmp, quality=94)                # JPEG 高质；原图本就是 jpg
        rect = fitz.Rect(0, 0, im.width / 300 * 72, im.height / 300 * 72)   # 300dpi 尺寸
        page = pdf.new_page(width=rect.width, height=rect.height)
        page.insert_image(rect, filename=tmp)
        os.remove(tmp)
    pdf.save(out_path)
    pdf.close()
    doc.close()
    head = [f"p{p}:({t[0]:.2f},{t[1]:.2f})" for p, t in fracs_log[:6]]
    tail = [f"p{p}:({t[0]:.2f},{t[1]:.2f})" for p, t in fracs_log[-4:]]
    print("  ->", out_path, "pages", len(imgs), "| 裁剪比:", head, "…", tail)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--book", choices=["基础", "强化"], default=None)
    ap.add_argument("--ch", default=None)
    ap.add_argument("--pages", default=None)
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--out", default=r"d:\obsidian'srepository\my\11408\裁剪pdf\27李良概统-分章")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    if a.all:
        books = [("基础", BASIC_CHS), ("强化", STRONG_CHS)]
        # --book 无参（默认空）或等于某本时过滤；--all 不带 --book 则跑两本
        if a.book:
            books = [b for b in books if b[0] == a.book]
        for book, chs in books:
            for name, s, e in chs:
                od = os.path.join(a.out, book)
                os.makedirs(od, exist_ok=True)
                build_chapter_pdf(os.path.join(od, name + ".pdf"), s, e)
    else:
        assert a.pages, "需要 --pages"
        assert a.book, "单章模式需要 --book 基础|强化"
        s, e = map(int, a.pages.split("-"))
        od = os.path.join(a.out, a.book)
        os.makedirs(od, exist_ok=True)
        build_chapter_pdf(os.path.join(od, a.ch + ".pdf"), s, e)

if __name__ == "__main__":
    main()