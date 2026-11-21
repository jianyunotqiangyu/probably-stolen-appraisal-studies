"""把纪念币底图复制成手册插图（Paper 用）。

手册里的字太小看不清，所以插图只放「币面本身」，编号写在图注里。
"""
import os
import shutil

ROOT = r"D:\DSH_workspace\mod-create"
BASE = os.path.join(ROOT, "assets", "items", "oddity_coin", "magnifier_base")
PAPER = os.path.join(ROOT, "assets", "paper")

PAIRS = {
    "coin_copper_normal.png": "ill_coin_copper_normal.png",
    "coin_silver_normal.png": "ill_coin_silver_normal.png",
    "coin_gold_normal.png": "ill_coin_gold_normal.png",
    "coin_gold_rare.png": "ill_coin_gold_rare.png",
    "coin_gold_collector.png": "ill_coin_gold_collector.png",
}


def main():
    os.makedirs(PAPER, exist_ok=True)
    for src, dst in PAIRS.items():
        shutil.copy2(os.path.join(BASE, src), os.path.join(PAPER, dst))
        print(dst)


if __name__ == "__main__":
    main()
