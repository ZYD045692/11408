# -*- coding: utf-8 -*-
"""李良概统 origin 标题层级规范化（分篇上下文感知）。

统一目标层级：
  H1  # 第N章 XXXX
  H2  ## 【题型N ...】 / ## 本章配套习题 / ## 【大纲要求】【本章重点】【基础知识】(基础篇)
  H3  ### 一、 小节（强化篇在题型下）/ ## → ### （基础篇 '一、'保持 H2，'（一）'→H3）
  H4  #### （一）子节 / #### 1. 数字条目
  裸行 <精选例题> <基础知识回顾> <考点及方法小结>

分篇规则：
  基础篇（无题型层）：
    '# 第N章'=H1 保持；'## 本章配套习题'=H2 保持；'## 【...】'=H2 保持；
    '## 一、'保持 H2；'## （一）'→###；'### 1.'→####；'## 良哥解读'→####；'## 考点及方法小结'→###
  强化篇（有题型层）：
    '# 第N章'=H1 保持（'## 第N章'→#）；'## 【题型N】'=H2 保持（'# 【题型N】'→##）；
    '## 一、'→###；'## （一）'→####；'### 1.'=####（在 （一） 下）；'## 良哥解读'→####；
    '## 考点及方法小结'→###；'# <标签>'→裸行

用法: python _norm_liang_headings.py --dry|--apply
"""
import argparse, glob, os, re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..")
ORIGIN = os.path.join(ROOT, "11408", "origin")

TAG_BARE = ["精选例题", "基础知识回顾", "考点及方法小结"]

def normalize(lines, strong):
    """strong=True 强化篇，False 基础篇。返回 (new_lines, hits)。"""
    out = []
    hits = []
    for i, ln in enumerate(lines, 1):
        orig = ln
        # ---- 标签裸行：去 #（若有）；裸行保持 ----
        m = re.match(r"^(#+)?\s*<([^>]+)>$", ln.strip())
        if m:
            tag = m.group(2)
            if tag in TAG_BARE or re.match(r"(精选|基础|考点|易错|例|知识)", tag):
                new = "<%s>" % tag
                if new != ln.strip():
                    hits.append((i, "标签去#", orig, new))
                out.append(new)
                continue
        # ---- 章标题 ----
        m = re.match(r"^(#{1,2})\s*(第[一二三四五六七]章\s+.+)$", ln)
        if m:
            new = "# " + m.group(2)
            if new != orig:
                hits.append((i, "章→H1", orig, new))
            out.append(new)
            continue
        # ---- 题型标题 ----
        m = re.match(r"^(#{1,2})\s*(【?\s*题型[一二三四五六七][^】]*】?.*)$", ln)
        if m:
            if m.group(1) == "#":
                new = "## " + m.group(2)
                hits.append((i, "题型#→##", orig, new))
                out.append(new)
            else:
                out.append(ln)   # ## 题型保持 H2
            continue
        # ---- 本章配套习题 ----
        if re.match(r"^#\s*本章配套习题", ln):
            new = "## " + ln[1:].strip()
            hits.append((i, "配套→##", orig, new))
            out.append(new)
            continue
        # ---- 提示框：良哥解读 / 考点及方法小结 → 加粗（不进大纲） ----
        m = re.match(r"^#{1,4}\s*(良哥解读|考点及方法小结)\s*$", ln.strip())
        if m:
            new = "**%s**" % m.group(1)
            if new != ln.strip():
                hits.append((i, "提示框→加粗", orig, new))
            out.append(new)
            continue
        # ---- 基础篇：## 一、→保持 H2；## （一）→###；### 1.→#### ----
        if not strong:
            m = re.match(r"^##\s*(一、|二、|三、|四、|五、|六、|七、)", ln)
            if m:
                out.append(ln)   # 基础篇小节 H2 保持
                continue
            m = re.match(r"^##\s*(（一）|（二）|（三）|（四）|（五）)", ln)
            if m:
                new = "### " + ln[2:].strip()
                hits.append((i, "（一）→###", orig, new))
                out.append(new); continue
            m = re.match(r"^###\s*(\d+\.)", ln)
            if m:
                new = "#### " + ln[3:].strip()
                hits.append((i, "1.→####", orig, new))
                out.append(new); continue
            if re.match(r"^##\s*良哥解读", ln):
                new = "#### " + ln[2:].strip()
                hits.append((i, "良哥→####", orig, new)); out.append(new); continue
            if re.match(r"^##\s*考点及方法小结", ln):
                new = "### " + ln[2:].strip()
                hits.append((i, "考点→###", orig, new)); out.append(new); continue
        # ---- 强化篇：## 一、→###；## （一）→####；### 1.→####（按需）----
        else:
            if re.match(r"^##\s*(考点及方法小结|切比雪夫不等式|几何概型的两个要点)", ln):
                new = "### " + ln[2:].strip()
                hits.append((i, "强化小节→###", orig, new)); out.append(new); continue
            m = re.match(r"^##\s*(一、|二、|三、|四、|五、|六、|七、)", ln)
            if m:
                new = "### " + ln[2:].strip()
                hits.append((i, "一、→###", orig, new)); out.append(new); continue
            m = re.match(r"^##\s*(（一）|（二）|（三）|（四）|（五）|良哥解读)", ln)
            if m:
                new = "#### " + ln[2:].strip()
                hits.append((i, "（一）→####", orig, new)); out.append(new); continue
        out.append(ln)
    return out, hits

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    total = 0
    for book, strong in (("27李良概统基础", False), ("27李良概统强化", True)):
        for md in sorted(glob.glob(os.path.join(ORIGIN, book, "*.md"))):
            lines = open(md, encoding="utf-8").read().split("\n")
            nl, hits = normalize(lines, strong)
            tag = "APPLY" if a.apply else "dry"
            mark = "✓" if nl != lines else "="
            print("[%s] %s %s/%s 改动%d" % (tag, mark, book, os.path.basename(md)[:18], len(hits)))
            for i, r, o, n in hits[:5]:
                print("      L%d %s: %s → %s" % (i, r, o[:42], n[:42]))
            total += len(hits)
            if a.apply and nl != lines:
                with open(md, "w", encoding="utf-8", newline="\n") as f:
                    f.write("\n".join(nl))
    print("\n共 %d 处%s" % (total, "" if a.apply else "（dry）"))

if __name__ == "__main__":
    main()