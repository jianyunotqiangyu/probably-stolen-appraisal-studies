"""生成带防伪编号的手册插图。

手册里只放币面看不清编号，所以按「底图 + 字模」合成几张**带编号**的插图：
  ill_coin_gold_collector_00077S.png   珍藏版 · 豹子号
  ill_coin_gold_collector_00005G.png   珍藏版 · 测试币
  ill_coin_copper_normal_04321G.png    铜质 · 末位 G（赝品示例）

字模与底图都已按同一矩形（16,73–240,175）裁过，所以在裁后坐标里
首字位置是 (54-16, 123-73) = (38, 50)，之后每字横移 5px。
"""
import os

from PIL import Image

ROOT = r"D:\DSH_workspace\mod-create"
ITEMS = os.path.join(ROOT, "assets", "items", "oddity_coin")
PAPER = os.path.join(ROOT, "assets", "paper")

GLYPH_DIR = os.path.join(ITEMS, "serial")
BASE_DIR = os.path.join(ITEMS, "magnifier_base")

STEP = 5
SCALE = 3   # 放大 3 倍，编号才看得清

JOBS = [
    ("coin_gold_collector", "00077S", "ill_coin_gold_collector_00077S"),
    ("coin_gold_collector", "00005G", "ill_coin_gold_collector_00005G"),
    ("coin_copper_normal", "04321G", "ill_coin_copper_normal_04321G"),
]


def glyph_path(material, ch):
    return os.path.join(GLYPH_DIR, f"coin_ch_{material}_{ch}.png")


def compose(base_key, serial, out_key):
    material = "gold" if "gold" in base_key else ("silver" if "silver" in base_key else "copper")
    img = Image.open(os.path.join(BASE_DIR, base_key + ".png")).convert("RGBA")
    img = img.resize((img.width * SCALE, img.height * SCALE), Image.NEAREST)

    for i, ch in enumerate(serial):
        path = glyph_path(material, ch)
        if not os.path.exists(path):
            print("缺字模:", path)
            continue
        # 字模与底图裁的是同一个矩形，字符已经在 (38,50)，整层右移 5px×序号即可
        layer = Image.open(path).convert("RGBA")
        layer = layer.resize((layer.width * SCALE, layer.height * SCALE), Image.NEAREST)
        img.alpha_composite(layer, (STEP * SCALE * i, 0))

    out = os.path.join(PAPER, out_key + ".png")
    img.save(out)
    print(out, img.size)


def main():
    for base_key, serial, out_key in JOBS:
        compose(base_key, serial, out_key)


if __name__ == "__main__":
    main()
