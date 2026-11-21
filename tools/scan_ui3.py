"""第三版：把放大镜 Mask 子树的组件类型（含脚本类名）和 CounterMoveChild 的参数读出来。"""
import os
import UnityPy

DATA = r"D:\SteamLibrary\steamapps\common\Probably Stolen\Probably Stolen_Data"
LEVEL = os.path.join(DATA, "level1")


def s(o, a, d=None):
    try:
        return getattr(o, a)
    except Exception:
        return d


def main():
    env = UnityPy.load(LEVEL)

    gos, trs, objs = {}, {}, {}
    for obj in env.objects:
        objs[obj.path_id] = obj
        t = obj.type.name
        if t == "GameObject":
            gos[obj.path_id] = obj.read()
        elif t in ("Transform", "RectTransform"):
            trs[obj.path_id] = obj.read()

    tr_by_go = {}
    name_of = {}
    for pid, t in trs.items():
        go = s(t, "m_GameObject")
        if go:
            tr_by_go[go.path_id] = pid
    for pid, g in gos.items():
        name_of[pid] = str(s(g, "m_Name", "?"))

    def script_info(comp_ptr):
        """返回 (类型名, 脚本类名, 字段dict)"""
        try:
            comp = comp_ptr.read()
        except Exception:
            return ("?", "", {})
        tn = type(comp).__name__
        cls = ""
        fields = {}
        # MonoBehaviour：拿脚本类名 + typetree 字段
        if "MonoBehaviour" in tn or tn == "MonoBehaviour":
            try:
                st = comp_ptr.read_typetree()
                if isinstance(st, dict):
                    fields = st
            except Exception:
                pass
            try:
                ms = comp.m_Script.read()
                cls = str(s(ms, "m_ClassName", "") or "")
            except Exception:
                pass
        return (tn, cls, fields)

    def dump(tr_id, depth=0, maxdepth=3):
        t = trs.get(tr_id)
        if t is None:
            return
        go_p = s(t, "m_GameObject")
        name = name_of.get(go_p.path_id, "?") if go_p else "?"
        print("  " * depth + f"- {name}")
        if go_p:
            for c in s(gos.get(go_p.path_id), "m_Component", []) or []:
                p = s(c, "component")
                if not p:
                    continue
                tn, cls, fields = script_info(p)
                extra = ""
                if cls:
                    extra += f" class={cls}"
                for k in ("movementMultiplier", "m_Maskable", "m_ShowMaskGraphic", "m_Script"):
                    if k in fields:
                        extra += f" {k}={fields[k]}"
                print("  " * (depth + 1) + f"* {tn}{extra}")
        if depth >= maxdepth:
            return
        for ch in s(t, "m_Children", []) or []:
            dump(ch.path_id, depth + 1, maxdepth)

    # 定位 MagnifiyingGlasse，打印到 3 层
    for pid, g in gos.items():
        if name_of.get(pid) != "MagnifiyingGlasse":
            continue
        tr = tr_by_go.get(pid)
        if tr is None:
            continue
        # 只要 _InspectionUI 下那份（父名 = _InspectionUI）
        father = s(trs[tr], "m_Father")
        fname = ""
        if father and father.path_id in trs:
            fgo = s(trs[father.path_id], "m_GameObject")
            fname = name_of.get(fgo.path_id, "") if fgo else ""
        if fname != "_InspectionUI":
            continue
        print(f"### {fname}/{name_of[pid]}")
        dump(tr, 0, 3)


if __name__ == "__main__":
    main()
