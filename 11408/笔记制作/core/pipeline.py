# -*- coding: utf-8 -*-
"""入口编排：收集任务 → 过滤(gen 断点续跑) → 线程池执行 → 重试 → 落盘 → 汇总/人工清单。

CLI 用法（见 make_notes.py 顶部 docstring）：
  --list    只列任务不调 API
  --pilot   试点数篇（408×2 + 数学讲×1 + 小节×1）
  --all     全量（默认）
  --type    只跑某类：408 | math_lecture | math_section
  --force   忽略已生成强制重跑
  位置参数   课程（数据结构）/ 书（30讲-高数）/ 讲名（第2讲-矩阵）过滤
"""
import io, os, sys, threading, time
from concurrent.futures import ThreadPoolExecutor, as_completed

from .config import cfg, model_tag, log, ROOT, RUNTIME
from .agent import Agent
from .organizers import ORGANIZERS, TYPES
from .parsers import PARSERS
from .parsers.base import already_gen

RETRY_HINT = ("\n\n（上次输出不是合法 JSON，或 LaTeX 定界符 $ 未配对，或闪卡没有放在 points[].cards 中。"
              "这次必须输出严格合法的单个 JSON 对象：不要代码栅栏、不要多余文字，"
              "$ 与 $$ 必须两两配对；每个考点必须自带 cards 数组。）")

_MANUAL_LOCK = threading.Lock()


# ---------- Pilot 固定目标 ----------
def is_pilot(task):
    if task.type == "408":
        return (task.meta["course"], task.meta["sec"]) in (("数据结构", "2.2"), ("操作系统", "1.1"))
    if task.type == "math_lecture":
        return task.meta["name"].startswith("第2讲-矩阵")
    if task.type == "math_section":
        return task.meta["sec"] == "1.1"
    return False


# ---------- 收集 ----------
def collect(pilot=False, only=None, ty=None):
    targets = []
    for t in sorted(TYPES):
        if ty and t != ty:
            continue
        org = ORGANIZERS[t]
        for task in org.scan(only):
            if pilot and not is_pilot(task):
                continue
            if not os.path.exists(task.note_path):
                continue
            targets.append(task)
    return targets


# ---------- raw 留档 ----------
def save_raw(task, job, text):
    """模型原始输出留档到 {raw_dir}/{raw_sub}/{tag}.{stage}.md（raw_dir 相对 vault 根）"""
    c = cfg()
    sub = task.meta.get("raw_sub", "misc")
    rd = c.get("raw_dir", "_notes_runtime/raw").strip("/\\")
    d = os.path.join(ROOT, rd, sub)
    os.makedirs(d, exist_ok=True)
    fname = task.tag.replace(":", "_").replace("/", "-") + ("." + job.stage if job.stage != "main" else "") + ".md"
    open(os.path.join(d, fname), "w", encoding="utf-8", newline="\n").write(text or "")


def append_manual(lines):
    c = cfg()
    path = c.get("manual_list", os.path.join(RUNTIME, "repair", "notes_manual.md"))
    with _MANUAL_LOCK:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "a", encoding="utf-8", newline="\n") as f:
            f.write("\n## 笔记填充待人工（" + time.strftime("%m-%d %H:%M") + "）\n")
            f.write("\n".join(lines) + "\n")


