"""初级图标重绘（2 倍尺寸 + 细节）：检测仪 / 腕表 / 汉堡 / 金币 / 邮票册 / 陨石。"""
from PIL import Image, ImageDraw
import os

OUT = (18, 20, 24, 255)
STEEL_D = (58, 66, 74, 255)
STEEL = (120, 132, 144, 255)
STEEL_L = (184, 196, 206, 255)
HI = (234, 242, 248, 255)
GOLD_D = (118, 86, 28, 255)
GOLD = (202, 162, 62, 255)
GOLD_L = (242, 212, 122, 255)
RED_D = (110, 36, 36, 255)
RED = (176, 66, 58, 255)
BROWN_D = (92, 58, 34, 255)
BUN = (150, 98, 52, 255)
BUN_L = (174, 120, 66, 255)
CHEESE = (232, 176, 64, 255)
GREEN = (96, 186, 112, 255)
GREEN_D = (62, 132, 78, 255)
CYAN = (70, 200, 224, 255)
DARK = (26, 32, 38, 255)

def canvas(w, h):
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    return img, ImageDraw.Draw(img)

def edge(img):
    w, h = img.size
    px = img.load()
    for y in range(h):
        for x in range(w):
            if px[x, y][3] == 0:
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < w and 0 <= ny < h and px[nx, ny][3] > 0 and px[nx, ny][:3] != OUT[:3]:
                        px[x, y] = OUT
                        break

def envscan():
    img, d = canvas(32, 64)
    d.line([24, 1, 24, 9], fill=STEEL_L, width=2)
    d.ellipse([22, 0, 26, 4], fill=CYAN, outline=OUT, width=1)
    d.rounded_rectangle([6, 8, 25, 58], radius=3, fill=STEEL_D, outline=OUT, width=2)
    d.rectangle([22, 32, 24, 54], fill=DARK)
    d.rectangle([9, 12, 21, 30], fill=DARK, outline=OUT, width=2)
    d.rectangle([10, 13, 20, 14], fill=CYAN)
    for i, h in enumerate((4, 8, 6, 11, 7, 9)):
        x = 10 + i * 2
        d.rectangle([x, 28 - h, x + 1, 28], fill=GREEN)
    for x in (10, 13, 16, 19):
        d.rectangle([x, 9, x + 1, 10], fill=CYAN)
    for bx, by, col in ((9, 36, GOLD), (15, 36, RED), (9, 42, CYAN), (15, 42, STEEL_L)):
        d.rectangle([bx, by, bx + 4, by + 3], fill=col, outline=OUT)
    for yy in (50, 53):
        d.line([9, yy, 20, yy], fill=DARK)
    edge(img)
    return img

def wrist():
    img, d = canvas(64, 32)
    d.rounded_rectangle([2, 8, 61, 24], radius=3, fill=(88, 62, 46, 255), outline=OUT, width=2)
    for x in range(6, 20, 4):
        d.rectangle([x, 11, x, 11], fill=STEEL_L)
        d.rectangle([x, 21, x, 21], fill=STEEL_L)
    d.rectangle([54, 10, 61, 22], fill=STEEL_D, outline=OUT, width=2)
    d.rectangle([57, 14, 58, 18], fill=DARK)
    d.rounded_rectangle([20, 2, 45, 30], radius=3, fill=STEEL_D, outline=OUT, width=2)
    d.rounded_rectangle([23, 5, 42, 27], radius=2, fill=STEEL, outline=OUT, width=2)
    d.rectangle([26, 8, 39, 24], fill=DARK, outline=OUT, width=2)
    for x, y in ((28, 11), (31, 11), (36, 11), (28, 14), (36, 14), (28, 17), (31, 17), (36, 17), (31, 20), (34, 20)):
        d.rectangle([x, y, x + 1, y + 2], fill=CYAN)
    d.rectangle([33, 11, 34, 12], fill=CYAN)
    d.rectangle([33, 16, 34, 17], fill=CYAN)
    d.rectangle([45, 10, 47, 14], fill=GOLD, outline=OUT)
    edge(img)
    return img

def burger():
    img, d = canvas(64, 32)
    # 顶面包：矮而宽
    d.ellipse([6, 2, 58, 10], fill=BUN, outline=OUT, width=1)
    d.arc([8, 3, 56, 9], start=190, end=260, fill=BUN_L, width=1)
    for sx, sy in ((14, 5), (23, 4), (32, 4), (41, 4), (48, 6), (20, 7), (36, 7), (29, 6)):
        d.ellipse([sx, sy, sx + 2, sy + 1], fill=HI)
    # 生菜
    for x in range(8, 57, 7):
        d.ellipse([x, 9, x + 8, 13], fill=GREEN, outline=OUT, width=1)
    d.rectangle([7, 10, 57, 12], fill=GREEN_D)
    # 肉饼：视觉主体，最厚
    d.rectangle([7, 14, 57, 24], fill=BROWN_D, outline=OUT, width=1)
    for x in range(11, 54, 5):
        d.rectangle([x, 17, x + 1, 18], fill=(64, 38, 22, 255))
        d.rectangle([x + 3, 21, x + 3, 21], fill=(122, 80, 46, 255))
    # 芝士：薄一点，带滴落
    d.rectangle([8, 13, 56, 16], fill=CHEESE, outline=OUT, width=1)
    for x in range(11, 54, 9):
        d.polygon([(x, 16), (x + 4, 16), (x + 3, 18)], fill=CHEESE)
    # 底面包：比肉饼薄一点
    d.rounded_rectangle([6, 24, 58, 30], radius=2, fill=BUN_L, outline=OUT, width=1)
    d.line([10, 26, 54, 26], fill=(202, 150, 96, 255))
    edge(img)
    return img

