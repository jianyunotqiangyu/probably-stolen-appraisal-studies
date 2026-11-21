"""检查 manifest 描述里是否残留 Markdown 语法（游戏不支持，会把符号原样显示）。"""
import io
import os
import re
import sys

PATH = os.path.join(r"D:\DSH_workspace\mod-create", "mod", "AppraisalExpansion", "manifest.xml")

BACKTICK = chr(96)
STAR2 = "*" * 2


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    text = io.open(PATH, encoding="utf-8").read()
    start = text.find("<![CDATA[")
    end = text.find("]]>")
    body = text[start:end]

    report = []
    if re.search(r"^#{1,6} ", body, re.M):
        report.append("标题 #")
    if STAR2 in body:
        report.append("粗体 **")
    if BACKTICK in body:
        report.append("反引号")
    if re.search(r"^\s*\*\s", body, re.M):
        report.append("星号列表")

    print("残留:", " / ".join(report) if report else "无")
    for i, line in enumerate(body.split("\n"), 1):
        if line.startswith("#") or BACKTICK in line or STAR2 in line:
            print(f"  {i}: {line}")


if __name__ == "__main__":
    main()
