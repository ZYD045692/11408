# -*- coding: utf-8 -*-
"""数学小节图谱补边（第三批：补齐低连接节点）。幂等。"""
import io, os, re, sys, glob
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Windows 中文字路径下 dirname 可能不指向 vault 根（脚本在 11408/笔记制作/scripts/），回退到 cwd 或向上搜索
if not os.path.exists(os.path.join(ROOT, "11408", "笔记")):
    ROOT = os.getcwd()
    while ROOT and not os.path.exists(os.path.join(ROOT, "11408", "笔记")):
        parent = os.path.dirname(ROOT)
        if parent == ROOT:
            break
        ROOT = parent
os.chdir(ROOT)
NOTE = "11408/笔记/数学"

ADD_GS = {
    "12.1": [("7.1", "易混对比", "微分侧变化率 vs 积分侧累积量（功/压力）"),
             ("9.2", "前置依赖", "积分法算功与压力")],
    "12.3": [("7.3", "易混对比", "边际/弹性用微分，总量/现值用积分")],
    "13.1": [("3.4", "前置依赖", "全微分是一元可微的升维")],
    "14.4": [("13.3", "相关知识", "闭区域最值需遍历边界"),
             ("18.1", "后续应用", "空间区域识别对应三维投影")],
    "15.1": [("3.1", "前置依赖", "微分方程是导数的方程")],
    "15.6": [("15.2", "易混对比", "差分是微分的离散化")],
    "16.6": [("1.1", "前置依赖", "奇偶性决定正弦/余弦级数")],
    "17.1": [("13.2", "后续应用", "梯度与方向导数用向量语言")],
    "18.1": [("14.2", "前置依赖", "三重积分 = 累次/切片法")],
    "18.6": [("18.4", "前置依赖", "斯托克斯是格林的升维")],
    "4.9": [("1.4", "相关知识", "1^∞ 型极限与幂指求导同源：e^(v·lnu)")],
    "5.1": [("13.3", "后续应用", "极值定义升维到多元")],
}
ADD_XD = {
    "3.1": [("2.1", "前置依赖", "矩阵是向量的批量处理"),
            ("4.1", "后续应用", "方程组 = 向量的线性组合")],
    "4.4": [("4.2", "前置依赖", "齐次解空间是公共解基础"),
            ("3.2", "相关知识", "公共解 ⇔ 两解空间相交")],
    "5.1": [("1.1", "前置依赖", "|λE−A|=0 源于体积缩放为零")],
    "6.4": [("5.6", "前置依赖", "正定 ⇔ 特征值全正")],
}

def sec_files(sub):
    out = {}
    for f in glob.glob(os.path.join(NOTE, sub, "小节", "*.md")):
        m = re.match(r"([\d.]+)-", os.path.basename(f))
        if m:
            out[m.group(1)] = os.path.basename(f)[:-3]
    return out

def insert(path, lines):
    t = open(path, encoding="utf-8").read()
    m = re.search(r"(?ms)^## 关联\n(.*?)(?=^## |\Z)", t)
    if not m:
        return 0
    body = m.group(1)
    add = [l for l in lines if l not in body]
    if not add:
        return 0
    newbody = body.rstrip("\n") + "\n" + "\n".join(add) + "\n\n"
    open(path, "w", encoding="utf-8", newline="\n").write(t[:m.start(1)] + newbody + t[m.end(1):])
    return len(add)

n = 0
for sub, adds in [("高数", ADD_GS), ("线代", ADD_XD)]:
    files = sec_files(sub)
    for sec, es in adds.items():
        lines = [f"- {rel}：[[{files[tgt]}]]（{why}）" for tgt, rel, why in es]
        n += insert(os.path.join(NOTE, sub, "小节", files[sec] + ".md"), lines)
print("新增语义边:", n)
