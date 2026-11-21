"""把像素画按指定尺寸缩小，并保住硬边 —— 对应「等比例缩小就糊」的解法。

做法（三步）：
  1. 用 BOX 面积平均缩小（像素画不能用 LANCZOS/bicubic，会振铃出光晕）；
  2. 从**原图**取主导色板，把每个像素吸附到最近的色板颜色（灰色过渡全部消失，边回到硬边）；
  3. alpha 二值化（>阈值 = 不透明，否则全透明），去掉半透明毛边。

用法：
  python tools/pixelize.py <源图> <输出png> <目标边长> [色板色数=16] [alpha阈值=96]
例：
  python tools/pixelize.py assets/items/oddity_tech_envscan/magnifier_base/envscan_good_ok.png \
                            assets/items/oddity_tech_envscan/icon/envscan_icon.png 48
"""
import os
import sys
from collections import Counter

from PIL import Image


def dominant_palette(art, n):
    """从原图的不透明像素里取主导色（量化到 8 的倍数再统计，避免色阶过细）。"""
    pixels = [p for p in art.getdata() if p[3] > 200]
    counts = Counter(((r // 8) * 8, (g // 8) * 8, (b // 8) * 8) for r, g, b, _ in pixels)
    return [c for c, _ in counts.most_common(n)]


def snap_to_palette(img, palette, alpha_cut):
    out = Image.new("RGBA", img.size, (0, 0, 0, 0))
    src, dst = img.load(), out.load()
    for y in range(img.height):
        for x in range(img.width):
            r, g, b, a = src[x, y]
            if a < alpha_cut:
                continue
            best, best_dist = palette[0], 1 << 30
            for pr, pg, pb in palette:
                d = (r - pr) ** 2 + (g - pg) ** 2 + (b - pb) ** 2
                if d < best_dist:
                    best_dist, best = d, (pr, pg, pb)
            dst[x, y] = (best[0], best[1], best[2], 255)
    return out


def pixelize(source, target, size, colors=16, alpha_cut=96, margin=1):
    src = Image.open(source).convert("RGBA")
    art = src.crop(src.getbbox())
    palette = dominant_palette(art, colors)

    scale = min((size - 2 * margin) / art.width, (size - 2 * margin) / art.height)
    small = art.resize((max(1, round(art.width * scale)), max(1, round(art.height * scale))), Image.BOX)

    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    canvas.alpha_composite(small, ((size - small.width) // 2, (size - small.height) // 2))
    return snap_to_palette(canvas, palette, alpha_cut), palette


def main():
    if len(sys.argv) < 4:
        print(__doc__)
        return 1
    source, target, size = sys.argv[1], sys.argv[2], int(sys.argv[3])
    colors = int(sys.argv[4]) if len(sys.argv) > 4 else 16
    alpha_cut = int(sys.argv[5]) if len(sys.argv) > 5 else 96

    img, palette = pixelize(source, target, size, colors, alpha_cut)
    os.makedirs(os.path.dirname(target), exist_ok=True)
    img.save(target)
    print(f"{target}  {img.size}  bbox={img.getbbox()}  色板 {len(palette)} 色")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
