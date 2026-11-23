"""指节定价整体上调，并同步代码、手册生成脚本。

新数值（2026-11-24 决定：只抬指节，不压其它三件）：
    基准 85 -> 120        下限 35 -> 50
    钢 +30 -> +45         镀金 +70 -> +100
    磨损 -25 -> -30       受损 -50 -> -60
    规格不明 -15 -> -20   EMG+ +15 -> +25
    => 上限 245¢，下限 50¢

用「精确文本替换」而不是按数字模糊替换——脚本里 y 坐标含 535 之类数字，模糊替换会改坏布局。
"""
import io
import os
import sys

ROOT = r"D:\DSH_workspace\mod-create"
CODE = os.path.join(ROOT, "mod", "AppraisalExpansion", "src", "KnuckleItem.cs")
BUILDER = os.path.join(ROOT, "tools", "build_knuckle_guide.py")

CODE_PAIRS = [
    ("BaseValue                = 85", "BaseValue                = 120"),
    ("MinValue                 = 35", "MinValue                 = 50"),
    ("SteelBonus               = 30", "SteelBonus               = 45"),
    ("GoldBonus                = 70", "GoldBonus                = 100"),
    ("WearPenalty              = -25", "WearPenalty              = -30"),
    ("DamagePenalty            = -50", "DamagePenalty            = -60"),
    ("NoInterfacePenalty       = -15", "NoInterfacePenalty       = -20"),
    ("EmgPlusBonus             = 15", "EmgPlusBonus             = 25"),
    ("        int num = 85;", "        int num = BaseValue;"),
    ("        return Math.Max(35, num);", "        return Math.Max(MinValue, num);"),
]

BUILDER_PAIRS = [
    # 第 1 页 总则
    ("Every knuckle starts at 85¢", "Every knuckle starts at 120¢"),
    ("never worth less than 35¢", "never worth less than 50¢"),
    ("初始价值均为 85¢", "初始价值均为 120¢"),
    ("最低价值为 35¢", "最低价值为 50¢"),
    # 第 2 页 材质
    ('f"Steel (+30{CUR})"', 'f"Steel (+45{CUR})"'),
    ('f"Gold-plated (+70{CUR})"', 'f"Gold-plated (+100{CUR})"'),
    ('f"钢 (+30{CUR})"', 'f"钢 (+45{CUR})"'),
    ('f"镀金 (+70{CUR})"', 'f"镀金 (+100{CUR})"'),
    # 第 3 页 品相
    ('f"Worn (-25{CUR})"', 'f"Worn (-30{CUR})"'),
    ('f"Damaged (-50{CUR})"', 'f"Damaged (-60{CUR})"'),
    ('f"磨损 (-25{CUR})"', 'f"磨损 (-30{CUR})"'),
    ('f"受损 (-50{CUR})"', 'f"受损 (-60{CUR})"'),
    # 第 4 页 接口
    ('f"Unknown (-15{CUR})"', 'f"Unknown (-20{CUR})"'),
    ('f"EMG+ (+15{CUR})"', 'f"EMG+ (+25{CUR})"'),
    ('f"规格不明 (-15{CUR})"', 'f"规格不明 (-20{CUR})"'),
    ('f"EMG+ (+15{CUR})"', 'f"EMG+ (+25{CUR})"'),
    # 第 5 页 计价表
    ('("Steel", "钢", "+30")', '("Steel", "钢", "+45")'),
    ('("Gold-plated", "镀金", "+70")', '("Gold-plated", "镀金", "+100")'),
    ('("Worn", "磨损", "-25")', '("Worn", "磨损", "-30")'),
    ('("Damaged", "受损", "-50")', '("Damaged", "受损", "-60")'),
    ('("Unknown", "规格不明", "-15")', '("Unknown", "规格不明", "-20")'),
    ('("EMG+", "EMG+", "+15")', '("EMG+", "EMG+", "+25")'),
    ("value = max({CUR}35, {CUR}85 + material + condition + interface)",
     "value = max({CUR}50, {CUR}120 + material + condition + interface)"),
    ("价值 = max({CUR}35, {CUR}85 + 材质 + 品相 + 接口)",
     "价值 = max({CUR}50, {CUR}120 + 材质 + 品相 + 接口)"),
    ("Limits: gold-plated + EMG+ + sound = 170¢; unknown + damaged = 35¢.",
     "Limits: gold-plated + EMG+ + sound = 245¢; unknown + damaged = 50¢."),
    ("上下限：镀金 + EMG+ + 无 = 170¢；规格不明 + 受损 = 35¢。",
     "上下限：镀金 + EMG+ + 无 = 245¢；规格不明 + 受损 = 50¢。"),
    # 第 6 页 示例一
    ('"Base: +85', '"Base: +120'),
    ('"Gold-plated: +70', '"Gold-plated: +100'),
    ('"EMG+: +15', '"EMG+: +25'),
    ("Total: 170¢", "Total: 245¢"),
    ("基础：+85", "基础：+120"),
    ("镀金：+70", "镀金：+100"),
    ("EMG+：+15", "EMG+：+25"),
    ("总计：170¢", "总计：245¢"),
    # 第 7 页 示例二（120 + 0 - 30 - 20 = 70）
    ('"Worn: -25', '"Worn: -30'),
    ('"Unknown: -15', '"Unknown: -20'),
    ("Subtotal: +45", "Subtotal: +70"),
    ("Total: 45¢", "Total: 70¢"),
    ("磨损：-25", "磨损：-30"),
    ("规格不明：-15", "规格不明：-20"),
    ("小计：+45", "小计：+70"),
    ("总计：45¢", "总计：70¢"),
]


def apply_pairs(path, pairs, label):
    text = io.open(path, encoding="utf-8").read()
    missed = []
    for old, new in pairs:
        if old in text:
            text = text.replace(old, new)
        else:
            missed.append(old)
    io.open(path, "w", encoding="utf-8", newline="\n").write(text)
    print(f"{label}: 命中 {len(pairs) - len(missed)}/{len(pairs)}")
    for m in missed:
        print("  未命中:", m[:70])


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    apply_pairs(CODE, CODE_PAIRS, "KnuckleItem.cs")
    apply_pairs(BUILDER, BUILDER_PAIRS, "build_knuckle_guide.py")


if __name__ == "__main__":
    main()
