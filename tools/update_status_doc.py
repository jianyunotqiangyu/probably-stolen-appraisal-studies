"""把 docs/00 的当前状态刷到 0.6.0 前瞻版。"""
import io
import os

PATH = os.path.join(r"D:\DSH_workspace\mod-create", "docs", "00-项目状态与工作日志.md")

REPLACEMENTS = [
    ("> 每次阶段性工作结束请更新 §1 与 §7。最近更新：**2026-11-17**（名片 + 电话预约考官 + 考核结算接通）。",
     "> 每次阶段性工作结束请更新 §1 与 §7。最近更新：**2026-11-20**（0.6.0 前瞻版：四件鉴定品 + 四本手册 + 考卷改为全池抽取 + 预约改为按天调度）。"),
    ("| 考证玩法（电话/考官上门） | 🟡 名片 + 电话预约 + 考官上门已打通；出题判定发证未做 |",
     "| 考证玩法（电话/考官上门） | 🟢 预约按天调度（`appraiser_visit_day`）→ 次日顾客生成时入队 → 叫号开考 → 三件过两件 → 缴费发证；考官被赶走或当天未接待即作废，不顺延 |"),
    ("| 版本 | 🟢 `0.5.2`（改名 + 署名 + 描述重写） |",
     "| 版本 | 🟢 `0.6.0`（前瞻版，manifest 内含中英「前瞻」说明） |"),
    ("；手册 3 本（纪念币手册待做） |", "；手册 4 本 |"),
    ("| 鉴定品数量 | 🟢 4 件：指节 27 / 检测仪 108 / 腕式终端 24 / **开港纪念币**（材质 3 × 版别 3，编号与赝品另判）",
     "| 鉴定品数量 | 🟢 4 件：指节 27 / 检测仪 108 / 腕式终端 24 / **开港纪念币**（材质 3 × 版别 3，编号与赝品另判）；10 张图标均为手绘 |"),
    ("| 能否部署进游戏 | ✅ 已部署 `0.4.0`：1 dll + manifest + `Books/knuckle_guide.json` + `Textures/Items` 14 张 + `Textures/Paper` 16 张 |",
     "| 能否部署进游戏 | ✅ 已部署 `0.6.0`：1 dll + manifest + `Books/` 5 个 + `Localization/` 3 个 + `Textures/Items` 91 张 + `Textures/Paper` 35 张 |"),
]


def main():
    text = io.open(PATH, encoding="utf-8").read()
    changed = 0
    for old, new in REPLACEMENTS:
        if old in text:
            text = text.replace(old, new)
            changed += 1
        else:
            print("未命中:", old[:40])
    io.open(PATH, "w", encoding="utf-8", newline="\n").write(text)
    print("替换", changed, "处")


if __name__ == "__main__":
    main()