# ---------- 单任务处理 ----------
def process(agent, task):
    """返回 (note_path, ok, ncards, manual_line)"""
    org = ORGANIZERS[task.type]
    psr = PARSERS[task.type]
    manual = []
    stage_results = []
    ok = True

    for job in org.jobs(task):
        data = None
        prompt = job.prompt
        # synth 阶段：用先前各块要点填占位
        if job.is_synth:
            src = org.synth_source(stage_results)
            if not src:
                stage_results.append((job.stage, None))
                ok = False
                continue
            prompt = job.prompt.format(CHUNKS=src)
        for attempt in (0, 1):
            try:
                text, _ = agent.chat(prompt + (RETRY_HINT if attempt else ""),
                                     json_mode=True, max_tokens=job.max_tokens,
                                     tag=f"{task.tag}/{job.stage}")
            except Exception as e:
                log(f"[pipeline] ✗ {task.tag}/{job.stage} 调用异常: {e}")
                manual.append(f"- [ ] {task.note_path} — 模型调用异常 {e}")
                break
            save_raw(task, job, text)
            data = psr.parse(text)
            if data is not None and psr.validate(data) and psr.raw_ok(text):
                break
            if attempt == 0:
                log(f"[pipeline] {task.tag}/{job.stage} 解析/校验未通过，重试")
        stage_results.append((job.stage, data))
        if data is None:
            ok = False

    gen_line = f"{model_tag()}-think" + ("" if ok else "-partial")
    content = ""
    ncards = 0
    try:
        content, ncards = psr.render(task, stage_results, gen_line)
    except Exception as e:
        log(f"[pipeline] ✗ {task.note_path} 渲染失败: {e}")
        ok = False
        manual.append(f"- [ ] {task.note_path} — 模板渲染异常 {e}")

    if ok and content:
        open(task.note_path, "w", encoding="utf-8", newline="\n").write(content)
    elif not ok:
        danger = f"- [ ] {task.note_path} — JSON 解析/$ 配平未完全通过（raw 在 _notes_runtime/raw/{task.meta.get('raw_sub', '')}/）"
        manual.append(danger)
    return task.note_path, ok, ncards, manual


# ---------- 入口 ----------
def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    force = "--force" in argv
    is_list = "--list" in argv
    pilot = "--pilot" in argv
    ty = None
    if "--type" in argv:
        i = argv.index("--type")
        ty = argv[i + 1] if i + 1 < len(argv) else None
        if ty not in TYPES:
            log(f"[pipeline] 未知类型 {ty}，可选: {' '.join(TYPES)}")
            return 1
    only = next((a for a in argv if not a.startswith("--") and a not in (ty or ())), None)

    c = cfg()
    agent = Agent(c)
    targets = collect(pilot=pilot, only=only, ty=ty)

    log(f"[pipeline] 收集任务 {len(targets)} 个（type={ty or '全部'} only={only or '-'} force={force}）")
    if is_list:
        for t in targets:
            mark = "done" if already_gen(t.note_path) else "todo"
            print(f"  [{mark}] {t.type:12s} {t.title:32s} -> {t.note_path}")
        return 0

    todo, manual_all = [], []
    skip = 0
    for t in targets:
        if already_gen(t.note_path) and not force:
            skip += 1
            continue
        todo.append(t)

    done = fail = 0
    n = len(todo)
    if n == 0:
        log(f"[pipeline] 无待生成任务（全部 {skip} 个已生成；--force 可重跑）")
        return 0

    threads = c.get("threads", 4)
    log(f"[pipeline] 开始生成 {n} 个，线程 {threads}")
    with ThreadPoolExecutor(max_workers=threads) as ex:
        futs = {ex.submit(process, agent, t): t for t in todo}
        for fut in as_completed(futs):
            t = futs[fut]
            try:
                note, ok, ncards, manual = fut.result()
            except Exception as e:
                log(f"[pipeline] ✗ {t.tag} 未处理异常: {e}")
                note, ok, ncards, manual = t.note_path, False, 0, [f"- [ ] {t.note_path} — 未处理异常 {e}"]
            done += 1
            log(f"[pipeline] {'✓' if ok else '△'} {t.tag} 闪卡{ncards}张")
            if not ok:
                fail += 1
            manual_all.extend(manual)

    if manual_all:
        append_manual(manual_all)
    log(f"[pipeline] 完成 生成{done} 跳过{skip} 失败{fail}")
    return 0 if fail == 0 else 2


if __name__ == "__main__":
    sys.exit(main())