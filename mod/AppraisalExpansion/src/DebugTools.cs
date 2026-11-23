// 调试按钮只在定义了 MOD_DEBUG 时编译进 DLL。
// 发布构建不带这个定义，玩家拿到的 dll 里没有这些按钮。
// 本地调试：scripts/build.ps1 -Debug

#if MOD_DEBUG
using UnityEngine;

/// <summary>
/// F9 调试按钮。按官方指南《添加你自己的调试按钮》：在 <c>OnEnable</c> 注册、<c>OnDisable</c> 移除，
/// 回调里的异常会被加载器捕获并写进 F8 控制台。
///
/// [非规范实现] “Knuckle Customer” 直接拼了一个鉴定顾客并塞进队列。
/// 依据：指南把顾客生成列为原生支持，但只支持在 <c>OnGenerateCustomer*</c> 钩子里往队列加人；
///       这里要在调试时“按下按钮立刻来一位带指节的顾客”，走的是原版
///       <c>StoreClientListAppraisal.CreateAppraisalRandom</c> 的同一条构造路径（任务里挑的是随机类型）。
/// 风险：<c>StoreClient</c> 的构造字段或 <c>StoreClientFactionSetup.InitScav</c> 变动时失效；
///       失效只影响调试按钮，不影响正式流程。
/// 回退：删掉 <c>SpawnCustomer</c> 与其按钮注册即可。
/// </summary>
internal static class DebugTools
{
    internal static void Register()
    {
        ModHelper.AddDebugFunction(
            AppraisalExpansionMod.ModId,
            ModHelper.DEBUG_CATEGORY_SPAWN,
            "Knuckle Random",
            () => Spawn(KnuckleItem.CreateRandom()));

        ModHelper.AddDebugFunction(
            AppraisalExpansionMod.ModId,
            ModHelper.DEBUG_CATEGORY_SPAWN,
            "Knuckle Pristine",
            () => SpawnVariant(KnuckleItem.GoldPlated, KnuckleItem.ConditionNone, KnuckleItem.InterfaceEmgPlus));

        ModHelper.AddDebugFunction(
            AppraisalExpansionMod.ModId,
            ModHelper.DEBUG_CATEGORY_SPAWN,
            "Knuckle Junk",
            () => SpawnVariant(KnuckleItem.AluminumAlloy, KnuckleItem.ConditionDamage, KnuckleItem.InterfaceNone));

        ModHelper.AddDebugFunction(
            AppraisalExpansionMod.ModId,
            ModHelper.DEBUG_CATEGORY_SPAWN,
            "Knuckle Guide",
            () => ModHelper.MoveItemToInventory(ModHelper.SpawnItem("knuckle_guide")));

        ModHelper.AddDebugFunction(
            AppraisalExpansionMod.ModId,
            ModHelper.DEBUG_CATEGORY_SPAWN,
            "Guild Card",
            () => ModHelper.MoveItemToInventory(ModHelper.SpawnItem(GuildCard.Id)));

        ModHelper.AddDebugFunction(
            AppraisalExpansionMod.ModId,
            ModHelper.DEBUG_CATEGORY_COMMAND,
            "Guild Card Check",
            GuildCard.EnsureGiven,
            tall: true);

        // 把入会对话人物（原版 CreateStoryAppraisalBoard）直接排进队列，方便测试入会流程
        ModHelper.AddDebugFunction(
            AppraisalExpansionMod.ModId,
            ModHelper.DEBUG_CATEGORY_SPAWN,
            "Guild Join Talk",
            () => PlayerStore.Instance.storeClientManager.AddNextClient(
                StoreClientListStory.CreateStoryAppraisalBoard()));

        // 复位入会状态与手册补发标记，便于重复测试
        ModHelper.AddDebugFunction(
            AppraisalExpansionMod.ModId,
            ModHelper.DEBUG_CATEGORY_COMMAND,
            "Reset Guild Join",
            ResetGuildJoin,
            tall: true);

        ModHelper.AddDebugFunction(
            AppraisalExpansionMod.ModId,
            ModHelper.DEBUG_CATEGORY_SPAWN,
            "EnvScan Random",
            () => Spawn(EnvScanItem.CreateRandom()));

        ModHelper.AddDebugFunction(
            AppraisalExpansionMod.ModId,
            ModHelper.DEBUG_CATEGORY_SPAWN,
            "EnvScan Full Kit",
            () => SpawnEnvScan(EnvScanItem.BodyGood, EnvScanItem.SensorOk,
                EnvScanItem.PluginBoth, EnvScanItem.VendorLuban));

        ModHelper.AddDebugFunction(
            AppraisalExpansionMod.ModId,
            ModHelper.DEBUG_CATEGORY_SPAWN,
            "EnvScan Junk",
            () => SpawnEnvScan(EnvScanItem.BodyBroken, EnvScanItem.SensorDead,
                EnvScanItem.PluginNone, EnvScanItem.VendorNone));

        ModHelper.AddDebugFunction(
            AppraisalExpansionMod.ModId,
            ModHelper.DEBUG_CATEGORY_SPAWN,
            "Wrist Random",
            () => Spawn(WristItem.CreateRandom()));

        ModHelper.AddDebugFunction(
            AppraisalExpansionMod.ModId,
            ModHelper.DEBUG_CATEGORY_SPAWN,
            "Wrist Luxe",
            () => SpawnWrist(WristItem.ConditionNew, WristItem.MaterialGold, WristItem.ServiceBoth));

        ModHelper.AddDebugFunction(
            AppraisalExpansionMod.ModId,
            ModHelper.DEBUG_CATEGORY_SPAWN,
            "Wrist Junk",
            () => SpawnWrist(WristItem.ConditionDamaged, WristItem.MaterialIron, WristItem.ServiceRelay));

        ModHelper.AddDebugFunction(
            AppraisalExpansionMod.ModId,
            ModHelper.DEBUG_CATEGORY_SPAWN,
            "Coin Guide",
            () => ModHelper.MoveItemToInventory(ModHelper.SpawnItem("coin_guide")));

        ModHelper.AddDebugFunction(
            AppraisalExpansionMod.ModId,
            ModHelper.DEBUG_CATEGORY_SPAWN,
            "Coin Random",
            () => Spawn(CoinItem.CreateRandom()));

        ModHelper.AddDebugFunction(
            AppraisalExpansionMod.ModId,
            ModHelper.DEBUG_CATEGORY_SPAWN,
            "Coin Test Coin",
            () => SpawnCoin(CoinItem.MaterialGold, CoinItem.EditionCollector, "00005G", false));

        ModHelper.AddDebugFunction(
            AppraisalExpansionMod.ModId,
            ModHelper.DEBUG_CATEGORY_SPAWN,
            "Coin Jaguar",
            () => SpawnCoin(CoinItem.MaterialSilver, CoinItem.EditionCollector, "00077S", false));

        ModHelper.AddDebugFunction(
            AppraisalExpansionMod.ModId,
            ModHelper.DEBUG_CATEGORY_SPAWN,
            "Coin Fake",
            () => SpawnCoin(CoinItem.MaterialCopper, CoinItem.EditionNormal, "04321G", true));

        ModHelper.AddDebugFunction(
            AppraisalExpansionMod.ModId,
            ModHelper.DEBUG_CATEGORY_COMMAND,
            "Knuckle Customer",
            SpawnCustomer,
            tall: true);

        // ---- 考官 / 考核 ----
        ModHelper.AddDebugFunction(
            AppraisalExpansionMod.ModId,
            ModHelper.DEBUG_CATEGORY_COMMAND,
            "Examiner Now",
            () => AppraiserVisit.Queue(),
            tall: true);

        ModHelper.AddDebugFunction(
            AppraisalExpansionMod.ModId,
            ModHelper.DEBUG_CATEGORY_COMMAND,
            "Examiner Tomorrow",
            AppraiserVisit.Book,
            tall: true);

        ModHelper.AddDebugFunction(
            AppraisalExpansionMod.ModId,
            ModHelper.DEBUG_CATEGORY_COMMAND,
            "Exam Ready 100%",
            FillPromotionProgress,
            tall: true);

        ModHelper.AddDebugFunction(
            AppraisalExpansionMod.ModId,
            ModHelper.DEBUG_CATEGORY_COMMAND,
            "Exam Clear Cooldown",
            ExamSession.ResetCooldown,
            tall: true);

        ModHelper.AddDebugFunction(
            AppraisalExpansionMod.ModId,
            ModHelper.DEBUG_CATEGORY_COMMAND,
            "Exam Cert Now",
            () =>
            {
                AppraisalRankHelper.Promote();
                Debug.Log($"[{AppraisalExpansionMod.ModId}] 调试：直接发证并晋级");
            },
            tall: true);
    }

