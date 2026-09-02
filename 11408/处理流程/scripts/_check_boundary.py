# -*- coding: utf-8 -*-
# 用法: python _check_boundary.py <md>  公式边界解析
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
md = sys.argv[1]
text = open(md, encoding="utf-8").read()
n = len(text)
in_code = False
in_block = None
in_inline = None
inblock_d = 0
i = 0
while i < n:
    if text.startswith("```", i):
        in_code = not in_code
        i += 3
        continue
    if in_code:
        i += 1
        continue
    if text[i] == "\\" and i + 1 < n and text[i+1] == "$":
        i += 2
        continue
    if text[i] == "$":
        if text.startswith("$$", i):
            in_block = None if in_block is not None else i
            i += 2
            continue
        else:
            if in_block is not None:
                inblock_d += 1
            elif in_inline is not None:
                in_inline = None
            else:
                in_inline = i
            i += 1
            continue
    i += 1
print(f"块内$计数: {inblock_d}")
print("未配$$:", "无" if in_block is None else "有!")
print("未配$:", "无" if in_inline is None else "有!")
