# -*- coding: utf-8 -*-
"""一次性工程目录整理脚本（2026-11-09）。

只做搬运与分类，不改任何代码内容。
运行后可删除；保留是为了留痕，便于回溯整理前后的路径。
"""
import os
import re
import shutil

W = r"D:\DSH_workspace\mod-create"
GAME_MODS = r"D:\SteamLibrary\steamapps\common\Probably Stolen\Mods\AppraisalExpansion"

def p(*parts):
    return os.path.join(W, *parts)

def ensure(d):
    os.makedirs(d, exist_ok=True)
    return d

def move(src, dst):
    if not os.path.exists(src):
        print("SKIP(missing)", src)
        return
    ensure(os.path.dirname(dst))
    if os.path.exists(dst):
        print("SKIP(exists)", dst)
        return
    shutil.move(src, dst)
    print("MOVE", os.path.relpath(src, W), "->", os.path.relpath(dst, W))

def movedir(src, dst):
    move(src, dst)

# ---------------------------------------------------------------- 1. 目录骨架
for d in ["docs", "mod", "assets/items", "assets/paper", "reference/guides",
          "reference/decompiled", "reference/vanilla-ui", "reference/examples",
          "reference/notes", "tools", "_archive"]:
    ensure(p(d))

# ---------------------------------------------------------------- 2. Mod 工程
MOD = p("mod", "AppraisalExpansion")
ensure(MOD)
ensure(p("mod", "AppraisalExpansion", "scripts"))

move(p("starter", "AppraisalExpansion.csproj"), p(MOD, "AppraisalExpansion.csproj"))
move(p("starter", "manifest.xml"), p(MOD, "manifest.xml"))
move(p("starter", "README.md"), p(MOD, "README.md"))
movedir(p("starter", "src"), p(MOD, "src"))
move(p("starter", "build.ps1"), p(MOD, "scripts", "build.ps1"))
if os.path.isdir(p("starter", "scripts")):
    for f in os.listdir(p("starter", "scripts")):
        move(p("starter", "scripts", f), p(MOD, "scripts", f))

# ---------------------------------------------------------------- 3. 美术素材
ITEMS = p("assets", "items")
SRC_TEX = p("starter", "Textures", "Items")

BURGER_OBSOLETE = {"magnifier_burger_layered.png", "magnifier_oddity_cult_burger.png"}
MATS = ("alu", "steel", "gold")

def knuckle_bucket(name):
    if name.startswith("knuckle_icon_"):
        return ("oddity_bio_knuckle", "icon_variant")
    if name.startswith("knuckle_var_"):
        return ("oddity_bio_knuckle", "magnifier_variant")
    if name.startswith("knuckle_overlay_"):
        return ("oddity_bio_knuckle", "magnifier_overlay")
    m = re.fullmatch(r"knuckle_(alu|steel|gold)_(normal|wear|damage)\.png", name)
    if m:
        return ("oddity_bio_knuckle", "magnifier_base")
    if name == "oddity_bio_knuckle.png":
        return ("oddity_bio_knuckle", "icon")
    m = re.fullmatch(r"(oddity_[a-z0-9_]+)\.png", name)
    if m:
        return (m.group(1), "icon")
    return None

if os.path.isdir(SRC_TEX):
    for name in sorted(os.listdir(SRC_TEX)):
        src = os.path.join(SRC_TEX, name)
        if not name.lower().endswith(".png"):
            continue
        if name.startswith("burger_") or name in BURGER_OBSOLETE:
            move(src, p("_archive", "obsolete-assets", "burger", name))
            continue
        bucket = knuckle_bucket(name)
        if bucket is None:
            move(src, p("_archive", "obsolete-assets", "unclassified", name))
            continue
        item, sub = bucket
        move(src, p(ITEMS, item, sub, name))

# 游戏目录里的中文名旧图（88->92 多出来的 8 张）视为废弃素材
if os.path.isdir(os.path.join(GAME_MODS, "Textures", "Items")):
    for name in os.listdir(os.path.join(GAME_MODS, "Textures", "Items")):
        if any(ord(ch) > 127 for ch in name):
            move(os.path.join(GAME_MODS, "Textures", "Items", name),
                 p("_archive", "obsolete-assets", "legacy-cn", name))

# ---------------------------------------------------------------- 4. 参考资料
R = p("reference")
move(p("research", "ModdingGuide.zh-CN.md"), p(R, "guides", "ModdingGuide.zh-CN.md"))
for extra in ["CodeOfConduct.zh-CN.md", "APIChanges.zh-CN.md", "README.zh-CN.md"]:
    move(os.path.join(r"D:\DSH_workspace\mod-create\research", extra), p(R, "guides", extra))

movedir(p("research", "decompiled"), p(R, "decompiled"))
move(p("research", "full"), p(R, "full"))
movedir(p("research", "vanilla_ui"), p(R, "vanilla-ui"))
move(p("research", "src"), p(R, "examples", "free-chat-src"))
move(p("research", "repo"), p(R, "examples", "mods-repo"))

for name in ["9game.txt", "free-chat-README.md", "knuckle_names.txt", "ludens.txt",
             "mods.txt", "pixellab.md", "pricing.txt", "rd_mcp.md",
             "retro_diffusion_skill.md", "retro_diffusion_styles.md", "tree.txt", "wiki.txt"]:
    move(p("research", name), p(R, "notes", name))

# 反编译工具链
move(p("research", "tools", "ilspy"), p("tools", "decompiler", "ilspy"))
move(p("research", "tools", "ilspycmd"), p("tools", "decompiler", "ilspycmd"))
move(p("research", "tools", "roslyn"), p("tools", "decompiler", "roslyn"))
move(p("research", "pylibs"), p("tools", "pylibs"))
if os.path.isdir(p("research", "tools")) and not os.listdir(p("research", "tools")):
    os.rmdir(p("research", "tools"))
if os.path.isdir(p("research", ".tmp")):
    shutil.rmtree(p("research", ".tmp"), ignore_errors=True)

# ---------------------------------------------------------------- 5. 归档
movedir(p("SD-Picture"), p("_archive", "sd-output"))
movedir(p("acl-recovery"), p("_archive", "acl-recovery"))
for f in ["sd-auto-mask.py", "sd-direct.ps1", "sd-inject.ps1"]:
    move(p(f), p("tools", "sd", f))

# ---------------------------------------------------------------- 6. 文档
move(p("mod策划案.md"), p("docs", "30-策划案-异质鉴定录.md"))
move(p("docs", "深空当铺-mod开发指南.md"), p("docs", "10-开发指南-加载器与工程.md"))
move(p("docs", "新手上手-跑通第一个Mod.md"), p("docs", "11-上手-跑通第一个Mod.md"))
move(p("docs", "指节-鉴定差分方案.md"), p("docs", "20-设计-指节差分.md"))

# ---------------------------------------------------------------- 7. 清空 starter
for junk in ["starter/bin", "starter/obj"]:
    if os.path.isdir(p(junk)):
        shutil.rmtree(p(junk), ignore_errors=True)
for junk in ["starter/test.dll", "starter/Textures"]:
    if os.path.isdir(p(junk)):
        shutil.rmtree(p(junk), ignore_errors=True)
    elif os.path.exists(p(junk)):
        os.remove(p(junk))
if os.path.isdir(p("starter")):
    leftover = [x for x in os.listdir(p("starter")) if x not in ("README.md",)]
    print("starter 剩余：", leftover)

print("DONE")
