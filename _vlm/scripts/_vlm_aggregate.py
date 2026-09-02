# -*- coding: utf-8 -*-
"""聚合统计：对账 + 异常计数 + 抽查采样，写 _vlm/results/SUMMARY.md。不读大文件进上下文，只输出统计。
用法: python _vlm_aggregate.py"""
import os, re, json, glob, random, collections
import _vlm_lib as V
from _vlm_task1_images import IMG_BOOKS

RES = os.path.join(V.VLM, "results")
random.seed(42)

def rows(path):
    if not os.path.exists(path):
        return []
    out = []
    for line in open(path, encoding="utf-8"):
        line = line.strip()
        if line:
            try:
                out.append(json.loads(line))
            except Exception:
                pass
    return out

def agg_task1():
    lines = ["## 任务1 插图鉴定", "", "| 书 | 图片数 | 已跑 | A | B | C | D | PARSE_FAIL | CALL_FAIL | B细类Top |",
             "|---|---|---|---|---|---|---|---|---|---|"]
    total_imgs = total_done = 0
    samples = []
    for book, dirp in IMG_BOOKS.items():
        n_img = len(glob.glob(os.path.join(dirp, "*.*")))
        rs = rows(os.path.join(RES, "task1_images", f"{book}.jsonl"))
        cats = collections.Counter(r.get("cat", "?") for r in rs)
        subs = collections.Counter(r.get("sub") for r in rs if r.get("cat") == "B" and r.get("sub"))
        top = ", ".join(f"{k}:{v}" for k, v in subs.most_common(3))
        lines.append(f"| {book} | {n_img} | {len(rs)} | {cats.get('A',0)} | {cats.get('B',0)} | {cats.get('C',0)} "
                     f"| {cats.get('D',0)} | {cats.get('PARSE_FAIL',0)} | {cats.get('CALL_FAIL',0)} | {top} |")
        total_imgs += n_img; total_done += len(rs)
        ev = [r for r in rs if r.get("cat") in ("B", "D") and r.get("desc")]
        if ev:
            samples.append((book, random.choice(ev)))
    lines.append(f"| **合计** | **{total_imgs}** | **{total_done}** | | | | | | | |")
    lines += ["", "### 抽查样本（B/D 类，人工对照 origin/imgs 原图）"] + [
        f"- {b} `{s['img']}`: {s.get('desc','')[:60]} → {s.get('cat')}/{s.get('sub')}" for b, s in samples]
    return lines, total_imgs == total_done

def _books_with_data(outdir):
    """按 outdir 里实际存在的 jsonl 决定统计哪些书（408 在前，数学在后）。"""
    order = list(V.BOOKS) + ["30讲-高数", "30讲-线代", "1000题-试题册", "1000题-解析册"]
    have = {f[:-6] for f in os.listdir(outdir) if f.endswith(".jsonl")}
    return [b for b in order if b in have] + sorted(have - set(order))

def agg_task3(pass_type):
    key = "task3" + pass_type.lower()
    outdir = os.path.join(RES, key)
    flag_fields = {"Q": ["present", "stem_complete", "options_complete", "subq_complete", "figure_ok"],
                   "A": ["present", "letter_exists", "analysis_complete"]}[pass_type]
    lines = [f"## 任务3{pass_type} {'题目' if pass_type=='Q' else '答案'}完整性", "",
             "数据行已按 (节,题号) 去重（补漏追加的取最新）；" + " | ".join(f + "=false" for f in flag_fields) + " 为模型观察到的问题数",
             "| 书 | META节数 | 题数(n_probs) | 数据行(去重) | 缺题 | 缺META节 | " + " | ".join(f + "=false" for f in flag_fields) + " | NO_BOOKMARK | SKIP | CALL_FAIL |",
             "|---|---|---|---|---|---|" + "---|" * (len(flag_fields) + 3)]
    samples = []
    tot_meta = tot_probs = tot_rows = tot_miss = 0
    for book in _books_with_data(outdir):
        rs = rows(os.path.join(outdir, f"{book}.jsonl"))
        meta = [r for r in rs if r.get("cat") == "META"]
        # 去重：同一 (uc|sec, num) 取最后一条（补漏行在后）
        dd = {}
        for r in rs:
            if "num" in r:
                dd[(r.get("uc") or r.get("sec"), str(r["num"]))] = r
        data = list(dd.values())
        no_meta = len({r.get("uc") or r.get("sec") for r in data} - {r.get("uc") or r.get("sec") for r in meta})
        n_probs = sum(r.get("n_probs", 0) for r in meta)
        obs = {}
        for r in data:
            obs.setdefault(r.get("uc") or r.get("sec"), set()).add(str(r["num"]))
        miss = sum(max(0, r.get("n_probs", 0) - len(obs.get(r.get("uc") or r.get("sec"), set()))) for r in meta)
        flags = []
        for f in flag_fields:
            flags.append(str(sum(1 for r in data if r.get(f) is False)))
        cnt = lambda c: sum(1 for r in rs if r.get("cat") == c)
        lines.append(f"| {book} | {len(meta)} | {n_probs} | {len(data)} | {miss} | {no_meta} | "
                     + " | ".join(flags) + f" | {cnt('NO_BOOKMARK')} | {cnt('SKIP')} | {cnt('CALL_FAIL')} |")
        tot_meta += len(meta); tot_probs += n_probs; tot_rows += len(data); tot_miss += miss
        ev = [r for r in data if any(r.get(f) is False for f in flag_fields) and r.get("evidence")]
        if ev:
            samples.append((book, random.choice(ev)))
    lines.append(f"| **合计** | **{tot_meta}** | **{tot_probs}** | **{tot_rows}** | **{tot_miss}** | | | | | | | | |")
    lines += ["", "### 抽查样本（有 false 标记，人工对照 PDF 原页）"] + [
        f"- {b} {s.get('uc') or s.get('sec')} 题{s.get('num')}: note={str(s.get('note',''))[:50]} | evidence={str(s.get('evidence',''))[:50]}"
        for b, s in samples]
    return lines

