# AppraisalExpansion · 深空当铺：鉴定学

《深空当铺》鉴定玩法内容扩展 Mod 的工程目录。游戏内显示名 `Appraisal Studies`。

## 结构

```
AppraisalExpansion/
├─ AppraisalExpansion.csproj    netstandard2.1，引用游戏 Managed 目录
├─ manifest.xml                 Mod 清单：ID / 版本 / 程序集 / 能力声明
├─ src/
│  ├─ AppraisalExpansionMod.cs  IMod 入口 + 鉴定类型注册 + 指节差分
│  └─ EndNightPatch.cs          Harmony 示例（调试用）
├─ scripts/
│  ├─ build.ps1                 直接用 Roslyn csc.dll 编译 -> build/
│  ├─ pack.ps1                  把工作区 assets/ 平铺成 Textures/ 结构
│  └─ deploy.ps1                build + pack + 同步到游戏 Mods 目录
├─ build/                       编译产物（生成，可删）
└─ Textures/                    运行时资源（pack.ps1 生成，可删，勿手改）
```

## 构建与部署

```powershell
pwsh -File scripts\build.ps1     # 只编译
pwsh -File scripts\pack.ps1      # 只更新素材
pwsh -File scripts\deploy.ps1    # 一条龙
```

`build.ps1` 直接调用 Roslyn 的 `csc.dll`，不经过 `dotnet build`：本机沙箱会拦截 MSBuild 给编译器子进程开的输出管道（`MSB3883 拒绝访问`），直接调 `csc.dll` 没有这个问题。

## 纪律要点（详见 `../../docs/01-编写纪律对照表.md`）

- 物品走 `ModHook.OnModItemDirectoryInit` + `dir.Add(id, factory)`；
- 鉴定类型走 `ModHelper.AddAppraisalItem(...)`；
- 贴图走 `Textures/Items/` + `SetSpriteAndShapeFromMod(modId, key)`，**每张图一个文件**；
- 清单能力声明：Harmony 补丁与反射游戏类型**不需要能力**，平常用 `<Capabilities />`；
- 超出官方指南覆盖范围的实现，就地写 `[非规范实现]` 注释（原因/依据/风险/回退）。

## 发布前

1. F8 运行 `mod-scan AppraisalExpansion`，确认 `declared` 覆盖 `detected`、无拒绝标记；
2. 部署目录只含 `AppraisalExpansion.dll`、`manifest.xml`、`Textures/`（不要带脚本、csproj、src）；
3. 改了 dll/manifest 后玩家需重新授权，属正常现象。
