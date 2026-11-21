"""生成纪念币编号用的点阵字模（0-9 与 G / S / C）。

5×7 的点阵，放大 4 倍 = 每个字符 20×28 像素，硬边不抗锯齿，
与像素美术同源；颜色统一用暗刻色，落在币面刻字线上。

输出：assets/items/oddity_coin/glyphs/coin_ch_<字符>.png
"""
import os

from PIL import Image

ROOT = r"D:\DSH_workspace\mod-create"
OUT = os.path.join(ROOT, "assets", "items", "oddity_coin", "glyphs")

SCALE = 4
INK = (58, 63, 74, 255)  # #3A3F4A

FONT = {
    "0": ["01110", "10001", "10011", "10101", "11001", "10001", "01110"],
    "1": ["00100", "01100", "00100", "00100", "00100", "00100", "01110"],
    "2": ["01110", "10001", "00001", "00010", "00100", "01000", "11111"],
    "3": ["11111", "00010", "00100", "00010", "00001", "10001", "01110"],
    "4": ["00010", "00110", "01010", "10010", "11111", "00010", "00010"],
    "5": ["11111", "10000", "11110", "00001", "00001", "10001", "01110"],
    "6": ["00110", "01000", "10000", "11110", "10001", "10001", "01110"],
    "7": ["11111", "00001", "00010", "00100", "01000", "01000", "01000"],
    "8": ["01110", "10001", "10001", "01110", "10001", "10001", "01110"],
    "9": ["01110", "10001", "10001", "01111", "00001", "00010", "01100"],
    "G": ["01110", "10001", "10000", "10111", "10001", "10001", "01111"],
    "S": ["01111", "10000", "10000", "01110", "00001", "00001", "11110"],
    "C": ["01110", "10001", "10000", "10000", "10000", "10001", "01110"],
}


def build(ch):
    rows = FONT[ch]
    w = max(len(r) for r in rows) * SCALE
    h = len(rows) * SCALE
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    px = img.load()
    for y, row in enumerate(rows):
        for x, bit in enumerate(row):
            if bit != "1":
                continue
            for dy in range(SCALE):
                for dx in range(SCALE):
                    px[x * SCALE + dx, y * SCALE + dy] = INK
    return img


def main():
    os.makedirs(OUT, exist_ok=True)
    for ch in FONT:
        img = build(ch)
        path = os.path.join(OUT, f"coin_ch_{ch}.png")
        img.save(path)
        print(f"{path}  {img.size}")
    print(f"共 {len(FONT)} 个字符")


if __name__ == "__main__":
    main()
