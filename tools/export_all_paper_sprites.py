"""把游戏里与纸质手册（PaperUI / 指南）相关的精灵全部导出成 PNG。

输出：reference/vanilla-paper/<名字>.png
清单：reference/vanilla-paper/_manifest.txt
"""
import os
import UnityPy

DATA = r"D:\SteamLibrary\steamapps\common\Probably Stolen\Probably Stolen_Data"
OUT = r"D:\DSH_workspace\mod-create\reference\vanilla-paper"

# 纸质手册用到的名字：PaperAssets 常量里出现的 + 背景/按钮/纹章
KEYS = {
    # 背景
    "notebook_manual", "guide_reworked", "guide", "tutorial_sheet",
    "business_card_template", "exchange", "test_strips", "mentors_notes",
    "wine_tutorial", "water_purity_2x",
    # 外框按钮
    "paper_buttons_close1", "paper_buttons_close2",
    "paper_buttons_screen_0", "paper_buttons_screen_1",
    "paper_buttons_l_1", "paper_buttons_l_2",
    "paper_buttons1", "paper_buttons2",
    "blue_button_2x",
    # 抬头
    "guide_logo",
}


def main():
    os.makedirs(OUT, exist_ok=True)
    lines = []
    found = {}
    for fn in ("sharedassets1.assets", "sharedassets0.assets", "resources.assets"):
        p = os.path.join(DATA, fn)
        if not os.path.exists(p):
            continue
        env = UnityPy.load(p)
        for obj in env.objects:
            if obj.type.name != "Sprite":
                continue
            try:
                d = obj.read()
            except Exception:
                continue
            name = str(getattr(d, "m_Name", ""))
            if name not in KEYS or name in found:
                continue
            try:
                img = d.image
            except Exception as e:
                lines.append(f"{name}\tERROR\t{e}")
                continue
            path = os.path.join(OUT, name + ".png")
            img.save(path)
            found[name] = (img.size, fn)
            lines.append(f"{name}\t{img.size[0]}x{img.size[1]}\t{fn}")

    # 顺便把所有以 paper_ 开头、page_ 开头的精灵也列出来，便于确认有没有漏
    extra = []
    for fn in ("sharedassets1.assets",):
        p = os.path.join(DATA, fn)
        env = UnityPy.load(p)
        for obj in env.objects:
            if obj.type.name != "Sprite":
                continue
            try:
                d = obj.read()
            except Exception:
                continue
            name = str(getattr(d, "m_Name", ""))
            if (name.startswith("paper_") or name.startswith("page_") or "button" in name.lower()) and name not in found:
                extra.append(name)

    with open(os.path.join(OUT, "_manifest.txt"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write("name\tw x h\tsource\n")
        fh.write("\n".join(lines))
        if extra:
            fh.write("\n\n# 其它含 paper_/page_/button 的精灵（未导出，供参考）\n")
            fh.write("\n".join(sorted(set(extra))))

    print("exported", len(found))
    for line in lines:
        print(line)
    print("\n其它候选（未导出）:", sorted(set(extra))[:40])


if __name__ == "__main__":
    main()
