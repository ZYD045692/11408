# -*- coding: utf-8 -*-
"""李良概统 origin 例题题目化：`【例N.M】题干` / `【例】题干` → `#### 例N.M` / `#### 例` 标题，题干留正文。

- 强化篇带编号：`【例1.27】...` → `#### 例1.27`（题干拆下一行）
- 基础篇无编号：`【例】...` → `#### 例`（题干拆下一行）
- 例题通常在 `### 精选例题` 之下 → 例标题 H4（`####`）
- 跳过代码围栏 / $$ 块内；备份到 _vlm/md_backup/
- 转换量断言（防误判），全部匹配才写盘；幂等（已有 `#### 例` 标题则跳过该编号）
"""
import glob, io, os, re, shutil, sys, time

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
BACKUP = os.path.join(ROOT, "_vlm", "md_backup", "liang_ti_" + time.strftime("%Y%m%d%H%M"))

# 每章各例题计数（转换前扫描，数量断言）
EXPECT = {
    "27李良概统基础": {"第一章-随机事件和概率.md": 36, "第二章-一维随机变量及其分布.md": 34,
                     "第三章-多维随机变量及其分布.md": 37, "第四章-数字特征.md": 27,
                     "第五章-大数定律和中心极限定理.md": 6, "第六章-数理统计的基本概念.md": 17,
                     "第七章-参数估计与假设检验.md": 19},
    "27李良概统强化": {"第一章-随机事件和概率.md": 30, "第二章-一维随机变量及其分布.md": 31,
                     "第三章-多维随机变量及其分布.md": 29, "第四章-数字特征.md": 36,
                     "第五章-大数定律和中心极限定理.md": 9, "第六章-数理统计的基本概念.md": 18,
                     "第七章-参数估计与假设检验.md": 16},
}

HEAD_RE = re.compile(r"^(#{1,6})\s+")

def transform(md):
    lines = open(md, encoding="utf-8").read().split("\n")
    out = []
    in_code = in_math = False
    n = 0
    last_title_lvl = 2
    for s in lines:
        t = s.strip()
        if t.startswith("```"):
            in_code = not in_code; out.append(s); continue
        if in_code:
            out.append(s); continue
        if s.count("$$") % 2 == 1:
            in_math = not in_math; out.append(s); continue
        if in_math:
            out.append(s); continue
        m = HEAD_RE.match(s)
        if m:
            last_title_lvl = len(m.group(1))
            out.append(s); continue
        # 例题行：强化 【例N.M】 / 基础 【例】
        m = re.match(r"【例\s*(\d+\.\d+)】\s*(.*)$", s)
        if m:
            num, body = m.groups()
            out.append("#### 例%s" % num)
            if body.strip():
                out.append("")
                out.append(body.strip())
            n += 1
            continue
        m = re.match(r"【例】\s*(.*)$", s)
        if m:
            body = m.group(1)
            out.append("#### 例")
            if body.strip():
                out.append("")
                out.append(body.strip())
            n += 1
            continue
        out.append(s)
    return out, n

def main():
    ok_files = 0
    for odir, fmap in EXPECT.items():
        src_dir = os.path.join(ROOT, "11408", "origin", odir)
        for fname, expect in fmap.items():
            md = os.path.join(src_dir, fname)
            lines = open(md, encoding="utf-8").read().split("\n")
            # 幂等：已有 `#### 例` 标题则跳过
            already = sum(1 for ln in lines if re.match(r"^#### 例", ln))
            if already:
                print("SKIP %s (已转换 %d)" % (fname, already))
                continue
            # 备份
            os.makedirs(BACKUP, exist_ok=True)
            shutil.copy(md, os.path.join(BACKUP, fname))
            out, n = transform(md)
            assert n == expect, "%s 例题数 %d != 预期 %d，不写盘（已备份）" % (fname, n, expect)
            open(md, "w", encoding="utf-8", newline="\n").write("\n".join(out))
            print("✓ %s: 转 %d 个例题标题" % (fname, n))
            ok_files += 1
    print("完成 %d 个文件，备份于 %s" % (ok_files, BACKUP))

if __name__ == "__main__":
    main()