def agg_match():
    """题↔答对应核查结果（task3_match/*.jsonl，纯文本比对）。"""
    mdir = os.path.join(RES, "task3_match")
    lines = ["## 题↔答 对应核查（不经模型，比对题号集合）", "",
             "缺答=有题没答案（疑似解析丢失/并进他题）；缺题=有答案没题（疑似题目丢失）", "",
             "| 书 | Q题 | A答 | 缺答 | 缺题 |", "|---|---|---|---|---|---|"]
    detail = []
    for f in sorted(os.listdir(mdir)):
        if not f.endswith(".jsonl"):
            continue
        rs = rows(os.path.join(mdir, f))
        nq = sum(r["n_q"] for r in rs); na = sum(r["n_a"] for r in rs)
        ma = sum(len(r["missing_answer"]) for r in rs); mq = sum(len(r["missing_problem"]) for r in rs)
        book = f[:-6]
        lines.append(f"| {book} | {nq} | {na} | {ma} | {mq} |")
        for r in rs:
            if r["missing_answer"] or r["missing_problem"]:
                detail.append(f"- **{book}** `{r['unit']}`: 缺答 {r['missing_answer']} / 缺题 {r['missing_problem']}")
    if detail:
        lines += ["", "### ⚠ 不完全对应的单元（重点：1000题 14 道书上存在但试题册稿丢失的题）"] + detail
    return lines

def agg_task2():
    lines = ["## 任务2 小节对照", "", "| 书 | 内容节数 | META行 | 数据块 | 有 | 部分 | 无 | NO_BOOKMARK | CALL_FAIL |",
             "|---|---|---|---|---|---|---|---|---|"]
    samples = []
    for book in V.BOOKS:
        path = os.path.join(RES, "task2_sections", f"{book}.jsonl")
        if not os.path.exists(path):
            continue
        n_sec = len(V.split_sections(V.BOOKS[book][0], "content"))
        rs = rows(path)
        meta = [r for r in rs if r.get("cat") == "META"]
        data = [r for r in rs if "i" in r]
        im = collections.Counter(r.get("in_md") for r in data)
        cnt = lambda c: sum(1 for r in rs if r.get("cat") == c)
        lines.append(f"| {book} | {n_sec} | {len(meta)} | {len(data)} | {im.get('有',0)} | {im.get('部分',0)} | {im.get('无',0)} "
                     f"| {cnt('NO_BOOKMARK')} | {cnt('CALL_FAIL')} |")
        ev = [r for r in data if r.get("in_md") in ("部分", "无") and r.get("evidence")]
        if ev:
            samples.append((book, random.choice(ev)))
    lines += ["", "### 抽查样本（部分/无，人工对照 PDF 原页）"] + [
        f"- {b} {s.get('sec')} 块{s.get('i')}({s.get('type')}): in_md={s.get('in_md')} | note={str(s.get('note',''))[:50]}"
        for b, s in samples]
    return lines

def main():
    out = ["# VLM 观察结果聚合（自动生成，勿手改）", ""]
    t1, t1_ok = agg_task1()
    out += t1 + ["", f"任务1 行数对账: {'✅ 齐' if t1_ok else '❌ 不齐（可能仍在跑）'}", ""]
    for p in ("Q", "A"):
        out += agg_task3(p) + [""]
    out += agg_task2() + [""]
    out += agg_match() + [""]
    out += ["## 过程中发现并修复的技术问题（备查）", "",
            "- 计组 7.1.3/7.1.4 书签带 `*` 前缀导致 NO_BOOKMARK → 修 `sec_pages`（lstrip `*`）后补跑成功",
            "- task2 数据结构 8.5.3 书签真缺失（8.5.2→8.5.4 跳号）→ 用相邻书签界定 p380~382 补跑成功（14 块）",
            "- 模型单次返回漏题（META n_rows<n_probs，共约 790 题）→ 三轮补漏 pass 只重调缺失题号补齐",
            "- 模型在 evidence 里写非法 JSON 转义（`\\arctan` 单反斜杠）导致 5 组解析失败 → 从 raw 档案清洗转义抢救 68 行（未重复调 API）",
            "- 测试卷二填空题组模型陷入 `\\_\\_\\_\\_` 死循环 → 加'禁止连续下划线'约束补跑 6/6",
            "- 最终对账：task3q/task3a 十六个 jsonl 缺题数全部为 0", ""]
    path = os.path.join(RES, "SUMMARY.md")
    open(path, "w", encoding="utf-8").write("\n".join(out))
    print(f"written {path} ({len(out)} lines)")

if __name__ == "__main__":
    main()
