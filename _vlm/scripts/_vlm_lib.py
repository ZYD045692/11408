# -*- coding: utf-8 -*-
"""VLM 流水线公共库：客户端(限速/重试)、JSONL 断点续跑、PDF 渲染、JSON 解析。"""
import os, re, json, time, base64, threading, collections, io, sys
import requests
import fitz

VLM = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # _vlm/ 目录
ROOT = os.path.dirname(VLM)                                          # vault 根目录
if sys.stdout is not None and hasattr(sys.stdout, "buffer") and (sys.stdout.encoding or "").lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

def load_config():
    cfg = json.load(open(os.path.join(VLM, "config.json"), encoding="utf-8"))
    key = os.environ.get("SILICONFLOW_API_KEY")
    envf = os.path.join(VLM, ".env")
    if not key and os.path.exists(envf):
        for line in open(envf, encoding="utf-8"):
            if line.startswith("SILICONFLOW_API_KEY="):
                key = line.strip().split("=", 1)[1]
    cfg["api_key"] = key
    assert key, "缺少 API key（_vlm/.env 或环境变量 SILICONFLOW_API_KEY）"
    return cfg

CFG = None
def cfg():
    global CFG
    if CFG is None:
        CFG = load_config()
    return CFG

# ---------- TPM/RPM 限速（滑动窗口，按 usage 实际值记账） ----------
class RateLimiter:
    def __init__(self, tpm, rpm):
        self.tpm, self.rpm = tpm, rpm
        self.events = collections.deque()   # (ts, tokens)
        self.lock = threading.Lock()
    def acquire(self, est_tokens):
        while True:
            with self.lock:
                now = time.time()
                while self.events and now - self.events[0][0] > 60:
                    self.events.popleft()
                used = sum(t for _, t in self.events)
                n_req = len(self.events)
                if used + est_tokens <= self.tpm and n_req + 1 <= self.rpm:
                    self.events.append((now, est_tokens))
                    return
                wait = 60 - (now - self.events[0][0]) + 0.5 if self.events else 1.0
            time.sleep(wait)   # 锁外睡眠，避免递归加锁死锁
    def settle(self, est_tokens, real_tokens):
        """用真实 usage 修正记账（追加差额）"""
        diff = real_tokens - est_tokens
        if diff > 0:
            with self.lock:
                self.events.append((time.time(), diff))

_limiter = None
def limiter():
    global _limiter
    if _limiter is None:
        c = cfg()
        _limiter = RateLimiter(c["tpm_limit"], c["rpm_limit"])
    return _limiter

# ---------- 客户端 ----------
def b64_image(path):
    ext = os.path.splitext(path)[1].lower().lstrip(".")
    mime = {"jpg": "image/jpeg", "jpeg": "image/jpeg", "png": "image/png", "webp": "image/webp"}.get(ext, "image/jpeg")
    with open(path, "rb") as f:
        return f"data:{mime};base64," + base64.b64encode(f.read()).decode()

def chat(prompt, images=None, max_tokens=4000, tag="", thinking=False):
    """prompt: str; images: [path]。返回 (text, usage_total_tokens)"""
    c = cfg()
    content = [{"type": "text", "text": prompt}]
    for p in images or []:
        content.append({"type": "image_url", "image_url": {"url": b64_image(p)}})
    est = 600 + len(prompt) // 2 + 1300 * len(images or [])
    last_err = None
    for attempt in range(c["max_retries"]):
        limiter().acquire(est)
        try:
            r = requests.post(
                c["base_url"] + "/chat/completions",
                headers={"Authorization": "Bearer " + c["api_key"], "Content-Type": "application/json"},
                json={"model": c["model"], "messages": [{"role": "user", "content": content}],
                      "max_tokens": max_tokens, "temperature": 0.0,
                      "enable_thinking": thinking},
                timeout=c["timeout"])
            if r.status_code == 200:
                j = r.json()
                usage = j.get("usage", {}).get("total_tokens", est)
                limiter().settle(est, usage)
                return j["choices"][0]["message"]["content"], usage
            last_err = f"HTTP {r.status_code}: {r.text[:200]}"
        except Exception as e:
            last_err = f"{type(e).__name__}: {e}"
        sleep_s = min(2 ** attempt * 5, 60)
        log(f"[retry {attempt+1}] {tag} {last_err} -> sleep {sleep_s}s")
        time.sleep(sleep_s)
    raise RuntimeError(f"调用失败({c['max_retries']}次): {tag} | {last_err}")

# ---------- JSON 解析（容错：截取首个 { 或 [） ----------
def parse_json(text):
    text = text.strip()
    text = re.sub(r"^```(json)?|```$", "", text, flags=re.M).strip()
    for i, ch in enumerate(text):
        if ch in "{[":
            for end in range(len(text), i, -1):
                try:
                    return json.loads(text[i:end])
                except Exception:
                    continue
            break
    return None

# ---------- JSONL 断点续跑 ----------
def load_done(path, key):
    done = set()
    if os.path.exists(path):
        for line in open(path, encoding="utf-8"):
            line = line.strip()
            if not line:
                continue
            try:
                done.add(str(json.loads(line)[key]))
            except Exception:
                continue
    return done

