# -*- coding: utf-8 -*-
"""从 origin 一次性重拆分 6 本书（4本408 + 30讲高数 + 30讲线代）。
图片引用重写为指向 origin/imgs 的相对路径。
用法: python _resplit_6books.py --dry   # 输出到 _new/ 供对比
      python _resplit_6books.py --apply  # 覆盖拆分稿
"""
import io, sys, re, os, glob, shutil
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BASE = "11408"
ORIGIN = os.path.join(BASE, "origin")
SPLIT = os.path.join(BASE, "拆分稿")
NEW = "_new_拆分稿"

BOOKS = [
    dict(course="数据结构",        odir="2027数据结构",        out="数据结构",     body=514, kind="408"),
    dict(course="操作系统",        odir="2027操作系统",        out="操作系统",     body=436, kind="408"),
    dict(course="计算机组成原理",  odir="2027计算机组成原理",  out="计算机组成原理", body=435, kind="408"),
    dict(course="计算机网络",      odir="2027计算机网络",      out="计算机网络",   body=523, kind="408"),
    dict(course="30讲-高数",       odir="27张宇基础30讲（高数）", out=os.path.join("数学", "30讲-高数"), body=107, kind="math"),
    dict(course="30讲-线代",       odir="27张宇基础30讲线代",  out=os.path.join("数学", "30讲-线代"), body=288, kind="math"),
]

CH   = re.compile(r"^# 第(\d+)章\s*(.*)$")
SEC  = re.compile(r"^## (\d+)\.(\d+)\s+(.*)$")
EX   = re.compile(r"^###\s*([\d.]*)\s*(本节(?:试题|习题)精选)\s*$")
ANS  = re.compile(r"^###\s*([\d.]*)\s*(答案与解析)\s*$")
LEC  = re.compile(r"^#{1,2}\s*第(\d+)讲\s*(.*)$")
IMG  = re.compile(r'(<img\s+src=")([^"]+)(")')
FM   = re.compile(r"(?s)^\s*---\s*\n.*?\n---\s*\n")


def safe(s):
    """文件名安全化：去掉 Windows/文件系统非法字符"""
    return re.sub(r'[\\/:*?"<>|]', '', s)


def read_fm(path):
    c = open(path, encoding="utf-8").read()
    m = FM.match(c)
    return m.group(0) if m else ""


def rewrite_img(text, rel_prefix):
    def repl(m):
        src = m.group(2)
        if src.startswith("imgs/"):
            return m.group(1) + rel_prefix + src + m.group(3)
        if src == "imgs/img_x.jpg":  # 兜底
            return m.group(1) + rel_prefix + src + m.group(3)
        return m.group(0)
    return IMG.sub(repl, text)


def walk_split(book_out):
    """扫描现状拆分稿，返回 [(abs_path, rel_path)]，rel 相对书目录"""
    root = os.path.join(SPLIT, book_out)
    res = []
    for dirpath, _, files in os.walk(root):
        for f in sorted(files):
            if f.endswith(".md"):
                ap = os.path.join(dirpath, f)
                rp = os.path.relpath(ap, root)
                res.append((ap, rp))
    return res


