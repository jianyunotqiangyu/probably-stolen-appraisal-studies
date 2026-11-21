"""从 sharedassets1 里把原版纸张精灵导出成 PNG（只用于参考/对比，不进模组）。"""
import os
import UnityPy

DATA = r"D:\SteamLibrary\steamapps\common\Probably Stolen\Probably Stolen_Data"
SRC = os.path.join(DATA, "sharedassets1.assets")
OUT = r"D:\DSH_workspace\mod-create\reference\vanilla-paper"

TARGETS = {"notebook_manual", "guide_logo", "wine_tutorial", "water_purity_2x"}

os.makedirs(OUT, exist_ok=True)
env = UnityPy.load(SRC)
for obj in env.objects:
    if obj.type.name != "Sprite":
        continue
    try:
        d = obj.read()
    except Exception:
        continue
    name = str(getattr(d, "m_Name", ""))
    if name not in TARGETS:
        continue
    img = d.image
    path = os.path.join(OUT, name + ".png")
    img.save(path)
    print("exported", name, img.size, "->", path)
