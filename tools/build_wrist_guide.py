"""生成 Books/wrist_guide.json —— 《腕式通讯终端鉴定指南》（6 页）。

写法与 knuckle/envscan 两本一致：书名固定在标题位、小节标题写在正文里、示例为清单式。
版式：628×804 设计空间 = 屏幕像素（1:1），正文区 172–740。

数值（2026-11-17 定稿）：
  基准 100，底线 40
  品相：全新 0 / 磨损 −20 / 损坏 −40
  材质：铸铁 0 / 镀金 +200
  服务：卫星中继 +40 / 加密通信 +50 / 双服务 +120
  轻奢套装：全新 + 镀金 +（卫星中继 或 双服务）→ 额外 +200

依赖的插图（由 tools/make_wrist_ill.py 用底图 + 叠层合成，放在 assets/paper/）：
  ill_wrist_relay / ill_wrist_crypt / ill_wrist_set / ill_wrist_floor
"""
import json
import os

OUT = r"D:\DSH_workspace\mod-create\mod\AppraisalExpansion\Books\wrist_guide.json"

CUR = "\u00a2"
BLUE = "#35526F"
INK = "#292234"
LIGHT = "#8b8375"

W, H = 628, 804
TITLE_EN = "Wrist Comm Terminal Appraisal Guide"
TITLE_ZH = "腕式通讯终端鉴定指南"


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
    return [
        text_el(144, 68, 346, 36, "STATION TRADE COMMISSION", "空间站贸易委员会",
                style="header", size=22, align="center", wrap=False, color=BLUE, ident="header"),
        text_el(56, 100, 524, 46, TITLE_EN, TITLE_ZH,
                style="title", size=24, align="center", wrap=False, color=BLUE, ident="title"),
    ]


def heading(en, zh, y=172):
    return text_el(70, y, 506, 26, en, zh, style="label", size=18, wrap=False, color=BLUE)


def body(x, y, w, h, en, zh, align="left", size=15):
    return text_el(x, y, w, h, en, zh, style="title", size=size, align=align, wrap=True, color=INK)


def caption(x, y, w, en, zh):
    return text_el(x, y, w, 20, en, zh, style="caption", size=15, align="center", wrap=False, color=INK)


def image(x, y, w, h, sprite):
    return {"type": "image", "x": x, "y": y, "w": w, "h": h, "sprite": sprite, "fit": "fit"}


def line(x, y, x2, y2, t=1.2):
    return {"type": "line", "x": x, "y": y, "x2": x2, "y2": y2, "thickness": t, "color": BLUE}


