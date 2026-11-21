"""把描述里残留的反引号去掉（游戏不支持 Markdown，反引号会原样显示）。"""
import io
import os
import sys

PATH = os.path.join(r"D:\DSH_workspace\mod-create", "mod", "AppraisalExpansion", "manifest.xml")
BACKTICK = chr(96)


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    text = io.open(PATH, encoding="utf-8").read()
    if BACKTICK in text:
        text = text.replace(BACKTICK, "")
        io.open(PATH, "w", encoding="utf-8", newline="\n").write(text)
        print("已去掉反引号")
    else:
        print("没有反引号")


if __name__ == "__main__":
    main()
