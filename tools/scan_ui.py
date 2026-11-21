"""扫描游戏资源包，定位鉴定面板（InspectionUIManager）预制体的层级结构。

用途：搞清楚原版“放大镜”到底怎么把大图显示出来的。
输出：找到的 GameObject 子树（名字 / 层级 / RectTransform 尺寸 / 组件类型）。

用法：
  python tools/scan_ui.py            # 打印概要
  python tools/scan_ui.py --full     # 打印完整子树
"""
import os
import sys

import UnityPy

DATA = r"D:\SteamLibrary\steamapps\common\Probably Stolen\Probably Stolen_Data"
TARGETS = [
    os.path.join(DATA, "sharedassets0.assets"),
    os.path.join(DATA, "sharedassets1.assets"),
    os.path.join(DATA, "resources.assets"),
    os.path.join(DATA, "level1"),
]

KEY_COMPONENTS = {"MagnifyingGlassMono", "CounterMoveChild", "InspectionUIManager", "AppHandUI"}
KEY_NAME_HINTS = ("magnif", "inspection", "hand_ui", "appraisal")


def safe(obj, attr, default=None):
    try:
        return getattr(obj, attr)
    except Exception:
        return default


def script_class_name(mb):
    try:
        script = mb.m_Script
        ms = script.read()
        for attr in ("m_ClassName", "m_Name"):
            v = safe(ms, attr)
            if v:
                return str(v)
    except Exception:
        pass
    return ""


def main():
    full = "--full" in sys.argv
    found = []

    for path in TARGETS:
        if not os.path.exists(path):
            continue
        print(f"[scan] {os.path.basename(path)}")
        env = UnityPy.load(path)

        # 先收集所有 MonoBehaviour，标记命中的 GameObject
        hits = {}
        for obj in env.objects:
            if obj.type.name != "MonoBehaviour":
                continue
            try:
                mb = obj.read()
            except Exception:
                continue
            cls = script_class_name(mb)
            if cls not in KEY_COMPONENTS:
                continue
            go_ptr = safe(mb, "m_GameObject")
            if not go_ptr:
                continue
            try:
                go = go_ptr.read()
            except Exception:
                continue
            name = str(safe(go, "m_Name", "?"))
            hits[obj.path_id] = (cls, name, go_ptr.path_id)
            print(f"  [{cls}] GameObject={name!r} file={os.path.basename(path)}")

        if not hits:
            continue

        # 收集该文件里所有 GameObject / Transform 的父子和组件关系
        gos, trs = {}, {}
        for obj in env.objects:
            if obj.type.name == "GameObject":
                try:
                    d = obj.read()
                except Exception:
                    continue
                gos[obj.path_id] = d
            elif obj.type.name in ("Transform", "RectTransform"):
                try:
                    d = obj.read()
                except Exception:
                    continue
                trs[obj.path_id] = d

        print(f"  GameObjects={len(gos)} Transforms={len(trs)}")

        if full:
            dump_roots(env, gos, trs, hits)

    if not full:
        print("\n跑 `--full` 看完整层级")


def dump_roots(env, gos, trs, hits):
    """从命中的 GameObject 往上找到根，然后打印整棵树。"""
    by_go = {}
    for pid, t in trs.items():
        go_ptr = safe(t, "m_GameObject")
        if go_ptr:
            by_go[go_ptr.path_id] = pid

    seen_roots = set()
    for cls, name, go_id in hits.values():
        tr_id = by_go.get(go_id)
        if tr_id is None:
            continue
        root = tr_id
        guard = 0
        while guard < 64:
            guard += 1
            t = trs[root]
            father = safe(t, "m_Father")
            if not father or not father.path_id:
                break
            root = father.path_id
        if root in seen_roots:
            continue
        seen_roots.add(root)
        print("\n" + "=" * 70)
        print(f"ROOT path_id={root}")
        walk(trs, gos, root, 0)


def walk(trs, gos, tr_id, depth):
    t = trs.get(tr_id)
    if t is None:
        return
    go_ptr = safe(t, "m_GameObject")
    go = gos.get(go_ptr.path_id) if go_ptr else None
    name = str(safe(go, "m_Name", "?")) if go is not None else "?"
    comps = []
    if go is not None:
        for c in safe(go, "m_Component", []) or []:
            p = safe(c, "component")
            ptr_id = p.path_id if p else None
            if ptr_id and ptr_id in TRS_BY_ID:
                pass
        comps = component_names(go)
    rect = ""
    if safe(t, "m_SizeDelta") is not None:
        sd = t.m_SizeDelta
        rect = f" size=({sd.x:.0f},{sd.y:.0f})"
        ap = safe(t, "m_AnchoredPosition")
        if ap is not None:
            rect += f" pos=({ap.x:.0f},{ap.y:.0f})"
    print("  " * depth + f"- {name}{rect} [{', '.join(comps)}]")
    for child in safe(t, "m_Children", []) or []:
        walk(trs, gos, child.path_id, depth + 1)


TRS_BY_ID = {}


def component_names(go):
    """从 GameObject 的 m_Component 里拿组件类型名（best effort）。"""
    names = []
    for c in safe(go, "m_Component", []) or []:
        p = safe(c, "component")
        if not p:
            continue
        try:
            comp = p.read()
        except Exception:
            continue
        names.append(type(comp).__name__)
    return names


if __name__ == "__main__":
    main()
