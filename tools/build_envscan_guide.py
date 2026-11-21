"""生成 Books/envscan_guide.json —— 《环境检测仪鉴定指南》（6 页）。

写法与 knuckle_guide 一致：书名固定在标题位、小节标题写在正文里、示例为清单式。
版式：628×804 设计空间 = 屏幕像素（1:1），正文区 172–740。

数值（2026-11-10 第 2 次调整）：
  基准 100，底线 40
  传感器：正常 0 / 偏移 −20 / 失效 −40
  机身  ：良好 0 / 磨损 −5 / 破损 −20
  插件  ：无 0 / 空气 +10 / 病菌 +15 / 双插件 +30
  厂商  ：无 0 / 蒸汽机械 +10 / 鲁班科技 +20
  套装  ：正常 + 良好 + 双插件 + 有厂商标 → 额外 +100
"""
import json
import os

OUT = r"D:\DSH_workspace\mod-create\mod\AppraisalExpansion\Books\envscan_guide.json"

CUR = "\u00a2"
BLUE = "#35526F"
INK = "#292234"
LIGHT = "#8b8375"

W, H = 628, 804
TITLE_EN = "Personal Environment Scanner Appraisal Guide"
TITLE_ZH = "环境检测仪鉴定指南"


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


def three_images(els, sprites, caps_en, caps_zh, y=236):
    for i, sprite in enumerate(sprites):
        x = 16 + i * 204 + (60, 30, 0)[i]
        els.append(image(x, y, 188, 236, sprite))
        els.append(caption(x - 4, y + 244, 196, caps_en[i], caps_zh[i]))


book = {
    "id": "envscan_guide",
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
"""Personal environment scanners are common on the station and their prices vary widely. This guide helps
fix a fair market value for any of them.

Every scanner starts at 100¢. The sensor, the body, the module and the maker all move the figure, but
whatever its state a scanner is never worth less than 40¢.""",
"""空间站上的个人环境检测仪种类繁多，价格也千差万别。本指南将帮助确定任何检测仪的公平市场价值。

所有检测仪的初始价值均为 100¢。传感器、机身、插件与厂商都会影响其价格，但无论状况如何，最低价值为 40¢。"""))
p1.append(heading("Base and floor value", "基础价值与最低价值", 286))
p1.append(body(70, 320, 506, 60,
"""Read the four factors in order, then add them up.""",
"""四项按顺序核定后相加。"""))
p1.append(image(226, 380, 176, 220, "envscan_good_ok"))
p1.append(caption(114, 606, 400, "Body good, sensor working.", "机身良好 · 传感器正常"))
book["pages"].append({"name": "Intro", "elements": p1})

# ============ 二、1.传感器状态 ============
p2 = page_head()
p2.append(heading("1. Sensor", "1.传感器状态"))
p2.append(body(70, 204, 506, 40,
"""Switch the device on and read the waveform and the indicator lamp.""",
"""开机，看波形与指示灯。"""))
three_images(p2,
             ["envscan_good_ok", "envscan_good_drift", "envscan_good_dead"],
             [f"Working (+0{CUR})", f"Offset (-20{CUR})", f"Dead (-40{CUR})"],
             [f"正常 (+0{CUR})", f"偏移 (-20{CUR})", f"失效 (-40{CUR})"])
p2.append(body(70, 526, 506, 130,
"""Working: the waveform is steady and the lamp is solid green.

Offset: the waveform drifts and the lamp is yellow.

Dead: the waveform no longer holds and the lamp is red.

The sensor is the one part that cannot be fixed with a screwdriver, tape or WD40.""",
"""正常：波形稳定，指示灯常绿。

偏移：波形偏移，指示灯为黄色。

失效：波形失去控制，指示灯为红色。

传感器是唯一无法使用螺丝刀、胶带和 WD40 修复的部件。"""))
book["pages"].append({"name": "Sensor", "elements": p2})

# ============ 三、2.机身品相 ============
p3 = page_head()
p3.append(heading("2. Body", "2.机身品相"))
p3.append(body(70, 204, 506, 40,
"""Check the seam, the coating and the screen.""",
"""检查接缝、表面涂层与屏幕。"""))
three_images(p3,
             ["envscan_good_ok", "envscan_worn_ok", "envscan_broken_ok"],
             [f"Good (+0{CUR})", f"Worn (-5{CUR})", f"Broken (-20{CUR})"],
             [f"良好 (+0{CUR})", f"磨损 (-5{CUR})", f"破损 (-20{CUR})"])
p3.append(body(70, 526, 506, 130,
"""Good: the seam is tight and the surface is clean and intact.

Worn: the surface is scratched and the coating is flaking.

Broken: the screen is damaged, buttons are missing and the coating has flaked away.

Light wear does not affect use, but heavy damage pulls the price down.""",
"""良好：接缝紧密，表面完好洁净。

磨损：表面有划痕，表面涂层存在剥落现象。

破损：屏幕损坏，按钮缺失，表面涂层剥落严重。

机身的轻微磨损不会影响使用，但严重的损坏会导致价值下跌。"""))
book["pages"].append({"name": "Body", "elements": p3})

