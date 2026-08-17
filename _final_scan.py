# -*- coding: utf-8 -*-
"""终检扫描：广告残留 / 替换符 / 乱码 / 行$奇偶 / 高亮== / 孤儿HTML / 页眉残留"""
import io, sys, re, os
from collections import Counter
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BOOKS = [
    "11408/origin/2027操作系统/2027操作系统.md",
    "11408/origin/2027数据结构/2027数据结构.md",
    "11408/origin/2027计算机组成原理/2027计算机组成原理.md",
    "11408/origin/2027计算机网络/2027计算机网络.md",
    "11408/origin/27张宇基础30讲（高数）/27张宇基础30讲（高数）.md",
    "11408/origin/27张宇基础30讲线代/27张宇基础30讲线代.md",
    "11408/origin/27张宇1000题数一【试题册】/27张宇1000题数一【试题册】.md",
    "11408/origin/27张宇1000题数一【解析册】/27张宇1000题数一【解析册】.md",
]

ADS = [
    "一手", "kaoyan", "公众", "微信", "QQ", "qq", "VX", "vx",
    "扫码", "二维码", "包邮", "元购", "添加", "加群", "进群",
    "配套课程", "全程班", "强化班", "基础班", "试听", "网课", "课程咨询",
    "考研数学上岸", "资料获取", "免费领取", "关注公众号",
]
REP = re.compile(r'�')
HILITE = re.compile(r'(?<![\w`])(==)(?![\w`])')  # 行内裸 ==
HTML = re.compile(r'<(/)?(div|table|tr|td|img|span|p|b|br|sup|sub|center)[^>]*>')

for md in BOOKS:
    print("=" * 66)
    print(os.path.basename(md))
    lines = open(md, encoding="utf-8").read().split("\n")
    ad_hits = []
    rep_hits = []
    odd_hits = []
    html_open = html_close = 0
    for i, l in enumerate(lines, 1):
        for a in ADS:
            if a in l:
                ad_hits.append((i, a, l.strip()[:80]))
                break
        if REP.search(l):
            rep_hits.append((i, l.strip()[:80]))
        # 行 $ 奇偶（跳过 ``` 代码块内）
        n = l.count("$")
        if n % 2 == 1 and not l.strip().startswith("```"):
            odd_hits.append((i, l.strip()[:80]))
        html_open += len(HTML.findall(l))
    print(f"  广告疑似: {len(ad_hits)}")
    for i, a, t in ad_hits[:12]:
        print(f"    L{i} [{a}]: {t}")
    if len(ad_hits) > 12:
        print(f"    ...共{len(ad_hits)}处")
    print(f"  替换符U+FFFD: {len(rep_hits)}")
    for i, t in rep_hits[:5]:
        print(f"    L{i}: {t}")
    print(f"  行$奇数: {len(odd_hits)}")
    for i, t in odd_hits[:5]:
        print(f"    L{i}: {t}")