_append_lock = threading.Lock()
def append_jsonl(path, obj):
    with _append_lock:
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(obj, ensure_ascii=False) + "\n")

# ---------- 日志 ----------
def log(msg):
    line = time.strftime("[%H:%M:%S] ") + str(msg)
    try:
        print(line, flush=True)
    except Exception:
        pass
    os.makedirs(os.path.join(VLM, "logs"), exist_ok=True)
    with open(os.path.join(VLM, "logs", "run.log"), "a", encoding="utf-8") as f:
        f.write(line + "\n")

# ---------- PDF 渲染（叠加页码标签） ----------
_render_lock = threading.Lock()
def render_pages(pdf_path, page_nos, out_dir, dpi=None, tag=""):
    """page_nos: 0-based。返回 [图片路径]。文件已存在则复用。多线程安全（全局渲染锁）。"""
    with _render_lock:
        dpi = dpi or cfg()["dpi"]
        os.makedirs(out_dir, exist_ok=True)
        doc = fitz.open(pdf_path)
        out = []
        for p in page_nos:
            p = max(0, min(p, doc.page_count - 1))
            fp = os.path.join(out_dir, f"{tag}_p{p+1}.jpg")
            if not os.path.exists(fp):
                pg = doc[p]
                pix = pg.get_pixmap(dpi=dpi)
                pg.insert_text((36, 24), f"PDF p{p+1}", fontsize=14, color=(1, 0, 0))
                pix = pg.get_pixmap(dpi=dpi)
                pix.save(fp, jpg_quality=80)
            out.append(fp)
        doc.close()
        return out

def pdf_toc(pdf_path):
    doc = fitz.open(pdf_path)
    toc = doc.get_toc()   # [[lvl, title, page1based], ...]
    n = doc.page_count
    doc.close()
    return toc, n

# ---------- origin 小节切分 ----------
BOOKS = {
    "数据结构": ("11408/origin/2027数据结构/2027数据结构.md", "11408/pdf/2027数据结构_高清带书签版.pdf"),
    "操作系统": ("11408/origin/2027操作系统/2027操作系统.md", "11408/pdf/2027操作系统-高清带书签.pdf"),
    "计算机组成原理": ("11408/origin/2027计算机组成原理/2027计算机组成原理.md", "11408/pdf/2027计算机组成原理_高清带书签版.pdf"),
    "计算机网络": ("11408/origin/2027计算机网络/2027计算机网络.md", "11408/pdf/2027计算机网络_高清带书签版.pdf"),
}
BOOKS = {k: (os.path.join(ROOT, md), os.path.join(ROOT, pdf)) for k, (md, pdf) in BOOKS.items()}

def split_sections(md_path, kinds):
    """kinds: 'exercise'|'content'。返回 [{sec:'1.2.3', name, kind:'Q'|'A'|'C', text}]"""
    lines = open(md_path, encoding="utf-8").read().split("\n")
    heads = []   # (line_idx, sec, name, kind)
    for i, l in enumerate(lines):
        m = re.match(r"^### (\d+\.\d+\.\d+)\s+(.*)$", l.strip())
        if not m:
            continue
        sec, name = m.group(1), m.group(2).strip()
        if re.search(r"(本节试题精选|本节习题精选)", name):
            kind = "Q"
        elif "答案与解析" in name:
            kind = "A"
        else:
            kind = "C"
        heads.append((i, sec, name, kind))
    out = []
    for k, (i, sec, name, kind) in enumerate(heads):
        if kinds == "exercise" and kind not in ("Q", "A"):
            continue
        if kinds == "content" and kind != "C":
            continue
        j = heads[k + 1][0] if k + 1 < len(heads) else len(lines)
        # 内容节在遇到 ## / # 时也应截断
        block = []
        for l in lines[i + 1:j]:
            if re.match(r"^#{1,2} ", l.strip()):
                break
            block.append(l)
        out.append({"sec": sec, "name": name, "kind": kind, "text": "\n".join(block).strip()})
    return out

def split_problems(section_text):
    """按 ##### NN 标题切成 {num: text}；前言部分挂在前一题(或 'pre')。"""
    parts = re.split(r"(?m)^(##### \d{1,2})\s*$", section_text)
    probs = {}
    pre = parts[0]
    for k in range(1, len(parts), 2):
        num = parts[k].split()[-1]
        body = (parts[k + 1] or "").strip()
        probs[num] = body
    return probs, pre.strip()

def sec_pages(toc, sec):
    """从书签找小节页范围（0-based, 含端点）。end=下一个 X.Y.Z 级书签所在页(小节内容可能跨到该页)。
    跳过小节内部的题型子书签(如'一、单项选择题')。找不到返回 None。"""
    idx = None
    for i, (lvl, title, page) in enumerate(toc):
        t = title.strip().replace(" ", "").lstrip("*")
        if t.startswith(sec):
            idx = i
            break
    if idx is None:
        return None
    start = toc[idx][2] - 1
    end = start
    for j in range(idx + 1, len(toc)):
        t = toc[j][1].strip().replace(" ", "").lstrip("*")
        if re.match(r"^\d+\.\d+\.\d+", t):   # 下一个节级书签
            end = toc[j][2] - 1
            break
    return start, max(end, start)
