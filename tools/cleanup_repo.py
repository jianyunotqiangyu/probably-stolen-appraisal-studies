"""把开发期临时脚本从仓库里剔除（文件仍留在本地，只是不再提交）。

分类依据：这些脚本要么是拆包研究、要么是 Stable Diffusion 工具、
要么是一次性改代码的补丁，和模组的构建/发布无关。
"""
import io
import subprocess
import sys

ROOT = r"D:\DSH_workspace\mod-create"

TEMPORARY = [
    # 拆包研究（会读取游戏原始资源）
    "tools/scan_ui.py",
    "tools/scan_ui2.py",
    "tools/scan_ui3.py",
    "tools/scan_hand_components.py",
    "tools/dump_vanilla_hand_guide.py",
    "tools/export_vanilla_paper.py",
    "tools/export_all_paper_sprites.py",
    "tools/inspect_magnifier.py",
    # Stable Diffusion / SDK 下载
    "tools/sd/sd-auto-mask.py",
    "tools/sd/sd-direct.ps1",
    "tools/sd/sd-inject.ps1",
    "tools/download_sd15.py",
    "tools/download_sd15_resume.py",
    "tools/download_sdxl.py",
    "tools/install_sdk.py",
    # 早期画图脚本（画的是已归档的旧设计）
    "tools/draw_icon_knuckle.py",
    "tools/draw_icon_knuckle2.py",
    "tools/draw_icons_tier1.py",
    "tools/draw_icons_tier1_v2.py",
    "tools/draw_burger_layers.py",
    "tools/draw_icon_festkit.py",
    "tools/draw_magnifier_burger.py",
    # 一次性改造脚本
    "tools/patch_exam_pool.py",
    "tools/quiet_diagnostics.py",
    "tools/tidy_items.py",
    "tools/add_footprint_guard.py",
    "tools/restore_sources.py",
    "tools/strip_manifest_backtick.py",
    "tools/_migrate_20261109.py",
    "tools/_inspect_decomp.py",
    # 运行时 sentinel
    "tools/dotnet-home/.dotnet/8.0.404.aspNetCertificateSentinel",
    "tools/dotnet-home/.dotnet/8.0.404.dotnetFirstUseSentinel",
    "tools/dotnet-home/.dotnet/8.0.404.toolpath.sentinel",
    # 旧工程说明（与根 README 重复且过时）
    "mod/AppraisalExpansion/README.md",
]

IGNORE_BLOCK = """
# 开发期临时脚本（保留在本地，不入库）
tools/_*.py
tools/scan_*.py
tools/dump_vanilla_*.py
tools/export_vanilla_*.py
tools/export_all_paper_sprites.py
tools/inspect_magnifier.py
tools/download_*.py
tools/install_sdk.py
tools/draw_*.py
tools/patch_*.py
tools/quiet_diagnostics.py
tools/tidy_items.py
tools/add_footprint_guard.py
tools/restore_sources.py
tools/strip_manifest_backtick.py
tools/sd/
tools/dotnet-home/
"""


def run(*args):
    return subprocess.run(args, cwd=ROOT, capture_output=True, text=True)


def main():
    sys.stdout.reconfigure(encoding="utf-8")

    tracked = set(run("git", "ls-files").stdout.replace("\n", "\x00").split("\x00"))
    to_remove = [p for p in TEMPORARY if p in tracked]

    if to_remove:
        res = run("git", "rm", "--cached", "--quiet", "--", *to_remove)
        print("已取消跟踪:", len(to_remove), "个")
        if res.returncode != 0:
            print(res.stderr)
    else:
        print("没有需要取消跟踪的文件")

    gi_path = ROOT + r"\.gitignore"
    gi = io.open(gi_path, encoding="utf-8").read()
    if "开发期临时脚本" not in gi:
        io.open(gi_path, "w", encoding="utf-8", newline="\n").write(gi.rstrip() + "\n" + IGNORE_BLOCK)
        print(".gitignore 已追加忽略规则")


if __name__ == "__main__":
    main()
