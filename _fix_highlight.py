# -*- coding: utf-8 -*-
# 修复正文里被 Obsidian 误识别为 ==高亮== 的 C 代码比较表达式
# 把含 == 的代码片段用反引号行内代码包裹（扩展边界到代码字符 + 紧邻代码的空格）
import io, sys, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

CJK = re.compile(r'[一-鿿]')
CODE_CHARS = set("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_[]()*&|!<>+-/%?:")
HL = re.compile(r"==[^=\n]+?==")

def left_bound(line, start):
    l = start
    while l > 0:
        c = line[l-1]
        if c in CODE_CHARS:
            l -= 1
        elif c == ' ' and l-2 >= 0 and line[l-2] in CODE_CHARS:
            l -= 1
        else:
            break
    return l

def right_bound(line, end):
    r = end
    n = len(line)
    while r < n:
        c = line[r]
        if c in CODE_CHARS:
            r += 1
        elif c == ' ' and r+1 < n and line[r+1] in CODE_CHARS:
            r += 1
        else:
            break
    return r

def process_line(line):
    new_line = list(line)
    auto = manual = 0
    matches = [(m.start(), m.end(), m.group(0)) for m in HL.finditer(line)]
    for start, end, h in reversed(matches):
        if CJK.search(h):
            manual += 1
            continue
        l = left_bound(line, start)
        r = right_bound(line, end)
        code = line[l:r]
        new_line[l:r] = '`' + code + '`'
        auto += 1
    return "".join(new_line), auto, manual

for md in sys.argv[1:]:
    lines = open(md, encoding="utf-8").read().split("\n")
    in_code = False
    auto_total = manual_total = 0
    for i, l in enumerate(lines):
        if l.strip().startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        new, auto, manual = process_line(l)
        if new != l:
            lines[i] = new
            auto_total += auto
            manual_total += manual
    open(md, "w", encoding="utf-8").write("\n".join(lines))
    print(f"{md.split('/')[-2]}: 自动修复 {auto_total} 处, 含中文需人工 {manual_total} 处")
