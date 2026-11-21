"""从 vdf 里把 description 抽出来，还原成开发者可读的纯文本（\\n 转回车），
方便贴到 Steam 网页编辑器里核对。输出到 tools/workshop/description.txt。
"""
import io
import os
import re
import sys

ROOT = r"D:\DSH_workspace\mod-create"
VDF = os.path.join(ROOT, "tools", "workshop", "AppraisalExpansion.vdf")
OUT = os.path.join(ROOT, "tools", "workshop", "description.txt")


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    text = io.open(VDF, encoding="utf-8").read()

    m = re.search(r'"description"\s+"((?:[^"\\]|\\.)*)"', text, re.S)
    if not m:
        print("没找到 description")
        return

    body = m.group(1)
    body = body.replace("\\n", "\n").replace('\\"', '"')

    io.open(OUT, "w", encoding="utf-8", newline="\n").write(body)
    print("写出", OUT)
    print("行数", body.count("\n") + 1, "字符", len(body))
    print("含 '----------' 分隔线:", "----------" in body)
    print("含 '电话预约考试':", "电话预约考试" in body)
    print("残留我加的段落（手册/安装与兼容/Credits）:",
          any(k in body for k in ("[h2]手册[/h2]", "安装与兼容", "Credits")))


if __name__ == "__main__":
    main()
