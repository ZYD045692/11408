# -*- coding: utf-8 -*-
"""金标校准（GO/NO-GO 全量前必跑）：
任务1: 6 张已知图（2 张附录文字页=B, 4 张结构图=A）
任务3: 合成缺陷注入（数据结构一节 Q 删选项 / 一节 A 并解析），验模型能否观察出来
结果写 _vlm/results/calibration/*.jsonl，终端只打印聚合分数。"""
import os, re, json, copy
import _vlm_lib as V
from _vlm_task1_images import PROMPT as T1_PROMPT
import _vlm_task3_qa as T3

CAL = os.path.join(V.VLM, "results", "calibration")
os.makedirs(CAL, exist_ok=True)

# ---------- 任务1 金标 ----------
# A: origin 里已人工确认的真实插图; B: 现场渲染的书页(本身就是文字截图)
T1_A = [
    "11408/origin/27张宇基础30讲（高数）/imgs/img_120.jpg",   # 结构图
    "11408/origin/27张宇基础30讲（高数）/imgs/img_847.jpg",   # 曲线图
    "11408/origin/2027计算机组成原理/imgs/img_55.jpg",        # Cache结构图
    "11408/origin/2027数据结构/imgs/img_100.jpg",             # 链表图
]
T1_B_SRC = [  # (pdf, 0-based页) 渲染出来当"文字截图"样本
    ("11408/pdf/2027数据结构_高清带书签版.pdf", 59),
    ("11408/pdf/2027计算机组成原理_高清带书签版.pdf", 74),
]

def cal_task1():
    os.makedirs(os.path.join(V.VLM, "pages", "cal"), exist_ok=True)
    cases = [(p, "A") for p in T1_A]
    for pdf, pno in T1_B_SRC:
        img = V.render_pages(pdf, [pno], os.path.join(V.VLM, "pages", "cal"), tag="cal")[0]
        cases.append((img, "B"))
    ok = 0
    for path, expect in cases:
        name = os.path.basename(path)
        text, usage = V.chat(T1_PROMPT, images=[path], max_tokens=400, tag=f"cal1:{name}")
        j = V.parse_json(text) or {}
        got = j.get("cat", "PARSE_FAIL")
        hit = got == expect
        ok += hit
        row = {"img": name, "expect": expect, "got": got, "hit": hit,
               "desc": j.get("desc", ""), "sub": j.get("sub")}
        V.append_jsonl(os.path.join(CAL, "task1.jsonl"), row)
        print(f"  t1 {name}: expect={expect} got={got}/{j.get('sub')} {'✓' if hit else '✗'} | {j.get('desc','')[:40]}")
    print(f"任务1 校准: {ok}/{len(cases)}")
    return ok, len(cases)

# ---------- 任务3 合成缺陷 ----------
def mutate_q_delete_options(text, num):
    """删掉题 num 的选项（兼容单行 'A. x B. y C. z D. w' 与每行一个选项两种排版）"""
    probs, pre = V.split_problems(text)
    body = probs.get(num, "")
    lines = body.split("\n")
    kept, removed = [], 0
    for l in lines:
        s = l.strip()
        if re.match(r"^[A-D]\s*[.、．]", s) and re.search(r"[B-D]\s*[.、．]", s[2:]):
            removed += 1          # 单行四选项，整行删
            continue
        if re.match(r"^[B-D]\s*[.、．]", s):
            removed += 1          # 每行一个选项
            continue
        kept.append(l)
    probs[num] = "\n".join(kept)
    new_text = pre + "\n\n" + "\n\n".join(f"##### {n}\n\n{b}" for n, b in probs.items())
    return new_text, removed

def mutate_a_merge(text, num):
    """把题 num 的答案字母行删除（模拟'解析并入上题'：只剩解析文字跟在字母消失后）"""
    probs, pre = V.split_problems(text)
    body = probs.get(num, "")
    lines = body.split("\n")
    kept = [l for l in lines if not re.match(r"^\s*[A-D]\s*$", l.strip())]
    probs[num] = "\n".join(kept)
    new_text = pre + "\n\n" + "\n\n".join(f"##### {n}\n\n{b}" for n, b in probs.items())
    return new_text, 1

def cal_task3(pass_type):
    book = "数据结构"
    md, pdf = V.BOOKS[book]
    toc, _ = V.pdf_toc(pdf)
    sections = [s for s in V.split_sections(md, "exercise") if s["kind"] == pass_type]
    # 找一题数适中(5~15)的节
    sec = None
    for s in sections:
        probs, _ = V.split_problems(s["text"])
        if 5 <= len(probs) <= 15:
            sec = s
            break
    probs, pre = V.split_problems(sec["text"])
    target = sorted(probs, key=lambda x: int(x))[2]   # 第3道题注入缺陷
    sec2 = copy.deepcopy(sec)
    if pass_type == "Q":
        sec2["text"], n_rm = mutate_q_delete_options(sec["text"], target)
        check = "options_complete"
    else:
        sec2["text"], n_rm = mutate_a_merge(sec["text"], target)
        check = "letter_exists"
    assert n_rm > 0, f"缺陷注入失败(删了0行): {pass_type} {sec['sec']} 题{target}"
    pages = V.sec_pages(toc, sec["sec"])
    start, end = pages
    end = end if end is not None else start
    page_nos = list(range(max(0, start - 1), end + 2))
    imgs = V.render_pages(pdf, page_nos, os.path.join(V.VLM, "pages", book), tag=f"{book[:2]}")
    core = f"p{start+1}~p{end+1}"
    prompt = T3.build_prompt(sec2, probs, pre, core, pass_type)
    text, usage = V.chat(prompt, images=imgs, max_tokens=4000, tag=f"cal3{pass_type}:{sec['sec']}")
    j = V.parse_json(text)
    rows = [r for r in (j if isinstance(j, list) else []) if isinstance(r, dict)]
    hit = miss_info = None
    for r in rows:
        r.update({"cal": True, "sec": sec["sec"], "kind": pass_type, "injected": target})
        V.append_jsonl(os.path.join(CAL, f"task3{pass_type}.jsonl"), r)
        if str(r.get("num", "")).lstrip("0") == target.lstrip("0"):
            flag = r.get(check)
            note = r.get("note", "")
            hit = (flag is False) or (isinstance(note, str) and len(note) > 5)
            miss_info = f"{check}={flag} note={note[:50]}"
    print(f"  t3{pass_type} {sec['sec']} 注入题{target}({check}缺陷): {'✓ 被识别' if hit else '✗ 未识别'} | {miss_info}")
    print(f"     返回行数 {len(rows)}/{len(probs)} 题")
    return bool(hit), len(rows) == len(probs)

if __name__ == "__main__":
    print("=== 任务1 校准 ===")
    o1, n1 = cal_task1()
    print("=== 任务3Q 校准（合成缺陷:删B/C/D选项）===")
    hq, full_q = cal_task3("Q")
    print("=== 任务3A 校准（合成缺陷:删答案字母）===")
    ha, full_a = cal_task3("A")
    print(f"\n汇总: 任务1 {o1}/{n1} | 3Q缺陷识别 {'✓' if hq else '✗'} 行数齐 {'✓' if full_q else '✗'}"
          f" | 3A缺陷识别 {'✓' if ha else '✗'} 行数齐 {'✓' if full_a else '✗'}")
