"""工作空间体检 —— 对应纪律 C4。

检查项：
  1. 手册 JSON 引用的图，在 assets/ 里是否都存在
  2. assets/ 里有没有没人引用的孤儿图（JSON 与 C# 字符串里都找不到）
  3. 临时/重复文件（*.tmp *.bak *~ Thumbs.db .DS_Store 等）
  4. 生成物是否被手改（mod/…/Textures 与 assets 的 md5 是否对得上）
  5. 文档是否落后于代码（src / Books 的最新修改时间 vs docs 的）

用法：python tools\\workspace_check.py
输出只报告，不改文件；清理动作由人确认后再做。
"""
import hashlib
import json
import sys
import os
import re
import time

ROOT = r"D:\DSH_workspace\mod-create"
MOD = os.path.join(ROOT, "mod", "AppraisalExpansion")
ASSETS = os.path.join(ROOT, "assets")
DOCS = os.path.join(ROOT, "docs")
BOOK = os.path.join(MOD, "Books", "knuckle_guide.json")

JUNK = (".tmp", ".bak", "~", ".orig", ".rej", ".log")
JUNK_NAMES = {"thumbs.db", ".ds_store", "desktop.ini"}
# 原版纸质面板的精灵图键：运行时由游戏解析，不进 assets，检查时放行
VANILLA_PAPER_KEYS = {
    "notebook_manual", "guide_reworked", "guide", "tutorial_sheet", "business_card_template",
    "exchange", "test_strips", "mentors_notes", "wine_tutorial", "water_purity_2x",
    "guide_logo", "blue_button_2x", "paper_buttons1", "paper_buttons2",
    "paper_buttons_close1", "paper_buttons_close2", "paper_buttons_l_1", "paper_buttons_l_2",
    "paper_buttons_screen_0", "paper_buttons_screen_1",
}


def md5(p):
    with open(p, "rb") as fh:
        return hashlib.md5(fh.read()).hexdigest()


def pngs(root):
    out = {}
    for base, _dirs, files in os.walk(root):
        for f in files:
            if f.lower().endswith((".png", ".jpg", ".jpeg")):
                out[os.path.splitext(f)[0]] = os.path.join(base, f)
    return out


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    problems = []
    notes = []

    # ---- 1/2：引用 vs 素材 ----
    refs = set()
    books_dir = os.path.dirname(BOOK)
    for name in sorted(os.listdir(books_dir)):
        if not name.endswith(".json"):
            continue
        book = json.load(open(os.path.join(books_dir, name), encoding="utf-8"))
        if book.get("background"):
            refs.add(book["background"])
        for el in list(book.get("chrome", [])) + [e for pg in book.get("pages", []) for e in pg.get("elements", [])]:
            if el.get("type") in ("image", "button") and el.get("sprite"):
                refs.add(el["sprite"])
    refs = {r for r in refs if "/" not in r and ":" not in r and r not in VANILLA_PAPER_KEYS}

    files = pngs(ASSETS)
    missing = sorted(r for r in refs if r not in files)
    if missing:
        problems.append("手册引用了但 assets 里没有：" + ", ".join(missing))

    # C# 里引用的键（物品精灵 keys 是代码里拼的，这里做一次宽松匹配）
    cs_text = ""
    for base, _dirs, fs in os.walk(os.path.join(MOD, "src")):
        for f in fs:
            if f.endswith(".cs"):
                cs_text += open(os.path.join(base, f), encoding="utf-8").read()

    orphans = []
    for key, path in files.items():
        if key in refs:
            continue
        if key in cs_text:
            continue
        # 差分素材常按前缀拼名（如 knuckle_{mat}_{cond}），按前缀宽松放过
        stem = re.split(r"[_\-]", key)[0]
        if stem and stem in cs_text:
            continue
        orphans.append(os.path.relpath(path, ROOT))
    if orphans:
        notes.append("可能没人引用的素材（确认后可归档到 _archive）：\n    " + "\n    ".join(sorted(orphans)))

    # ---- 3：临时文件 ----
    junk = []
    # 跳过隐藏目录（.git/.dsh-vision-router/.edge-profile* 等）与只读参考目录
    for base, dirs, fs in os.walk(ROOT):
        dirs[:] = [d for d in dirs if not d.startswith(".") and d not in ("reference", "_archive", "tools", "node_modules", "backup")]
        for f in fs:
            low = f.lower()
            p = os.path.join(base, f)
            if low in JUNK_NAMES or low.endswith(JUNK):
                junk.append(os.path.relpath(p, ROOT))
    if junk:
        problems.append("临时文件（建议删除）：\n    " + "\n    ".join(sorted(junk)))

    # ---- 4：生成物是否被手改 ----
    for kind, src_root in (("Paper", os.path.join(ASSETS, "paper")),):
        gen = os.path.join(MOD, "Textures", kind)
        if not os.path.isdir(gen):
            continue
        for f in sorted(os.listdir(gen)):
            sp = os.path.join(src_root, f)
            gp = os.path.join(gen, f)
            if os.path.exists(sp) and os.path.exists(gp) and md5(sp) != md5(gp):
                problems.append(f"生成物与源素材不一致（被手改过？）：{os.path.relpath(gp, ROOT)}")

    # ---- 5：文档新鲜度 ----
    newest_code = 0.0
    for base in (os.path.join(MOD, "src"), os.path.join(MOD, "Books")):
        for b2, _d, fs in os.walk(base):
            for f in fs:
                newest_code = max(newest_code, os.path.getmtime(os.path.join(b2, f)))
    newest_doc = 0.0
    for f in os.listdir(DOCS):
        if f.endswith(".md"):
            newest_doc = max(newest_doc, os.path.getmtime(os.path.join(DOCS, f)))
    trail = (newest_code - newest_doc) / 3600.0
    if trail > 0.5:
        problems.append(f"文档落后于代码约 {trail:.1f} 小时：记得更新 00 §1 / 30 / 01")

    # ---- 报告 ----
    print("=" * 56)
    print("工作空间体检")
    print("=" * 56)
    print(f"手册引用键 {len(refs)} 个（{len(os.listdir(os.path.dirname(BOOK)))} 本手册） | assets 图片 {len(files)} 张")
    print(f"最新代码 {time.strftime('%m-%d %H:%M', time.localtime(newest_code))} | "
          f"最新文档 {time.strftime('%m-%d %H:%M', time.localtime(newest_doc))}")
    print()
    if not problems and not notes:
        print("通过：无缺失引用、无临时文件、生成物与源一致、文档不落后。")
    for p in problems:
        print("[!] " + p)
    for n in notes:
        print("[?] " + n)
    print()


if __name__ == "__main__":
    main()
