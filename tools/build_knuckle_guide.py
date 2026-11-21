"""生成 Books/knuckle_guide.json —— 仿照游戏内《仿生机械手鉴定指南》的排版与写法。

依据（2026-11-10 从 resources.assets 里直接读出的原版文本，偏移 55,827,920 附近）：
  1. 每页第 2 行是**书名**：「仿生指节鉴定指南」，不是页面主题；
  2. 小节标题写在正文里：「基础价值与最低价值」「1.材料」「2.品相」「3.控制接口」；
  3. 小节下先一句判定方法，再横排三张图，图注只写名称（铝合金 / 钢 / 镀金）；
  4. 示例段是**清单式**：基础：+85 / 镀金：+70 / 无：+0 / EMG+：+15 / 总计：170¢，
     对应原版“基础：+100 / 碳复合材料：+50 / 磨损：-35 / EMG+：+45 / 总计：160信用点”；
  5. 中文走 translations（zh-Hans + zh），英文为兜底 text；
  6. 每页填充目标 75%–85%（内容底边 y≈604–684）。
"""
import json
import os

OUT = r"D:\DSH_workspace\mod-create\mod\AppraisalExpansion\Books\knuckle_guide.json"

CUR = "\u00a2"
BLUE = "#35526F"
INK = "#292234"
LIGHT = "#8b8375"

W, H = 628, 804
BOOK_TITLE_EN = "Cybernetic Knuckle Appraisal Guide"
BOOK_TITLE_ZH = "仿生指节鉴定指南"


def tr(zh):
    return {"zh-Hans": zh, "zh": zh}


def text_el(x, y, w, h, en, zh, style="title", size=15, align="left", wrap=True, color=INK, ident=None):
    el = {"type": "text", "x": x, "y": y, "w": w, "h": h, "text": en,
          "translations": tr(zh), "style": style, "fontSize": size,
          "align": align, "wrap": wrap, "color": color}
    if ident:
        el["id"] = ident
    return el


def page_head():
    """机构名 + 书名（原版每页都是书名，不是页面主题）。"""
    return [
        text_el(144, 68, 346, 36, "STATION TRADE COMMISSION", "空间站贸易委员会",
                style="header", size=22, align="center", wrap=False, color=BLUE, ident="header"),
        text_el(56, 100, 524, 46, BOOK_TITLE_EN, BOOK_TITLE_ZH,
                style="title", size=24, align="center", wrap=False, color=BLUE, ident="title"),
    ]


def heading(en, zh, y=172):
    """小节标题：写在正文里（原版是「1.材料」这种），不是页面标题。"""
    return text_el(70, y, 506, 26, en, zh, style="label", size=18, wrap=False, color=BLUE)


def body(x, y, w, h, en, zh, align="left", size=15):
    return text_el(x, y, w, h, en, zh, style="title", size=size, align=align, wrap=True, color=INK)


def caption(x, y, w, en, zh, size=15):
    return text_el(x, y, w, 20, en, zh, style="caption", size=size, align="center", wrap=False, color=INK)


def image(x, y, w, h, sprite):
    return {"type": "image", "x": x, "y": y, "w": w, "h": h, "sprite": sprite, "fit": "fit"}


def line(x, y, x2, y2, t=1.2):
    return {"type": "line", "x": x, "y": y, "x2": x2, "y2": y2, "thickness": t, "color": BLUE}


def three_images(els, sprites, caps_en, caps_zh, y=236):
    for i, sprite in enumerate(sprites):
        x = 16 + i * 204 + (60, 30, 0)[i]
        els.append(image(x, y, 188, 236, sprite))
        els.append(caption(x - 4, y + 244, 196, caps_en[i], caps_zh[i]))


book = {
    "id": "knuckle_guide",
    "title": BOOK_TITLE_EN,
    "background": "paper_bg",
    "designWidth": W,
    "designHeight": H,
    "width": W,
    "height": H,
    "posX": -450,
    "posY": 0,
    "chrome": [
        {"type": "button", "id": "close", "action": "close", "sprite": "btn_close",
         "x": 582, "y": 17, "w": 28, "h": 30},
        {"type": "button", "id": "zoom", "action": "zoom", "sprite": "btn_zoom",
         "x": 535, "y": 19, "w": 28, "h": 30},
        {"type": "button", "id": "flip_left", "action": "flip_left", "sprite": "btn_prev",
         "x": 253, "y": 760, "w": 28, "h": 30},
        {"type": "button", "id": "flip_right", "action": "flip_right", "sprite": "btn_next",
         "x": 347, "y": 761, "w": 28, "h": 30},
        {"type": "text", "id": "page_indicator", "action": "page_indicator", "style": "page_number",
         "fontSize": 30, "color": LIGHT, "align": "center", "valign": "middle", "wrap": False,
         "x": 281, "y": 748, "w": 66, "h": 50},
    ],
    "pages": [],
}

