"""打印 level1 里 _InspectionUI / MagnifiyingGlasse 的层级与 localScale。

对应问题：原版镜片里的复制品到底是不是 2 倍。
输出形如：
    [缩进] 名称  scale=(x,y,z)
"""
import os
import sys

import UnityPy

GAME = r"D:\SteamLibrary\steamapps\common\Probably Stolen\Probably Stolen_Data"
LEVEL = os.path.join(GAME, "level1")


def main():
    env = UnityPy.load(LEVEL)

    go_names = {}
    transforms = {}

    for obj in env.objects:
        if obj.type.name == "GameObject":
            try:
                d = obj.read()
            except Exception:
                continue
            go_names[obj.path_id] = getattr(d, "m_Name", "") or ""

    for obj in env.objects:
        if obj.type.name not in ("Transform", "RectTransform"):
            continue
        try:
            d = obj.read()
        except Exception:
            continue
        go = getattr(d, "m_GameObject", None)
        name = go_names.get(getattr(go, "path_id", None), "") if go else ""
        scale = getattr(d, "m_LocalScale", None)
        father = getattr(d, "m_Father", None)
        children = [getattr(c, "path_id", None) for c in (getattr(d, "m_Children", None) or [])]
        transforms[obj.path_id] = (name, scale, getattr(father, "path_id", 0), children, obj.type.name)

    roots = [pid for pid, (n, _s, f, _c, _t) in transforms.items() if n in ("_InspectionUI", "MagnifiyingGlasse")]

    def dump(pid, depth=0):
        if pid not in transforms:
            return
        name, scale, _f, children, kind = transforms[pid]
        s = f"({scale.x:g},{scale.y:g},{scale.z:g})" if scale else "-"
        print(f"{'  ' * depth}{name or '<无名>':30} scale={s}")
        if depth < 4:
            for c in children:
                dump(c, depth + 1)

    for pid in roots:
        print("=" * 60)
        dump(pid)


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    main()
