"""dump 原版 MultiPageUIManager 的 books 列表，并把第 6 本（仿生械手鉴定指南）的页面结构打印出来。"""
import UnityPy

LEVEL = r"D:\SteamLibrary\steamapps\common\Probably Stolen\Probably Stolen_Data\level1"


def s(o, a, d=None):
    try:
        return getattr(o, a)
    except Exception:
        return d


env = UnityPy.load(LEVEL)
gos, trs, objs = {}, {}, {}
for obj in env.objects:
    objs[obj.path_id] = obj
    t = obj.type.name
    if t == "GameObject":
        gos[obj.path_id] = obj.read()
    elif t in ("Transform", "RectTransform"):
        trs[obj.path_id] = obj.read()

name_of = {p: str(s(g, "m_Name", "?")) for p, g in gos.items()}
tr_by_go = {}
for p, t in trs.items():
    go = s(t, "m_GameObject")
    if go:
        tr_by_go[go.path_id] = p


def tree_path(tr_id):
    names = []
    cur = tr_id
    while cur is not None:
        t = trs[cur]
        go = s(t, "m_GameObject")
        names.append(name_of.get(go.path_id, "?") if go else "?")
        f = s(t, "m_Father")
        cur = f.path_id if f and f.path_id else None
    return "/".join(reversed(names))


# 找 MultiPageUIManager 的 MonoBehaviour：typetree 里有 books 字段
target = None
for obj in env.objects:
    if obj.type.name != "MonoBehaviour":
        continue
    try:
        tt = obj.read_typetree()
    except Exception:
        continue
    if isinstance(tt, dict) and "books" in tt:
        target = (obj, tt)
        break

if not target:
    print("not found")
    raise SystemExit

obj, tt = target
go = s(obj.read(), "m_GameObject")
print("MultiPageUIManager on:", name_of.get(go.path_id, "?"))
books = tt["books"]
print("books:", len(books))
for i, b in enumerate(books):
    pid = b.get("m_PathID")
    t = trs.get(pid)
    if t is None:
        print(i, "missing", pid)
        continue
    g = s(t, "m_GameObject")
    print(f"[{i}] {name_of.get(g.path_id, '?')} children={len(s(t,'m_Children') or [])}")

# dump book 6
STYLES = {}
TMP_FIELDS = ("m_text", "m_text_", "m_Text")


def comp_info(go):
    out = []
    for c in s(go, "m_Component", []) or []:
        p = s(c, "component")
        if not p:
            continue
        try:
            ct = p.read_typetree()
        except Exception:
            out.append(("?", {}))
            continue
        out.append((p.type.name, ct))
    return out


def dump(tr_id, depth=0):
    t = trs.get(tr_id)
    if t is None or depth > 5:
        return
    go_p = s(t, "m_GameObject")
    name = name_of.get(go_p.path_id, "?") if go_p else "?"
    sd = s(t, "m_SizeDelta")
    ap = s(t, "m_AnchoredPosition")
    sc = s(t, "m_LocalScale")
    info = f"{'  ' * depth}- {name}"
    if sd is not None:
        info += f" size=({sd.x:.0f},{sd.y:.0f})"
    if ap is not None:
        info += f" pos=({ap.x:.1f},{ap.y:.1f})"
    if sc is not None and (abs(sc.x - 1) > 1e-3):
        info += f" scale=({sc.x:.2f})"
    print(info)
    if go_p:
        for tn, ct in comp_info(gos.get(go_p.path_id)):
            extra = ""
            if tn == "MonoBehaviour":
                sp = ct.get("m_Sprite")
                if sp:
                    try:
                        extra += " sprite=" + str(s(sp.read(), "m_Name", ""))
                    except Exception:
                        pass
                txt = ct.get("m_text") or ct.get("m_text_")
                if txt:
                    extra += " text=" + repr(txt)[:80]
            print("  " * (depth + 1) + f"* {tn}{extra}")
    for ch in s(t, "m_Children", []) or []:
        dump(ch.path_id, depth + 1)


bidx = 6
b = books[bidx]
t = trs[b["m_PathID"]]
g = s(t, "m_GameObject")
print("\n=== BOOK", bidx, name_of.get(g.path_id, "?"), "===")
dump(t.path_id, 0)
