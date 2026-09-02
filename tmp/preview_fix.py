# -*- coding: utf-8 -*-
"""自包含预览：复制 fix_all/fix_bmatrix 逻辑，不 import 目标模块（避免其修改全局 stdout）。"""
import io, sys, glob, os, re, difflib
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
BS = chr(92)
B2 = BS + BS

def fix_bmatrix(text):
    ENVS = ["bmatrix", "vmatrix", "matrix", "pmatrix", "Bmatrix",
            "cases", "aligned", "split", "array"]
    out = text
    for env in ENVS:
        beg = BS + "begin{" + env + "}"
        end = BS + "end{" + env + "}"
        if beg not in out:
            continue
        chunks = out.split(beg)
        res = [chunks[0]]
        for c in chunks[1:]:
            if end in c:
                head, tail = c.split(end, 1)
                head = head.replace(BS + " ", B2 + " ")
                res.append(beg + head + end + tail)
            else:
                res.append(beg + c)
        out = "".join(res)
    return out

def fix_all(text):
    text = fix_bmatrix(text)
    text = re.sub(B2 + r"(?=[a-zA-Z\[\{])", lambda m: BS, text)
    text = re.sub(BS + r"text\{(∫|≤|≥|±)\}", lambda m: {"∫": BS+"int", "≤": BS+"leq", "≥": BS+"geq", "±": BS+"pm"}[m.group(1)], text)
    for full, cmd in [("∫", "int"), ("≤", "leq"), ("≥", "geq"), ("±", "pm"), ("λ", "lambda")]:
        text = text.replace(full, BS + cmd)
    for old, new in [
        (BS+"intwidehat{", BS+"widehat{"), (BS+"intbegin{", BS+"begin{"), (BS+"intend{", BS+"end{"),
        (BS+"inty=", "y="), (BS+"intalpha", BS+"alpha"), (BS+"intbeta", BS+"beta"),
        (BS+"intold", BS+"old"), (BS+"intleft", BS+"left"),
    ]:
        text = text.replace(old, new)
    for old, new in [
        (BS+"bigpropto", BS+"propto"), (BS+"pmi", BS+"pm i"),
        (BS+"leqM", BS+"leq M"), (BS+"by", ""),
    ]:
        text = text.replace(old, new)
    text = re.sub(B2 + r"(\{[^}]*\})", r"\1", text)
    text = text.replace("1^" + BS + "lim", "1^" + BS + "infty")
    return text

for f in glob.glob(r"d:\obsidian'srepository\my\11408\笔记"+os.sep+"**"+os.sep+"*.md", recursive=True):
    t = open(f, encoding="utf-8").read()
    if "gen:" not in t[:600]:
        continue
    nt = fix_all(t)
    if nt != t:
        rel = os.path.relpath(f, r"d:\obsidian'srepository\my\11408\笔记")
        print("CHG #", rel)
        shown = 0
        for d in difflib.ndiff(t.split("\n"), nt.split("\n")):
            if d.startswith("- ") or d.startswith("+ "):
                mark = "- " if d.startswith("- ") else "+ "
                print("   %s%s" % (mark, d[2:][:110]))
                shown += 1
                if shown >= 16:
                    print("   ...")
                    break
print("DONE")