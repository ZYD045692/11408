# -*- coding: utf-8 -*-
# 修复线代 L7904 垃圾公式块：例6.4 二次型被 OCR 毁掉
# 用后文解法的矩阵 A=[[2,2,-2],[2,5,-4],[-2,-4,5]] 重建：
# f = 2x1^2+5x2^2+5x3^2+4x1x2-4x1x3-8x2x3
import io, sys, glob
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

md = glob.glob("11408/origin/27张宇基础30讲线代/*.md")[0]
lines = open(md, encoding="utf-8").read().split("\n")

# 定位垃圾行：含 "例 6.4" 的下一个 ```c 块
start = None
for i, l in enumerate(lines):
    if "例 6.4 用正交变换化二次型" in l:
        for j in range(i + 1, min(i + 5, len(lines))):
            if lines[j].strip() == "```c":
                start = j
                break
        break
if start is None:
    print("未找到 例6.4 代码块")
    sys.exit(1)

# 找块结束
end = None
for j in range(start + 1, len(lines)):
    if lines[j].strip() == "```":
        end = j
        break
if end is None:
    print("未找到块结束 ```")
    sys.exit(1)

# 重建二次型
formula = r" $f(x_{1},x_{2},x_{3})=2x_{1}^{2}+5x_{2}^{2}+5x_{3}^{2}+4x_{1}x_{2}-4x_{1}x_{3}-8x_{2}x_{3}$"

# 替换块(含 ```c 围栏)为 公式行 + 空行
new_block = [formula, ""]
lines = lines[:start] + new_block + lines[end + 1:]

open(md, "w", encoding="utf-8").write("\n".join(lines))
print(f"已替换 L{start+1}-L{end+1} 垃圾代码块 → 重建的二次型公式")
