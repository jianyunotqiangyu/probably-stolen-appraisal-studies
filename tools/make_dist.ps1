# 生成发布文件夹 dist\ProbablyStolen-AppraisalStudies（路径固定，不随版本变）
# 只从「游戏里已部署的那一份」复制，保证发布包与实测版本一致。
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
$ErrorActionPreference = "Stop"

$rootPath = "D:\DSH_workspace\mod-create"
$distPath = "$rootPath\dist\ProbablyStolen-AppraisalStudies"
$deployed = "D:\SteamLibrary\steamapps\common\Probably Stolen\Mods\AppraisalExpansion"
$pythonExe = "D:\DSH_Desktop\DSH Desktop\resources\office-runtime\primary-runtime\dependencies\python\python.exe"
$previewSource = "$rootPath\mod\AppraisalExpansion\preview.png"

# 版本号从 manifest 读，避免两处不一致
[xml]$manifest = Get-Content -Raw -Encoding UTF8 "$rootPath\mod\AppraisalExpansion\manifest.xml"
$version = $manifest.ModManifest.ModVersion
Write-Host "版本: $version"
Write-Host "目标: $distPath"

if (Test-Path $distPath) { Remove-Item $distPath -Recurse -Force }
New-Item -ItemType Directory -Force -Path $distPath | Out-Null

Copy-Item "$deployed\AppraisalExpansion.dll" $distPath
Copy-Item "$deployed\manifest.xml" $distPath
robocopy "$deployed\Books" "$distPath\Books" /E /NFL /NDL /NJH /NJS | Out-Null
robocopy "$deployed\Localization" "$distPath\Localization" /E /NFL /NDL /NJH /NJS | Out-Null
robocopy "$deployed\Textures" "$distPath\Textures" /E /NFL /NDL /NJH /NJS | Out-Null

if (Test-Path $previewSource) {
    $env:PREVIEW_SRC = $previewSource
    $env:PREVIEW_DST = "$distPath\preview.png"
    & $pythonExe "$rootPath\tools\workshop\make_preview.py"
} else {
    Write-Host "缺少 preview.png（$previewSource）"
}

$zipPath = "$rootPath\dist\ProbablyStolen-AppraisalStudies-$version.zip"
if (Test-Path $zipPath) { Remove-Item $zipPath -Force }
Compress-Archive -Path $distPath -DestinationPath $zipPath -CompressionLevel Optimal

$files = Get-ChildItem $distPath -Recurse -File
Write-Host ("dist: {0} 个文件, {1} MB" -f $files.Count, [math]::Round(($files | Measure-Object Length -Sum).Sum / 1MB, 2))
Write-Host ("zip : {0} ({1} MB)" -f (Split-Path $zipPath -Leaf), [math]::Round((Get-Item $zipPath).Length / 1MB, 2))
