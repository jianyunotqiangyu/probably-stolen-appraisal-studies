"""列出指节手册里含数值的文本段，便于按新定价更新。"""
import io
import json
import os
import re
import sys

PATH = os.path.join(r"D:\DSH_workspace\mod-create", "mod", "AppraisalExpansion", "Books", "knuckle_guide.json")
NUMBERS = ("85", "35", "170", "70", "60", "45", "100", "120", "245", "30", "25", "20", "15", "50")


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    book = json.load(io.open(PATH, encoding="utf-8"))

    for index, page in enumerate(book["pages"], 1):
        title = page.get("name", "?")
        for element in page.get("elements", []):
            english = element.get("text") or ""
            chinese = (element.get("translations") or {}).get("zh-Hans", "")
            blob = english + " " + chinese
            if not any(re.search(r"\b" + n + r"\b", blob) for n in NUMBERS):
                continue
            print("=" * 12, f"第{index}页 {title}")
            if chinese:
                print("[中]", chinese)
            if english:
                print("[英]", english)
            print()


if __name__ == "__main__":
    main()
