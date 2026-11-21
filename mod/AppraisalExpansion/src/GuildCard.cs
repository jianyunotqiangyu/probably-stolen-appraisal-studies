using UnityEngine;

/// <summary>
/// 鉴定行会名片：加入行会（在鉴定公告板上完成入会对话）后自动放到柜台上。
///
/// 为什么用「检测 + 补发」而不是挂钩子：
/// 入会是一段写死在原版对话里的流程（扣费、发导师笔记 / 手记 / 放大镜 / 证书），
/// 模组没有「入会完成」这个钩子。所以改为在每次读档与每天开店时检查一次：
/// <c>PlayerStore.isAppraisalIntroduced</c> 为真、且柜台上还没有这张卡，就补一张。
/// 判定用 <c>EmporiumEntry.GetItemCountById</c> 去重，和原版发指南的写法一致。
///
/// 图标是占位图（16×16），正式美术可覆盖 Textures 里的 appraiser_card.png。
/// </summary>
public static class GuildCard
{
    public const string Id = "appraiser_card";

    public static string Name => ModHelper.GetLocalized(AppraisalExpansionMod.ModId, "card_name");
    public static string Description => ModHelper.GetLocalized(AppraisalExpansionMod.ModId, "card_desc");

    /// <summary>读档后 / 开店时调用：已入会但没有名片就补一张。</summary>
    internal static void EnsureGiven()
    {
        PlayerStore store = PlayerStore.Instance;
        if (store == null || !store.isAppraisalIntroduced)
        {
            return;
        }

        if (EmporiumEntry.Instance == null)
        {
            return;
        }

        if (EmporiumEntry.Instance.GetItemCountById(Id) > 0)
        {
            return;
        }

        store.AddDirectSellingItemToTable(Id, isOwend: true);
        Debug.Log($"[{AppraisalExpansionMod.ModId}] 已入会但没有名片，补发一张 {Id}");
    }
}
