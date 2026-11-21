"""把纪念币底图压成 16×16 的背包图标。

**关键**：图标必须取「单枚币」，不能取两枚并排的整图。
原因在游戏那边：`GameItem.SetSpriteAndShapeFromMod` 是用**每个格子的中心像素**
的 alpha 来算占格的（16×16 图标 → 采样 (8,8)）。两枚币的整图中心正好落在
两枚币之间的空隙里，alpha = 0 → 算出来的形状是**空**的 → 物品不占格子、
可以互相重叠、选中也没有格子高亮。

所以这里先切左侧那枚（正面），再按包围盒缩进 16×16。
"""
import os

from PIL import Image

ROOT = r"D:\DSH_workspace\mod-create"
BASE = os.path.join(ROOT, "assets", "items", "oddity_coin", "magnifier_base")
ICON = os.path.join(ROOT, "assets", "items", "oddity_coin", "icon")

SIZE = 16
ALPHA_MIN = 96
MATERIALS = ["gold", "silver", "copper"]


def main():
    os.makedirs(ICON, exist_ok=True)
    for mat in MATERIALS:
        src = os.path.join(BASE, f"coin_{mat}_normal.png")
        img = Image.open(src).convert("RGBA")

        # 只要左半边（正面那枚）
        w, h = img.size
        img = img.crop((0, 0, w // 2, h))

        bbox = img.getbbox()
        if bbox:
            img = img.crop(bbox)

        w, h = img.size
        scale = min(SIZE / w, SIZE / h)
        tw, th = max(1, round(w * scale)), max(1, round(h * scale))
        small = img.resize((tw, th), Image.BOX)

        out = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
        out.paste(small, ((SIZE - tw) // 2, (SIZE - th) // 2))

        px = out.load()
        for y in range(SIZE):
            for x in range(SIZE):
                r, g, b, a = px[x, y]
                px[x, y] = (r, g, b, 255) if a >= ALPHA_MIN else (0, 0, 0, 0)

        # 自检：中心像素必须不透明，否则游戏算不出占格
        center = out.getpixel((SIZE // 2, SIZE // 2))
        assert center[3] > 0, f"{mat} 图标中心透明，会被算成不占格子"

        path = os.path.join(ICON, f"coin_icon_{mat}.png")
        out.save(path)
        print(f"{path}  {out.size}  中心={center}")


if __name__ == "__main__":
    main()