# ============ 一、引言 + 基础价值与最低价值 ============
p1 = page_head()
p1.append(body(70, 166, 506, 100,
"""Cybernetic knuckles are many and their prices vary widely. This guide helps fix a fair market value
for any of them.

Every knuckle starts at 85¢. Shell material, condition and interface marking all move the figure, but
whatever its state a knuckle is never worth less than 35¢.""",
"""空间站上的仿生指节种类繁多，价格也千差万别。本指南将帮助确定任何仿生指节的公平市场价值。

所有仿生指节的初始价值均为 85¢。材质、品相与接口刻字都会影响其价格。但无论状况如何，仿生指节的最低价值为 35¢。"""))
p1.append(heading("Base and floor value", "基础价值与最低价值", 286))
p1.append(body(70, 320, 506, 60,
"""Evaluate the three factors in order, then add them up. Note the floor before arguing the total.""",
"""三项按顺序核定后相加。先记底线，再谈总数。"""))
p1.append(image(226, 380, 176, 220, "ill_iface_emg"))
p1.append(caption(114, 606, 400, "Steel shell, no wear, EMG marking.",
                  "钢壳 · 品相无 · EMG 刻号"))
book["pages"].append({"name": "Intro", "elements": p1})

# ============ 二、1.材料 ============
p2 = page_head()
p2.append(heading("1. Material", "1.材料"))
p2.append(body(70, 204, 506, 60,
"""Turn the piece in daylight and read the highlight and the grain.""",
"""在自然光下转动物件，看高光与表面颗粒。"""))
three_images(p2,
             ["ill_material_alu", "ill_material_steel", "ill_material_gold"],
             [f"Aluminium alloy (+0{CUR})", f"Steel (+30{CUR})", f"Gold-plated (+70{CUR})"],
             [f"铝合金 (+0{CUR})", f"钢 (+30{CUR})", f"镀金 (+70{CUR})"])
p2.append(body(70, 526, 506, 110,
"""Aluminium is matte and cold; steel has fine rolled grain and a hard highlight; gold plating is warm
and fades toward the edges.

The gap follows processing cost and supply: gold plating was a custom order, so scarcity drives it.
Turn the piece rather than the lamp: highlights at corners shift with the angle of reflection.""",
"""铝合金哑光偏冷；钢有细密轧制纹路、高光硬；镀金偏暖，向边缘渐弱。

价差来自加工成本与存量：镀金原为定制件，溢价主要源于稀有度。读数时应转动物件，而不是移动光源——高光在转角处会因反光角度而失真。"""))
book["pages"].append({"name": "Material", "elements": p2})

# ============ 三、2.品相 ============
p3 = page_head()
p3.append(heading("2. Condition", "2.品相"))
p3.append(body(70, 204, 506, 60,
"""Open the joint gap with the magnifier and inspect the pins and the cable run.""",
"""用放大镜撑开关节缝隙，检视销钉与走线。"""))
three_images(p3,
             ["ill_condition_normal", "ill_condition_wear", "ill_condition_damage"],
             [f"None (+0{CUR})", f"Worn (-25{CUR})", f"Damaged (-50{CUR})"],
             [f"无 (+0{CUR})", f"磨损 (-25{CUR})", f"受损 (-50{CUR})"])
p3.append(body(70, 526, 506, 110,
"""The knuckle is a double-pin part: the gap is designed clearance. A gap is not looseness; looseness
is a pin moving in its bore. Exposed cable or restricted travel is damage, and is priced as such; damage is the only grade
that affects whether the part still works, so it carries the largest deduction. No solvents inside the gap;
a dry cloth is enough.""",
"""指节为双销结构，缝隙是设计预留量：有缝隙不等于松动，判断松动看销钉能否在孔内晃动。走线外露或转动受阻即为受损，按受损一档计价。三档之中，只有受损会影响能否正常使用，故扣减最多。缝隙内不得使用溶剂，干布擦拭即可。"""))
book["pages"].append({"name": "Condition", "elements": p3})

# ============ 四、3.控制接口 ============
p4 = page_head()
p4.append(heading("3. Interface marking", "3.控制接口"))
p4.append(body(70, 204, 506, 60,
"""Read the plate below the joint; confirm the depth of the cut with the magnifier.""",
"""辨认关节下方的铭牌；必要时用放大镜确认刻痕深度。"""))
three_images(p4,
             ["ill_iface_none", "ill_iface_emg", "ill_iface_emgplus"],
             [f"Unknown (-15{CUR})", f"EMG (+0{CUR})", f"EMG+ (+15{CUR})"],
             [f"规格不明 (-15{CUR})", f"EMG (+0{CUR})", f"EMG+ (+15{CUR})"])
