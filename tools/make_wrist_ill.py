"""把腕式终端的底图与叠层合成手册用的插图画（放 assets/paper/）。

生成：
  ill_wrist_relay  = wrist_iron_new      + wrist_service_relay
  ill_wrist_crypt  = wrist_iron_new      + wrist_service_crypt
  ill_wrist_set    = wrist_gold_new      + relay + crypt
  ill_wrist_floor  = wrist_iron_damaged  + relay

用法：python tools/make_wrist_ill.py
缺图时会明确报出缺哪张，不会生成半成品。
"""
import os
import sys

from PIL import Image

ROOT = r"D:\DSH_workspace\mod-create"
ITEMS = os.path.join(ROOT, "assets", "items", "oddity_tech_wrist")
PAPER = os.path.join(ROOT, "assets", "paper")

JOBS = [
    ("ill_wrist_relay", ["magnifier_base/wrist_iron_new.png", "magnifier_overlay/wrist_service_relay.png"]),
    ("ill_wrist_crypt", ["magnifier_base/wrist_iron_new.png", "magnifier_overlay/wrist_service_crypt.png"]),
    ("ill_wrist_both", ["magnifier_base/wrist_iron_new.png", "magnifier_overlay/wrist_service_both.png"]),
    ("ill_wrist_set", ["magnifier_base/wrist_gold_new.png", "magnifier_overlay/wrist_service_both.png"]),
    ("ill_wrist_floor", ["magnifier_base/wrist_iron_damaged.png",
                         "magnifier_overlay/wrist_service_relay.png"]),
]


def main():
    missing = []
    for name, parts in JOBS:
        for rel in parts:
            if not os.path.exists(os.path.join(ITEMS, rel)):
                missing.append(os.path.join(ITEMS, rel))
    if missing:
        print("缺少素材，先补齐再跑：")
        for m in sorted(set(missing)):
            print("  " + m)
        return 1

    os.makedirs(PAPER, exist_ok=True)
    for name, parts in JOBS:
        img = Image.open(os.path.join(ITEMS, parts[0])).convert("RGBA")
        for rel in parts[1:]:
            overlay = Image.open(os.path.join(ITEMS, rel)).convert("RGBA")
            img = Image.alpha_composite(img, overlay)
        out = os.path.join(PAPER, name + ".png")
        img.save(out)
        print(f"{out}  {img.size}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
