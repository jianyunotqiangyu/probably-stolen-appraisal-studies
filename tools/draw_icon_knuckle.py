"""程序化像素图标：民用义体指节 oddity_bio_knuckle（32×32）。"""
from PIL import Image, ImageDraw
import math
import os

S = 32
OUT = (18, 20, 24, 255)
DARK = (60, 68, 76, 255)
MID = (124, 136, 148, 255)
LIGHT = (182, 194, 204, 255)
HI = (232, 240, 246, 255)
ACCENT = (70, 200, 224, 255)

img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
d = ImageDraw.Draw(img)

cx, cy = 16, 16

# 上下安装耳
d.rounded_rectangle([11, 0, 20, 9], radius=2, fill=DARK, outline=OUT)
d.rounded_rectangle([11, 23, 20, 31], radius=2, fill=DARK, outline=OUT)
# 耳上的螺栓孔
d.rectangle([14, 3, 17, 5], fill=OUT)
d.rectangle([14, 26, 17, 28], fill=OUT)

# 外圈
d.ellipse([cx - 13, cy - 13, cx + 12, cy + 12], fill=DARK, outline=OUT)
d.ellipse([cx - 11, cy - 11, cx + 10, cy + 10], fill=MID)

# 右下阴影 / 左上高光
d.pieslice([cx - 11, cy - 11, cx + 10, cy + 10], start=0, end=90, fill=DARK)
d.pieslice([cx - 11, cy - 11, cx + 10, cy + 10], start=180, end=270, fill=LIGHT)

# 内轴承
d.ellipse([cx - 6, cy - 6, cx + 5, cy + 5], fill=DARK, outline=OUT)
d.ellipse([cx - 4, cy - 4, cx + 3, cy + 3], fill=MID)

# 中心螺栓
d.ellipse([cx - 3, cy - 3, cx + 2, cy + 2], fill=LIGHT, outline=OUT)
d.line([cx - 1, cy, cx + 1, cy], fill=OUT)
d.line([cx, cy - 1, cx, cy + 1], fill=OUT)

# 一圈小铆钉
for ang in (45, 135, 225, 315):
    rx = cx + int(round(9 * math.cos(math.radians(ang))))
    ry = cy + int(round(9 * math.sin(math.radians(ang))))
    d.rectangle([rx - 1, ry - 1, rx, ry], fill=OUT)

# 状态灯
d.rectangle([15, 6, 16, 7], fill=ACCENT)

# 外轮廓修边：把透明像素边缘压暗一点，保证读得清
px = img.load()
for y in range(S):
    for x in range(S):
        if px[x, y][3] == 0:
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = x + dx, y + dy
                if 0 <= nx < S and 0 <= ny < S and px[nx, ny][3] > 0 and px[nx, ny][:3] != OUT[:3]:
                    px[x, y] = OUT
                    break

out_dir = os.path.join("starter", "Textures", "Items")
os.makedirs(out_dir, exist_ok=True)
png = os.path.join(out_dir, "oddity_bio_knuckle.png")
img.save(png)

# 6 倍预览（棋盘底，方便看透明区域）
prev = Image.new("RGBA", (S * 6, S * 6), (40, 44, 50, 255))
for yy in range(0, S * 6, 12):
    for xx in range(0, S * 6, 12):
        if (xx // 12 + yy // 12) % 2 == 0:
            ImageDraw.Draw(prev).rectangle([xx, yy, xx + 11, yy + 11], fill=(54, 58, 64, 255))
prev.alpha_composite(img.resize((S * 6, S * 6), Image.NEAREST))
prev_path = os.path.join("SD-Picture", "preview_knuckle.png")
os.makedirs("SD-Picture", exist_ok=True)
prev.save(prev_path)

# 检查占格（16px 格子的中心）：(8,8) (24,8) (8,24) (24,24)
alphas = [(x, y, img.getpixel((x, y))[3]) for x, y in ((8, 8), (24, 8), (8, 24), (24, 24))]
print("saved", png)
print("preview", prev_path)
print("cell centers alpha:", alphas)
