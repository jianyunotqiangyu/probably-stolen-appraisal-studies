"""对比外层/内层 _App1Hand 的组件构成，确认镜片复制品上挂了什么。"""
import os
import UnityPy

DATA = r"D:\SteamLibrary\steamapps\common\Probably Stolen\Probably Stolen_Data"
LEVEL = os.path.join(DATA, "level1")


def s(o, a, d=None):
    try:
        return getattr(o, a)
    except Exception:
        return d


env = UnityPy.load(LEVEL)
gos, trs = {}, {}
for obj in env.objects:
    if obj.type.name == "GameObject":
        gos[obj.path_id] = obj.read()
    elif obj.type.name in ("Transform", "RectTransform"):
        trs[obj.path_id] = obj.read()

tr_by_go = {}
for pid, t in trs.items():
    go = s(t, "m_GameObject")
    if go:
        tr_by_go[go.path_id] = pid
name_of = {pid: str(s(g, "m_Name", "?")) for pid, g in gos.items()}


def path_of(tr_id):
    names = []
    cur = tr_id
    while cur is not None:
        t = trs[cur]
        go = s(t, "m_GameObject")
        names.append(name_of.get(go.path_id, "?") if go else "?")
        f = s(t, "m_Father")
        cur = f.path_id if f and f.path_id else None
    return "/".join(reversed(names))


for pid, g in gos.items():
    if name_of.get(pid) != "_App1Hand":
        continue
    tr = tr_by_go.get(pid)
    print("\n=== " + path_of(tr))
    for c in s(g, "m_Component", []) or []:
        p = s(c, "component")
        if not p:
            continue
        print(f"  component pathID={p.path_id} fileID={getattr(p,'file_id',None)}")
        try:
            st = p.read_typetree()
            keys = [k for k in st.keys() if not k.startswith("m_")]
            print("    typetree keys:", keys[:12])
            if "m_Script" in st:
                print("    m_Script:", st["m_Script"])
            for k in ("movementMultiplier",):
                if k in st:
                    print(f"    {k} = {st[k]}")
        except Exception as e:
            print("    read_typetree failed:", e)
