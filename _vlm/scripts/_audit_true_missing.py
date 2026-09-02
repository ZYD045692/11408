# -*- coding: utf-8 -*-
"""真实少提取审计：origin 非标题内容行在拆分稿中缺失的数量（复用 _verify_fingerprint 的 normalize）"""
import io, sys, re, os, glob, importlib.util
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))

spec = importlib.util.spec_from_file_location("vf", "_verify_fingerprint.py")
# 不 exec 整个脚本（它会直接跑），手工复制其 normalize/NOISE
NOISE = re.compile(r"配套课程|配套煤压|联系微信|公众号|考研数学题源探析经典1000题|"
                   r"4\.9元包邮|5分钱|服务自年度|张宇\s*_+|^\.{4,}\d+$|^第\d+章.*\d{2,3}$|^目录$|^视频讲解$")
def normalize(line):
    s = line.strip()
    s = re.sub(r"<[^>]+>", "", s)
    s = re.sub(r"^#+\s*", "", s)
    s = re.sub(r"\$", "", s)
    s = re.sub(r"\s+", "", s)
    s = re.sub(r"[，。、；：？！（）【】《》「」『』·—…“”‘’\"'`~!@#%&,.;:?()\[\]{}\\\|/]", "", s)
    return s
def split_fm(content):
    m = re.match(r"(?s)^\s*---\s*\n.*?\n---\s*\n", content)
    return content[m.end():] if m else content

KEYS = {"30讲-高数": "27张宇基础30讲（高数）", "30讲-线代": "27张宇基础30讲线代"}
for book, key in KEYS.items():
    ofile = glob.glob(os.path.join("11408/origin", f"*{key}*", "*.md"))[0]
    o_fp = {}
    for i, l in enumerate(open(ofile, encoding="utf-8").read().split("\n"), 1):
        s = l.strip()
        if not s or s.startswith("#"):
            continue
        fp = normalize(s)
        if fp and len(fp) >= 3 and fp not in o_fp:
            o_fp[fp] = (i, s)
    s_set = set()
    for f in glob.glob(os.path.join("11408/拆分稿/数学", book, "*.md")):
        for l in split_fm(open(f, encoding="utf-8").read()).split("\n"):
            s = l.strip()
            if not s or s.startswith("#") or s.startswith("---"):
                continue
            fp = normalize(s)
            if fp and len(fp) >= 3:
                s_set.add(fp)
    missing = [(ln, raw) for fp, (ln, raw) in o_fp.items()
               if fp not in s_set and not NOISE.search(fp)]
    print(f"{book}: origin内容行指纹{len(o_fp)} 真·少提取{len(missing)}")
    for ln, raw in missing[:10]:
        print(f"   L{ln}: {raw[:80]}")
