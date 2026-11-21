"""程序化像素图标：初级 8 件（指节已有，这里画其余 7 件）。"""
from PIL import Image, ImageDraw
import os

OUT = (18, 20, 24, 255)
STEEL_D = (60, 68, 76, 255)
STEEL = (120, 132, 144, 255)
STEEL_L = (182, 194, 204, 255)
HI = (234, 242, 248, 255)
GOLD_D = (120, 88, 28, 255)
GOLD = (202, 162, 62, 255)
GOLD_L = (242, 212, 122, 255)
RED_D = (112, 38, 38, 255)
RED = (176, 66, 58, 255)
BROWN_D = (92, 58, 34, 255)
BUN = (206, 156, 94, 255)
GREEN = (96, 186, 112, 255)
CYAN = (70, 200, 224, 255)
DARK = (28, 34, 40, 255)

def canvas(w, h):
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    return img, ImageDraw.Draw(img)

def outline_pass(img, color=OUT):
    w, h = img.size
    px = img.load()
    for y in range(h):
        for x in range(w):
            if px[x, y][3] == 0:
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < w and 0 <= ny < h and px[nx, ny][3] > 0 and px[nx, ny][:3] != color[:3]:
                        px[x, y] = color
                        break

def envscan():
    img, d = canvas(16, 32)
    d.line([12, 0, 12, 4], fill=STEEL_D)
    d.rounded_rectangle([3, 4, 12, 27], radius=2, fill=STEEL_D, outline=OUT)
    d.rectangle([5, 4, 10, 5], fill=CYAN)
    d.rectangle([5, 6, 10, 13], fill=DARK, outline=OUT)
    d.rectangle([6, 7, 9, 8], fill=(70, 150, 90, 255))
    d.rectangle([6, 10, 7, 11], fill=CYAN)
    d.rectangle([8, 10, 9, 11], fill=CYAN)
    for bx, by in ((5, 17), (8, 17), (5, 20), (8, 20)):
        d.rectangle([bx, by, bx + 1, by + 1], fill=STEEL_L, outline=OUT)
    for yy in (23, 25):
        d.line([5, yy, 10, yy], fill=DARK)
    outline_pass(img)
    return img

def wrist():
    img, d = canvas(32, 16)
    d.rounded_rectangle([2, 5, 29, 10], radius=2, fill=(86, 60, 44, 255), outline=OUT)
    d.rectangle([26, 6, 29, 9], fill=STEEL_D, outline=OUT)
    d.rounded_rectangle([10, 1, 21, 14], radius=2, fill=STEEL_D, outline=OUT)
    d.rectangle([12, 3, 19, 11], fill=DARK, outline=OUT)
    d.rectangle([13, 4, 14, 5], fill=CYAN)
    d.rectangle([16, 4, 17, 5], fill=CYAN)
    d.rectangle([13, 7, 17, 8], fill=(70, 150, 90, 255))
    d.rectangle([21, 5, 22, 7], fill=GOLD, outline=OUT)
    outline_pass(img)
    return img

def burger():
    img, d = canvas(32, 16)
    d.ellipse([3, 1, 28, 9], fill=BUN, outline=OUT)
    for sx, sy in ((8, 4), (13, 3), (18, 4), (23, 5), (11, 6), (20, 6)):
        d.rectangle([sx, sy, sx, sy], fill=HI)
    for x in range(4, 28, 4):
        d.rectangle([x, 8, x + 2, 9], fill=GREEN, outline=OUT)
    d.rectangle([4, 9, 27, 11], fill=BROWN_D, outline=OUT)
    d.rounded_rectangle([4, 11, 27, 15], radius=2, fill=BUN, outline=OUT)
    outline_pass(img)
    return img

def portcoin():
    img, d = canvas(16, 16)
    d.ellipse([1, 1, 14, 14], fill=GOLD_D, outline=OUT)
    d.ellipse([2, 2, 13, 13], fill=GOLD)
    d.ellipse([4, 4, 11, 11], fill=GOLD_L, outline=OUT)
    d.ellipse([6, 6, 9, 9], fill=GOLD, outline=OUT)
    d.line([8, 3, 8, 5], fill=GOLD_D)
    d.line([8, 10, 8, 12], fill=GOLD_D)
    d.line([3, 8, 5, 8], fill=GOLD_D)
    d.line([10, 8, 12, 8], fill=GOLD_D)
    outline_pass(img)
    return img

