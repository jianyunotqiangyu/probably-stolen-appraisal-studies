"""程序化像素图标：民用义体指节（16×32，1×2 格），带上下两段指骨。"""
from PIL import Image, ImageDraw
import os

W, H = 16, 32
OUT = (18, 20, 24, 255)
DARK = (62, 70, 78, 255)
MID = (124, 136, 148, 255)
LIGHT = (184, 196, 206, 255)
HI = (234, 242, 248, 255)
ACCENT = (70, 200, 224, 255)

img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
d = ImageDraw.Draw(img)

# 上段指骨
d.rounded_rectangle([4, 0, 11, 13], radius=3, fill=MID, outline=OUT)
# 上段指骨的高光/阴影
d.line([5, 2, 5, 11], fill=LIGHT)
d.line([10, 2, 10, 11], fill=DARK)
# 上段指骨上的铆钉
d.rectangle([7, 4, 8, 5], fill=DARK)

# 下段指骨
d.rounded_rectangle([4, 19, 11, 31], radius=3, fill=MID, outline=OUT)
d.line([5, 21, 5, 29], fill=LIGHT)
d.line([10, 21, 10, 29], fill=DARK)
d.rectangle([7, 26, 8, 27], fill=DARK)

# 中间关节壳
d.ellipse([2, 11, 13, 21], fill=DARK, outline=OUT)
d.ellipse([4, 13, 11, 19], fill=MID)
# 关节轴
d.ellipse([6, 14, 9, 18], fill=LIGHT, outline=OUT)
d.rectangle([7, 15, 8, 17], fill=DARK)
# 关节高光
d.arc([3, 12, 12, 20], start=180, end=270, fill=LIGHT)
# 状态灯
d.rectangle([7, 9, 8, 10], fill=ACCENT)

# 顶部指尖盖
d.rounded_rectangle([5, 0, 10, 2], radius=1, fill=HI, outline=OUT)
# 底部指尖盖
d.rounded_rectangle([5, 29, 10, 31], radius=1, fill=HI, outline=OUT)

# 外轮廓补暗，增强可读性
px = img.load()
for y in range(H):
    for x in range(W):
        if px[x, y][3] == 0:
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = x + dx, y + dy
                if 0 <= nx < W and 0 <= ny < H and px[nx, ny][3] > 0 and px[nx, ny][:3] != OUT[:3]:
                    px[x, y] = OUT
                    break

out_dir = os.path.join("starter", "Textures", "Items")
os.makedirs(out_dir, exist_ok=True)
png = os.path.join(out_dir, "oddity_bio_knuckle.png")
img.save(png)

# 8 倍预览
prev = Image.new("RGBA", (W * 8, H * 8), (40, 44, 50, 255))
pd = ImageDraw.Draw(prev)
for yy in range(0, H * 8, 16):
    for xx in range(0, W * 8, 16):
        if (xx // 16 + yy // 16) % 2 == 0:
            pd.rectangle([xx, yy, xx + 15, yy + 15], fill=(54, 58, 64, 255))
prev.alpha_composite(img.resize((W * 8, H * 8), Image.NEAREST))
prev_path = os.path.join("SD-Picture", "preview_knuckle.png")
os.makedirs("SD-Picture", exist_ok=True)
prev.save(prev_path)

print("saved", png, img.size)
print("cell centers alpha:", [(8, 8, img.getpixel((8, 8))[3]), (8, 24, img.getpixel((8, 24))[3])])
