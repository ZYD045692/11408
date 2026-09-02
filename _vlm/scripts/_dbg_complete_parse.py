# -*- coding: utf-8 -*-
"""调试：对 complete.jsonl 里 content 为空的行单独跑 parse_one"""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from _repair_complete import parse_one

for line in open("repair/complete.jsonl", encoding="utf-8"):
    line = line.strip()
    if not line:
        continue
    try:
        r = json.loads(line)
    except Exception:
        continue
    if r.get("content"):
        continue
    raw = r.get("raw") or ""
    j = parse_one(raw)
    if j is None:
        info = None
    else:
        info = {"keys": list(j.keys()), "clen": len(str(j.get("content", ""))), "trunc": j.get("truncated")}
    print("rid", r["rid"], "raw_len", len(raw), "-> parse:", info)
    if j is not None and not str(j.get("content", "")):
        print("   j =", repr(j)[:300])
        print("   raw_head =", repr(raw[:200]))
