"""生成 Books/coin_guide.json —— 《开港纪念币鉴定指南》（6 页）。

版式与另三本一致：书名固定在标题位、小节标题写在正文里、示例为清单式。
填充目标 75%–85%（628×804 设计空间，内容底边 603–684）。
"""
import json
import os

OUT = r"D:\DSH_workspace\mod-create\mod\AppraisalExpansion\Books\coin_guide.json"

BLUE = "#35526F"
INK = "#292234"
LIGHT = "#8b8375"

W, H = 628, 804
TITLE_EN = "Ninth Ring Port Commemorative Coin Appraisal Guide"
TITLE_ZH = "开港纪念币鉴定指南"


def tr(zh):
    return {"zh-Hans": zh, "zh": zh}


def text_el(x, y, w, h, en, zh, style="title", size=15, align="left", wrap=True,
            color=INK, ident=None):
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


def body(x, y, w, h, en, zh, size=15, align="left"):
    return text_el(x, y, w, h, en, zh, style="title", size=size, align=align, wrap=True, color=INK)


def caption(x, y, w, en, zh):
    return text_el(x, y, w, 20, en, zh, style="caption", size=14, align="center", wrap=False, color=INK)


def image(x, y, w, h, sprite):
    return {"type": "image", "x": x, "y": y, "w": w, "h": h, "sprite": sprite, "fit": "fit"}


def line(x, y, x2, y2):
    return {"type": "line", "x": x, "y": y, "x2": x2, "y2": y2, "thickness": 1.2, "color": BLUE}


