# -*- coding: utf-8 -*-
"""数学小节图谱补边（第二批高价值语义边）：互逆公式 / 定义统一 / 升维对应。
幂等：已存在同链接行则跳过。"""
import io, os, re, sys, glob, shutil
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
    "4.1": [("9.1", "易混对比", "求导公式与积分公式互逆，正反各一张表")],
    "9.1": [("4.1", "易混对比", "基本积分公式由求导公式反推")],
    "9.4": [("8.3", "前置依赖", "变限积分求导是计算的起点")],
    "9.5": [("8.4", "前置依赖", "反常积分计算按敛散分类")],
    "13.3": [("5.2", "前置依赖", "多元无条件极值判别是一元判别法的升维"),
             ("14.4", "相关知识", "闭区域最值需结合边界")],
    "2.1": [("16.1", "后续应用", "级数 = 部分和数列的极限")],
    "15.4": [("5.6", "相关知识", "切线/法线方程是几何应用")],
    "15.5": [("12.1", "相关知识", "物理模型列微分方程")],
    "18.3": [("14.1", "后续应用", "第一型曲面积分是面积微元升维")],
    "4.2": [("2.4", "相关知识", "求导四则与极限四则同构")],
}
ADD_XD = {
    "1.3": [("1.1", "易混对比", "逆序数定义与本质定义是同一行列式的两种刻画")],
    "1.5": [("5.3", "后续应用", "范德蒙德等特殊行列式用于求特征值")],
    "2.1": [("3.1", "相关知识", "矩阵是向量的批量处理")],
    "6.1": [("5.6", "前置依赖", "二次型矩阵是实对称，靠正交对角化"),
            ("2.2", "前置依赖", "x^T A x 是矩阵运算的直接应用")],
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
        print("!! 无关联区:", path); return 0
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
        assert sec in files, sec
        lines = [f"- {rel}：[[{files[tgt]}]]（{why}）" for tgt, rel, why in es]
        n += insert(os.path.join(NOTE, sub, "小节", files[sec] + ".md"), lines)
print("新增语义边:", n)
