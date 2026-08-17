# -*- coding: utf-8 -*-
# 用法: python _find_first_bb.py <md>  找第一个异常 $$（栈配对）
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
md = sys.argv[1]
text = open(md, encoding="utf-8").read()
n = len(text)
in_code = False
in_block = None
i = 0
total = 0
first_issue = None
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
    if text.startswith("$$", i):
        total += 1
        if in_block is not None:
            in_block = None  # 关闭
        else:
            in_block = i
        i += 2
        continue
    i += 1
print(f"$$ 总数: {total}")
if in_block is not None:
    ln = text.count("\n", 0, in_block) + 1
    ctx = text[max(0,in_block-35):in_block+35].replace("\n", "⏎")
    print(f"未配 $$ 在 L{ln}: ...{ctx!r}")
