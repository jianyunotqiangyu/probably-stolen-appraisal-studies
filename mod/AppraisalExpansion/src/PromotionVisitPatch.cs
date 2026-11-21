using HarmonyLib;

/// <summary>
/// 关掉原版「满足晋升条件后委员会自动上门」这条路径，改由玩家打电话预约。
///
/// [非规范实现] 前置补丁，让 <c>AppraisalRankHelper.HandlePromotionClient</c> 直接返回。
/// 依据：指南没有「晋升上门时机」的 API；这是对游戏代码打补丁（能力免费），
///       不动存档里的任何字段。
/// 风险：游戏改动该方法名/签名时补丁失效 → 原版自动上门会恢复（不会崩）。
/// 回退：删掉本文件即可恢复原版行为。
/// </summary>
[HarmonyPatch(typeof(AppraisalRankHelper), nameof(AppraisalRankHelper.HandlePromotionClient))]
internal static class PromotionVisitPatch
{
    private static bool Prefix()
    {
        return false;
    }
}
