"""在四件鉴定品的工厂里，给每处 SetSpriteAndShapeFromMod 之后补上 ItemFootprint.Ensure。

安全写法：先把文件内容读进变量，再写回（上次就是被 `open(p,'w').write(open(p).read())`
这种先开写句柄的写法把文件清空了）。
"""
import io
import os
import re

SRC = os.path.join(r"D:\DSH_workspace\mod-create\mod\AppraisalExpansion\src")
FILES = ["KnuckleItem.cs", "EnvScanItem.cs", "WristItem.cs", "CoinItem.cs"]

PATTERN = re.compile(r"^(\s*)(\w+)\.SetSpriteAndShapeFromMod\([^;]*\);\s*$", re.M)


def main():
    for name in FILES:
        path = os.path.join(SRC, name)
        text = io.open(path, encoding="utf-8").read()
        if "ItemFootprint.Ensure" in text:
            print(f"{name}: 已有兜底，跳过")
            continue

        def repl(match):
            indent, var = match.group(1), match.group(2)
            return f"{match.group(0)}\n{indent}ItemFootprint.Ensure({var});"

        new_text, count = PATTERN.subn(repl, text)
        io.open(path, "w", encoding="utf-8", newline="\n").write(new_text)
        print(f"{name}: 插入 {count} 处")


if __name__ == "__main__":
    main()
