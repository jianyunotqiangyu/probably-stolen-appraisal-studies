"""裁掉纪念币贴图四周的留白，让放大镜里看起来更大。

做法：
  1. 取 9 张底图的不透明包围盒并集（再留 4px 边距），保证九张裁完仍互相对齐；
  2. 用同一个矩形裁 9 张底图；
  3. 用同一个矩形裁 39 张字码（字码原本画在 256 画布的首字位置，裁完位置关系不变）。

原图先备份到 _archive/coin-uncropped/，可随时回滚。
"""
import os
import shutil

from PIL import Image

ROOT = r"D:\DSH_workspace\mod-create"
COIN = os.path.join(ROOT, "assets", "items", "oddity_coin")
BASE = os.path.join(COIN, "magnifier_base")
GLYPH = os.path.join(COIN, "serial")
BACKUP = os.path.join(ROOT, "_archive", "coin-uncropped")

MARGIN = 4
ALPHA_MIN = 8


def union_bbox(paths):
    left = top = 10 ** 6
    right = bottom = -1
    for p in paths:
        img = Image.open(p).convert("RGBA")
        bbox = img.point(lambda v: 255 if v > ALPHA_MIN else 0).getbbox()
        if not bbox:
            continue
        left = min(left, bbox[0])
        top = min(top, bbox[1])
        right = max(right, bbox[2])
        bottom = max(bottom, bbox[3])
    return (max(0, left - MARGIN), max(0, top - MARGIN), right + MARGIN, bottom + MARGIN)


def crop_all(root, rect, pattern):
    count = 0
    for name in sorted(os.listdir(root)):
        if not name.endswith(pattern):
            continue
        p = os.path.join(root, name)
        backup = os.path.join(BACKUP, os.path.relpath(p, COIN))
        os.makedirs(os.path.dirname(backup), exist_ok=True)
        if not os.path.exists(backup):
            shutil.copy2(p, backup)
        img = Image.open(backup).convert("RGBA")
        img.crop(rect).save(p)
        count += 1
    return count


def main():
    if os.path.isdir(GLYPH):
        glyph_files = [os.path.join(GLYPH, n) for n in os.listdir(GLYPH) if n.endswith(".png")]
    else:
        glyph_files = [os.path.join(GLYPH, n) for n in os.listdir(COIN) if n.startswith("coin_ch_")]
        GLYPH_DIR = COIN

    base_files = [os.path.join(BASE, n) for n in os.listdir(BASE) if n.endswith(".png")]
    rect = union_bbox(base_files + glyph_files)
    print("裁切矩形:", rect, "尺寸:", (rect[2] - rect[0], rect[3] - rect[1]))

    n1 = crop_all(BASE, rect, ".png")
    glyph_dir = GLYPH if os.path.isdir(GLYPH) else COIN
    n2 = crop_all(glyph_dir, rect, ".png")
    print(f"底图 {n1} 张，字码 {n2} 张")


if __name__ == "__main__":
    main()
