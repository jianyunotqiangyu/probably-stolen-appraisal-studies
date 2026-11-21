"""拆分反编译文件，列出顶层类型与起止位置（诊断用）。"""
import io
import re

DEC = r"D:\DSH_workspace\mod-create\_tmp-decomp\src\AppraisalExpansion.decompiled.cs"

PATTERN = re.compile(
    r"^(?:public |internal )?(?:static |sealed |abstract |partial )*(?:class|struct|enum|interface) (\w+)",
    re.M,
)


def main():
    text = io.open(DEC, encoding="utf-8-sig").read()
    hits = [(m.group(1), m.start()) for m in PATTERN.finditer(text)]
    print("顶层类型数:", len(hits))
    for i, (name, start) in enumerate(hits):
        end = hits[i + 1][1] if i + 1 < len(hits) else len(text)
        print(f"{name:24} {start:6} .. {end:6}  ({end - start} 字节)")


if __name__ == "__main__":
    main()