def festkit():
    img, d = canvas(32, 32)
    d.rectangle([4, 12, 27, 28], fill=RED_D, outline=OUT)
    d.rectangle([3, 9, 28, 15], fill=RED, outline=OUT)
    d.rectangle([14, 9, 17, 28], fill=GOLD, outline=OUT)
    d.rectangle([14, 9, 14, 28], fill=GOLD_L)
    d.ellipse([10, 3, 15, 9], fill=GOLD, outline=OUT)
    d.ellipse([16, 3, 21, 9], fill=GOLD, outline=OUT)
    d.rectangle([15, 6, 16, 8], fill=GOLD_L, outline=OUT)
    d.ellipse([13, 18, 18, 23], fill=GOLD_L, outline=OUT)
    d.rectangle([15, 19, 16, 21], fill=RED_D)
    outline_pass(img)
    return img

def stampbook():
    img, d = canvas(32, 16)
    # 横放的集邮册：深蓝封面 + 左侧书脊 + 内页邮票格
    d.rounded_rectangle([2, 2, 29, 14], radius=1, fill=(44, 84, 112, 255), outline=OUT)
    d.rectangle([2, 2, 4, 14], fill=DARK)
    d.line([5, 2, 5, 14], fill=STEEL_L)
    for gy in (4, 9):
        for gx in (8, 13, 18):
            d.rectangle([gx, gy, gx + 3, gy + 3], fill=HI, outline=OUT)
            d.rectangle([gx + 1, gy + 1, gx + 2, gy + 2], fill=(176, 66, 58, 255))
    # 右侧书签/标签
    d.rectangle([23, 5, 27, 11], fill=GOLD, outline=OUT)
    d.line([24, 7, 26, 7], fill=RED_D)
    d.line([24, 9, 26, 9], fill=RED_D)
    outline_pass(img)
    return img

def ironstone():
    img, d = canvas(16, 16)
    d.polygon([(3, 10), (4, 6), (7, 3), (11, 4), (13, 8), (12, 12), (8, 14), (4, 13)],
              fill=(76, 70, 66, 255), outline=OUT)
    d.polygon([(5, 6), (7, 4), (10, 5), (8, 7)], fill=(104, 96, 90, 255))
    vein = (206, 64, 48, 255)
    vein_d = (132, 40, 34, 255)
    d.line([3, 10, 7, 8], fill=vein)
    d.line([7, 8, 9, 9], fill=vein)
    d.line([9, 9, 12, 6], fill=vein)
    d.line([7, 8, 7, 5], fill=vein_d)
    d.line([9, 9, 10, 12], fill=vein_d)
    d.rectangle([8, 8, 9, 9], fill=vein)
    d.rectangle([11, 5, 12, 6], fill=vein)
    outline_pass(img)
    return img

items = [
    ("oddity_tech_envscan", envscan()),
    ("oddity_tech_wrist", wrist()),
    ("oddity_cult_burger", burger()),
    ("oddity_cult_portcoin", portcoin()),
    ("oddity_cult_festkit", festkit()),
    ("oddity_cult_stampbk", stampbook()),
    ("oddity_xeno_iron", ironstone()),
]

out_dir = os.path.join("starter", "Textures", "Items")
os.makedirs(out_dir, exist_ok=True)
for name, img in items:
    img.save(os.path.join(out_dir, name + ".png"))
    print("saved", name, img.size)

# 拼一张 4 倍预览（含已完成的指节）
all_items = [("oddity_bio_knuckle", Image.open(os.path.join(out_dir, "oddity_bio_knuckle.png")))] + items
scale = 4
pad = 8
width = sum(im.width * scale + pad for _, im in all_items) + pad
height = max(im.height * scale for _, im in all_items) + pad * 2
prev = Image.new("RGBA", (width, height), (40, 44, 50, 255))
pd = ImageDraw.Draw(prev)
for yy in range(0, height, 16):
    for xx in range(0, width, 16):
        if (xx // 16 + yy // 16) % 2 == 0:
            pd.rectangle([xx, yy, xx + 15, yy + 15], fill=(54, 58, 64, 255))
x = pad
for _, im in all_items:
    big = im.resize((im.width * scale, im.height * scale), Image.NEAREST)
    prev.alpha_composite(big, (x, pad))
    x += big.width + pad
out_prev = os.path.join("SD-Picture", "preview_tier1.png")
os.makedirs("SD-Picture", exist_ok=True)
prev.save(out_prev)
print("preview", out_prev, prev.size)
