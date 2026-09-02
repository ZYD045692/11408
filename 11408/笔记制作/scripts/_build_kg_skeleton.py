# -*- coding: utf-8 -*-
"""知识图谱骨架生成：笔记层考点 stub + 课程 MOC。
- 408 四本：按拆分稿考点文件逐一生成 stub（frontmatter 沿用拆分稿字段 + status/mastery）
- 数学：30讲 高数18讲/线代7讲 生成讲级 stub（沿用已有 第1讲-行列式.md 的字段约定）
- 已存在的文件一律跳过（绝不覆盖用户笔记）
- MOC：4 个课程 MOC + 数学-MOC，含章节树 + Dataview 进度统计
"""
import io, os, re, sys, glob
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(ROOT)

BASE_SPLIT = "11408/拆分稿"
BASE_NOTE = "11408/笔记"
COURSES = ["数据结构", "操作系统", "计算机组成原理", "计算机网络"]

def read_fm(path):
    """读 frontmatter dict（简单字段够用）"""
    t = open(path, encoding="utf-8").read()
    m = re.match(r"(?s)^---\s*\n(.*?)\n---", t)
    fm = {}
    if m:
        for line in m.group(1).split("\n"):
            kv = re.match(r"^(\w+):\s*(.*)$", line)
            if kv:
                fm[kv.group(1)] = kv.group(2).strip().strip('"')
    return fm

PROTECT = {os.path.normpath(os.path.join(BASE_NOTE, "数学", "线代", "第1讲-行列式.md"))}

def write_new(path, content):
    # 骨架已全部就位且考点笔记已开始填内容：任何已存在的文件都不再动，防覆盖
    if os.path.exists(path):
        return False
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, "w", encoding="utf-8", newline="\n").write(content)
    return True

# ---------- 408 考点 stub ----------
stub_body = """# {title}

> [!abstract] 一句话总结
>

## 核心要点
-

## 易混与对比
-

## 真题与错题
- 习题原文：{exlink}

## 关联考点
- 前置：
- 后续/易混：

## 闪卡
-
"""

course_data = {}
for course in COURSES:
    chapters = {}   # (cno, ctitle) -> [ {section, title, stub_path, split_path, exlink} ]
    for ch_dir in sorted(glob.glob(os.path.join(BASE_SPLIT, course, "*/"))):
        ch_name = os.path.basename(os.path.normpath(ch_dir))     # NN-章名（兼容反斜杠）
        m = re.match(r"(\d+)-(.+)", ch_name)
        cno, ctitle = (int(m.group(1)), m.group(2)) if m else (0, ch_name)
        for kf in sorted(glob.glob(os.path.join(ch_dir, "考点", "*.md"))):
            fm = read_fm(kf)
            base = os.path.basename(kf)[:-3]                     # x.y-节名
            bm = re.match(r"([\d.]+)-(.+)", base)
            sec = fm.get("section") or (bm.group(1) if bm else "")
            title = fm.get("point_title") or (f"{sec} {bm.group(2)}" if bm else base)
            rel_split = kf.replace("\\", "/")
            stub_path = os.path.join(BASE_NOTE, course, "考点", os.path.basename(kf))
            # 习题文件（同章节目录下 习题/x.y-*.md）
            exlink = ""
            ex = glob.glob(os.path.join(ch_dir, "习题", f"{sec}-*.md"))
            if ex:
                exrel = ex[0].replace("\\", "/")[:-3]
                exlink = f"[[{exrel}|{sec} 本节习题与解析]]"
            chapters.setdefault((cno, ctitle), []).append({
                "sec": sec, "title": title, "stub": stub_path.replace("\\", "/"),
                "split": rel_split, "exlink": exlink,
                "dao": os.path.exists(os.path.join(ch_dir, "导读.md")),
                "ch_dir": ch_dir.replace("\\", "/")})
            body = stub_body.format(title=title, exlink=exlink or "（无）")
            fmtext = f"""---
type: 考点
course: {course}
chapter_no: {cno}
chapter_title: {ctitle}
section: "{sec}"
point_title: "{title}"
status: 未开始
mastery: 0
tags:
  - 408/{course}
  - 考点
source: "[[{rel_split[:-3]}]]"
---

{body}"""
            write_new(stub_path, fmtext)
    course_data[course] = chapters

# ---------- 408 课程 MOC ----------
for course in COURSES:
    chapters = course_data[course]
    lines = [f"""---
type: MOC
course: {course}
tags:
  - 408
  - MOC
---

# {course} MOC

> 王道 2027《{course}》考点骨架。[[11408/笔记/408-MOC|← 返回 408 总览]]

## 章节目录
"""]
    for (cno, ctitle), items in sorted(chapters.items()):
        lines.append(f"### 第{cno}章 {ctitle}")
        if items and items[0]["dao"]:
            lines.append(f"- 📖 [[{items[0]['ch_dir']}/导读|本章导读]]")
        for it in items:
            lines.append(f"- [[{it['stub'][:-3]}|{it['title']}]]（[[{it['split'][:-3]}|原文]]）")
        lines.append("")
    lines.append("""## 学习进度

```dataview
TABLE WITHOUT ID status AS 状态, length(rows) AS 考点数
FROM "11408/笔记/""" + course + """"
WHERE type = "考点"
GROUP BY status
```

## 考点清单

```dataview
TABLE WITHOUT ID link(file.link, point_title) AS 考点, status AS 状态, mastery AS 掌握度
FROM "11408/笔记/""" + course + """"
WHERE type = "考点"
SORT chapter_no ASC, section ASC
```
""")
    write_new(os.path.join(BASE_NOTE, course, f"{course}-MOC.md"), "\n".join(lines))