    internal static void Unregister()
    {
        ModHelper.RemoveDebugFunctions(AppraisalExpansionMod.ModId);
    }

    private static void SpawnVariant(string material, string condition, string interfaceType)
    {
        GameItem item = DirectoryMaster.Item(KnuckleItem.Id);
        KnuckleItem.ApplyVariant(item, material, condition, interfaceType);
        Spawn(item);
    }

    private static void SpawnEnvScan(string body, string sensor, string plugin, string vendor)
    {
        GameItem item = DirectoryMaster.Item(EnvScanItem.Id);
        EnvScanItem.ApplyVariant(item, body, sensor, plugin, vendor);
        Spawn(item);
    }

    private static void SpawnCoin(string material, string edition, string serial, bool fake)
    {
        GameItem item = DirectoryMaster.Item(CoinItem.Id);
        CoinItem.ApplyVariant(item, material, edition, serial, fake);
        Spawn(item);
    }

    private static void SpawnWrist(string condition, string material, string service)
    {
        GameItem item = DirectoryMaster.Item(WristItem.Id);
        WristItem.ApplyVariant(item, condition, material, service);
        Spawn(item);
    }


    /// <summary>调试：把入会状态与手册补发标记复位，方便反复测试入会流程。</summary>
    private static void ResetGuildJoin()
    {
        PlayerStore store = PlayerStore.Instance;
        if (store != null)
        {
            store.isAppraisalIntroduced = false;
        }

        ModHelper.SetModDataBool(AppraisalExpansionMod.ModId, "guides_granted", false);
        Debug.Log($"[{AppraisalExpansionMod.ModId}] 调试：入会状态与手册补发标记已复位");
    }