# ---------- 408 ----------
def split_408(book):
    odir, out, body = book["odir"], book["out"], book["body"]
    src = os.path.join(ORIGIN, odir, odir + ".md")
    all_lines = open(src, encoding="utf-8").read().split("\n")
    lines = all_lines[find_body(all_lines):]
    files = walk_split(out)

    # 1) 用现状文件名建立 (章,节) 映射
    fm_map = {}   # rel_path -> frontmatter
    name_map = {} # (chapter, section) -> dict(考点=rel, 习题=rel)
    guide_map = {} # chapter -> 导读 rel
    for ap, rp in files:
        fm_map[rp] = read_fm(ap)
        base = os.path.basename(rp)
        m = re.match(r"(\d+)\.(\d+)-", base)
        if base.endswith("-导读.md"):
            m2 = re.match(r"(\d+)-", base)
            if m2: guide_map[int(m2.group(1))] = rp
        elif m:
            key = (int(m.group(1)), int(m.group(2)))
            name_map.setdefault(key, {})
            if "习题" in rp: name_map[key]["习题"] = rp
            else: name_map[key]["考点"] = rp

    # 2) 解析 origin 结构
    cur_ch = None; cur_sec = None
    chapters = {}   # ch -> {title_lines, guide:[], secs:[sec_no: {title_line, exam:[], body:[]}]}
    cur = None
    def new_chapter(n, raw):
        return {"no": n, "raw": raw, "guide": [], "secs": {}}
    def new_sec(no, raw):
        return {"no": no, "raw": raw, "body": [], "exam": [], "in_exam": False}
    for ln in lines:
        s = ln.strip()
        m = CH.match(s)
        if m:
            cur_ch = int(m.group(1))
            cur = new_chapter(cur_ch, ln)
            chapters[cur_ch] = cur
            cur_sec = None
            continue
        if cur is None:  # 正文起点之前的杂行（如封面残留）
            continue
        m = SEC.match(s)
        if m:
            n = (int(m.group(1)), int(m.group(2)))
            cur_sec = new_sec(n, ln)
            cur["secs"][n] = cur_sec
            continue
        if cur_sec is None:
            cur["guide"].append(ln)
            continue
        m = EX.match(s) or ANS.match(s)
        if m:
            cur_sec["in_exam"] = True
            cur_sec["exam"].append(ln)
            continue
        if cur_sec["in_exam"]:
            cur_sec["exam"].append(ln)
        else:
            cur_sec["body"].append(ln)

    # 3) 生成：导读在 <书>/<章>/（3级到11408），考点/习题在 <书>/<章>/考点|习题/（4级）
    depth_guide = "../" * 3 + "origin/" + odir + "/"
    depth_deep  = "../" * 4 + "origin/" + odir + "/"
    outdir = os.path.join(NEW if DRY else SPLIT, out)
    if os.path.exists(outdir) and not DRY:
        shutil.rmtree(outdir)
    n_guide = n_kao = n_ex = 0
    for ch_no in sorted(chapters):
        ch = chapters[ch_no]
        # 章名（去掉"第N章"前缀和多余空格）
        cm = re.match(r"^#\s*第\d+章\s+(.+)$", ch["raw"].strip())
        ch_name = safe(cm.group(1).strip()) if cm else f"第{ch_no}章"
        ch_dir = f"{ch_no}-{ch_name}"
        # 导读
        g_rp = guide_map.get(ch_no) or os.path.join(ch_dir, f"{ch_no:02d}-{ch_name}-导读.md")
        content = fm_map.get(g_rp, "") + "\n".join([ch["raw"]] + ch["guide"]) + "\n"
        content = rewrite_img(content, depth_guide)
        write_to(outdir, g_rp, content)
        n_guide += 1
        # 节
        for (a, b) in sorted(ch["secs"].keys()):
            sec = ch["secs"][(a, b)]
            sm = re.match(r"^##\s*\d+\.\d+\s+(.+)$", sec["raw"].strip())
            sec_title = safe(sm.group(1).strip()) if sm else f"{a}.{b}"
            k_rp = name_map.get((a, b), {}).get("考点") or os.path.join(ch_dir, "考点", f"{a}.{b}-{sec_title}.md")
            e_rp = name_map.get((a, b), {}).get("习题") or os.path.join(ch_dir, "习题", f"{a}.{b}-本节习题与解析.md")
            body_txt = "\n".join([sec["raw"]] + sec["body"])
            exam_txt = "\n".join(sec["exam"])
            content = fm_map.get(k_rp, "") + body_txt + ("\n" if body_txt else "")
            content = rewrite_img(content, depth_deep)
            write_to(outdir, k_rp, content)
            n_kao += 1
            if exam_txt.strip():
                # 题区/答案区：原行透传（origin 已含 ### 本节习题精选 / ### 答案与解析）
                content = fm_map.get(e_rp, "") + exam_txt + "\n"
                content = rewrite_img(content, depth_deep)
                write_to(outdir, e_rp, content)
                n_ex += 1
    print(f"  {book['course']}: 导读{n_guide} 考点{n_kao} 习题{n_ex}")

    # 4) 校验覆盖：现状有但新生成没有的文件
    old = set(files)
    if DRY:
        return
    newset = set()
    for dirpath, _, fs in os.walk(outdir):
        newset.update(os.path.relpath(os.path.join(dirpath, f), outdir) for f in fs if f.endswith(".md"))
    missing = [rp for _, rp in old if rp not in newset]
    if missing:
        print(f"  ⚠ 未生成(现状有): {missing[:5]}")


