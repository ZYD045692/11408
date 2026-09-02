# -*- coding: utf-8 -*-
"""408 四本 origin：代码块整理。
1) 修复相邻重复栅栏（```c\\n```c → ```c）
2) 把未包裹的代码行段包进 ``` 栅栏（跳过：已有栅栏内、HTML 表格内、$$ 数学块内、含 $ 的行、表格行、标题行）
3) 代码段后紧跟的孤儿注释行（//…）并入代码块
默认 dry-run 输出样本；--apply 写盘。语言标签：含汇编助记符→asm，含C信号→c，否则无标签。
"""
import io, os, re, sys, glob, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(ROOT)
APPLY = "--apply" in sys.argv

ASM = re.compile(r"^(mov|movzbl|movl|movw|movb|add|sub|mul|imul|div|idiv|jmp|call|ret|push|pop|lw|sw|slli|srli|srai|cmp|jge|jle|jg|jl|je|jne|ja|jb|jae|jbe|nop|lea|xor|shl|shr|sal|sar|inc|dec|xchg|loop|halt|in|out|ld|st|beq|bne|blt|bge)\b", re.I)
# 软中断指令 int 0x80 / int 21H（int 单独作为 C 关键字太常见，只有这种形态才算汇编）
ASM_INT = re.compile(r"^int\s+(0x[0-9a-fA-F]+|[0-9]+[hH]?)\s*$", re.I)
# 与英文单词撞名的助记符，要求后面跟寄存器/立即数才算汇编
ASM_AMBIG = re.compile(r"^(and|or|not|test|neg|adc|sbb|xadd)\s+(e?[abcds][xip]|[er]?[sb]p|r\d+|[0-9-])", re.I)
CKW = re.compile(r"^(#define|#include|#if|#endif|#pragma|typedef|struct|void|int|char|float|double|long|short|unsigned|signed|bool|return|if|else|for|while|do|switch|case|break|continue|static|const|enum|sizeof|union|extern)\b")
CJK = re.compile(r"[一-鿿]")

def is_asm(l):
    s = l.strip()
    return bool(ASM.match(s) or ASM_INT.match(s) or ASM_AMBIG.match(s))

def is_ckw(l):
    s = l.strip()
    return bool(CKW.match(s)) and not ASM_INT.match(s)

def is_fence(l):
    return l.strip().startswith("```")

def codeish(l):
    s = l.strip()
    if not s or "$" in l or is_fence(l):
        return False
    if s.startswith(("# ", "## ", "### ", "#### ", "##### ", "###### ")) or s.startswith("|") or s.startswith("<"):
        return False
    if s.startswith("【"):                       # 题注行（【2020 统考真题】…）
        return False
    if re.match(r"^[A-D][.、．]\s", s):          # 选择题选项行
        return False
    if CJK.search(s) and re.search(r"[÷×]", s):  # 含 ÷× 的是计算步骤不是代码
        return False
    if re.search(r"(?<!:)//", s) or "/*" in s:   # 排除 http:// 里的 //
        return True
    if CKW.match(s) and not ASM_INT.match(s):
        return True
    if is_asm(s):
        return True
    if re.search(r"(->|\+\+|--)[^>+-]?", s) and not CJK.search(s.split("//")[0]):
        return True
    if re.search(r"[{};]\s*$|^\}|\{$", s):
        return True
    if re.match(r"^(\s{2,}|\t)\S", l) and re.search(r"[=;{}()\[\]]", s) and not re.match(r"^\d+[）.]", s):
        return True
    if re.search(r"\)\s*;?\s*$", s) and re.match(r"^\w[\w\s]*\(", s) and not CJK.search(s):
        return True
    return False

def orphan_comment(l):
    return bool(re.match(r"^\s*//\S", l)) and not codeish(l)

def is_ellipsis(l):
    return l.strip() in ("...", "…", "……", "⋮", "︙")

def pseudoish(l):
    """中文伪代码步骤行：如「从缓冲区中取出一个产品」「资源足够，分配资源，做一系列相应处理；」"""
    s = l.strip()
    if not s or not CJK.search(s) or "$" in s or len(s) > 40:
        return False
    if re.search(r"[。！？：]", s):
        # 短标签（goto 式，如「叫号：」）仍算伪代码
        if not re.fullmatch(r"[一-鿿A-Za-z]{1,8}：", s):
            return False
    if s.startswith(("#", "|", "<", "【", "（", "(", "*", "-", ">")):
        return False
    if re.search(r"\d[.)]|[A-D][.)]", s):   # 题号/选项编号
        return False
    return True

