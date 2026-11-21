"""把指节 / 检测仪 / 终端的鉴定大图裁掉四周留白（底图与叠层用同一矩形）。

为什么裁：四件物品里只有纪念币裁过，它在面板里正好占满；另外三件的 256 画布上
内容只占中间一块（指节 114×148、检测仪 160×218、终端 138×187），显示出来自然偏小。
裁切不改像素内容，只去掉透明边，面板里就会显得更大、更清楚。

原图先备份到 _archive/item-art-uncropped/，可随时回滚。
"""
import os
import shutil

from PIL import Image

ROOT = r"D:\DSH_workspace\mod-create"
ITEMS = os.path.join(ROOT, "assets", "items")
BACKUP = os.path.join(ROOT, "_archive", "item-art-uncropped")

MARGIN = 4
ALPHA_MIN = 8

TARGETS = ["oddity_bio_knuckle", "oddity_tech_envscan", "oddity_tech_wrist"]
SUBDIRS = ["magnifier_base", "magnifier_overlay"]


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


def main():
    for item in TARGETS:
        files = []
        for sub in SUBDIRS:
            d = os.path.join(ITEMS, item, sub)
            if not os.path.isdir(d):
                continue
            files += [os.path.join(d, f) for f in sorted(os.listdir(d)) if f.endswith(".png")]

        if not files:
            print(item, "没有素材，跳过")
            continue

        rect = union_bbox(files)
        w, h = rect[2] - rect[0], rect[3] - rect[1]
        print(f"{item}: 裁到 {w}×{h}（原 256×256）")

        for p in files:
            rel = os.path.relpath(p, ITEMS)
            backup = os.path.join(BACKUP, rel)
            os.makedirs(os.path.dirname(backup), exist_ok=True)
            if not os.path.exists(backup):
                shutil.copy2(p, backup)
            Image.open(backup).convert("RGBA").crop(rect).save(p)


if __name__ == "__main__":
    main()
