# -*- coding: utf-8 -*-
"""数据结构 课后习题题目化收尾修复（连续性交叉验证发现的13处）:
粘连拆行×5、丢点×3、全角点×2、div包裹×1、乱序移动×1、PDF补答×1。
内容锚定+断言。一次性,可删。"""
import io, sys, shutil
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

path = "11408/origin/2027数据结构/2027数据结构.md"
shutil.copy(path, "_backup_round2/数据结构_before_tifix408.md")
lines = open(path, encoding="utf-8").read().split("\n")

def find(anchor, start=0):
    hits = [i for i in range(start, len(lines)) if anchor in lines[i]]
    assert hits, f"锚点找不到: {anchor[:40]!r}"
    return hits[0]

# 1. 3.2 A缺2: 粘连拆行
i = find("限定表中插入和删除操作位置的不同。02\\. B")
lines[i:i+1] = ["限定表中插入和删除操作位置的不同。", "", "02. B"]
print(f"OK L{i+1}: 拆出 02. B")

# 2. 3.3 Q缺15: 丢题号
i = find("【2015统考真题】已知程序如下：")
assert not lines[i].strip().startswith("15")
lines[i] = "15. " + lines[i].strip()
print(f"OK L{i+1}: 补题号15")

# 3. 3.3 A缺18: 丢点
i = find("18 B")
assert lines[i].strip() == "18 B"
lines[i] = "18. B"
print(f"OK L{i+1}: 18 B -> 18. B")

# 4. 5.3 A缺3: 粘连拆行
i = find("因此 b 一定在 c 的前面访问。03. C")
lines[i:i+1] = ["三种遍历方式中，都先遍历左子树，再遍历右子树，因此 b 一定在 c 的前面访问。", "", "03. C"]
print(f"OK L{i+1}: 拆出 03. C")

# 5. 5.4 Q缺11: 全角点
i = find("11．某二叉树结点的中序序列为 BDAECF")
lines[i] = lines[i].replace("11．", "11. ", 1)
print(f"OK L{i+1}: 11．-> 11.")

# 6. 5.5 A缺21: div包裹
i = find('<div style="text-align: center;">21. D</div>')
assert lines[i].strip() == '<div style="text-align: center;">21. D</div>'
lines[i] = "21. D"
print(f"OK L{i+1}: 去div 21. D")

# 7. 7.2 Q二缺2: 粘连拆行
i = find("要求一次查找能找出所有元素。02. 有序顺序表中的元素依次为")
s = lines[i]
pre, post = s.split("。02. ", 1)
lines[i:i+1] = [pre + "。", "", "02. " + post]
print(f"OK L{i+1}: 拆出 02.")

# 8. 7.3 Q缺32: 乱序,整块移到 ##### 33 前
i33 = find("【2021 统考真题】给定平衡二叉树如右图所示")
i33 = next(j for j in range(i33, i33-5, -1) if lines[j].strip() == "##### 33")
i32 = find("32. 【2020 统考真题】下列给定的关键字输入序列中")
assert i32 > i33
iD = find("D. 4, 2, 1, 3, 5", i32)
block = lines[i32:iD+1]
assert block[0].startswith("32. ") and block[-1].startswith("D. ")
del lines[i32:iD+2]  # 含块后空行
lines[i33:i33] = block + [""]
print(f"OK L{i32+1}: 块32移到 ##### 33 前")

# 9. 8.2 Q缺4: 粘连拆行
i = find("D.$n(n-1)/2$04. 数据序列{8, 10, 13, 4, 6, 7, 22, 2, 3}只能是（")
s = lines[i]
pre, post = s.split("$04. ", 1)
lines[i:i+1] = [pre + "$", "", "04. " + post]
print(f"OK L{i+1}: 拆出 04.")

# 10. 8.2 Q缺11: 全角点
i = find("11．对序列{E, A, S, Y, Q, U, E, S, T, I, O, N}")
lines[i] = lines[i].replace("11．", "11. ", 1)
print(f"OK L{i+1}: 11．-> 11.")

# 11. 8.2 Q缺14: 粘连拆行
i = find("D.$O(n^3)$14. 有些排序算法在每趟排序过程中")
s = lines[i]
pre, post = s.split("$14. ", 1)
lines[i:i+1] = [pre + "$", "", "14. " + post]
print(f"OK L{i+1}: 拆出 14.")

# 12. 8.5 A缺13: 丢点
i = find("基数排序中建立的队列个数等于进制数") - 2
assert lines[i].strip() == "13 D", lines[i]
lines[i] = "13. D"
print(f"OK L{i+1}: 13 D -> 13. D")

# 13. 8.6 A缺2: 补答02(书p377: 02. C, 解析句已在01下)
i = find("堆排序和快速排序不是稳定排序算法，而直接插入排序算法的时间复杂度为")
lines[i:i] = ["02. C", ""]
print(f"OK L{i+1}前: 插入 02. C")

open(path, "w", encoding="utf-8", newline="\n").write("\n".join(lines))
print("\n数据结构 13处修复写盘完成")
