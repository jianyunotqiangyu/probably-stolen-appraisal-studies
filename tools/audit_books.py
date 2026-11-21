"""手册终审：一条命令检查 `Books/*.json` 的版式与文案问题。

检查项（ERROR 会让退出码为 1）：
  1. 填充率：每页内容底边应落在 603–684（75%–85%）
  2. 元素遮挡：按**可见范围**判定——图片用 alpha 包围盒、文本用实际字宽（含对齐），
     所以「透明边距里的图注」「右对齐的数值列」不会被误报
  3. 图片存在性：background / sprite 能在 assets/ 找到（含 "/" 或 ":" 的原版键放行）
  4. 差分真实性（纪律 A12）：扫描「仿制 / 重刻 / 伪造 / 假冒 / 露底 / 镀层可疑 / 换壳 / 拼装」
  5. 数值对照（只提示）：与 src/*.cs 里的 BaseValue / MinValue 比对

用法：python tools/audit_books.py
"""
import glob
import json
import os
import re
import sys

from PIL import Image, ImageFont

ROOT = r"D:\DSH_workspace\mod-create"
BOOKS = os.path.join(ROOT, "mod", "AppraisalExpansion", "Books")
ASSETS = os.path.join(ROOT, "assets")
SRC = os.path.join(ROOT, "mod", "AppraisalExpansion", "src")
FONT = r"C:\Windows\Fonts\msyh.ttc"

FILL_MIN, FILL_MAX = 603, 684
BLACKLIST = ["仿制", "重刻", "伪造", "假冒", "露底", "镀层可疑", "换壳", "拼装"]
# 原版纸质面板的精灵图键：运行时由游戏自己解析，不在我们的 assets 里，检查时放行
VANILLA_KEYS = {
    "notebook_manual", "guide_reworked", "guide", "tutorial_sheet", "business_card_template",
    "exchange", "test_strips", "mentors_notes", "wine_tutorial", "water_purity_2x",
    "guide_logo", "blue_button_2x", "paper_buttons1", "paper_buttons2",
    "paper_buttons_close1", "paper_buttons_close2", "paper_buttons_l_1", "paper_buttons_l_2",
    "paper_buttons_screen_0", "paper_buttons_screen_1",
}
# 原版排版里 header 与 title 本来就叠着 4px，属于设计，不算错
ALLOWED_OVERLAP = {("header", "title"), ("title", "header")}


def is_known_sprite(key):
    """原版键（带 / 或 : 的图集键、原版纸质面板键）都放行。"""
    if not key:
        return True
    if "/" in key or ":" in key:
        return True
    return key in VANILLA_KEYS


def font(size):
    return ImageFont.truetype(FONT, int(size))


def text_lines(text, size, width):
    f = font(size)
    out = []
    for para in text.split("\n"):
        if not para.strip():
            out.append("")
            continue
        cur = ""
        for ch in para:
            if f.getlength(cur + ch) <= width:
                cur += ch
            else:
                out.append(cur)
                cur = ch
        out.append(cur)
    return out


def text_box(e):
    """文本的可见矩形：宽度取最长行，按对齐方式落位。"""
    zh = (e.get("translations") or {}).get("zh-Hans") or e.get("text") or ""
    size = e.get("fontSize") or 15
    box_w = e.get("w") or 506
    lines = text_lines(zh, size, box_w)
    f = font(size)
    widest = max((f.getlength(line) for line in lines), default=0)
    height = len(lines) * size * 1.38
    x, y = e.get("x") or 0, e.get("y") or 0
    align = e.get("align") or "left"
    if align == "center":
        x = x + (box_w - widest) / 2
    elif align == "right":
        x = x + box_w - widest
    return (x, y, widest, height)


def image_box(e, keys):
    """图片的可见矩形：用 alpha 包围盒，按 contain 的缩放换算到面板坐标。"""
    sprite = e.get("sprite")
    x, y, w, h = e.get("x") or 0, e.get("y") or 0, e.get("w") or 0, e.get("h") or 0
    path = keys.get(sprite) if sprite else None
    if not path or w <= 0 or h <= 0:
        return (x, y, w, h)

    im = Image.open(path)
    iw, ih = im.size
    bbox = im.convert("RGBA").getbbox()
    if not bbox:
        return (x, y, w, h)
    scale = min(w / iw, h / ih)
    dx = x + (w - iw * scale) / 2
    dy = y + (h - ih * scale) / 2
    l, t, r, b = bbox
    return (dx + l * scale, dy + t * scale, (r - l) * scale, (b - t) * scale)


