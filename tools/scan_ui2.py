"""第二版：把鉴定面板里“放大镜”那块子树连同 scale / sprite / 组件 一起 dump 出来。

重点回答三个问题：
1. MagnifiyingGlasse 的 Mask 下面复制了什么？
2. 内外两份内容的 localScale 差多少（即放大倍数）？
3. 内层复制品的锚点/位置和外层是什么关系？
"""
import os
import UnityPy

DATA = r"D:\SteamLibrary\steamapps\common\Probably Stolen\Probably Stolen_Data"
LEVEL = os.path.join(DATA, "level1")

WANT_ROOTS = ("MagnifiyingGlasse", "_AppHand", "_InspectionUI")


def s(o, a, d=None):
    try:
        return getattr(o, a)
    except Exception:
        return d


def vec(v):
    try:
        return f"({v.x:.1f},{v.y:.1f},{v.z:.1f})"
    except Exception:
        return "(?)"


def main():
    env = UnityPy.load(LEVEL)

    gos, trs, comps = {}, {}, {}
    for obj in env.objects:
        t = obj.type.name
        if t == "GameObject":
            gos[obj.path_id] = obj.read()
        elif t in ("Transform", "RectTransform"):
            trs[obj.path_id] = obj.read()
        else:
            comps[obj.path_id] = t

    tr_by_go = {}
    for pid, t in trs.items():
        go = s(t, "m_GameObject")
        if go:
            tr_by_go[go.path_id] = pid

    # 组件类型名（MonoBehaviour 用脚本类名）
    def comp_names(go):
        out = []
        for c in s(go, "m_Component", []) or []:
            p = s(c, "component")
            if not p:
                continue
            out.append(comps.get(p.path_id, "?"))
        return out

    def sprite_of(go):
        # 找到 Image / SpriteRenderer 组件，读它的 sprite 名
        for c in s(go, "m_Component", []) or []:
            p = s(c, "component")
            if not p:
                continue
            if p.path_id not in comps:
                continue
            try:
                comp = p.read()
            except Exception:
                continue
            sp = s(comp, "m_Sprite")
            if sp:
                try:
                    return str(s(sp.read(), "m_Name", ""))
                except Exception:
                    return "?"
        return ""

    name_of = {}
    for pid, g in gos.items():
        name_of[pid] = str(s(g, "m_Name", "?"))

    def walk(tr_id, depth):
        t = trs.get(tr_id)
        if t is None:
            return
        go_p = s(t, "m_GameObject")
        go = gos.get(go_p.path_id) if go_p else None
        name = name_of.get(go_p.path_id, "?") if go_p else "?"
        sc = s(t, "m_LocalScale")
        sd = s(t, "m_SizeDelta")
        ap = s(t, "m_AnchoredPosition")
        line = "  " * depth + f"- {name}"
        if sc is not None:
            line += f" scale={vec(sc)}"
        if sd is not None:
            line += f" size=({sd.x:.0f},{sd.y:.0f})"
        if ap is not None:
            line += f" pos=({ap.x:.0f},{ap.y:.0f})"
        cn = comp_names(go) if go is not None else []
        line += f" [{', '.join(cn)}]"
        sp = sprite_of(go) if go is not None else ""
        if sp:
            line += f" sprite={sp}"
        print(line)
        if depth > 6:
            return
        for ch in s(t, "m_Children", []) or []:
            walk(ch.path_id, depth + 1)

    # 找目标根
    for pid, g in gos.items():
        if name_of.get(pid) not in WANT_ROOTS:
            continue
        tr = tr_by_go.get(pid)
        if tr is None:
            continue
        # 只要 _InspectionUI 下那一份
        father = s(trs[tr], "m_Father")
        parent_name = name_of.get(s(trs[s(father, "path_id", -1)], "m_GameObject").path_id, "") if False else ""
        print("\n" + "#" * 80)
        print(f"### {name_of.get(pid)}")
        walk(tr, 0)


if __name__ == "__main__":
    main()
