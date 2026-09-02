# -*- coding: utf-8 -*-
"""高数 origin 题目化收尾修复（交叉验证发现的15处）:
A 漏转换6(☆/☐☑/★ ★/$$包裹) B 粘连题号3(2.31/2.51/2.61)
C $$裹解答2(1.6/3.6) D 粘连题1(6.10) E 跨页幻影2(例8.17/例16.35)
F 误转1(例1.20的两个结论) G 丢标题4(例2.16/答4.4/例14.1/例13.17+补题干)
全部内容锚定+断言。一次性,可删。"""
import io, sys, shutil
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

path = "11408/origin/27张宇基础30讲（高数）/27张宇基础30讲（高数）.md"
shutil.copy(path, "_backup_round2/高数_before_tifix2.md")
lines = open(path, encoding="utf-8").read().split("\n")

def find(anchor, start=0, n=1):
    hits = [i for i in range(start, len(lines)) if anchor in lines[i]]
    assert len(hits) >= n, f"锚点找不到: {anchor[:40]!r} (只有{len(hits)}处)"
    return hits[0] if n == 1 else hits

def replace_line(i, *new):
    print(f"OK L{i+1}: {lines[i][:38]!r} -> {len(new)}行")
    lines[i:i+1] = list(new)

# ---------- E 跨页幻影(先删,自下而上) ----------
i = find("例16.36 例16.37")
assert lines[i-1].strip() == "###### 例16.35"
print(f"DEL L{i}~L{i+1}: 幻影例16.35 + 垃圾行")
del lines[i-1:i+1]

i = find("###### 例8.17")
assert lines[i+1].strip() == "以下反常积分发散的是（）" and lines[i+2].strip() == ""
assert lines[i+3].strip() == "###### 例8.17"
print(f"DEL L{i+1}~L{i+3}: 幻影例8.17 + 重复题干 + 空行")
del lines[i:i+3]

# ---------- F 误转: 例1.20的两个结论(并回正文) ----------
i = find("###### 例1.20", find("###### ★ 例1.20"))
assert lines[i+1].startswith("的两个结论")
print(f"OK L{i+1}: 误转标题并回正文")
lines[i:i+2] = ["例1.20" + lines[i+1]]

# ---------- C $$裹解答 ----------
i = find(r"$$1.6\quad\frac{x}{1+nx}")
replace_line(i, "##### 1.6", "",
             r"$\frac{x}{1+nx}(n=1,2,3,\cdots)$ 解 $f_{2}(x)=f[f_{1}(x)]=\frac{f_{1}(x)}{1+f_{1}(x)}=\frac{\frac{x}{1+x}}{1+\frac{x}{1+x}}=\frac{x}{1+2x}.$")

i = find(r"$$\begin{aligned}3.6\quad")
s = lines[i]
head_old = r"$$\begin{aligned}3.6\quad-\frac{1}{4}f^{\prime}(0)\quad 解 \qquad"
assert head_old in s
rest = s.replace(head_old, r"$$\begin{aligned}", 1)
replace_line(i, "##### 3.6", "", r"$-\frac{1}{4}f^{\prime}(0)$ 解", "", rest)

# ---------- B 粘连题号 2.31/2.51/2.61 ----------
for bad, good in [("##### 2.31", "##### 2.3"), ("##### 2.51", "##### 2.5"), ("##### 2.61", "##### 2.6")]:
    i = find(bad)
    assert lines[i].strip() == bad
    print(f"OK L{i+1}: {bad} -> {good} + 答案1")
    lines[i] = good
    lines.insert(i+1, "")
    lines.insert(i+2, "1 " + lines[i+2].strip() if not lines[i+2].startswith("解") else "1 " + lines[i+2].strip())

# ---------- D 粘连题 6.10 ----------
i = find(r"$6.10 设$p$,$q$是大于 1 的常数")
s = lines[i]
pos = s.find("$6.10 ")
assert pos > 0
tail = s[pos+1:]  # "6.10 设..."
replace_line(i, s[:pos] + "$", "", "##### 6.10", "", tail[len("6.10 "):])

# ---------- A 漏转换 ----------
i = find("☆例1.34 ")
s = lines[i]
replace_line(i, "###### ☆ 例1.34", "", s.replace("☆例1.34 ", "", 1).strip())

i = find(r"$$例 9.3\quad")
s = lines[i].strip()
inner = s.strip("$").strip()
inner = inner.replace(r"例 9.3\quad ", "", 1)
m = inner.split(" ", 1)
replace_line(i, "###### 例9.3", "", m[0] + " $\\int\\sqrt{a^{2}-x^{2}}\\mathrm{d}x(a>0)$"
             if False else "求不定积分 $\\int\\sqrt{a^{2}-x^{2}}\\mathrm{d}x(a>0)$")

i = find(r"$$例 9.15\quad")
replace_line(i, "###### 例9.15", "",
             r"$\int_{0}^{1}x\arcsin\sqrt{4x-4x^{2}}\mathrm{d}x=$ ___.")

i = find("★★★ ☐ 例9.24 ")
s = lines[i]
replace_line(i, "###### ★★★ 例9.24", "", s.replace("★★★ ☐ 例9.24 ", "", 1).strip())

i = find("★★★ ☑ 例9.28 ")
s = lines[i]
replace_line(i, "###### ★★★ 例9.28", "", s.replace("★★★ ☑ 例9.28 ", "", 1).strip())

i = find("★ ★ 例 11.2 ")
s = lines[i]
replace_line(i, "###### ★★ 例11.2", "", s.replace("★ ★ 例 11.2 ", "", 1).strip())

# ---------- G 丢标题插入 ----------
i = find("“对任意给定的  $k \\in \\mathbb{N}$")
print(f"OK L{i+1}前: 插入 ##### 例2.16")
lines[i:i] = ["##### 例2.16", ""]

i = find(r"$$-\frac{(1+2t)(1+t^2)}{2t}$$")
print(f"OK L{i+1}前: 插入 ##### 4.4")
lines[i:i] = ["##### 4.4", ""]

i = find("设平面闭区域 $D_{i}(i=1,2,3,4)$分别是由")
print(f"OK L{i+1}前: 插入 ###### 例14.1")
lines[i:i] = ["###### 例14.1", ""]
j = find("(2分析) 此题是同一个函数在不同区域的积分比大小")
lines[j] = lines[j].replace("(2分析)", "分析", 1)
print(f"OK L{j+1}: (2分析) -> 分析")

i = find("$y_{0}$处取得极值的（）.")
print(f"OK L{i+1}前: 插入 ###### 例13.17 + 补题干")
lines[i:i] = ["###### 例13.17", "",
              "二元函数 $f(x, y)$ 在点 $(x_0, y_0)$ 处取得极值是一元函数 $f(x, y_0)$ 和 $f(x_0, y)$ 分别在 $x_0$ 和", ""]

open(path, "w", encoding="utf-8", newline="\n").write("\n".join(lines))
print("\n全部修复写盘完成")