    private static void Spawn(GameItem item)
    {
        if (PlayerStore.Instance == null)
        {
            Debug.LogWarning($"[{AppraisalExpansionMod.ModId}] 调试按钮需要在店内使用");
            return;
        }
        ModHelper.MoveItemToFrontCounter(item);

        // 诊断：把「堆叠」相关状态打出来。
        // 若两件物品的 shape 位置完全重合而 unitCount 都是 1，说明是重叠摆放，不是堆叠。
        if (item != null)
        {
            string shape = item.modifiedShape == null
                ? "null"
                : $"{item.modifiedShape.width}x{item.modifiedShape.height}@({item.modifiedShape.minX},{item.modifiedShape.minY})";
            Debug.Log($"[{AppraisalExpansionMod.ModId}] spawn {item.identifier} unitCount={item.unitCount} "
                + $"shape={shape} hasStackFunc={item.mayStackItemFunc != null} "
                + $"parent={(item.parentInventory != null)}");
        }
    }

    private static void SpawnCustomer()
    {
        if (PlayerStore.Instance == null)
        {
            Debug.LogWarning($"[{AppraisalExpansionMod.ModId}] 调试按钮需要在店内使用");
            return;
        }

        PlayerStore.Instance.isAppraisalIntroduced = true;
        // 与电话预约共用同一段构造逻辑，避免两处各写一遍 Customer
        AppraiserVisit.Queue();
    }

    /// <summary>调试用：把晋升进度直接拉满，方便测预约与考核。</summary>
    private static void FillPromotionProgress()
    {
        PlayerStore store = PlayerStore.Instance;
        if (store == null)
        {
            Debug.LogWarning($"[{AppraisalExpansionMod.ModId}] 调试按钮需要在店内使用");
            return;
        }

        double threshold = AppraisalRankHelper.GetThreshold();
        store.appraisalProgress = threshold;
        Debug.Log($"[{AppraisalExpansionMod.ModId}] 调试：晋升进度已拉到 {AppraisalRankHelper.GetProgressPercent()}%");
    }
}
#endif