def guess_lang(block):
    text = "\n".join(block)
    asm_n = sum(1 for l in block if is_asm(l))
    ckw_n = sum(1 for l in block if is_ckw(l))
    if ckw_n:
        return "c"
    if asm_n and asm_n >= max(1, len(block) // 2):
        return "asm"
    if re.search(r"[;{}]|//|/\*|typedef|#define|#include|->|malloc|printf|scanf|\breturn\b", text):
        return "c"
    if asm_n:
        return "asm"
    return ""

def fix_file(path):
    lines = open(path, encoding="utf-8").read().split("\n")
    # ---- 第1步：相邻重复栅栏合并 ----
    out, i, dup_fixed = [], 0, 0
    while i < len(lines):
        if is_fence(lines[i]) and i + 1 < len(lines) and is_fence(lines[i + 1]):
            out.append(lines[i]); i += 2; dup_fixed += 1
            continue
        out.append(lines[i]); i += 1
    lines = out

    # ---- 第2步：状态扫描 + 包裹 ----
    result, i, n = [], 0, len(lines)
    in_fence = in_math = in_table = False
    blocks = []
    while i < n:
        l = lines[i]
        if is_fence(l):
            in_fence = not in_fence
            result.append(l); i += 1; continue
        if not in_fence:
            if "<table" in l: in_table = True
            if "</table>" in l: in_table = False
            dd = l.count("$$")
            if dd % 2 == 1: in_math = not in_math
            if not in_table and not in_math and codeish(l):
                # 收集代码段
                blk = [l]; j = i + 1
                while j < n:
                    l2 = lines[j]
                    if is_fence(l2) or "<table" in l2 or "$" in l2:
                        break
                    if codeish(l2):
                        blk.append(l2); j += 1; continue
                    # 黏合区：空行(≤2)/中文伪代码步骤/省略号，若向后落到代码行则整段并入
                    k2, blanks, ok = j, 0, False
                    while k2 < n:
                        l3 = lines[k2]
                        if is_fence(l3) or "<table" in l3 or "$" in l3:
                            break
                        if codeish(l3):
                            ok = True; break
                        s3 = l3.strip()
                        if not s3:
                            blanks += 1
                            if blanks > 2: break
                        elif not (is_ellipsis(l3) or pseudoish(l3)):
                            break
                        k2 += 1
                    if ok:
                        blk.extend(lines[j:k2 + 1]); j = k2 + 1; continue
                    break
                # 并入紧随的孤儿注释（允许隔一个空行；含 $ 的注释说明夹带数学，不能进栅栏）
                k = j
                while k < n and not lines[k].strip(): k += 1
                orph = []
                while k < n and re.match(r"^\s*//\S", lines[k]) and "$" not in lines[k]:
                    orph.append(lines[k]); k += 1
                if orph and len(orph) <= 4:
                    blk.extend(lines[j:k])  # 连空行一起并入，不丢行
                    j = k
                strong = len(blk) >= 2 or re.search(r"[;}{]\s*$|//|^\s*#", blk[0])
                # 单行且以 (4) 之类的枚举编号开头 → 是题目小问不是代码块起点，不包
                if len(blk) == 1 and re.match(r"^[（(【]?\d{1,2}[）).、]\s*\S", blk[0].strip()):
                    strong = False
                # 单行且只有括号/分号字符（OCR 残留的公式碎片，如 }、\}）→ 不包
                if len(blk) == 1 and re.fullmatch(r"[}\]){(;\\\s]+", blk[0].strip()):
                    strong = False
                # 单行纯中文句（除末尾分号外无代码运算符）→ 是正文描述不是代码
                if (len(blk) == 1 and CJK.search(blk[0])
                        and not re.search(r"[=(){}<>+*/&|]|//|->", blk[0])):
                    strong = False
                # 紧跟在已有栅栏收尾 ``` 之后的 }/注释尾巴 → 不新建栅栏，保持原样
                if strong and blk[0].strip().startswith("}"):
                    p = len(result) - 1
                    while p >= 0 and not result[p].strip(): p -= 1
                    if p >= 0 and result[p].strip() == "```":
                        strong = False
                if strong:
                    lang = guess_lang(blk)
                    blocks.append((i + 1, blk, lang))
                    result.append("```" + lang); result.extend(blk); result.append("```")
                    i = j; continue
                # 不包：整段原样回吐（避免块内代码行被二次扫描又包成碎栅栏）
                result.extend(blk); i = j; continue
        result.append(l); i += 1
    return lines, result, dup_fixed, blocks

tot_blk = 0
for f in sorted(glob.glob("11408/origin/2027*/*.md")):
    lines, result, dup, blocks = fix_file(f)
    # 安全断言：剥掉栅栏行后内容序列必须与原文件完全一致（只允许新增栅栏/合并重复栅栏）
    assert [x for x in result if not is_fence(x)] == [x for x in lines if not is_fence(x)], f"内容行不一致: {f}"
    sizes = collections.Counter(min(len(b), 10) for _, b, _ in blocks)
    print(f"{os.path.basename(f)}: 重复栅栏修复={dup} 新包裹代码块={len(blocks)} 行数分布(截10)={dict(sorted(sizes.items()))}")
    tot_blk += len(blocks)
    if not APPLY:
        for ln, blk, lang in blocks[:4]:
            print(f"  ── 块@行{ln} ```{lang}")
            for bl in blk[:6]:
                print("   ", bl[:88])
            if len(blk) > 6: print("    …")
        # 调试：`}` 开头的块（疑似从已有栅栏里掉出来的收尾），打印前文
        brace_blocks = [(ln, b, lg) for ln, b, lg in blocks if b[0].strip().startswith("}")]
        singles = [(ln, b, lg) for ln, b, lg in blocks if len(b) == 1]
        if brace_blocks:
            print(f"  ⚠ `}}`开头块 {len(brace_blocks)} 个：")
            for ln, blk, lang in brace_blocks[:6]:
                print(f"   ── @行{ln} ```{lang} 前文：")
                for pl in lines[max(0, ln - 7):ln - 1]:
                    print("    |", pl[:88])
                for bl in blk[:4]:
                    print("    >", bl[:88])
        print(f"  单行块 {len(singles)} 个，样本：")
        for ln, blk, lang in singles[:6]:
            print(f"   @{ln} ```{lang} {blk[0][:80]}")
    elif len(result) != len(lines) or dup:
        open(f, "w", encoding="utf-8", newline="\n").write("\n".join(result))
print("总代码块:", tot_blk, "| 模式:", "APPLY" if APPLY else "dry-run")