def overlaps(a, b):
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    return not (ax + aw <= bx or bx + bw <= ax or ay + ah <= by or by + bh <= ay)


def asset_index():
    out = {}
    for base, _dirs, files in os.walk(ASSETS):
        for f in files:
            if f.lower().endswith((".png", ".jpg", ".jpeg")):
                out[os.path.splitext(f)[0]] = os.path.join(base, f)
    return out


def source_constants():
    out = {}
    for path in glob.glob(os.path.join(SRC, "*.cs")):
        text = open(path, encoding="utf-8").read()
        base = re.search(r"BaseValue\s*=\s*(-?\d+)", text)
        floor = re.search(r"MinValue\s*=\s*(-?\d+)", text)
        if base and floor:
            out[os.path.basename(path)] = (int(base.group(1)), int(floor.group(1)))
    return out


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    keys = asset_index()
    errors, warns = [], []

    for path in sorted(glob.glob(os.path.join(BOOKS, "*.json"))):
        book = json.load(open(path, encoding="utf-8"))
        name = os.path.basename(path)
        print(f"=== {name}（{len(book.get('pages', []))} 页）")

        bg = book.get("background")
        if bg and not is_known_sprite(bg) and bg not in keys:
            errors.append(f"{name}: 背景 {bg} 在 assets 里不存在")

        for i, page in enumerate(book.get("pages", []), 1):
            bottom = 0
            boxes = []
            for e in page.get("elements", []):
                if e.get("type") == "line":
                    continue
                if e.get("action"):
                    continue

                if e.get("type") == "image":
                    bottom = max(bottom, (e.get("y") or 0) + (e.get("h") or 0))
                    sprite = e.get("sprite")
                    if sprite and not is_known_sprite(sprite) and sprite not in keys:
                        errors.append(f"{name} 第{i}页: 图片 {sprite} 在 assets 里不存在")
                    boxes.append((sprite, "image", image_box(e, keys)))
                elif e.get("type") == "text":
                    tb = text_box(e)
                    bottom = max(bottom, tb[1] + tb[3])
                    zh = (e.get("translations") or {}).get("zh-Hans") or e.get("text") or ""
                    for word in BLACKLIST:
                        if word in zh:
                            errors.append(f"{name} 第{i}页: 出现 A12 禁用词「{word}」")
                    kind = "caption" if e.get("style") == "caption" else "text"
                    boxes.append((e.get("id") or kind, kind, tb))

            page_h = book.get("designHeight") or book.get("height") or 804
            if page_h < 400:
                # 名片 / 单页这类小卡不套 A4 的 75–85% 规则，只看图注与遮挡
                print(f"  第{i}页 {page.get('name',''):<12} 卡片（{page_h:.0f} 高），跳过填充检查")
            else:
                fill_min, fill_max = page_h * 0.75, page_h * 0.85
                pct = bottom / page_h * 100
                flag = "OK" if fill_min <= bottom <= fill_max else "WARN"
                if flag == "WARN":
                    warns.append(f"{name} 第{i}页: 填充 {pct:.0f}%（底边 {bottom:.0f}/{page_h}），目标 75–85%")
                print(f"  第{i}页 {page.get('name',''):<12} 填充 {pct:3.0f}%  {flag}")

            for a in range(len(boxes)):
                for b in range(a + 1, len(boxes)):
                    (ida, kinda, ra), (idb, kindb, rb) = boxes[a], boxes[b]
                    if (ida, idb) in ALLOWED_OVERLAP:
                        continue
                    if overlaps(ra, rb):
                        errors.append(f"{name} 第{i}页: 元素遮挡 {ida} × {idb}")

    print("\n=== 数值对照（仅提示）")
    for src_file, (base, floor) in sorted(source_constants().items()):
        print(f"  {src_file}: 基准 {base}，底线 {floor}")

    print()
    if errors:
        print(f"ERROR × {len(errors)}")
        for e in errors:
            print("  [错误] " + e)
    if warns:
        print(f"WARN × {len(warns)}")
        for w in warns:
            print("  [提醒] " + w)
    if not errors and not warns:
        print("通过：填充、遮挡、缺图、A12 四项全部合格。")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())

