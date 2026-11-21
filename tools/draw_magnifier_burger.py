"""程序化绘制：汉堡的放大镜大幅素材 456×402（像素风、透明底）。"""
from PIL import Image, ImageDraw
import os

W, H = 456, 402
OUT = (24, 26, 30, 255)
BUN_T = (176, 120, 66, 255)
BUN_T_L = (208, 152, 92, 255)
BUN_T_D = (134, 88, 48, 255)
BUN_B = (198, 140, 82, 255)
BUN_B_D = (150, 100, 56, 255)
LET = (98, 172, 98, 255)
LET_L = (132, 198, 122, 255)
LET_D = (62, 122, 68, 255)
CHE = (238, 186, 74, 255)
CHE_D = (194, 138, 46, 255)
PAT = (94, 60, 38, 255)
PAT_D = (62, 38, 24, 255)
PAT_L = (124, 82, 52, 255)
PAPER = (216, 204, 180, 255)
PAPER_L = (238, 230, 210, 255)
PAPER_D = (176, 162, 136, 255)
WHITE = (244, 240, 232, 255)
RED = (178, 62, 52, 255)

img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
d = ImageDraw.Draw(img)

# ---- 包装纸（在汉堡后面） ----
d.polygon([(34, 300), (70, 258), (150, 244), (228, 250), (306, 244), (386, 258), (424, 300),
           (420, 384), (390, 396), (66, 396), (36, 384)], fill=PAPER, outline=OUT, width=4)
# 纸张折痕
d.line([70, 270, 96, 388], fill=PAPER_D, width=3)
d.line([386, 270, 360, 388], fill=PAPER_D, width=3)
d.line([120, 262, 130, 300], fill=PAPER_L, width=3)
d.line([330, 262, 320, 300], fill=PAPER_L, width=3)

# ---- 底面包 ----
d.rounded_rectangle([74, 262, 382, 322], radius=26, fill=BUN_B, outline=OUT, width=4)
d.line([96, 286, 360, 286], fill=BUN_B_D, width=3)
d.arc([88, 272, 368, 316], start=200, end=340, fill=(228, 176, 112, 255), width=4)

# ---- 肉饼 ----
d.rounded_rectangle([70, 210, 386, 274], radius=18, fill=PAT, outline=OUT, width=4)
for x in range(92, 370, 26):
    d.ellipse([x, 224, x + 22, 236], fill=PAT_D)
    d.ellipse([x + 8, 246, x + 20, 254], fill=PAT_L)
d.line([84, 220, 372, 220], fill=(140, 96, 62, 255), width=3)

# ---- 芝士（带滴落） ----
d.rectangle([78, 194, 378, 224], fill=CHE, outline=OUT, width=4)
for x in range(92, 366, 34):
    d.polygon([(x, 222), (x + 26, 222), (x + 22, 248), (x + 12, 236), (x + 4, 246)], fill=CHE, outline=OUT)

# ---- 生菜 ----
for x in range(66, 380, 24):
    d.ellipse([x, 176, x + 34, 208], fill=LET, outline=OUT, width=3)
for x in range(78, 372, 30):
    d.arc([x, 180, x + 28, 204], start=200, end=340, fill=LET_L, width=3)
d.rectangle([74, 190, 382, 200], fill=LET_D)

# ---- 顶面包 ----
d.ellipse([62, 54, 394, 196], fill=BUN_T, outline=OUT, width=4)
d.arc([84, 70, 372, 184], start=196, end=262, fill=BUN_T_L, width=10)
d.arc([84, 70, 372, 184], start=40, end=120, fill=BUN_T_D, width=8)
# 芝麻
for sx, sy in ((120, 96), (156, 80), (196, 72), (238, 70), (280, 74), (318, 84), (352, 100),
               (142, 118), (184, 104), (228, 100), (272, 102), (310, 112), (338, 128),
               (168, 138), (210, 132), (252, 132), (292, 138)):
    d.ellipse([sx, sy, sx + 14, sy + 8], fill=WHITE, outline=OUT, width=2)

# ---- 包装纸上的标签 ----
d.rounded_rectangle([292, 316, 392, 378], radius=6, fill=WHITE, outline=OUT, width=3)
for x in range(302, 382, 8):
    d.line([x, 328, x, 356], fill=OUT, width=3)
d.rectangle([302, 360, 350, 366], fill=RED)
d.ellipse([360, 356, 380, 372], outline=RED, width=3)

img.save(os.path.join("starter", "Textures", "Items", "_magnifier_burger.png"))
print("saved", img.size)
