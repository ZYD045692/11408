# -*- coding: utf-8 -*-
# 删除 origin 里的王道书广告页 / 张宇关注公众号广告
# 形式A: 购买王道书，就上\n\n王道官方考研书店\n\nwangdao.taobao.com
# 形式B: # 购买王道书，就上 王道官方考研书店\n\nwangdao.taobao.com
# 单行:  关注公众号获取更多免费咨询
import io, sys, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BOOKS = [
    "11408/origin/2027数据结构/2027数据结构.md",
    "11408/origin/2027计算机组成原理/2027计算机组成原理.md",
    "11408/origin/2027计算机网络/2027计算机网络.md",
    "11408/origin/27张宇基础30讲（高数）/27张宇基础30讲（高数）.md",
]

AD_END = "wangdao.taobao.com"

def clean_blank(lines, i):
    """删除块 i..j 后，确保 out 末尾最多一个空行"""
    while lines and lines[-1].strip() == "":
        lines.pop()
    lines.append("")

for md in BOOKS:
    lines = open(md, encoding="utf-8").read().split("\n")
    out = []
    removed = 0
    i = 0
    n = len(lines)
    while i < n:
        s = lines[i].strip()
        if s.startswith("购买王道书") or s.startswith("# 购买王道书"):
            j = i
            while j < n and lines[j].strip() != AD_END:
                j += 1
            if j < n:
                # 删除 i..j（广告文本行 + 中间空行），out 末尾保证一个空行
                clean_blank(out, i)
                removed += 1
                # 跳过广告块后的一个空行（若有），避免双空行
                k = j + 1
                while k < n and lines[k].strip() == "":
                    k += 1
                i = k
                continue
        if s == "关注公众号获取更多免费咨询":
            clean_blank(out, i)
            removed += 1
            k = i + 1
            while k < n and lines[k].strip() == "":
                k += 1
            i = k
            continue
        out.append(lines[i])
        i += 1
    open(md, "w", encoding="utf-8").write("\n".join(out))
    print(f"{md}: 删除广告块 {removed} 处")
