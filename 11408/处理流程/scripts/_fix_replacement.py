# -*- coding: utf-8 -*-
# 修复 U+FFFD 替换字符（汉字编码损坏成 2-3 个 �），按语义恢复原字
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

REP = "�"

FIXES = {
    "11408/origin/2027数据结构/2027数据结构.md": [
        ("外层循" + REP + REP + "的条件", "外层循环的条件"),
        ("工作指针" + REP + REP + "别为", "工作指针分别为"),
        ("先序序" + REP + REP + "和后序", "先序序列和后序"),
        ("度为 0 " + REP + REP + REP + " m 的结点", "度为 0 和 m 的结点"),
        ("直接后继" + REP + REP + "或前驱", "直接后继（或前驱"),
        ("两者的查" + REP + REP + "、插入", "两者的查找、插入"),
        ("在删" + REP + REP + REP + "过程中", "在删除过程中"),
        ("则其" + REP + REP + REP + "度范围为", "则其高度范围为"),
    ],
    "11408/origin/2027操作系统/2027操作系统.md": [
        ("进程存在" + REP + REP + "唯一标志", "进程存在的唯一标志"),
        ("转换" + REP + REP + "就绪态", "转换为就绪态"),
        ("才能" + REP + REP + REP + "用 signal()", "才能调用 signal()"),
        ("页面的大" + REP + REP + "，所以", "页面的大小，所以"),
        ("数据" + REP + REP + "构。", "数据结构。"),
        ("发起请" + REP + REP + "的进程", "发起请求的进程"),
        ("数据文" + REP + REP + REP + "的目录", "数据文件的目录"),
        ("① " + REP + REP + "高了 I/O", "① 提高了 I/O"),
        ("考点追踪 " + "" + " 管程", "考点追踪 管程"),
    ],
    "11408/origin/2027计算机组成原理/2027计算机组成原理.md": [
        ("在机" + REP + REP + REP + "数中", "在机器数中"),
        ("编码" + REP + REP + REP + "位十进制", "编码一位十进制"),
        ("每个" + REP + REP + "道有 12 个扇区", "每个磁道有 12 个扇区"),
        ("计算方法，" + REP + REP + REP + "及CISC", "计算方法，以及CISC"),
        ("第" + REP + REP + REP + "个字节为相对偏移", "第二个字节为相对偏移"),
        ("指令" + REP + REP + "式和寻址", "指令格式和寻址"),
        ("循环读" + REP + REP + REP + "外设", "循环读取外设"),
    ],
    "11408/origin/2027计算机网络/2027计算机网络.md": [
        ("从 A " + REP + REP + REP + "达 B 的时间", "从 A 到达 B 的时间"),
        ("任何站" + REP + REP + "只要收到", "任何站点只要收到"),
        ("再次" + REP + REP + "试重发", "再次尝试重发"),
        ("R1的路由" + REP + REP + "如表4.7", "R1的路由表如表4.7"),
    ],
    "11408/origin/27张宇基础30讲（高数）/27张宇基础30讲（高数）.md": [
        ("函数值" + REP + REP + "排列成数列", "函数值排列成数列"),
    ],
    "11408/origin/27张宇基础30讲线代/27张宇基础30讲线代.md": [
        (REP + REP + REP + "应选(D)", "故应选(D)"),
    ],
}

total = 0
for md, fixes in FIXES.items():
    txt = open(md, encoding="utf-8").read()
    n = 0
    for old, new in fixes:
        if old in txt:
            txt = txt.replace(old, new, 1)
            n += 1
        else:
            print(f"  ⚠ 未命中: {old[:30]}...")
    open(md, "w", encoding="utf-8").write(txt)
    print(f"{md.split('/')[-2]}: 修复 {n} 处")
    total += n
print(f"总计修复 {total} 处")