# ---------- 数学讲级 stub ----------
for book, tag, sub in [("30讲-高数", "考研数学/高数", "高数"), ("30讲-线代", "考研数学/线代", "线代")]:
    files = sorted(glob.glob(os.path.join(BASE_SPLIT, "数学", book, "*.md")))
    def lecno(p):
        m = re.search(r"第(\d+)讲", os.path.basename(p))
        return int(m.group(1)) if m else 0
    files.sort(key=lecno)
    for f in files:
        name = os.path.basename(f)[:-3]          # 第N讲-讲名
        n = lecno(f)
        topic = name.split("-", 1)[1] if "-" in name else name
        stub = os.path.join(BASE_NOTE, "数学", sub, name + ".md")
        rel = f.replace("\\", "/")
        prev_link = f"[[{os.path.basename(files[i-1])[:-3]}]]" if False else ""
        fmtext = f"""---
type: 笔记
course: 数学
book: {book}
lecture: {n}
topic: "{topic}"
status: 未开始
mastery: 0
tags:
  - {tag}
  - 笔记
source: "[[{name}]]"
---

# {name.replace('-', ' ')}

> [!abstract] 一句话总结
>

## 核心考点

## 易错点

## 闪卡（Spaced Repetition）
-

## 复习清单
- [ ] 通读原文 [[{name}]]（拆分稿）
- [ ] 1000题 对应章节

## 关联
- 原文：[[{name}]]（拆分稿）
"""
        write_new(stub, fmtext)

# ---------- 数学 MOC ----------
math_lines = ["""---
type: MOC
course: 数学
tags:
  - 考研数学
  - MOC
---

# 数学 MOC

> 张宇基础 30 讲 + 1000 题。[[11408/笔记/408-MOC|408 总览]]

## 30讲-高数
"""]
for book, sub in [("30讲-高数", "高数"), ("30讲-线代", "线代")]:
    if book == "30讲-线代":
        math_lines.append("\n## 30讲-线代\n")
    files = sorted(glob.glob(os.path.join(BASE_SPLIT, "数学", book, "*.md")),
                   key=lambda p: int(re.search(r"第(\d+)讲", os.path.basename(p)).group(1)))
    for f in files:
        name = os.path.basename(f)[:-3]
        math_lines.append(f"- [[11408/笔记/数学/{sub}/{name}|{name}]]（[[{f.replace(chr(92),'/')[:-3]}|原文]]）")
math_lines.append("""
## 1000题（题库，做题时直接翻对应篇章）

**试题册**
```dataview
LIST WITHOUT ID link(file.link, replace(file.name, ".md", ""))
FROM "11408/拆分稿/数学/1000题-试题册"
SORT file.path ASC
```

**解析册**
```dataview
LIST WITHOUT ID link(file.link, replace(file.name, ".md", ""))
FROM "11408/拆分稿/数学/1000题-解析册"
SORT file.path ASC
```

（错题记到对应讲笔记的"复习清单"里）

## 学习进度

```dataview
TABLE WITHOUT ID link(file.link, topic) AS 讲, status AS 状态, mastery AS 掌握度
FROM "11408/笔记/数学"
WHERE type = "笔记"
SORT lecture ASC
```
""")
write_new(os.path.join(BASE_NOTE, "数学", "数学-MOC.md"), "\n".join(math_lines))

# ---------- 408 总 MOC（覆盖旧的空文件） ----------
moc408 = """---
type: MOC
course: 408
tags:
  - 408
  - MOC
---

# 408 计算机统考 · 知识库

> 王道 408 系列考研辅导书整理的考点知识库。数据结构、操作系统、计算机组成原理、计算机网络四门课。

## 📚 课程导航

- **[[11408/笔记/数据结构/数据结构-MOC|📊 数据结构]]** — 绪论、线性表、栈队列数组、串、树与二叉树、图、查找、排序
- **[[11408/笔记/操作系统/操作系统-MOC|🖥️ 操作系统]]** — 计算机系统概述、进程与线程、内存管理、文件管理、输入输出管理
- **[[11408/笔记/计算机组成原理/计算机组成原理-MOC|🔧 计算机组成原理]]** — 系统概述、数据表示与运算、存储系统、指令系统、中央处理器、总线、输入输出
- **[[11408/笔记/计算机网络/计算机网络-MOC|🌐 计算机网络]]** — 体系结构、物理层、数据链路层、网络层、传输层、应用层

## 📊 各课考点进度

```dataview
TABLE WITHOUT ID course AS 课程, length(rows) AS 考点数, length(filter(rows, (r) => r.status = "已完成")) AS 已完成
FROM "11408/笔记"
WHERE type = "考点"
GROUP BY course
SORT course ASC
```

## 🔗 相关

- [[11408/笔记/数学/数学-MOC|数学 MOC]]（30讲 + 1000题）
- [[11408/拆分稿/408-MOC|拆分稿 408-MOC]]（原文侧导航）
- 源库全文：[[11408/origin/2027数据结构/2027数据结构|数据结构]] / [[11408/origin/2027操作系统/2027操作系统|操作系统]] / [[11408/origin/2027计算机组成原理/2027计算机组成原理|计算机组成原理]] / [[11408/origin/2027计算机网络/2027计算机网络|计算机网络]]
"""
write_new(os.path.join(BASE_NOTE, "408-MOC.md"), moc408)

# ---------- 统计 ----------
n_kaodian = len(glob.glob(os.path.join(BASE_NOTE, "*", "考点", "*.md")))
n_note = len(glob.glob(os.path.join(BASE_NOTE, "数学", "*", "*.md")))
n_moc = len(glob.glob(os.path.join(BASE_NOTE, "**", "*MOC.md"), recursive=True))
print(f"考点 stub: {n_kaodian} | 数学讲笔记: {n_note} | MOC: {n_moc}")
