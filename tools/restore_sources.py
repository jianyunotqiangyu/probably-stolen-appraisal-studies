"""从反编译文件里拆出四件鉴定品的源码，写回 src/。

背景：2026-11-19 我用一行 python 覆写源码时把四个文件截成 0 字节
（`io.open(p,'w').write(io.open(p).read())` 的写句柄先求值，读到的是空串）。
恢复办法是反编译**当时已部署的 DLL**，把四个类拆回独立文件。

反编译会丢掉注释，写回时补回文件头注释；方法级注释不再恢复。
"""
import io
import os
import re

SRC = os.path.join(r"D:\DSH_workspace\mod-create\mod\AppraisalExpansion\src")
DEC = os.path.join(r"D:\DSH_workspace\mod-create\_tmp-decomp\src\AppraisalExpansion.decompiled.cs")

TARGETS = ("KnuckleItem", "EnvScanItem", "WristItem", "CoinItem")

HEADER = """// 由反编译恢复（2026-11-19）：源码文件被误截断后，从当时已部署的 DLL 反编译还原。
// 逻辑与数据以该 DLL 为准；此文件只保留文件头注释，方法级注释未恢复。

using System;
using System.Collections.Generic;
using System.Reflection;
using UnityEngine;

"""

PATTERN = re.compile(
    r"^(?:public |internal )?(?:static |sealed |abstract |partial )*(?:class|struct|enum|interface) (\w+)",
    re.M,
)


def main():
    text = io.open(DEC, encoding="utf-8-sig").read()
    hits = [(m.group(1), m.start()) for m in PATTERN.finditer(text)]

    for i, (name, start) in enumerate(hits):
        if name not in TARGETS:
            continue
        end = hits[i + 1][1] if i + 1 < len(hits) else len(text)
        body = text[start:end].rstrip()

        # 切到本类闭合的那个顶层 } —— 下一个类型的特性行（[HarmonyPatch...]）不算本类
        cut = body.rfind("\n}")
        if cut > 0:
            body = body[: cut + 2]

        body = body.replace("        UniqueItem.Make(item);\n", "")
        body = body.replace("            UniqueItem.Make(item);\n", "")
        body = re.sub(r"^\s*UniqueItem\.Make\(\w+\);\s*$", "", body, flags=re.M)
        # 反编译把全限定名简化了，这里补回去，避免与 System.Random 冲突
        body = re.sub(r"(?<!UnityEngine\.)\bRandom\.Range\(", "UnityEngine.Random.Range(", body)

        path = os.path.join(SRC, name + ".cs")
        io.open(path, "w", encoding="utf-8", newline="\n").write(HEADER + body + "\n")
        print(f"{name}.cs  {len(body)} 字节")


if __name__ == "__main__":
    main()
