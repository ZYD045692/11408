# -*- coding: utf-8 -*-
"""8 本 origin 终检：跳级 / div·td 平衡 / ==高亮 / 广告 / 替换符 / 行$奇偶 / 标题=正文泄漏残留"""
import io, sys, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

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

ADS = ["一手", "kaoyan", "公众", "微信", "QQ", "qq", "VX", "vx", "扫码", "二维码",
       "包邮", "元购", "添加", "加群", "进群", "配套课程", "全程班", "强化班", "基础班",
       "试听", "网课", "课程咨询", "考研数学上岸", "资料获取", "免费领取", "关注公众号"]
REP = re.compile(r"�")
HILITE = re.compile(r"(?<![\w`])(==)(?![\w`])")
HEAD = re.compile(r"^(#{1,6})\s+(.*)$")

for md in BOOKS:
    lines = open(md, encoding="utf-8").read().split("\n")
    jumps, div_o, div_c, td_o, td_c, ad_hits, rep_hits, hl_hits, odd_hits, leak_hits = [], 0, 0, 0, 0, [], [], [], [], []
    prev_lv = 0
    for i, l in enumerate(lines, 1):
        m = HEAD.match(l)
        if m:
            lv = len(m.group(1))
            if prev_lv and lv > prev_lv + 1:
                jumps.append((i, lv, m.group(2).strip()[:50]))
            prev_lv = lv
        for a in ADS:
            if a in l:
                ad_hits.append(i)
                break
        if REP.search(l):
            rep_hits.append(i)
        if HILITE.search(l):
            hl_hits.append(i)
        if l.count("$") % 2 == 1 and not l.strip().startswith("```"):
            odd_hits.append(i)
        div_o += len(re.findall(r"<div\b", l, re.I))
        div_c += len(re.findall(r"</div>", l, re.I))
        td_o += len(re.findall(r"<td\b", l, re.I))
        td_c += len(re.findall(r"</td>", l, re.I))

    ok = (not jumps and div_o == div_c and td_o == td_c and not ad_hits
          and not rep_hits and not hl_hits and not odd_hits)
    print(f"{'✅' if ok else '❌'} {md.split('/')[-2]}: 跳级{len(jumps)} div{div_o}/{div_c} td{td_o}/{td_c} "
          f"广告{len(ad_hits)} 替换符{len(rep_hits)} ==高亮{len(hl_hits)} 行$奇{len(odd_hits)}")
    for i, lv, t in jumps[:6]:
        print(f"    跳级 L{i} H{lv}: {t}")
    if odd_hits[:4]:
        print("    行$奇示例:", [(i, lines[i-1][:40]) for i in odd_hits[:4]])
print("done")
