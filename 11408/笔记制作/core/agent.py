# -*- coding: utf-8 -*-
"""Agent：只发请求，不含任何业务逻辑。

- 配置：base_url / api_key / model / enable_thinking / timeout / max_retries 全部来自 config。
- 限速：滑动窗口 TPM/RPM（按 usage 真实值记账修正）；每模型限额从 notes_config.json 的 models 注册表读取。
- json_mode：默认带 response_format={"type":"json_object"}；模型不支持时服务端报 4xx/5xx → 自动降级普通请求再试。
- 重试：指数退避（2^n*5 封顶 60s）。线程安全（limiter 自带锁）。
"""
import collections, threading, time
import requests
from .config import log

class RateLimiter:
    """滑动窗口限速（TPM/RPM 双限）。

    acquire() 预扣 est 并返回一张"凭证" rid；settle(rid, real) 用真实 usage
    替换该凭证占用的预扣（并发同 est 也不串）。窗口 60s 滑动过期。
    """
    def __init__(self, tpm, rpm):
        self.tpm, self.rpm = tpm, rpm
        self.events = collections.deque()   # (ts, tokens_used, rid)
        self._rid = 0
        self.lock = threading.Lock()

    def _sweep(self, now):
        while self.events and now - self.events[0][0] > 60:
            self.events.popleft()

    def acquire(self, est_tokens, max_wait=300):
        """预扣 est。窗口放行则返回 rid，否则等待（最长 max_wait，超时抛 TimeoutError）。"""
        deadline = time.time() + max_wait
        while True:
            with self.lock:
                now = time.time()
                self._sweep(now)
                used = sum(t for _, t, _ in self.events)
                n_req = len(self.events)
                if used + est_tokens <= self.tpm and n_req + 1 <= self.rpm:
                    self._rid += 1
                    self.events.append((now, est_tokens, self._rid))
                    return self._rid
                if time.time() >= deadline:
                    raise TimeoutError(
                        f"限速窗口 {max_wait}s 内未放行 (used={used}/{self.tpm}, req={n_req}/{self.rpm})")
                wait = min(60 - (now - self.events[0][0]) + 0.5 if self.events else 1.0,
                           deadline - time.time())
            time.sleep(wait)   # 锁外睡眠，避免递归加锁死锁

    def settle(self, rid, real_tokens):
        """用真实 usage 替换 rid 这条预扣（record 已是预扣值则替换，多退少补不重复计）。"""
        with self.lock:
            now = time.time()
            for i, (ts, tok, r) in enumerate(self.events):
                if r == rid:
                    if real_tokens > 0:
                        self.events[i] = (now, real_tokens, rid)
                    else:
                        del self.events[i]
                    return
            # 凭证已被窗口淘汰：直接补记真实消耗
            if real_tokens > 0:
                self.events.append((now, real_tokens, -1))


def _request_timeout(c):
    """(连接超时, 读超时)：连接 15s 连不上立即失败；读超时沿用配置 timeout 兜底。
    requests 的 timeout 只传一个数字时是"单一超时"——连接阶段也可能干等整段，
    之前出现过请求挂死十几分钟不返回的情况。"""
    return (15, c.get("timeout", 300))


class Agent:
    def __init__(self, cfg):
        self.cfg = cfg
        m = cfg["model"]
        spec = (cfg.get("models") or {}).get(m) or {}
        rpm = spec.get("rpm") or cfg.get("rpm")
        tpm = spec.get("tpm") or cfg.get("tpm")
        if not rpm or not tpm:
            log(f"[agent] 警告: model={m} 未在 models 注册表配置 RPM/TPM，使用默认 60 rpm / 60000 tpm")
            rpm, tpm = rpm or 60, tpm or 60000
        self.limiter = RateLimiter(int(tpm), int(rpm))
        log(f"[agent] model={m} rpm={rpm} tpm={tpm} threads={cfg.get('threads')} json_mode=on")

    def chat(self, prompt, *, json_mode=True, max_tokens=None, tag=""):
        """返回 (content, usage_total_tokens)。只发请求，不做任何解析。

        max_tokens 缺省时读配置的 max_tokens（思考模型请给足，否则 content 可能为空：
        官方文档=max_tokens 不含思维链，窗口 128K 建议预留 ~10k 缓冲）。
        """
        c = self.cfg
        max_tokens = max_tokens if max_tokens is not None else c.get("max_tokens", 128000)
        est = 600 + len(prompt) // 2
        last_err = None
        for attempt in range(c.get("max_retries", 5)):
            rid = self.limiter.acquire(est)
            body = {
                "model": c["model"],
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": max_tokens,
                "temperature": 0.0,
                "enable_thinking": bool(c.get("enable_thinking", True)),
            }
            if json_mode:
                body["response_format"] = {"type": "json_object"}
            try:
                r = requests.post(
                    c["base_url"] + "/chat/completions",
                    headers={"Authorization": "Bearer " + c["api_key"], "Content-Type": "application/json"},
                    json=body, timeout=_request_timeout(c))
                if r.status_code == 200:
                    j = r.json()
                    usage = j.get("usage", {}).get("total_tokens", est)
                    self.limiter.settle(rid, usage)
                    msg = j["choices"][0]["message"]
                    # 注意：thinking 模式时 reasoning_content 是思考草稿，不能当正文。
                    # 只要 max_tokens 给够（官方：不含思维链，窗口 128K 应预留 ~10k 缓冲），
                    # content 就会有最终 JSON；content 为空多为 max_tokens 过小。
                    return msg.get("content") or "", usage
                if json_mode and r.status_code in (400, 422, 500):
                    # 模型不支持 response_format → 降级普通请求（不占这次重试额度）
                    body.pop("response_format", None)
                    try:
                        r2 = requests.post(
                            c["base_url"] + "/chat/completions",
                            headers={"Authorization": "Bearer " + c["api_key"], "Content-Type": "application/json"},
                            json=body, timeout=_request_timeout(c))
                        if r2.status_code == 200:
                            j = r2.json()
                            usage = j.get("usage", {}).get("total_tokens", est)
                            self.limiter.settle(rid, usage)
                            msg = j["choices"][0]["message"]
                            return msg.get("content") or "", usage
                        last_err = f"HTTP {r2.status_code}: {r2.text[:200]}"
                    except Exception as e2:
                        last_err = f"{type(e2).__name__}: {e2}"
                last_err = f"HTTP {r.status_code}: {r.text[:200]}"
            except Exception as e:
                last_err = f"{type(e).__name__}: {e}"
            sleep_s = min(2 ** attempt * 5, 60)
            log(f"[retry {attempt+1}] {tag} {last_err} -> sleep {sleep_s}s")
            time.sleep(sleep_s)
        raise RuntimeError(f"调用失败({c.get('max_retries', 5)}次): {tag} | {last_err}")