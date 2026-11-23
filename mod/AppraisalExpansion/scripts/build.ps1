param(
    [string]$GameDir = "D:\SteamLibrary\steamapps\common\Probably Stolen",
    [string]$Configuration = "Release",
    [string]$AssemblyName = "AppraisalExpansion",
    [switch]$Debug
)

# 说明：本机沙箱会拦截 MSBuild 给子进程开的输出管道，所以这里直接调用 Roslyn 的 csc.dll 编译，
# 不经过 dotnet build。需要 .NET SDK（用于 csc.dll）和游戏 Managed 目录。

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot              # ...\mod\AppraisalExpansion
$workspaceRoot = Split-Path -Parent (Split-Path -Parent $projectRoot)  # ...\mod-create

$managed = Join-Path $GameDir "Probably Stolen_Data\Managed"
$assembly = Join-Path $managed "Assembly-CSharp.dll"
if (-not (Test-Path $assembly)) { throw "找不到游戏程序集：$assembly" }

# 找 csc.dll：优先工作区内的本地 SDK，其次系统 SDK
$csc = $null
$localSdk = Join-Path $workspaceRoot "tools\dotnet\sdk"
if (Test-Path $localSdk) {
    $csc = Get-ChildItem -Path $localSdk -Filter csc.dll -Recurse -ErrorAction SilentlyContinue |
        Where-Object { $_.FullName -like "*Roslyn*bincore*" } |
        Sort-Object FullName -Descending | Select-Object -First 1 -ExpandProperty FullName
}
if (-not $csc) {
    $systemSdk = "C:\Program Files\dotnet\sdk"
    if (Test-Path $systemSdk) {
        $csc = Get-ChildItem -Path $systemSdk -Filter csc.dll -Recurse -ErrorAction SilentlyContinue |
            Where-Object { $_.FullName -like "*Roslyn*bincore*" } |
            Sort-Object FullName -Descending | Select-Object -First 1 -ExpandProperty FullName
    }
}
if (-not $csc) { throw "找不到 csc.dll，请安装 .NET SDK 8" }

$dotnet = Join-Path $workspaceRoot "tools\dotnet\dotnet.exe"
if (-not (Test-Path $dotnet)) { $dotnet = "dotnet" }

$outDir = Join-Path $projectRoot "build"
New-Item -ItemType Directory -Force -Path $outDir | Out-Null
$out = Join-Path $outDir "$AssemblyName.dll"

$sources = Get-ChildItem -Path (Join-Path $projectRoot "src") -Filter *.cs -Recurse | ForEach-Object { $_.FullName }
if (-not $sources) { throw "src 下没有 .cs 文件" }

$refs = @(
    (Join-Path $managed "mscorlib.dll"),
    (Join-Path $managed "netstandard.dll"),
    (Join-Path $managed "System.dll"),
    (Join-Path $managed "System.Core.dll"),
    (Join-Path $managed "UnityEngine.CoreModule.dll"),
    (Join-Path $managed "UnityEngine.UI.dll"),
    (Join-Path $managed "Unity.TextMeshPro.dll"),
    (Join-Path $managed "QFSW.QC.dll"),
    (Join-Path $managed "0Harmony.dll"),
    $assembly
)
foreach ($r in $refs) { if (-not (Test-Path $r)) { throw "缺少引用：$r" } }

$args2 = @(
    "-nologo", "-noconfig", "-nostdlib+", "-target:library", "-platform:x64",
    "-langversion:latest", "-nullable:disable", "-out:$out"
) + $(if ($Debug) { @("-define:MOD_DEBUG") } else { @() }) + ($refs | ForEach-Object { "-r:$_" }) + $sources

& $dotnet exec $csc @args2
if ($LASTEXITCODE -ne 0) { throw "编译失败（exit $LASTEXITCODE）" }

Write-Host "已生成 $out"
