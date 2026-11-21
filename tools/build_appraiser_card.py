"""生成 Books/appraiser_card.json —— 鉴定行会名片（单页，原版名片底板）。

版式：原版 `business_card_template` 是 200×125 的空白米色卡面。
设计空间就用 200×125，显示尺寸放大到 400×250（文本是矢量，放大不糊）。

卡片内容（给玩家看的全部信息）：
  抬头  空间站贸易委员会
  主标  鉴定行会
  持证人 ________________
  预约考官 1717
  底注  凭此卡预约鉴定考官 · 请勿转借
"""
import json
import os

OUT = r"D:\DSH_workspace\mod-create\mod\AppraisalExpansion\Books\appraiser_card.json"

BLUE = "#35526F"
INK = "#292234"
LIGHT = "#8b8375"

DESIGN_W, DESIGN_H = 200, 125
SHOW_W, SHOW_H = 400, 250
TITLE_EN = "Station Appraiser Guild Card"
TITLE_ZH = "鉴定行会名片"


def tr(zh):
    return {"zh-Hans": zh, "zh": zh}


def text_el(x, y, w, h, en, zh, style="title", size=8, align="left", wrap=True,
            color=INK, ident=None):
    el = {"type": "text", "x": x, "y": y, "w": w, "h": h, "text": en,
          "translations": tr(zh), "style": style, "fontSize": size,
          "align": align, "wrap": wrap, "color": color}
    if ident:
        el["id"] = ident
    return el


page = [
    # 抬头
    text_el(0, 10, DESIGN_W, 12, "STATION TRADE COMMISSION", "空间站贸易委员会",
            style="header", size=8, align="center", wrap=False, color=BLUE, ident="header"),
    # 主标题
    text_el(0, 26, DESIGN_W, 22, "APPRAISER GUILD", "鉴定行会",
            style="title", size=18, align="center", wrap=False, color=BLUE, ident="title"),
    # 分隔线
    {"type": "line", "x": 24, "y": 56, "x2": 176, "y2": 56, "thickness": 1.0, "color": BLUE},
    # 预约号：卡面唯一的信息
    text_el(0, 66, DESIGN_W, 12, "Appointments", "预约", style="label", size=8,
            align="center", wrap=False, color=INK),
    text_el(0, 78, DESIGN_W, 24, "1717", "1717", style="title", size=20,
            align="center", wrap=False, color=BLUE, ident="phone"),
    # 底注
    text_el(0, 110, DESIGN_W, 10, "Show this card to book an appraiser.",
            "凭此卡预约鉴定考官 · 请勿转借",
            style="caption", size=8, align="center", wrap=False, color=INK),
]

book = {
    "id": "appraiser_card",
    "title": TITLE_EN,
    "background": "business_card_template",
    "width": SHOW_W,
    "height": SHOW_H,
    "designWidth": DESIGN_W,
    "designHeight": DESIGN_H,
    "posX": 0,
    "posY": 0,
    "draggable": True,
    "zoomable": False,
    "chrome": [
        {"type": "button", "id": "close", "action": "close", "sprite": "btn_close",
         "x": 172, "y": 6, "w": 22, "h": 24},
    ],
    "pages": [{"name": "Card", "elements": page}],
    "item": {
        "id": "appraiser_card",
        "name": TITLE_EN,
        "nameLoc": "card_name",
        "description": "Issued by the appraiser guild on joining.",
        "descriptionLoc": "card_desc",
        "sprite": "appraiser_card",
        "value": 0,
        "important": True,
    },
}

os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(book, fh, ensure_ascii=False, indent=2)
print("written", OUT)