# ============ 四、3.拓展插件 / 4.生产厂商 ============
p4 = page_head()
p4.append(heading("3. Module / 4. Maker", "3.拓展插件 / 4.生产厂商"))
p4.append(body(70, 204, 506, 40,
"""The module sits in the slot on the right side of the casing; the maker plate is on the left, above centre.""",
"""插件位于机身右侧的插槽内；厂商铭牌位于机身左侧面偏上的位置。"""))
# 四张示例图只有 50 高（原图本来就小），排成 2×2，图注紧贴图下
cells = [
    (60, 262, 19, "ill_envscan_plugin_air", "Air module (+10¢)", "空气插件 (+10¢)"),
    (318, 262, 18, "ill_envscan_plugin_bio", "Bio module (+15¢)", "病菌插件 (+15¢)"),
    (60, 356, 28, "ill_envscan_vendor_steam", "Steam Works (+10¢)", "蒸汽机械 (+10¢)"),
    (318, 356, 28, "ill_envscan_vendor_luban", "Luban Tech (+20¢)", "鲁班科技 (+20¢)"),
]
for cx, cy, w, sprite, cap_en, cap_zh in cells:
    p4.append(image(cx + (250 - w) // 2, cy, w, 50, sprite))
    p4.append(caption(cx, cy + 56, 250, cap_en, cap_zh))
p4.append(body(70, 436, 506, 90,
"""Modules can be fitted together, and two at once are worth more.

The maker plate also adds value.""",
"""插件可以同时插入，同时拥有两个插件可以带来额外价值。

厂商铭牌也会为检测仪带来额外的价值。"""))
p4.append(line(100, 552, 528, 552))
p4.append(body(70, 568, 506, 80,
"""Module: air +10¢, bio +15¢, both +30¢.
Maker: Steam Works +10¢, Luban Tech +20¢.""",
"""插件：空气 +10¢ ／ 病菌 +15¢ ／ 双插件 +30¢
厂商：蒸汽机械 +10¢ ／ 鲁班科技 +20¢"""))
book["pages"].append({"name": "Modules", "elements": p4})

# ============ 五、5.套装 ============
p5 = page_head()
p5.append(heading("5. Full kit", "5.套装"))
p5.append(body(70, 204, 506, 96,
"""A scanner with a working sensor, a good body, both modules fitted and a maker plate is called a full kit,
and adds a further 100¢ to the total.

The kit bonus is added once, after the four factors; it does not stack with itself.""",
"""传感器正常、机身良好、同时装有两个插件、并带厂商铭牌的检测仪，称为顶配套装，在四项合计之外额外加 100¢。

套装加成只计一次，加在四项之后，不再重复计算。"""))
p5.append(image(184, 320, 260, 260, "ill_envscan_set"))
p5.append(caption(70, 588, 506, "Working sensor, good body, both modules, maker plate.",
                  "传感器正常 · 机身良好 · 双插件 · 带厂商标"))
p5.append(body(70, 626, 506, 60,
"""A full kit of 250¢ is the upper limit of the class.""",
"""顶配套装的 250¢ 是本类物件的价格上限。"""))
book["pages"].append({"name": "Full kit", "elements": p5})

# ============ 六、示例 ============
p6 = page_head()
p6.append(heading("Example", "示例"))
p6.append(body(70, 206, 250, 150,
"""Full kit
Base: +100
Body good: +0
Sensor working: +0
Both modules: +30
Luban Tech: +20
Full kit: +100
Total: 250¢""",
"""顶配套装
基础：+100
机身良好：+0
传感器正常：+0
双插件：+30
鲁班科技：+20
套装加成：+100
总计：250¢"""))
p6.append(body(358, 206, 250, 150,
"""Floor piece
Base: +100
Body broken: -20
Sensor dead: -40
Subtotal: 40
Total: 40¢""",
"""底线件
基础：+100
机身破损：-20
传感器失效：-40
小计：40
总计：40¢"""))
p6.append(image(100, 386, 200, 200, "ill_envscan_set"))
p6.append(caption(94, 592, 212, "Full kit", "顶配套装"))
p6.append(image(328, 386, 200, 200, "ill_envscan_floor"))
p6.append(caption(322, 592, 212, "Floor piece", "底线件"))
book["pages"].append({"name": "Example", "elements": p6})

book["item"] = {
    "id": "envscan_guide",
    "name": TITLE_EN,
    "nameLoc": "envscan_guide_name",
    "description": "How to price a personal environment scanner.",
    "descriptionLoc": "envscan_guide_desc",
    "sprite": "items_misc/manual1",
    "value": 50,
    "important": True,
}

os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(book, fh, ensure_ascii=False, indent=2)
print("written", OUT, "pages", len(book["pages"]))
