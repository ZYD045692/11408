# -*- coding: utf-8 -*-
"""1000题 拆分脚本（分篇 → 分科 → 章），从清洗后的 origin 一次生成拆分稿。
结构: 拆分稿/数学/1000题-试题册/{基础篇,强化篇,综合篇}/{高数,线代,概率}/第N章 章名.md
用法: python _split_1000.py [--apply]   # 默认 --dry 输出到 _new_拆分稿/
"""
import io, sys, os, re, shutil
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BASE = "11408"
ORIGIN = os.path.join(BASE, "origin")
SPLIT = os.path.join(BASE, "拆分稿")
NEW = "_new_拆分稿"

BOOKS = [
    dict(book="1000题-试题册", odir="27张宇1000题数一【试题册】"),
    dict(book="1000题-解析册", odir="27张宇1000题数一【解析册】"),
]

PIAN = re.compile(r"^# (基础篇|强化篇|综合篇)\s*$")
SUBJ = re.compile(r"^## (高数|线代|概率论)\s*$")
ZHANG = re.compile(r"^#{2,3} 第(\d+)章\s+(.+)$")
LING = re.compile(r"^#{2,3} 零\s*基础.*$")
TEST = re.compile(r"^## (测试卷[一二三四])\s*$")

SUBJ_DIR = {"高数": "高数", "线代": "线代", "概率论": "概率"}
IMG = re.compile(r'(<img\s+src=")([^"]+)(")')

XIANDAI = ["行列式", "余子式", "矩阵", "向量组", "线性方程组", "特征值", "相似", "二次型"]
GAILV = ["随机事件", "随机变量", "数字特征", "大数定律", "数理统计", "统计量", "参数估计"]

def subject_of(title):
    if any(k in title for k in GAILV):
        return "概率"
    if any(k in title for k in XIANDAI):
        return "线代"
    return "高数"

def rewrite_img(text, rel):
    def repl(m):
        src = m.group(2)
        return m.group(1) + rel + src + m.group(3) if src.startswith("imgs/") else m.group(0)
    return IMG.sub(repl, text)

def main(book):
    b, odir = book["book"], book["odir"]
    src = os.path.join(ORIGIN, odir, odir + ".md")
    lines = open(src, encoding="utf-8").read().split("\n")
    outroot = os.path.join(NEW if DRY else SPLIT, "数学", b)
    if os.path.exists(outroot) and not DRY:
        shutil.rmtree(outroot)

    cur_pian = None       # 基础篇/强化篇/综合篇
    cur_subject = None    # 高数/线代/概率
    cur_zhang = None      # (chapter_no, title, lines[])
    files = []            # (relpath, content)
    zhang_list = []       # (pian, subject, no, title)

    def flush():
        nonlocal cur_zhang
        if cur_zhang is None:
            return
        no, title, seg = cur_zhang
        if title.startswith("零"):
            name = "零基础摸底.md"
        elif title.startswith("测试卷"):
            name = f"{title}.md"
        else:
            name = f"第{no}章 {title}.md"
        sub = SUBJ_DIR.get(cur_subject) if cur_subject else subject_of(title)
        if cur_pian == "综合篇":
            rel = os.path.join("综合篇", name)
        else:
            rel = os.path.join(cur_pian, sub, name)
        files.append((rel, "\n".join(seg)))
        zhang_list.append((cur_pian, sub, no, title))
        cur_zhang = None

    for raw in lines:
        s = raw.strip()
        m = PIAN.match(s)
        if m:
            flush()
            cur_pian = m.group(1)
            cur_subject = None
            continue
        if cur_pian is None:
            continue
        m = SUBJ.match(s)
        if m:
            flush()
            cur_subject = m.group(1)
            continue
        m = ZHANG.match(s)
        if m:
            flush()
            cur_zhang = [int(m.group(1)), m.group(2).strip(), [raw]]
            continue
        m = LING.match(s)
        if m:
            flush()
            cur_zhang = [0, "零 基础", [raw]]
            continue
        m = TEST.match(s)
        if m:
            flush()
            cur_zhang = [0, m.group(1), [raw]]
            continue
        if cur_zhang is not None:
            cur_zhang[2].append(raw)
    flush()

    # 写文件
    depth_pian = "../" * 3          # 数学/1000题-x/基础篇/高数/ → 3级到 origin? 算: 文件在 拆分稿/数学/1000题-x/基础篇/高数/x.md
    # 深度：数学(1) 1000题-x(2) 基础篇(3) 高数(4) → 到 拆分稿/ 需要 4 级 → 到 11408 需要 5 级? 不对:
    # 拆分稿/数学/1000题-x/基础篇/高数/x.md: .. = 基础篇, ../.. = 1000题-x, ../../.. = 数学, ../../../.. = 拆分稿, ../../../../.. = 11408
    depth_pian = "../" * 5
    depth_zong = "../" * 4          # 综合篇: 拆分稿/数学/1000题-x/综合篇/x.md → 4级到11408
    for rel, content in files:
        if rel.startswith("综合篇"):
            content = rewrite_img(content, depth_zong + "origin/" + odir + "/")
        else:
            content = rewrite_img(content, depth_pian + "origin/" + odir + "/")
        parts = rel.split(os.sep)
        subj = parts[1] if len(parts) > 1 and parts[0] != "综合篇" else ""
        fm = (f"---\ntype: 习题\ncourse: 数学\nbook: {b}\n"
              f"pian: {parts[0]}\n"
              + (f"subject: {subj}\n" if subj else "")
              + "tags:\n  - 考研数学\n  - 1000题\n"
              + ("  - 解析册\n" if b == "解析册" else "  - 试题册\n")
              + f"chapter_title: {os.path.basename(rel)[:-3]}\n---\n\n")
        p = os.path.join(outroot, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, "w", encoding="utf-8").write(fm + content.rstrip("\n") + "\n")

    # 报告结构
    import collections
    cnt = collections.Counter((p, s) for p, s, n, t in zhang_list)
    for k in sorted(cnt):
        print(f"  {k[0]}/{k[1]}: {cnt[k]} 章")
    print(f"  共 {len(files)} 个文件")

DRY = "--apply" not in sys.argv
if os.path.exists(NEW):
    shutil.rmtree(NEW)
for b in BOOKS:
    print(f"===== {b['book']} =====")
    main(b)
print("完成。", "输出在 _new_拆分稿/（对比用）" if DRY else "已覆盖拆分稿/")
