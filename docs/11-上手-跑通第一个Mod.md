# 11 · 上手：把 Mod 装进游戏并确认它真的加载了

> 目标：跑通「编译 → 部署 → 启用 → 日志确认」这一圈。这一圈通了，后面写鉴定内容才有意义。
> 日常改代码只看 [`00-项目状态与工作日志.md`](00-项目状态与工作日志.md) §4 的命令即可，本文是第一次上手用的详细版。

---

## 先认识三个位置

| 名称 | 路径 | 作用 |
|---|---|---|
| 工程目录 | `D:\DSH_workspace\mod-create\mod\AppraisalExpansion` | 源码、清单、构建脚本 |
| 编译产物 | `mod\AppraisalExpansion\build\AppraisalExpansion.dll` | 游戏真正加载的文件 |
| 游戏目录 | `D:\SteamLibrary\steamapps\common\Probably Stolen` | `Mods\AppraisalExpansion\` 在它下面 |

游戏里的一个 Mod 至少需要两样东西：

```
Mods\AppraisalExpansion\
    ├── manifest.xml              ← 我叫什么、版本多少、加载哪个 dll、声明哪些能力
    ├── AppraisalExpansion.dll    ← 真正的代码
    └── Textures\Items\*.png      ← 物品精灵图（有就加载，平铺、不递归）
```

---

## 第 1 步：编译

```powershell
pwsh -NoProfile -File D:\DSH_workspace\mod-create\mod\AppraisalExpansion\scripts\build.ps1
```

成功会打印：`已生成 ...\build\AppraisalExpansion.dll`。

> 不要用 `dotnet build`：本机沙箱会拦截 MSBuild 给编译器子进程开的管道，报 `MSB3883 拒绝访问`。
> `build.ps1` 直接调 Roslyn 的 `csc.dll`，绕开这个问题。

## 第 2 步：部署（编译 + 打包素材 + 复制）

```powershell
pwsh -NoProfile -File D:\DSH_workspace\mod-create\mod\AppraisalExpansion\scripts\deploy.ps1
```

它做四件事：编译 → 把 `assets/` 平铺进 `Textures/` → 清掉游戏目录里的旧 `Textures/` → 复制 dll 和清单。

部署完检查一下游戏目录，**不要多套一层**：

```
D:\SteamLibrary\steamapps\common\Probably Stolen\Mods\AppraisalExpansion\
    manifest.xml
    AppraisalExpansion.dll
    Textures\Items\...
```

> 部署目录里不要出现 `.ps1` / `.csproj` / `src`：模组扫描器会检查文件夹里的脚本和可执行文件。

## 第 3 步：启用

1. 启动游戏 → 主菜单的 Mod 页面（中文界面可能叫「改装件」）；
2. 勾选启用 `Oddity Appraisal`；
3. 按提示**重启游戏**（启用/禁用需要重启才生效）。

> 只要 dll 或 manifest 变了一个字节，就会要求重新批准——这是加载器的防篡改设计，不是 bug。

## 第 4 步：确认加载

日志目录：`%USERPROFILE%\AppData\LocalLow\Questing Goose Studio\Probably Stolen\`，文件名是 `GameLog_日期_时间.txt`（不是 `Player.log`）。

用 `F8` 打开游戏内控制台更快，搜索 `[AppraisalExpansion]`，应该看到：

```
[AppraisalExpansion] Init v0.2.0
[AppraisalExpansion] OnEnable: 1 appraisal type registered
```

- 想直接自查能力声明：F8 里输入 `mod-scan AppraisalExpansion`，要求 `declared` 覆盖 `detected`、没有拒绝标记；
- 想直接看物品：F9 开发菜单的 Spawn 列有 `Knuckle Random` / `Knuckle Pristine` / `Knuckle Junk`，
  Command 列有 `Knuckle Customer`（排一位带指节的鉴定顾客）。

> F9 需要游戏根目录存在 **`dev.txt`**（空文件，名字必须正好是 `dev.txt`，不能是 `1dev.txt`）。

---

## 常见故障

| 现象 | 排查 |
|---|---|
| Mod 页面看不到本 Mod | 目录名必须等于 `<ID>`；`manifest.xml` 必须在目录根；dll 必须在 `<Assemblies>` 里列出 |
| 勾不上 / 一勾就退回 | 清单能力声明与扫描结果不符；用 `mod-scan` 看 `detected` 比 `declared` 多了什么 |
| 物品贴图是“未知”问号 | `Textures/Items/` 下没有对应文件名的 png；键 = 不含扩展名的文件名，且**不递归** |
| 物品名显示空白 | 游戏字体没有该字形（中文）；物品名要用 ASCII，见 `00` 的 P1 |
| 大图不显示 | `KnuckleInspectionOverlay` 的补丁没生效，或 `Textures/Items/` 里缺 `knuckle_<材质>_<状态>.png` |
