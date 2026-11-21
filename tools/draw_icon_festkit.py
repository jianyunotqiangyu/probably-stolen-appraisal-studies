"""节庆纪念套件：打开的首饰盒/展示盒，里面放徽章、铭牌和小摆件。64×64。"""
from PIL import Image, ImageDraw
import os

OUT = (18, 20, 24, 255)
BLUE_D = (26, 34, 58, 255)
BLUE = (38, 50, 82, 255)
VELVET = (74, 30, 38, 255)
GOLD_D = (120, 88, 28, 255)
GOLD = (202, 162, 62, 255)
GOLD_L = (242, 212, 122, 255)
SILVER = (170, 182, 192, 255)
SILVER_L = (222, 230, 236, 255)
RED = (176, 66, 58, 255)

img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
d = ImageDraw.Draw(img)

# 盒盖（打开，立在后面）
d.rounded_rectangle([8, 2, 55, 13], radius=2, fill=BLUE, outline=OUT, width=2)
d.rectangle([11, 5, 52, 10], outline=GOLD_D)
d.rectangle([30, 5, 33, 10], fill=RED, outline=OUT)

# 盒身
d.rounded_rectangle([8, 14, 55, 58], radius=3, fill=BLUE_D, outline=OUT, width=2)
# 内衬绒面
d.rounded_rectangle([12, 18, 51, 54], radius=2, fill=VELVET, outline=OUT, width=2)

# 左侧徽章
d.ellipse([12, 22, 30, 40], fill=GOLD, outline=OUT, width=2)
d.ellipse([16, 26, 26, 36], fill=GOLD_L, outline=GOLD_D)
d.polygon([(21, 28), (23, 32), (27, 32), (24, 35), (25, 39), (21, 36), (17, 39), (18, 35), (15, 32), (19, 32)],
          fill=GOLD_D)

# 中间铭牌
d.rectangle([32, 22, 49, 34], fill=SILVER, outline=OUT, width=2)
for yy in (25, 28, 31):
    d.line([35, yy, 46, yy], fill=(90, 100, 110, 255))
d.rectangle([38, 24, 43, 25], fill=GOLD_D)

# 右下小摆件（纪念章/摆件）
d.ellipse([34, 38, 50, 52], fill=RED, outline=OUT, width=2)
d.ellipse([38, 41, 46, 49], fill=GOLD_L, outline=GOLD_D)
d.rectangle([41, 34, 43, 38], fill=GOLD, outline=OUT)

# 盒扣
d.rectangle([28, 54, 35, 58], fill=GOLD, outline=OUT)
d.rectangle([30, 55, 33, 57], fill=GOLD_D)

out_dir = os.path.join("starter", "Textures", "Items")
os.makedirs(out_dir, exist_ok=True)
png = os.path.join(out_dir, "oddity_cult_festkit.png")
img.save(png)

prev = Image.new("RGBA", (64 * 4, 64 * 4), (40, 44, 50, 255))
pd = ImageDraw.Draw(prev)
for yy in range(0, 64 * 4, 16):
    for xx in range(0, 64 * 4, 16):
        if (xx // 16 + yy // 16) % 2 == 0:
            pd.rectangle([xx, yy, xx + 15, yy + 15], fill=(54, 58, 64, 255))
prev.alpha_composite(img.resize((256, 256), Image.NEAREST))
prev_path = os.path.join("SD-Picture", "preview_festkit.png")
prev.save(prev_path)
print("saved", png, img.size, "preview", prev_path)
