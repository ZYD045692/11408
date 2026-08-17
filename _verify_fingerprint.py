# -*- coding: utf-8 -*-
"""6 本书行指纹精确验证：多提取(拆分稿有origin无) + 少提取(origin有拆分稿无)。"""
import io, sys, re, os, glob
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BASE = "11408/拆分稿"
ORIGIN = "11408/origin"
KEYS = {"数据结构": "2027数据结构", "操作系统": "2027操作系统",
        "计算机组成原理": "2027计算机组成原理", "计算机网络": "2027计算机网络",
        "30讲-高数": "27张宇基础30讲（高数）", "30讲-线代": "27张宇基础30讲线代"}
BOOKS = ["数据结构", "操作系统", "计算机组成原理", "计算机网络",
         "30讲-高数", "30讲-线代"]
BODY_START = {}  # 自动定位，不再硬编码
BODY_PAT = re.compile(r"^# 第\d+章|^#{1,2}\s*第\d+讲|^# 基础篇")


def find_body(lines):
    for i, l in enumerate(lines):
        if BODY_PAT.match(l.strip()):
            return i + 1
    return 1


NOISE = re.compile(r"配套课程|配套煤压|联系微信|公众号|考研数学题源探析经典1000题|"
                   r"4\.9元包邮|5分钱|服务自年度|张宇\s*_+|^\.{4,}\d+$|^第\d+章.*\d{2,3}$|^目录$|^视频讲解$")


def normalize(line):
    s = line.strip()
    s = re.sub(r"<[^>]+>", "", s)
    s = re.sub(r"^#+\s*", "", s)
    s = re.sub(r"\$", "", s)
    s = re.sub(r"\s+", "", s)
    s = re.sub(r"[，。、；：？！（）【】《》「」『』·—…“”‘’\"'`~!@#%&,.;:?()\[\]{}\\\|/]", "", s)
    return s


def split_fm(content):
    m = re.match(r"(?s)^\s*---\s*\n.*?\n---\s*\n", content)
    return content[m.end():] if m else content


def body_fps(path):
    content = split_fm(open(path, encoding="utf-8").read())
    out = []
    for l in content.split("\n"):
        s = l.strip()
        if not s or s.startswith("---"):
            continue
        if re.match(r"^#+\s", s):
            continue
        fp = normalize(s)
        if fp and len(fp) >= 3:
            out.append(fp)
    return out


for book in BOOKS:
    key = KEYS[book]
    origin_file = glob.glob(os.path.join(ORIGIN, f"*{key}*", "*.md"))[0]
    lines = open(origin_file, encoding="utf-8").read().split("\n")
    start = find_body(lines)

    o_fp = {}
    skip_toc = False
    for i in range(start - 1, len(lines)):
        s = lines[i].strip()
        if not s:
            continue
        if s == "## 📑 快速跳转":
            skip_toc = True
            continue
        if skip_toc:
            if s == "---":
                skip_toc = False
            continue
        fp = normalize(s)
        if fp and len(fp) >= 3:
            if fp not in o_fp:
                o_fp[fp] = (i + 1, s)

    if book.startswith("30讲"):
        md_files = glob.glob(os.path.join(BASE, "数学", book, "*.md"))
    else:
        md_files = glob.glob(os.path.join(BASE, book, "**", "*.md"), recursive=True)
    s_fp = []
    for f in md_files:
        s_fp.extend(body_fps(f))
    s_set = set(s_fp)

    # 多提取：拆分稿有，origin无
    extra = [fp for fp in s_set if fp not in o_fp]
    # 少提取：origin有，拆分稿无（过滤噪音+标题+短行）
    missing = []
    for fp, (ln, raw) in o_fp.items():
        if fp in s_set:
            continue
        if NOISE.search(fp):
            continue
        if re.match(r"^\d+(\.\d+)*\s*[^\s]*$", fp):
            continue
        if re.match(r"^第\d+章", fp) or "考点追踪" in fp:
            continue
        if "本节试题精选" in fp or "答案与解析" in fp or "本章小结" in fp or "本章疑难点" in fp or "常见问题" in fp or "复习提示" in fp or "考纲内容" in fp or "知识框架" in fp:
            continue
        if re.match(r"^#{1,6}|^【", fp):
            continue
        missing.append((ln, raw, fp))

    print(f"{book}: origin指纹{len(o_fp)} 拆分稿指纹{len(s_set)} | 多提取{len(extra)} 少提取{len(missing)}")
    if extra:
        print(f"  多提取前3: {[e[:50] for e in sorted(extra)[:3]]}")
    if missing:
        print(f"  少提取前5:")
        for ln, raw, fp in sorted(missing, key=lambda x: x[0])[:5]:
            print(f"    L{ln}: {raw[:70]}")