def row_images(els, cells):
    """cells: [(cx, cy, w, h, sprite, cap_en, cap_zh)]，图在 220 宽格内居中，图注在格下。"""
    for cx, cy, w, h, sprite, cap_en, cap_zh in cells:
        els.append(image(cx + (220 - w) // 2, cy, w, h, sprite))
        els.append(caption(cx - 2, cy + h + 6, 224, cap_en, cap_zh))


book = {
    "id": "wrist_guide",
    "title": TITLE_EN,
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

# ============ 一、总则 ============
p1 = page_head()
p1.append(body(70, 166, 506, 100,
"""Wrist comm terminals are sold on every ring of the station. This guide fixes a fair market value for
any of them.

Every terminal starts at 100¢. Condition, casing and the services enabled on it move the figure, but
whatever its state a terminal is never worth less than 40¢.""",
"""腕式通讯终端在各环层都有流通。本指南用于确定任何一台终端的公平市场价值。

所有终端的初始价值均为 100¢。品相、材质与所开通的服务都会影响其价格，但无论状况如何，最低价值为 40¢。"""))
p1.append(heading("Base and floor value", "基础价值与最低价值", 286))
p1.append(body(70, 320, 506, 60,
"""Read the three factors in order, then add them up.""",
"""三项按顺序核定后相加。"""))
p1.append(image(226, 380, 176, 220, "ill_wrist_relay"))
p1.append(caption(114, 606, 400, "Cast casing, new, relay service.", "铸铁材质 · 全新 · 卫星中继"))
book["pages"].append({"name": "Intro", "elements": p1})

# ============ 二、1.品相 ============
p2 = page_head()
p2.append(heading("1. Condition", "1.品相"))
p2.append(body(70, 204, 506, 40,
"""Check the screen, the buttons and the coating.""",
"""检查屏幕、按键与表面涂层。"""))
for i, (sprite, cap_en, cap_zh) in enumerate([
        ("wrist_iron_new", "New (+0¢)", "全新 (+0¢)"),
        ("wrist_iron_worn", "Worn (-20¢)", "磨损 (-20¢)"),
        ("wrist_iron_damaged", "Damaged (-40¢)", "损坏 (-40¢)")]):
    x = 16 + i * 204 + (60, 30, 0)[i]
    p2.append(image(x, 236, 188, 236, sprite))
    p2.append(caption(x - 4, 480, 196, cap_en, cap_zh))
p2.append(body(70, 520, 506, 120,
"""New: the screen is unmarked and every button clicks.

Worn: fine scratches on the case, and the leather strap is worn.

Damaged: the screen is badly cracked.""",
"""全新：屏幕无痕，按键回弹正常。

磨损：表面有细划痕，皮革表带磨损。

损坏：屏幕开裂严重。"""))
book["pages"].append({"name": "Condition", "elements": p2})

# ============ 三、2.材质 ============
p3 = page_head()
p3.append(heading("2. Casing", "2.材质"))
p3.append(body(70, 204, 506, 40,
"""Compare the colour of the highlight and the grain under daylight.""",
"""在自然光下比较高光色调与表面纹理。"""))
row_images(p3, [
    (70, 244, 200, 250, "wrist_iron_new", "Cast iron (+0¢)", "铸铁 (+0¢)"),
    (338, 244, 200, 250, "wrist_gold_new", "Gold-plated (+200¢)", "镀金 (+200¢)"),
])
p3.append(body(70, 545, 506, 110,
"""Cast iron reads cold and matte, with a broad soft highlight.

Gold plating reads warm, and the highlight falls away toward the edges; the grain of the base metal
still shows at the corners.""",
"""铸铁偏冷、哑光，高光宽而柔。

镀金偏暖，高光向边缘减弱，转角处仍能看见底层金属的纹理。"""))
book["pages"].append({"name": "Casing", "elements": p3})

# ============ 四、3.支持服务 ============
p4 = page_head()
p4.append(heading("3. Services", "3.支持服务"))
p4.append(body(70, 204, 506, 46,
"""Read the two service tags at the top right of the screen; the relay tag is a simplified satellite and the
encryption tag is a key.""",
"""辨认屏幕右上角的两枚服务标：卫星中继的图标是一颗简化的卫星，加密通信的图标是一把钥匙。"""))
p4.append(body(70, 254, 506, 90,
"""Both tags together give +120¢, which is more than the two separate figures added up: a terminal that
carries both was a subscriber unit, not a retail one.

No tag at all means no service, and no service adds nothing.""",
"""两枚标同时在，按双服务 +120¢ 计，高于两项单独相加——同时开通两项的通常是合约机，不是零售机。

两枚标都没有即未开通，本项不加价；开通了哪几项，估值时就记哪几项。"""))
for i, (sprite, cap_en, cap_zh) in enumerate([
        ("wrist_iron_new", "None (+0¢)", "未开通 (+0¢)"),
        ("ill_wrist_relay", "Satellite relay (+40¢)", "卫星中继 (+40¢)"),
        ("ill_wrist_crypt", "Encrypted comms (+50¢)", "加密通信 (+50¢)"),
        ("ill_wrist_both", "Both (+120¢)", "双服务 (+120¢)")]):
    cx = 70 if i % 2 == 0 else 338
    cy = 344 if i < 2 else 512
    p4.append(image(cx + 40, cy, 140, 140, sprite))
    p4.append(caption(cx, cy + 146, 220, cap_en, cap_zh))
book["pages"].append({"name": "Services", "elements": p4})

# ============ 五、4.轻奢套装 ============
p5 = page_head()
p5.append(heading("4. Luxe kit", "4.轻奢套装"))
p5.append(body(70, 204, 506, 96,
"""A terminal that is new, gold-plated, and carries the satellite relay tag (alone or with encryption) is
called a luxe kit, and adds a further 200¢.

The kit bonus is added once, after the three factors.""",
"""全新、镀金、且带卫星中继标（单独或与加密通信同时具备）的终端，称为轻奢套装，在三项合计之外再额外加 200¢。

套装加成只计一次，加在三项之后。"""))
p5.append(image(184, 320, 260, 260, "ill_wrist_set"))
p5.append(caption(70, 588, 506, "New, gold-plated, both services.", "全新 · 镀金 · 双服务"))
p5.append(body(70, 626, 506, 60,
"""A luxe kit of 620¢ is the upper limit of this item.""",
"""轻奢套装的 620¢ 是本类物件的价格上限。"""))
book["pages"].append({"name": "Luxe kit", "elements": p5})

# ============ 六、示例 ============
p6 = page_head()
p6.append(heading("Example", "示例"))
p6.append(body(70, 206, 250, 160,
"""Luxe kit
Base: +100
New: +0
Gold-plated: +200
Both services: +120
Luxe kit: +200
Total: 620¢""",
"""轻奢套装
基础：+100
全新：+0
镀金：+200
双服务：+120
套装加成：+200
总计：620¢"""))
p6.append(body(358, 206, 250, 160,
"""Ordinary piece
Base: +100
Damaged: -40
Cast iron: +0
Relay only: +40
Total: 100¢""",
"""普通件
基础：+100
损坏：−40
铸铁：+0
仅卫星中继：+40
总计：100¢"""))
p6.append(image(100, 396, 200, 200, "ill_wrist_set"))
p6.append(caption(94, 602, 212, "Luxe kit", "轻奢套装"))
p6.append(image(328, 396, 200, 200, "ill_wrist_floor"))
p6.append(caption(322, 602, 212, "Ordinary piece", "普通件"))
book["pages"].append({"name": "Example", "elements": p6})

book["item"] = {
    "id": "wrist_guide",
    "name": TITLE_EN,
    "nameLoc": "wrist_guide_name",
    "description": "How to price a wrist comm terminal.",
    "descriptionLoc": "wrist_guide_desc",
    "sprite": "items_misc/manual1",
    "value": 50,
    "important": True,
}

os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(book, fh, ensure_ascii=False, indent=2)
print("written", OUT, "pages", len(book["pages"]))
