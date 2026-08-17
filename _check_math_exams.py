# -*- coding: utf-8 -*-
# 数学书：假设每章/每讲都有题目
# 1000题-试题册：每章文件应有题目；解析册：每章应有解析
# 30讲：每讲文件应含例题/习题
import io, sys, os, re, glob
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

def count_questions(path, pats):
    n = 0
    for p in pats:
        with open(path, encoding="utf-8") as f:
            n += len(re.findall(p, f.read()))
    return n

print("===== 1000题-试题册（按篇/科/章，每章应有题） =====")
root = "11408/拆分稿/数学/1000题-试题册"
empty = []
for dirpath, _, files in os.walk(root):
    for f in sorted(files):
        if not f.endswith(".md"):
            continue
        p = os.path.join(dirpath, f)
        sz = os.path.getsize(p)
        if sz < 200:
            empty.append((os.path.relpath(p, root), sz))
if empty:
    for rp, sz in empty:
        print(f"  ⚠ 文件过小({sz}B): {rp}")
else:
    print("  ✓ 70个章文件均非空")

print("\n===== 1000题-解析册（每章应有解析） =====")
root = "11408/拆分稿/数学/1000题-解析册"
empty = []
for dirpath, _, files in os.walk(root):
    for f in sorted(files):
        if not f.endswith(".md"):
            continue
        p = os.path.join(dirpath, f)
        sz = os.path.getsize(p)
        if sz < 200:
            empty.append((os.path.relpath(p, root), sz))
if empty:
    for rp, sz in empty:
        print(f"  ⚠ 文件过小({sz}B): {rp}")
else:
    print("  ✓ 70个章文件均非空")

print("\n===== 30讲-高数（每讲应含例题） =====")
root = "11408/拆分稿/数学/30讲-高数"
for f in sorted(os.listdir(root)):
    if not f.endswith(".md"):
        continue
    p = os.path.join(root, f)
    txt = open(p, encoding="utf-8").read()
    n_ex = len(re.findall(r"例\s*\d+", txt))
    sz = os.path.getsize(p)
    flag = "  ⚠ 无明显例题!" if n_ex == 0 else ""
    print(f"  {f[:22]}: {sz}B 例题{n_ex}{flag}")

print("\n===== 30讲-线代（每讲应含例题） =====")
root = "11408/拆分稿/数学/30讲-线代"
for f in sorted(os.listdir(root)):
    if not f.endswith(".md"):
        continue
    p = os.path.join(root, f)
    txt = open(p, encoding="utf-8").read()
    n_ex = len(re.findall(r"例\s*\d+", txt))
    sz = os.path.getsize(p)
    flag = "  ⚠ 无明显例题!" if n_ex == 0 else ""
    print(f"  {f[:22]}: {sz}B 例题{n_ex}{flag}")