p4.append(body(70, 526, 506, 110,
"""Factory marks are cold-struck, leaving a regular squeeze pattern at the bottom of the groove. EMG+ is
the factory stamp, EMG the civilian standard; a plate without a mark is priced as unknown. The gap
between EMG and EMG+ reflects compatibility with factory hosts. The plate sits under the shell edge; read it
in raking light. An unreadable cut is priced as unknown.""",
"""原厂刻号为冷冲压成形，槽底留有规则挤压纹。EMG+ 为原厂刻号，EMG 为民用标准刻号；未有刻号者一律按规格不明计价。EMG 与 EMG+ 的差价，来自与原厂主机的兼容程度。铭牌被外壳边缘遮挡，需侧光查看。刻痕过浅或不可辨者，按规格不明处理。"""))
book["pages"].append({"name": "Interface", "elements": p4})

# ============ 五、4.计价 ============
rows = [
    ("Material", "材质", [("Aluminium alloy", "铝合金", "+0"), ("Steel", "钢", "+30"), ("Gold-plated", "镀金", "+70")]),
    ("Condition", "品相", [("None", "无", "+0"), ("Worn", "磨损", "-25"), ("Damaged", "受损", "-50")]),
    ("Interface", "接口", [("Unknown", "规格不明", "-15"), ("EMG", "EMG", "+0"), ("EMG+", "EMG+", "+15")]),
]
p5 = page_head()
p5.append(heading("4. Pricing", "4.计价"))
p5.append(body(70, 206, 506, 26,
               f"value = max({CUR}35, {CUR}85 + material + condition + interface)",
               f"价值 = max({CUR}35, {CUR}85 + 材质 + 品相 + 接口)", "center", 16))
p5.append(line(100, 246, 528, 246))
y = 258
for group_en, group_zh, entries in rows:
    p5.append(text_el(70, y, 240, 20, group_en, group_zh, style="label", size=16, wrap=False, color=BLUE))
    y += 22
    for k_en, k_zh, v in entries:
        p5.append(body(90, y, 438, 20, f"{k_en}  {v}{CUR}", f"{k_zh}  {v}{CUR}", "right", 15))
        y += 21
    y += 8
p5.append(line(100, y, 528, y))
p5.append(body(70, y + 16, 506, 130,
"""Take the base from the shell, subtract for condition, then adjust for the marking. Round to 5¢ at the
counter; tolerance is ±5%.

Limits: gold-plated + EMG+ + sound = 170¢; unknown + damaged = 35¢.""",
"""先由外壳取基准，再按品相扣减，最后按接口调整。成交按 5¢ 取整，容差 ±5%。

上下限：镀金 + EMG+ + 无 = 170¢；规格不明 + 受损 = 35¢。"""))
book["pages"].append({"name": "Pricing", "elements": p5})

# ============ 六、示例 一 ============
e1 = page_head()
e1.append(heading("Example I", "示例 · 一"))
e1.append(body(70, 208, 506, 118,
"""Base: +85
Gold-plated: +70
Sound: +0
EMG+: +15
Total: 170¢""",
"""基础：+85
镀金：+70
无：+0
EMG+：+15
总计：170¢"""))
e1.append(image(184, 300, 260, 260, "ill_example_gold"))
e1.append(caption(70, 526, 506, "Gold-plated shell, no wear, EMG+ marking.",
                  "镀金外壳 · 品相无 · EMG+ 刻号"))
e1.append(body(70, 580, 506, 60,
"""The upper limit of the class, and the reference sample for gold-plated pieces; check the three factors
the same way, price nothing else, and record nothing extra.""",
"""该类上限，也是镀金件的参照样本。遇同类件照此核对三项，不另计价，亦不写入备注。"""))
book["pages"].append({"name": "Example I", "elements": e1})

# ============ 七、示例 二 ============
e2 = page_head()
e2.append(heading("Example II", "示例 · 二"))
e2.append(body(70, 208, 506, 124,
"""Base: +85
Aluminium alloy: +0
Worn: -25
Unknown: -15
Subtotal: +45
Total: 45¢""",
"""基础：+85
铝合金：+0
磨损：-25
规格不明：-15
小计：+45
总计：45¢"""))
e2.append(image(184, 300, 260, 260, "ill_example_alu"))
e2.append(caption(70, 526, 506, "Aluminium shell, worn joint, no marking.",
                  "铝合金外壳 · 磨损关节 · 未打刻铭牌"))
e2.append(body(70, 580, 506, 60,
"""The lower end of the ordinary range: a common second-hand part, taken only with a note on source.
Below this figure the piece is broken for parts.""",
"""普通品相下限：常见二手件，须在备注中记明来源；低于此价者按拆件处理。"""))
book["pages"].append({"name": "Example II", "elements": e2})

book["item"] = {
    "id": "knuckle_guide",
    "name": BOOK_TITLE_EN,
    "nameLoc": "guide_name",
    "description": "How to price a cybernetic knuckle: shell, condition and interface.",
    "descriptionLoc": "guide_desc",
    "sprite": "items_misc/manual1",
    "value": 50,
    "important": True,
}

os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(book, fh, ensure_ascii=False, indent=2)
print("written", OUT, "pages", len(book["pages"]))
