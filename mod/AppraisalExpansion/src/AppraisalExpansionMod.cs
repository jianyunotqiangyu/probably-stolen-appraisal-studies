using UnityEngine;

/// <summary>
/// 异质鉴定录的入口。按官方模组指南的写法：
/// <list type="bullet">
/// <item>钩子只在 <see cref="OnEnable"/> 订阅、<see cref="OnDisable"/> 退订；</item>
/// <item>物品工厂通过 <c>dir.Add</c> 注册；</item>
/// <item>鉴定类型通过 <c>ModHelper.AddAppraisalItem</c> 注册；</item>
/// <item>Harmony 补丁交给加载器统一 PatchAll，不自己 new Harmony。</item>
/// </list>
/// </summary>
public sealed class AppraisalExpansionMod : IMod
{
    public const string ModId = "AppraisalExpansion";

    private ModManifest _manifest;

    public void Init(ModManifest manifest)
    {
        _manifest = manifest;
        Debug.Log($"[{ModId}] Init v{manifest.ModVersion}");
    }

    public void OnEnable()
    {
        ModHook.OnModItemDirectoryInit += OnModItemDirectoryInit;
        // 入会没有钩子，改为读档后与每天开店时检查一次（见 GuildCard 注释）
        ModHook.OnGameLoadedLate += GuildCard.EnsureGiven;
        ModHook.OnGameLoadedLate += GuideGrant.EnsureGiven;
        ModHook.OnShutterOpenedEarly += GuildCard.EnsureGiven;
        ModHook.OnShutterOpenedEarly += GuideGrant.EnsureGiven;
        // 电话：对话构造器注册一次；号码簿每局读档后补登；预约的考官次日开店时到店
        GuildPhone.RegisterDialogue();
        ModHook.OnGameLoadedLate += GuildPhone.EnsureRegistered;
        ModHook.OnShutterOpenedEarly += GuildPhone.EnsureRegistered;
        ModHook.OnGenerateCustomerLate += AppraiserVisit.OnCustomersGenerated;

        ModHelper.AddAppraisalItem(
            ModId,
            KnuckleItem.Id,
            KnuckleItem.Id,
            AppraisalRankHelper.RANK_JUNIOR,
            KnuckleItem.CreateRandom,
            KnuckleItem.GetCorrectValue,
            KnuckleItem.IsKnuckle,
            KnuckleItem.GuideItemId,
            () => ModHelper.GetLocalized(ModId, "appraisal_type"));

        ModHelper.AddAppraisalItem(
            ModId,
            EnvScanItem.Id,
            EnvScanItem.Id,
            AppraisalRankHelper.RANK_JUNIOR,
            EnvScanItem.CreateRandom,
            EnvScanItem.GetCorrectValue,
            EnvScanItem.IsEnvScan,
            EnvScanItem.GuideItemId,
            () => ModHelper.GetLocalized(ModId, "envscan_type"));

        ModHelper.AddAppraisalItem(
            ModId,
            WristItem.Id,
            WristItem.Id,
            AppraisalRankHelper.RANK_JUNIOR,
            WristItem.CreateRandom,
            WristItem.GetCorrectValue,
            WristItem.IsWrist,
            WristItem.GuideItemId,
            () => ModHelper.GetLocalized(ModId, "wrist_type"));

        ModHelper.AddAppraisalItem(
            ModId,
            CoinItem.Id,
            CoinItem.Id,
            AppraisalRankHelper.RANK_JUNIOR,
            CoinItem.CreateRandom,
            CoinItem.GetCorrectValue,
            CoinItem.IsCoin,
            CoinItem.GuideItemId,
            () => ModHelper.GetLocalized(ModId, "coin_type"));

        DebugTools.Register();
        Debug.Log($"[{ModId}] OnEnable: 4 appraisal types registered");
    }

    public void OnDisable()
    {
        ModHook.OnModItemDirectoryInit -= OnModItemDirectoryInit;
        ModHook.OnGameLoadedLate -= GuildCard.EnsureGiven;
        ModHook.OnGameLoadedLate -= GuideGrant.EnsureGiven;
        ModHook.OnShutterOpenedEarly -= GuildCard.EnsureGiven;
        ModHook.OnShutterOpenedEarly -= GuideGrant.EnsureGiven;
        ModHook.OnGameLoadedLate -= GuildPhone.EnsureRegistered;
        ModHook.OnShutterOpenedEarly -= GuildPhone.EnsureRegistered;
        ModHook.OnGenerateCustomerLate -= AppraiserVisit.OnCustomersGenerated;
        GuildPhone.Unregister();
        ModHelper.RemoveAppraisalItems(ModId);
        DebugTools.Unregister();
        KnuckleInspectionOverlay.Reset();
        Debug.Log($"[{ModId}] OnDisable");
    }

    private static void OnModItemDirectoryInit(ModItemDirectory directory)
    {
        directory.Add(KnuckleItem.Id, KnuckleItem.CreateBase);
        directory.Add(EnvScanItem.Id, EnvScanItem.CreateBase);
        directory.Add(WristItem.Id, WristItem.CreateBase);
        directory.Add(CoinItem.Id, CoinItem.CreateBase);
        // 名片不在这里注册：它由 Books/appraiser_card.json 的 item 段声明（和手册同一套）
    }
}
