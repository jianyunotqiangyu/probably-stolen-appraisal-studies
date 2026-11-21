param()

# 素材打包：把工作区 assets/ 下按类别存放的源素材，平铺成游戏要求的运行时结构。
#   assets/items/<物品ID>/<类别>/xxx.png      -> Textures/Items/xxx.png   （点采样，像素画）
#   assets/paper/xxx.png                      -> Textures/Items/xxx.png   （点采样，见下方说明）
#   assets/sounds/xxx.wav|ogg|mp3             -> Sounds/xxx.wav
# 游戏只扫一层目录、不递归，资源键 = 不含扩展名的文件名，所以平铺后不能重名。
#
# 为什么 paper 也进 Textures/Items：
#   ModLoader.LoadPaperTextures 把 Textures/Paper 的图硬编码成 FilterMode.Bilinear，
#   而手册是按设计单位 314x402 放大到 628x804 显示的，双线性会把像素画糊成一团。
#   Textures/Items 走的是 LoadTexturesFromFolder(pixelArt: true) → FilterMode.Point，
#   和游戏本体的像素画一致；PaperAssets.FromMod 也是先查 PaperSprites 再查 Sprites，
#   所以放进 Items 依然能被手册的 background/sprite 键解析到。
# 本脚本是纯开发工具，不进游戏 Mods 目录。

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
$workspaceRoot = Split-Path -Parent (Split-Path -Parent $projectRoot)
$assetsRoot = Join-Path $workspaceRoot "assets"

$map = @{
    "items"  = @{ Dir = "Textures\Items"; Ext = @(".png", ".jpg") }
    "paper"  = @{ Dir = "Textures\Paper"; Ext = @(".png", ".jpg") }
    "sounds" = @{ Dir = "Sounds";         Ext = @(".wav", ".ogg", ".mp3") }
}

# 全局键集合：items 和 paper 会落进同一个目录，必须跨类别查重
$globalSeen = @{}
$prepared = @{}

# 先整体清掉上一次生成的 Textures，避免旧的 Textures\Paper 之类残留被一起部署
$texturesRoot = Join-Path $projectRoot "Textures"
if (Test-Path $texturesRoot) { Remove-Item -LiteralPath $texturesRoot -Recurse -Force }

foreach ($kind in $map.Keys) {
    $srcRoot = Join-Path $assetsRoot $kind
    $dir = $map[$kind].Dir
    $target = Join-Path $projectRoot $dir

    if (-not $prepared.ContainsKey($dir)) {
        if (Test-Path $target) { Remove-Item -LiteralPath $target -Recurse -Force }
        $prepared[$dir] = $true
    }
    if (-not (Test-Path $srcRoot)) { continue }

    $files = @(Get-ChildItem -Path $srcRoot -Recurse -File |
        Where-Object { $map[$kind].Ext -contains $_.Extension.ToLowerInvariant() })
    if ($files.Count -eq 0) { continue }

    $count = 0
    foreach ($f in $files) {
        $key = [System.IO.Path]::GetFileNameWithoutExtension($f.Name)
        if ($globalSeen.ContainsKey($key)) {
            throw "资源键重复：'$key'（$($globalSeen[$key]) 与 $($f.FullName)）。运行时按文件名作键，不能重名。"
        }
        $globalSeen[$key] = $f.FullName
        New-Item -ItemType Directory -Force -Path $target | Out-Null
        Copy-Item -LiteralPath $f.FullName -Destination (Join-Path $target $f.Name) -Force
        $count++
    }

    Write-Host ("{0}: {1} 个资源 -> {2}" -f $kind, $count, $dir)
}

Write-Host "素材打包完成：$projectRoot"