def portcoin():
    img, d = canvas(32, 32)
    d.ellipse([1, 1, 30, 30], fill=GOLD_D, outline=OUT, width=2)
    d.ellipse([3, 3, 28, 28], fill=GOLD, outline=OUT, width=1)
    d.ellipse([6, 6, 25, 25], outline=GOLD_L)
    d.ellipse([10, 10, 21, 21], outline=GOLD_D)
    d.ellipse([13, 13, 18, 18], fill=GOLD_D)
    for cx, cy in ((15, 15), (13, 12), (18, 12), (12, 18), (19, 18)):
        d.rectangle([cx, cy, cx, cy], fill=GOLD_L)
    d.line([15, 6, 15, 9], fill=GOLD_D)
    d.line([15, 22, 15, 25], fill=GOLD_D)
    d.line([6, 15, 9, 15], fill=GOLD_D)
    d.line([22, 15, 25, 15], fill=GOLD_D)
    d.arc([2, 2, 29, 29], start=190, end=250, fill=GOLD_L)
    edge(img)
    return img

def stampbook():
    img, d = canvas(64, 32)
    d.rounded_rectangle([2, 3, 61, 29], radius=2, fill=(42, 80, 108, 255), outline=OUT, width=2)
    d.rectangle([2, 3, 9, 29], fill=(30, 56, 78, 255))
    for y in (9, 15, 21):
        d.line([3, y, 8, y], fill=STEEL_L)
    d.rectangle([10, 3, 10, 29], fill=STEEL_L)
    for gy in (6, 18):
        for gx in (14, 27, 40):
            d.rectangle([gx, gy, gx + 9, gy + 9], fill=HI, outline=OUT, width=1)
            for px_ in range(gx + 1, gx + 9, 2):
                d.rectangle([px_, gy - 1, px_, gy - 1], fill=OUT)
                d.rectangle([px_, gy + 10, px_, gy + 10], fill=OUT)
            d.rectangle([gx + 2, gy + 2, gx + 7, gy + 7], fill=(176, 66, 58, 255), outline=OUT)
            d.rectangle([gx + 4, gy + 3, gx + 5, gy + 4], fill=GOLD_L)
    d.rectangle([52, 6, 58, 26], fill=GOLD, outline=OUT, width=1)
    for y in (9, 13, 17, 21):
        d.line([53, y, 57, y], fill=RED_D)
    edge(img)
    return img

def ironstone():
    img, d = canvas(32, 32)
    d.polygon([(5, 22), (6, 12), (12, 5), (21, 6), (27, 13), (26, 24), (19, 29), (9, 27)],
              fill=(74, 68, 64, 255), outline=OUT)
    d.polygon([(9, 11), (13, 7), (19, 8), (16, 13)], fill=(104, 96, 90, 255))
    d.polygon([(20, 19), (25, 15), (26, 23), (21, 25)], fill=(60, 55, 52, 255))
    vein = (214, 66, 48, 255)
    vein_d = (132, 40, 34, 255)
    d.line([5, 21, 12, 15, 18, 17, 25, 11], fill=vein_d, width=3)
    d.line([5, 21, 12, 15, 18, 17, 25, 11], fill=vein, width=1)
    d.line([12, 15, 11, 9], fill=vein_d, width=3)
    d.line([12, 15, 11, 9], fill=vein)
    d.line([18, 17, 19, 24], fill=vein_d, width=3)
    d.line([18, 17, 19, 24], fill=vein)
    d.rectangle([8, 12, 9, 12], fill=vein)
    d.rectangle([22, 21, 24, 21], fill=vein)
    d.ellipse([14, 20, 17, 22], fill=(50, 46, 44, 255))
    edge(img)
    return img

items = [
    ("oddity_tech_envscan", envscan()),
    ("oddity_tech_wrist", wrist()),
    ("oddity_cult_burger", burger()),
    ("oddity_cult_portcoin", portcoin()),
    ("oddity_cult_stampbk", stampbook()),
    ("oddity_xeno_iron", ironstone()),
]

out_dir = os.path.join("starter", "Textures", "Items")
os.makedirs(out_dir, exist_ok=True)
for name, img in items:
    p = os.path.join(out_dir, name + ".png")
    tmp = p + ".tmp.png"
    img.save(tmp)
    os.replace(tmp, p)
    print("saved", name, img.size)

names = ["oddity_bio_knuckle"] + [n for n, _ in items] + ["oddity_cult_festkit"]
ims = [Image.open(os.path.join(out_dir, n + ".png")) for n in names]
scale = 3
pad = 12
width = sum(im.width * scale + pad for im in ims) + pad
height = max(im.height * scale for im in ims) + pad * 2
prev = Image.new("RGBA", (width, height), (40, 44, 50, 255))
pd = ImageDraw.Draw(prev)
for yy in range(0, height, 16):
    for xx in range(0, width, 16):
        if (xx // 16 + yy // 16) % 2 == 0:
            pd.rectangle([xx, yy, xx + 15, yy + 15], fill=(54, 58, 64, 255))
x = pad
for im in ims:
    big = im.resize((im.width * scale, im.height * scale), Image.NEAREST)
    prev.alpha_composite(big, (x, (height - big.height) // 2))
    x += big.width + pad
os.makedirs("SD-Picture", exist_ok=True)
prev.save("SD-Picture/preview_tier1_v2.png")
print("preview", prev.size)
