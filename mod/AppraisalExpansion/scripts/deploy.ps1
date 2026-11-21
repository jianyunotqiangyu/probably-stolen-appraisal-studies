param(
    [string]$GameDir = "D:\SteamLibrary\steamapps\common\Probably Stolen",
    [string]$Configuration = "Release",
    [switch]$SkipBuild
)

# 部署 = 编译 + 打包素材 + 同步到游戏 Mods 目录。
# 只同步运行时需要的东西：AppraisalExpansion.dll、manifest.xml、preview.png、Textures/ 等资源目录。
# 脚本本身、csproj、src/ 都不进游戏目录（扫描器会检查模组文件夹里的脚本文件）。

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
$dll = Join-Path $projectRoot "build\AppraisalExpansion.dll"

if (-not $SkipBuild) {
    & (Join-Path $PSScriptRoot "build.ps1") -GameDir $GameDir -Configuration $Configuration
    if ($LASTEXITCODE -ne 0) { throw "编译失败" }
}
& (Join-Path $PSScriptRoot "pack.ps1")
if ($LASTEXITCODE -ne 0) { throw "素材打包失败" }

if (-not (Test-Path $dll)) { throw "找不到构建产物：$dll" }

$modsDir = Join-Path $GameDir "Mods\AppraisalExpansion"

# 目标目录必须是游戏 Mods 下的本模组目录，防止误删
if ($modsDir -notlike "*\Mods\AppraisalExpansion") {
    throw "部署目标路径不符合预期：$modsDir"
}
New-Item -ItemType Directory -Force -Path $modsDir | Out-Null

# 游戏运行时会把已加载的 dll 映射进内存，覆盖会报“用户映射区域”。
# 先探测一次，早失败，避免只更新了清单/资源、dll 还是旧的这种半成品状态。
$deployedDll = Join-Path $modsDir "AppraisalExpansion.dll"
if (Test-Path $deployedDll) {
    try {
        $probe = [System.IO.File]::Open($deployedDll, [System.IO.FileMode]::Open, [System.IO.FileAccess]::ReadWrite, [System.IO.FileShare]::None)
        $probe.Close()
    }
    catch {
        throw "游戏正在运行（AppraisalExpansion.dll 被占用）。请先完全退出 Probably Stolen，再重新运行本脚本。"
    }
}

Copy-Item -LiteralPath $dll -Destination $modsDir -Force
Copy-Item -LiteralPath (Join-Path $projectRoot "manifest.xml") -Destination $modsDir -Force
if (Test-Path (Join-Path $projectRoot "preview.png")) {
    Copy-Item -LiteralPath (Join-Path $projectRoot "preview.png") -Destination $modsDir -Force
}

# 资源目录整体替换，避免上一次部署的废弃贴图残留在游戏目录里
foreach ($folder in @("Textures", "Books", "Localization", "Sounds")) {
    $src = Join-Path $projectRoot $folder
    $dst = Join-Path $modsDir $folder
    if (Test-Path $src) {
        if (Test-Path $dst) { Remove-Item -LiteralPath $dst -Recurse -Force }
        Copy-Item -LiteralPath $src -Destination $modsDir -Recurse -Force
    }
}

$itemCount = 0
$itemsDir = Join-Path $modsDir "Textures\Items"
if (Test-Path $itemsDir) { $itemCount = (Get-ChildItem -Path $itemsDir -File).Count }

Write-Host "已部署到 $modsDir（物品精灵图 $itemCount 张）"
Write-Host "启动游戏 -> Mod 页面启用 -> 按提示重启；F8 控制台可运行 mod-scan AppraisalExpansion 自查能力声明"
