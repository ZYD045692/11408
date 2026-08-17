# -*- coding: utf-8 -*-
"""6 本书内容完整性校验：字数对比 + 图片对比。自动定位正文起点（跳过文件头部的快速跳转目录）。"""
import io, sys, re, os, glob
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BASE = "11408/拆分稿"
ORIGIN = "11408/origin"
KEYS = {"数据结构": "2027数据结构", "操作系统": "2027操作系统",
        "计算机组成原理": "2027计算机组成原理", "计算机网络": "2027计算机网络",
        "30讲-高数": "27张宇基础30讲（高数）", "30讲-线代": "27张宇基础30讲线代"}
BOOKS = ["数据结构", "操作系统", "计算机组成原理", "计算机网络",
         "30讲-高数", "30讲-线代"]

IMG_DIV = re.compile(r"<(img|/div|div|table|/table|tr|/tr|td|/td)[^>]*>", re.I)
FN_SUP = re.compile(r"\$\^\{[^}]*\}\$")
BODY_PAT = re.compile(r"^# 第\d+章|^#{1,2}\s*第\d+讲|^# 基础篇")


def find_body(lines):
    for i, l in enumerate(lines):
        if BODY_PAT.match(l.strip()):
            return i + 1
    return 1


def clean_text(content):
    if content.lstrip().startswith("---"):
        m = re.match(r"(?s)^\s*---\s*\n.*?\n---\s*\n", content)
        if m:
            content = content[m.end():]
    chunks = []
    skip_toc = False
    for raw in content.split("\n"):
        s = raw.strip()
        if not s:
            continue
        if s == "## 📑 快速跳转":
            skip_toc = True
            continue
        if skip_toc:
            if s == "---":
                skip_toc = False
            continue
        if s.startswith("#"):
            continue
        if IMG_DIV.match(s):
            continue
        if s in ("视频讲解",) or s.startswith("【考纲") or s.startswith("【知识框架") or s.startswith("【复习提示"):
            continue
        s = FN_SUP.sub("", s)
        s = re.sub(r"<[^>]+>", "", s)
        s = s.replace("　", "").replace(" ", "").replace("\t", "")
        if s:
            chunks.append(s)
    return "".join(chunks)


def count_file(path):
    c = open(path, encoding="utf-8").read()
    return len(clean_text(c)), len(c)


for book in BOOKS:
    key = KEYS[book]
    origin_file = glob.glob(os.path.join(ORIGIN, f"*{key}*", "*.md"))[0]
    lines = open(origin_file, encoding="utf-8").read().split("\n")
    start = find_body(lines)
    o_txt = "\n".join(lines[start - 1:])
    o_clean = len(clean_text(o_txt))

    if book.startswith("30讲"):
        md_files = glob.glob(os.path.join(BASE, "数学", book, "*.md"))
        sub = "讲"
    else:
        md_files = glob.glob(os.path.join(BASE, book, "**", "*.md"), recursive=True)
        sub = "章"

    total_clean = 0
    for f in md_files:
        c, _ = count_file(f)
        total_clean += c
    ratio = total_clean / o_clean * 100 if o_clean else 0

    o_imgs = set(re.findall(r"imgs/(img_\d+\.\w+)", o_txt))
    s_all = "".join(open(f, encoding="utf-8").read() for f in md_files)
    s_imgs = set(re.findall(r"imgs/(img_\d+\.\w+)", s_all))
    miss = o_imgs - s_imgs

    verdict = "✅" if ratio >= 97 and not miss else ("⚠️" if ratio >= 90 else "❌")
    print(f"{verdict} {book}: 完整度 {ratio:6.2f}% | 正文图 {len(o_imgs)}/{len(s_imgs)} | 缺 {len(miss)}")
    if miss:
        print(f"     缺图: {sorted(miss)[:8]}")
