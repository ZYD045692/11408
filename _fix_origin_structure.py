# -*- coding: utf-8 -*-
# 修复 408 四本 origin 的破坏性结构异常（精确字符串替换）
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

FIXES = {
    "11408/origin/2027数据结构/2027数据结构.md": [
        ("## 第5章", "# 第5章", True),      # 整行
        ("## 第8章", "# 第8章", True),
        ("###  $^{4.1}$ 串的定义和实现 $^{①}$", "### 4.1 串的定义和实现", False),
        ("###  $^{8}$5.3 计数排序", "#### 8.5.3 计数排序", False),
    ],
    "11408/origin/2027操作系统/2027操作系统.md": [
        ("###  $^{3}$2.5 抖动和工作集", "#### 3.2.5 抖动和工作集", False),
        ("###  $^{4}$2.5 目录实现", "#### 4.2.5 目录实现", False),
    ],
    "11408/origin/2027计算机组成原理/2027计算机组成原理.md": [
        ("## 第7章", "# 第7章", True),
        ("###  $^{*}1.1$ 计算机发展历程 $^{①}$", "### 1.1 计算机发展历程", False),
        ("###  $^{6}$1.2 常见的总线标准 $^{①}$", "#### 6.1.2 常见的总线标准", False),
        ("###  $^{*}7.1$ I/O 系统基本概念 $^{①}$", "### 7.1 I/O 系统基本概念", False),
        ("###  $^{7}$1.3 本节习题精选", "#### 7.1.3 本节习题精选", False),
        ("###  $^{7}$1.4 答案与解析", "#### 7.1.4 答案与解析", False),
        ("####  $^{*}7.1.1$ 输入/输出系统", "#### 7.1.1 输入/输出系统", False),
        ("####  $^{*}7.1.2$ 外部设备", "#### 7.1.2 外部设备", False),
    ],
    "11408/origin/2027计算机网络/2027计算机网络.md": [
        ("###  $^{3}$8.1 网桥的基本概念", "#### 3.8.1 网桥的基本概念", False),
    ],
}

total = 0
for md, pairs in FIXES.items():
    lines = open(md, encoding="utf-8").read().split("\n")
    n_fix = 0
    for old, new, whole_line in pairs:
        done = 0
        for i, l in enumerate(lines):
            if whole_line:
                if l.strip() == old:
                    lines[i] = new
                    done += 1
            else:
                if old in l:
                    lines[i] = l.replace(old, new, 1)
                    done += 1
        if done == 0:
            print(f"  ⚠ 未命中: {old}")
        n_fix += done
    open(md, "w", encoding="utf-8").write("\n".join(lines))
    print(f"{md.split('/')[-2]}: 修复 {n_fix} 处")
    total += n_fix
print(f"总计修复 {total} 处")
