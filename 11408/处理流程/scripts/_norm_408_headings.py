# -*- coding: utf-8 -*-
"""408 四本 origin 标题层级规范化（v2）。"""
import io, sys, re, os
from collections import Counter
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BOOKS = [
    "11408/origin/2027操作系统/2027操作系统.md",
    "11408/origin/2027数据结构/2027数据结构.md",
    "11408/origin/2027计算机组成原理/2027计算机组成原理.md",
    "11408/origin/2027计算机网络/2027计算机网络.md",
]

HEAD = re.compile(r'^(#{1,6})\s+(.*)$')
CH   = re.compile(r'^第\s*\d+\s*[章]')
KG   = re.compile(r'^【考纲内容】|^【复习提示】')
ZKD  = re.compile(r'^考点追踪')
SUB4 = re.compile(r'^(\d+)\.(\d+)\.(\d+)\.(\d+)\s+\S')
SUB  = re.compile(r'^(\d+)\.(\d+)\.(\d+)\s+\S')
SEC  = re.compile(r'^(\d+)\.(\d+)\s+\S')
TX   = re.compile(r'^(?:[一二三四]、\s*)?(单项选择题|多项选择题|不定项选择题|综合应用题|综合题|填空题|算法设计题|简答题|选择题|应用题|判断题)\s*$')
NUMITEM = re.compile(r'^\d{1,3}\s*[\\]?\.\s+\S')
PAREN_AR = re.compile(r'^（\s*\d+\s*[）)]\s*\S|^\(\s*\d+\s*\)\s*\S')
PAREN_CN = re.compile(r'^（[一二三四五六七八九十]+）\s*\S')
ANSWER   = re.compile(r'^\d{1,3}\s*[\\]?\.\s*[A-Z](?:[、,，]\s*[A-Z])*\s*[\\]?\s*$')
ANSWER2  = re.compile(r'^\d{1,3}\s+[A-Z](?:[、,，]\s*[A-Z])*\s*$')
ANSWER3  = re.compile(r'^[A-E](?:[A-E]){4,}\s*…?$')  # ABECDEABECDE …
SOLVE    = re.compile(r'^解\s*应选\s*[A-D]')
QX       = re.compile(r'^\d{1,3}\s*[）)]\s*\S')
SUPER_NUM = re.compile(r'^\$\^.*\$\s*\d*\s*[\.．]?\s*\S')  # $^{*}1$. 单级目录结构 / $^{4}$ 无环图
BULLET   = re.compile(r'^•\s')
PROSE    = re.compile(
    r'^(?:方案[一二三四五六]：|由题目.*[：:]$|下面.*[。：:]$|综上，.*[。]$|本题代码如下[：:]'
    r'|【解答\d*】|结论\s*\d+[：:]|for\s+\S.*$|C\d+:\s|或等价地|流水线设计遵循以下原则[：:]'
    r'|分组交换技术的缺点[：:]|分层的基本原则如下[：:]|约定生成多项式|发送方生成FCS|接收方校验'
    r'|下面举例说明|回答下列问题[：:]|下面通过一个简单的例子来说明|IGMP 的工作可分为两个阶段[：:]'
    r'|TCP 采用四种算法)')

CALL_BOX_EXACT = {"注意","提示","提 示","思维拓展","归纳总结","技巧","思考","误区",
                  "说明","评分说明","补充知识","参考文献","【知识框架】","本章小结","视频讲解"}
CALL_BOX_PREFIX = ["问题分析", "问题描述"]
SOLVE_EXACT = {"解：", "解:"}

# 章名重复残留（纯页眉/封面残留，紧邻 # 第N章 章名）→ 整行删除
DELETE_H2 = {
    "11408/origin/2027数据结构/2027数据结构.md": {"## 线性表", "## 图", "## 查找"},
    "11408/origin/2027计算机组成原理/2027计算机组成原理.md": {"## 存储系统", "## 中央处理器", "## 总线", "## 数据的表示和运算"},
    "11408/origin/2027计算机网络/2027计算机网络.md": {"## 物理层", "## 数据链路层", "## 网络层", "## 传输层", "## 应用层"},
}

def classify(t):
    if CH.match(t):  return ('keep', 1)
    if KG.match(t):  return ('keep', 2)
    if ZKD.match(t): return ('keep', 3)
    if SUB4.match(t): return ('keep', 4)
    if SUB.match(t): return ('keep', 3)
    if SEC.match(t): return ('keep', 2)
    if ANSWER.match(t) or ANSWER2.match(t) or ANSWER3.match(t) or SOLVE.match(t): return ('text', None)
    if SUPER_NUM.match(t): return ('keep', 4)
    if t in ("变形补码", "模运算（了解）") or t.startswith("【例 "): return ('keep', 4)
    if BULLET.match(t): return ('text', None)
    if PROSE.match(t): return ('text', None)
    if TX.match(t):  return ('keep', 4)
    if NUMITEM.match(t): return ('keep', 4)
    if PAREN_AR.match(t): return ('keep', 5)
    if PAREN_CN.match(t): return ('keep', 3)
    if t in CALL_BOX_EXACT: return ('bold', None)
    if any(t.startswith(p) for p in CALL_BOX_PREFIX) or t in SOLVE_EXACT: return ('bold', None)
    if QX.match(t): return ('text', None)
    return ('skip', None)

for md in BOOKS:
    delset = DELETE_H2.get(md, set())
    lines = open(md, encoding="utf-8").read().split("\n")
    keep_lv = Counter(); n_text = n_bold = n_del = n_skip = 0
    skipped = Counter()
    new = []
    for l in lines:
        if l.strip() in delset:
            n_del += 1
            continue
        m = HEAD.match(l)
        if not m:
            new.append(l); continue
        t = m.group(2).strip()
        if t.startswith("📑"):
            new.append(l); continue
        kind, arg = classify(t)
        if kind == 'keep':
            keep_lv[arg] += 1
            new.append("#" * arg + " " + t)
        elif kind == 'text':
            n_text += 1
            new.append(t)
        elif kind == 'bold':
            n_bold += 1
            new.append("**" + t + "**")
        else:
            n_skip += 1
            skipped[t] += 1
            new.append(l)
    open(md, "w", encoding="utf-8").write("\n".join(new))
    print("=" * 60)
    print(os.path.basename(md))
    print("  层级: H1:%d H2:%d H3:%d H4:%d H5:%d" % (
        keep_lv[1], keep_lv[2], keep_lv[3], keep_lv[4], keep_lv[5]))
    print(f"  去#普通: {n_text}  加粗: {n_bold}  删除残留: {n_del}  未匹配: {n_skip}")
    if skipped:
        print("  未匹配(前30):")
        for t, n in skipped.most_common(30):
            print(f"    ×{n}: {t[:58]}")