book = {
    "id": "coin_guide",
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
p1.append(body(70, 166, 506, 110,
"""Commemorative coins from the Ninth Ring Port are traded on every level of the station. This guide fixes a
fair market value for any of them.

Every coin starts at 100¢ and is never worth less than 40¢.""",
"""第九环港开港纪念币在各环层都有流通。本指南用于确定任何一枚纪念币的公平市场价值。

所有纪念币的初始价值均为 100¢，无论状况如何，最低价值为 40¢。"""))
p1.append(heading("Three things to check", "三项核定", 286))
p1.append(body(70, 320, 506, 80,
"""Commemorative coins generally do not circulate, so worn specimens are rare and this guide has no
condition grade. Read the metal, the reverse design and the serial number.""",
"""纪念币一般不流通，基本不出现品相较差的情况，故本指南不设品相一项。

核定只看三处：币面材质、背面版别图案、防伪编号。"""))
p1.append(image(214, 396, 200, 96, "ill_coin_copper_normal"))
p1.append(caption(114, 500, 400, "Copper, ordinary issue.", "铜质 · 普通版"))
p1.append(line(100, 585, 528, 585))
p1.append(body(70, 599, 506, 60,
"""Any piece judged counterfeit is quoted at 40¢ without exception.""",
"""经检查判定为赝品的，一律按 40 报价。"""))
book["pages"].append({"name": "Intro", "elements": p1})

# ============ 二、材质 ============
p2 = page_head()
p2.append(heading("1. Metal", "1.材质"))
p2.append(body(70, 204, 506, 40,
"""Compare the warmth of the highlight and the tone of the shadow under daylight.""",
"""在自然光下比较高光的冷暖与暗部的色调。"""))
for i, (sprite, en, zh) in enumerate([
        ("ill_coin_copper_normal", "Copper (+0¢)", "铜 (+0¢)"),
        ("ill_coin_silver_normal", "Silver-plated (+30¢)", "镀银 (+30¢)"),
        ("ill_coin_gold_normal", "Gold-plated (+60¢)", "镀金 (+60¢)")]):
    x = 16 + i * 204 + (44, 22, 0)[i]
    p2.append(image(x, 252, 180, 88, sprite))
    p2.append(caption(x - 10, 348, 200, en, zh))
p2.append(body(70, 392, 506, 120,
"""Copper reads warm and red; its highlight is the dullest of the three.

Silver plating reads cool and white, with a bright narrow highlight.

Gold plating reads warm yellow, with a strong highlight that fades toward the rim.""",
"""铜偏红棕，三种里高光最暗。

镀银偏冷白，高光窄而亮。

镀金偏暖黄，高光强、向边缘逐渐减弱。"""))
p2.append(line(100, 578, 528, 578))
p2.append(body(70, 592, 506, 60,
"""The metal is also stamped into the serial number; see section 3.""",
"""材质同时会印在防伪编号的末位字母上，见第 3 节。"""))
book["pages"].append({"name": "Metal", "elements": p2})

# ============ 三、版别 ============
p3 = page_head()
p3.append(heading("2. Issue", "2.版别"))
p3.append(body(70, 204, 506, 40,
"""The reverse design tells the issue; the plainer the engraving, the commoner the coin.""",
"""背面图案决定版别：刻得越简，版别越普通。"""))
for i, (sprite, en, zh) in enumerate([
        ("ill_coin_gold_normal", "Ordinary (+0¢)", "普通 (+0¢)"),
        ("ill_coin_gold_rare", "Rare (+80¢)", "稀有 (+80¢)"),
        ("ill_coin_gold_collector", "Collector (+200¢)", "珍藏 (+200¢)")]):
    x = 16 + i * 204 + (44, 22, 0)[i]
    p3.append(image(x, 252, 180, 88, sprite))
    p3.append(caption(x - 10, 348, 200, en, zh))
p3.append(body(70, 388, 506, 140,
"""Ordinary issue, The Ninefold Orbit: nine station segments encircling a central planet, with a Roman IX
engraved on the top segment.

Rare issue, By Repulsion, Not Attraction: a tilted satellite orbit around an apple standing for gravity,
carrying a Roman IX on the orbit.

Collector issue, To the Stars at Last: three launch trails running from a planet at the lower right to a
cluster of stars at the upper left.""",
"""普通版【九段绕星】：九段空间站围绕中央星球，正上方一段刻有罗马数字 9。

稀有版【以离代引】：一段倾斜的卫星轨道环绕代表重力的苹果，轨道上有罗马数字 9。

珍藏版【终抵群星】：三条发射轨迹从右下角的星球出发，指向左上角的群星。"""))
p3.append(line(100, 578, 528, 578))
p3.append(body(70, 592, 506, 60,
"""An issue that does not match its serial number range is counterfeit.""",
"""版别与编号号段对不上的，按赝品处理。"""))
book["pages"].append({"name": "Issue", "elements": p3})

# ============ 四、编号 ============
p4 = page_head()
p4.append(heading("3. Serial number", "3.防伪编号"))
p4.append(body(70, 204, 506, 60,
"""A serial is five digits followed by the metal letter: G for gold, S for silver, C for copper.""",
"""防伪编号为五位数字加一位材质字母：G 为镀金、S 为镀银、C 为铜。"""))
p4.append(body(70, 262, 506, 96,
"""The number range fixes the issue:
ordinary 10000-99999, rare 01000-09999, collector 00001-00999.""",
"""号段对应版别：普通版 10000–99999，稀有版 01000–09999，珍藏版 00001–00999。"""))
p4.append(image(134, 356, 400, 182, "ill_coin_gold_collector_00077S"))
p4.append(caption(70, 546, 506, "Collector issue, serial 00077S — a triple number.",
                  "珍藏版 · 编号 00077S（豹子号）"))
p4.append(line(100, 566, 528, 566))
p4.append(body(70, 578, 506, 150,
"""Triple number: after dropping leading zeros, at least two digits remain and all of them are the same.
00077 counts; 00007 does not. Such a coin adds 100¢.

Test coin: the first nine numbers of any range - 10001-10009, 01001-01009, 00001-00009 - adds 600¢.""",
"""豹子号：去掉前导 0 后至少两位、且各位数字相同。00077 算，00007 不算。这类编号加 100¢。

测试币：各号段起始的九个号——10001–10009、01001–01009、00001–00009——加 600¢。"""))
book["pages"].append({"name": "Serial", "elements": p4})

# ============ 五、赝品 ============
p5 = page_head()
p5.append(heading("4. Counterfeits", "4.赝品"))
p5.append(body(70, 204, 506, 96,
"""Two mismatches mark a counterfeit. Either one is enough.

First: the serial range does not match the reverse design.""",
"""两种不符即为赝品，出现任何一条都成立。

其一：编号所在号段与背面版别图案不符。"""))
p5.append(body(70, 300, 506, 96,
"""Second: the letter at the end of the serial does not match the metal of the coin.""",
"""其二：编号末位字母与币面实际材质不符。"""))
p5.append(image(134, 396, 400, 182, "ill_coin_copper_normal_04321G"))
p5.append(caption(70, 586, 506, "Copper coin ending in G — the letter does not match the metal.",
                  "铜质币 · 编号 04321G，末位与材质不符"))
p5.append(line(100, 612, 528, 612))
p5.append(body(70, 626, 506, 80,
"""Any piece judged counterfeit is quoted at 40¢; no premium of any kind is added.""",
"""经检查判定为赝品的，一律按 40 报价，任何加成一律不计。"""))
book["pages"].append({"name": "Counterfeits", "elements": p5})

# ============ 六、示例 ============
p6 = page_head()
p6.append(heading("Examples", "示例"))
p6.append(body(70, 206, 250, 200,
"""Test coin
Base: +100
Gold-plated: +60
Collector: +200
Test coin: +600
Total: 960¢""",
"""测试币
基础：+100
镀金：+60
珍藏：+200
测试币：+600
总计：960¢"""))
p6.append(body(358, 206, 250, 200,
"""Counterfeit
Copper, ordinary issue
Serial 04321G
Quoted: 40¢""",
"""赝品
铜质 · 普通版
编号 04321G
报价：40¢"""))
p6.append(image(70, 416, 240, 110, "ill_coin_gold_collector_00005G"))
p6.append(caption(70, 534, 240, "Gold collector, serial 00005G.", "镀金珍藏 · 编号 00005G"))
p6.append(image(318, 416, 240, 110, "ill_coin_copper_normal_04321G"))
p6.append(caption(318, 534, 240, "Copper, serial 04321G.", "铜质 · 编号 04321G"))
p6.append(line(100, 578, 528, 578))
p6.append(body(70, 592, 506, 80,
"""A test coin is the highest figure a coin of this class can reach; a counterfeit is the lowest.""",
"""测试币是本类物件的价格上限，赝品是下限。"""))
book["pages"].append({"name": "Examples", "elements": p6})

book["item"] = {
    "id": "coin_guide",
    "name": TITLE_EN,
    "nameLoc": "coin_guide_name",
    "description": "How to price a Ninth Ring Port commemorative coin.",
    "descriptionLoc": "coin_guide_desc",
    "sprite": "items_misc/manual1",
    "value": 50,
    "important": True,
}

os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(book, fh, ensure_ascii=False, indent=2)
print("written", OUT, "pages", len(book["pages"]))