# ---------- 数学 ----------
BODY_PAT = re.compile(r"^# 第\d+章|^#{1,2}\s*第\d+讲|^# 基础篇")

def find_body(lines):
    for i, l in enumerate(lines):
        if BODY_PAT.match(l.strip()):
            return i
    return 0


def split_math(book):
    odir, out, body = book["odir"], book["out"], book["body"]
    src = os.path.join(ORIGIN, odir, odir + ".md")
    all_lines = open(src, encoding="utf-8").read().split("\n")
    b = find_body(all_lines)
    lines = all_lines[b:]
    files = walk_split(out)
    fm_map = {rp: read_fm(ap) for ap, rp in files}

    # 讲边界
    bounds = []  # (no, idx, line)
    for i, l in enumerate(lines):
        m = LEC.match(l.strip())
        if m:
            bounds.append((int(m.group(1)), i, l))
    outdir = os.path.join(NEW if DRY else SPLIT, out)
    if os.path.exists(outdir) and not DRY:
        shutil.rmtree(outdir)
    depth = "../" * 3 + "origin/" + odir + "/"
    n = 0
    for k, (no, i, l) in enumerate(bounds):
        end = bounds[k + 1][1] if k + 1 < len(bounds) else len(lines)
        seg = lines[i:end]
        # 匹配现状文件名；无则用默认名（第N讲-讲名.md）
        rp = None
        for r in fm_map:
            if re.match(r"第%d讲-" % no, os.path.basename(r)):
                rp = r; break
        if rp is None:
            # 讲名：讲标题后第一个裸文本行
            title = ""
            for j in range(i + 1, min(i + 4, len(seg))):
                s = seg[j].strip()
                if s and not s.startswith("<") and not s.startswith("#") and len(s) < 30:
                    title = s
                    break
            rp = f"第{no}讲" + (f"-{safe(title)}" if title else "") + ".md"
            fm = (f"---\ntype: 讲\ncourse: 数学\nbook: {book['course']}\nlecture: {no}\n"
                  f"tags:\n  - 考研数学\nlecture_title: 第{no}讲 {safe(title)}\n---\n\n")
        else:
            fm = fm_map[rp]
        content = fm + "\n".join(seg) + "\n"
        content = rewrite_img(content, depth)
        write_to(outdir, rp, content)
        n += 1
    print(f"  {book['course']}: 讲文件 {n}/{len(bounds)}")


def write_to(outdir, rel, content):
    p = os.path.join(outdir, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    # 清理尾部多余空行
    content = content.rstrip("\n") + "\n"
    open(p, "w", encoding="utf-8").write(content)


DRY = "--dry" in sys.argv
assert "--apply" in sys.argv or DRY, "需要 --dry 或 --apply"

if os.path.exists(NEW):
    shutil.rmtree(NEW)
for b in BOOKS:
    if b["kind"] == "408":
        split_408(b)
    else:
        split_math(b)
print("完成。", "输出在 _new_拆分稿/（对比用）" if DRY else "已覆盖拆分稿/")
