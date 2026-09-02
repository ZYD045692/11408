# -*- coding: utf-8 -*-
"""修复 1000题 新版 origin 的 16 处坏公式（OCR 问题：\\→$、丢括号、中文逗号、\displaylimits、双上标等）"""
import io, sys, os, glob
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

FIXES = {
    "27张宇1000题数一【试题册】": [
        ("f(x^y^2)", "f(x^{y^2})"),
        (r"}{(\ln(1-x\sin x)}", r"}{\ln(1-x\sin x)}"),
        (r"&x\leq0,\$ x+1)\mathrm{e}^x,&x>0\end{case",
         r"&x\leq0,\\ (x+1)\mathrm{e}^x,&x>0\end{cases}$"),
        (r"&x\leq0,\ $x-1)\mathrm{e}^x,&x>0\end{cases}$",
         r"&x\leq0,\\ (x-1)\mathrm{e}^x,&x>0\end{cases}$"),
        (r"=____. $$", r"=\underline{\qquad}. $$"),
        (r"}{\ln(1-x\sin x)}}=$___。", r"}{\ln(1-x\sin x)}=$___。"),
        (r"+1,&x\leq0,\$ x-1)\mathrm{e}^x,&x>0\end{cases} ",
         r"+1,&x\leq0,\\ (x-1)\mathrm{e}^x,&x>0\end{cases} "),
    ],
    "27张宇1000题数一【解析册】": [
        (r"\boldsymbol{B}^{*}\ $ -1)^{n}", r"\boldsymbol{B}^{*}\\ (-1)^{n}"),
        (r"\begin{cases}a_{11}^{2}\leq1,\$ a_{11}+2)^{2}\leq1,\end{cases} ",
         r"\begin{cases}a_{11}^{2}\leq1,\\ (a_{11}+2)^{2}\leq1,\end{cases} "),
        (r"\left.x\cos\pi x\right.\right|_{0}^{1}", r"\left.x\cos\pi x\right|_{0}^{1}"),
        (r"P\left\{\frac{1}{2}<X<\frac{3}{2}\right|Y=0\right\}",
         r"P\left\{\left.\frac{1}{2}<X<\frac{3}{2}\right|Y=0\right\}"),
        (r"\xrightarrow{\text{第2列右边乘}(-A^\mathrm{T})，加至第1列}}",
         r"\xrightarrow{\text{第2列右边乘}(-A^\mathrm{T})\text{，加至第1列}}"),
        (r"\xrightarrow{\text{第1行左边乘}(-A^\mathrm{T} A)，加至第2行}}",
         r"\xrightarrow{\text{第1行左边乘}(-A^\mathrm{T} A)\text{，加至第2行}}"),
        (r"\xrightarrow{\text{第1列右边乘}(-C)，加至第2列}}",
         r"\xrightarrow{\text{第1列右边乘}(-C)\text{，加至第2列}}"),
        (r"\xrightarrow{\text{第1行左边乘}(-A)，加至第2行}}",
         r"\xrightarrow{\text{第1行左边乘}(-A)\text{，加至第2行}}"),
        (r"\bigg|_{x=0\atop y=0}", r"\bigg|_{\substack{x=0\\y=0}}"),
        (r"\right|_{x=0\atop y=0\atop z=1}", r"\right|_{\substack{x=0\\y=0\\z=1}}"),
        (r"\displaylimits", ""),
        (r"\frac{f(a+t)-f(a)}{f(a)}}$", r"\frac{f(a+t)-f(a)}{f(a)}$"),
        (r",\ $z-2)^{3},&2<z\leq3,", r",\\ (z-2)^{3},&2<z\leq3,"),
    ],
}

for book, fixes in FIXES.items():
    md = glob.glob(f"11408/origin/{book}/*.md")[0]
    txt = open(md, encoding="utf-8").read()
    for old, new in fixes:
        c = txt.count(old)
        if c == 0:
            print(f"WARN {book}: 未找到: {old[:50]}")
        elif c > 1:
            print(f"WARN {book}: 多处({c}): {old[:50]}")
        else:
            txt = txt.replace(old, new)
            print(f"OK   {book}: {old[:42]} -> {new[:42]}")
    open(md, "w", encoding="utf-8").write(txt)
print("完成")
