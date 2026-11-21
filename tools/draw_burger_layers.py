"""照着原版肋明治的规格，画汉堡的分层放大素材（265×104，透明底）。"""
from PIL import Image, ImageDraw
import os

W, H = 265, 104
OUT = (41, 34, 52, 255)      # 原版描边 #292234
BUN = (186, 137, 83, 255)
BUN_L = (204, 185, 135, 255)
BUN_D = (149, 92, 75, 255)
BUN_M = (177, 120, 77, 255)
PAT = (100, 52, 59, 255)
PAT_D = (74, 47, 56, 255)
PAT_L = (133, 55, 55, 255)
PAT_H = (125, 79, 74, 255)
LET = (111, 138, 78, 255)
LET_D = (86, 111, 70, 255)
CHE = (204, 185, 135, 255)
CHE_D = (186, 137, 83, 255)
LABEL = (92, 111, 70, 255)
LABEL_L = (224, 208, 155, 255)
PAPER = (224, 208, 155, 255)

def canvas():
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    return img, ImageDraw.Draw(img)

def top_bun(fake=False):
    img, d = canvas()
    base = (166, 120, 96, 255) if fake else BUN
    d.ellipse([26, 2, 238, 56], fill=base, outline=OUT, width=2)
    d.arc([40, 8, 224, 50], start=198, end=262, fill=BUN_L, width=6)
    d.arc([40, 8, 224, 50], start=30, end=110, fill=BUN_D, width=5)
    seeds = ((62, 16), (94, 10), (128, 8), (162, 9), (194, 14), (214, 24),
             (76, 28), (110, 22), (146, 20), (180, 22), (206, 34))
    for sx, sy in seeds:
        d.ellipse([sx, sy, sx + 7, sy + 4], fill=BUN_L, outline=OUT, width=1)
    return img

def lettuce():
    img, d = canvas()
    for x in range(24, 236, 16):
        d.ellipse([x, 46, x + 22, 62], fill=LET, outline=OUT, width=2)
    d.rectangle([30, 52, 234, 58], fill=LET_D)
    for x in range(34, 230, 22):
        d.arc([x, 48, x + 16, 58], start=200, end=340, fill=(140, 166, 100, 255), width=2)
    return img

def cheese():
    img, d = canvas()
    d.rectangle([28, 54, 236, 66], fill=CHE, outline=OUT, width=2)
    for x in range(36, 230, 22):
        d.polygon([(x, 64), (x + 14, 64), (x + 12, 74), (x + 7, 68), (x + 2, 73)], fill=CHE, outline=OUT)
    d.line([32, 57, 232, 57], fill=CHE_D, width=2)
    return img

def patty():
    img, d = canvas()
    d.rounded_rectangle([22, 62, 242, 90], radius=9, fill=PAT, outline=OUT, width=2)
    for x in range(30, 232, 18):
        d.ellipse([x, 64, x + 16, 72], fill=PAT_D)
        d.ellipse([x + 5, 78, x + 13, 84], fill=PAT_H)
    for x in range(36, 228, 26):
        d.rectangle([x, 70, x + 2, 71], fill=PAT_L)
        d.rectangle([x + 8, 74, x + 9, 75], fill=(196, 138, 118, 255))
    return img

def bottom_bun():
    img, d = canvas()
    d.rounded_rectangle([30, 84, 236, 102], radius=8, fill=BUN_M, outline=OUT, width=2)
    d.line([44, 92, 222, 92], fill=BUN_D, width=2)
    d.arc([38, 86, 228, 100], start=200, end=340, fill=BUN_L, width=2)
    return img

def logo():
    img, d = canvas()
    d.rectangle([108, 30, 158, 48], fill=LABEL, outline=OUT, width=2)
    d.rectangle([112, 33, 154, 45], outline=LABEL_L)
    d.rectangle([126, 36, 140, 38], fill=LABEL_L)
    d.rectangle([122, 40, 144, 42], fill=LABEL_L)
    return img

def barcode():
    img, d = canvas()
    d.rectangle([40, 82, 92, 100], fill=PAPER, outline=OUT, width=2)
    for x in range(44, 88, 5):
        d.line([x, 85, x, 97], fill=OUT, width=2)
    return img

layers = [bottom_bun(), patty(), cheese(), lettuce(), top_bun(False), logo(), barcode()]
out_dir = r"starter\Textures\Items"
for name, im in zip(["burger_bottom_bun","burger_patty","burger_cheese","burger_lettuce","burger_top_bun","burger_logo","burger_barcode"], layers):
    im.save(os.path.join(out_dir, name + ".png"))
top_bun(True).save(os.path.join(out_dir, "burger_top_bun_fake.png"))

# 合成预览
comp = Image.new("RGBA", (W, H), (0, 0, 0, 0))
for im in layers:
    comp.alpha_composite(im)
comp.save(os.path.join(out_dir, "magnifier_burger_layered.png"))

from PIL import ImageDraw
c = Image.new("RGBA", (W*3+40, H*3+40), (40, 44, 50, 255))
dd = ImageDraw.Draw(c)
for yy in range(0, c.height, 16):
    for xx in range(0, c.width, 16):
        if (xx//16+yy//16) % 2 == 0:
            dd.rectangle([xx, yy, xx+15, yy+15], fill=(54, 58, 64, 255))
c.alpha_composite(comp.resize((W*3, H*3), Image.NEAREST), (20, 20))
c.save(r"SD-Picture\burger_layered_preview.png")
print("done", comp.size)
