# -*- coding: utf-8 -*-
"""检查 8 本 origin div 收支平衡"""
import io, sys, re, glob, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

for f in sorted(glob.glob("11408/origin/*/*.md")):
    bal = 0
    for l in open(f, encoding="utf-8"):
        bal += len(re.findall(r"<div\b", l, re.I)) - len(re.findall(r"</div>", l, re.I))
    print(os.path.basename(os.path.dirname(f)), "div收支:", bal)
