# -*- coding: utf-8 -*-
"""配置加载：notes_config.json + 顶层 _vlm/.env 的 SILICONFLOW_API_KEY（与 VLM 审计共享的密钥，沿用旧约定，key 不入库）。

运行时产物（raw/repair/logs）不落在 _vlm/ 下，而是统放顶层 _notes_runtime/，
避免与 VLM 审计管线的 own 产物（_vlm/repair、_vlm/logs）混在一起。
"""
import io, json, os, sys, time

CORE = os.path.dirname(os.path.abspath(__file__))                      # 笔记制作/core/
NOTES_DIR = os.path.dirname(CORE)                                      # 笔记制作/
ROOT = os.path.dirname(os.path.dirname(NOTES_DIR))                     # vault 根
VLM = os.path.join(ROOT, "_vlm")                                       # 仅用于读共享 api key
RUNTIME = os.path.join(ROOT, "_notes_runtime")                         # 笔记系统运行时产物根

if sys.stdout is not None and hasattr(sys.stdout, "buffer") and (sys.stdout.encoding or "").lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

BASE_SPLIT = os.path.join(ROOT, "11408", "拆分稿")
BASE_NOTE = os.path.join(ROOT, "11408", "笔记")

def load_config():
    cfg = json.load(open(os.path.join(NOTES_DIR, "notes_config.json"), encoding="utf-8"))
    key = os.environ.get("SILICONFLOW_API_KEY")
    envf = os.path.join(VLM, ".env")
    if not key and os.path.exists(envf):
        for line in open(envf, encoding="utf-8"):
            if line.startswith("SILICONFLOW_API_KEY="):
                key = line.strip().split("=", 1)[1]
    cfg["api_key"] = key
    assert key, "缺少 API key（_vlm/.env 或环境变量 SILICONFLOW_API_KEY）"
    return cfg

_CFG = None
def cfg():
    global _CFG
    if _CFG is None:
        _CFG = load_config()
    return _CFG

def model_tag():
    """模型尾段小写 → frontmatter gen 前缀，如 Qwen/Qwen3.5-35B-A3B -> qwen3.5-35b-a3b"""
    m = (cfg().get("model") or "").split("/")[-1]
    return m.lower()

def log(msg):
    line = time.strftime("[%H:%M:%S] ") + str(msg)
    try:
        print(line, flush=True)
    except Exception:
        pass
    try:
        os.makedirs(os.path.join(RUNTIME, "logs"), exist_ok=True)
        with open(os.path.join(RUNTIME, "logs", "run.log"), "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass