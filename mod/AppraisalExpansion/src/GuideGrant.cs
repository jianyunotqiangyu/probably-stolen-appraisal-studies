using System.Collections.Generic;
using HarmonyLib;
using UnityEngine;

/// <summary>
/// 鉴定手册补发。
///
/// 原版只在「加入行会」和「晋级」时发指南：
/// <c>AppraisalRankHelper.SetRank()</c> 里遍历 <c>GetUnlockedAt(rank)</c>，
/// 对每个 <c>guideItemId</c> 检查 <c>EmporiumEntry.GetItemCountById &lt;= 0</c> 才发放。
///
/// 这对模组有两个坑：
/// <list type="bullet">
/// <item>玩家已经入会/晋级过了，之后再装模组或更新版本，那一次发放永远不会再发生；</item>
/// <item>四位鉴定品都在初级档（rank 0），而发指南的判定是「本等级**新解锁**的物品」，
///       初级档玩家没有下一次晋级，手册就一直发不下来。</item>
/// </list>
/// 实测入会流程（原版 <c>CreateStoryAppraisalBoard</c>）是**硬编码**的：
/// 直接把 <c>isAppraisalIntroduced = true</c>，再手动塞 hand_guide / magnifier / cert1，
/// **根本不调用 SetRank**，所以初级档手册在入会时不会自动发。
/// 因此除了读档与开店，还要挂到「对话结束」这个时机（见 GuideGrantPatch）。
///
/// 补发策略：已入会、且对应手册不在手上时发一本。
/// 用模组数据记一个「已补发」标记，避免玩家卖掉手册后又被凭空补出来。
/// </summary>
internal static class GuideGrant
{
    private const string GrantedKey = "guides_granted";

    private static readonly string[] GuideIds =
    {
        "knuckle_guide",
        "envscan_guide",
        "wrist_guide",
        "coin_guide",
    };

    internal static void EnsureGiven()
    {
        PlayerStore store = PlayerStore.Instance;
        if (store == null || !store.isAppraisalIntroduced || EmporiumEntry.Instance == null)
        {
            return;
        }

        if (ModHelper.GetModDataBool(AppraisalExpansionMod.ModId, GrantedKey))
        {
            return;
        }

        List<string> given = new List<string>();
        foreach (string id in GuideIds)
        {
            if (EmporiumEntry.Instance.GetItemCountById(id) > 0)
            {
                continue;
            }

            store.AddDirectSellingItemToTable(id, isOwend: true);
            given.Add(id);
        }

        ModHelper.SetModDataBool(AppraisalExpansionMod.ModId, GrantedKey, true);

        if (given.Count > 0)
        {
            Debug.Log($"[{AppraisalExpansionMod.ModId}] 补发鉴定手册：{string.Join(", ", given)}");
        }
        else
        {
            Debug.Log($"[{AppraisalExpansionMod.ModId}] 四本手册都已在手上，无需补发");
        }
    }
}

/// <summary>
/// 入会对话走完后立刻补发手册。
/// 原版入会（CreateStoryAppraisalBoard）不调用 SetRank，只在对话里硬编码发 hand_guide 等物件，
/// 所以没有「等级变化」可以挂钩；CurrentClientLeave 是这段对话结束时一定会调用的方法。
/// 补发本身带「已发过」标记，反复调用不会重复发。
/// </summary>
[HarmonyPatch(typeof(DialogUIManager), nameof(DialogUIManager.CurrentClientLeave))]
internal static class GuideGrantPatch
{
    private static void Postfix()
    {
        GuideGrant.EnsureGiven();
    }
}
