using System;
using System.Collections.Generic;
using UnityEngine;

/// <summary>
/// 鉴定考官上门：电话预约后**次日开店时**把一位考官排进顾客队列。
///
/// 为什么要用到存档数据：预约发生在当天营业中途，而顾客队列是「今天」的，
/// 直接塞进去会当天立刻出现。改为在 <c>SetModDataBool</c> 记一个待办标记，
/// 下一次 <c>OnShutterOpenedEarly</c>（次日开店）时消费它。
/// 用 <c>ModHelper</c> 的模组数据，不碰原版存档字段（纪律 B9）。
///
/// [非规范实现] 直接拼一个 <see cref="StoreClient"/> 塞进队列。
/// 依据：指南把顾客生成列为原生支持，但原生钩子只能在游戏已经决定生成顾客时修改，
///       没有「立刻叫一位客人来」的 API；这里走的是原版
///       <c>StoreClientListAppraisal.CreateAppraisalRandom</c> 的同一条构造路径。
/// 风险：<c>StoreClient</c> 的字段或 <c>StoreClientFactionSetup.InitScav</c> 变动时失效；
///       失效只影响「预约」按钮，不影响鉴定本身。
/// 回退：删掉本文件，电话里只保留道别选项。
/// </summary>
public static class AppraiserVisit
{
    /// <summary>考官顾客的 identifier，考核判定要拿它认人。</summary>
    internal const string Identifier = "appraiserGuild";

    /// <summary>考核件数，与 ExamSession 保持一致。</summary>
    internal const int ExamItemCount = 3;

    /// <summary>
    /// 预约的到店日（存档里的天数），-1 表示没有预约。
    /// 用「日期比较」而不是「布尔待办标记」，是因为布尔标记会在预约当天就被消费掉：
    /// 预约那一刻若正好有一次顾客生成，标记立刻变 false，次日就再也不会来人。
    /// 原版同样按天数算（见 StoreRequest 里 `StoreStation.GetDayCounter() + N` 的写法）。
    /// </summary>
    private const string VisitDayKey = "appraiser_visit_day";

    private static string ModId => AppraisalExpansionMod.ModId;

    /// <summary>电话里选「预约」时调用：登记「明天来」，不立刻排队。</summary>
    internal static void Book()
    {
        int today = StoreStation.GetDayCounter();
        ModHelper.SetModDataInt(ModId, VisitDayKey, today + 1);
        Debug.Log($"[{ModId}] 已预约：第 {today + 1} 天到店（今天第 {today} 天）");
    }

    /// <summary>考官已到场服务（被叫号或已完成考核）时调用：本次预约用掉。</summary>
    internal static void MarkServed()
    {
        ModHelper.SetModDataInt(ModId, VisitDayKey, -1);
    }

    /// <summary>
    /// 顾客生成钩子：原版每天的特殊顾客（房东、通缉、供应商……）都在
    /// <c>StoreClientManager.GenerateClient()</c> 里由 <c>HandleXxxClient()</c> 逐个塞进队列，
    /// <c>OnGenerateCustomerLate</c> 就落在这个方法内部。这里按「预约日 == 今天」判断后入队，
    /// 一天内生成流程触发几次都不会重复（队列里已有就跳过）。
    /// </summary>
    internal static void OnCustomersGenerated(StoreClientManager manager)
    {
        if (manager == null || ExamSession.IsActive)
        {
            return;
        }

        int visitDay = ModHelper.GetModDataInt(ModId, VisitDayKey);
        if (visitDay < 0)
        {
            return;
        }

        int today = StoreStation.GetDayCounter();
        if (today < visitDay)
        {
            return;
        }

        if (today > visitDay)
        {
            // 过了预约日没接待：按约定作废，不顺延
            ModHelper.SetModDataInt(ModId, VisitDayKey, -1);
            Debug.Log($"[{ModId}] 预约日第 {visitDay} 天已过，未接待，作废");
            return;
        }

        foreach (StoreClient c in manager.clientStack)
        {
            if (c != null && c.identifier == Identifier)
            {
                return;
            }
        }

        Queue(manager);
    }

    /// <summary>立刻排一位考官到店，带上三件待鉴定物品。</summary>
    internal static void Queue(StoreClientManager manager = null)
    {
        PlayerStore store = PlayerStore.Instance;
        if (store == null)
        {
            Debug.LogWarning($"[{ModId}] 预约失败：不在店内");
            return;
        }

        StoreClientManager clientManager = manager ?? store.storeClientManager;
        if (clientManager == null)
        {
            Debug.LogWarning($"[{ModId}] 预约失败：顾客队列未就绪");
            return;
        }

        StoreClient client = new StoreClient();
        client.identifier = Identifier;
        // 外观与名字都用原版「鉴定委员会成员」那一套：clerk 精灵 + 委员会成员的名字
        client.displayName = LocHelper.GetLocalizedClientName("name_appraiser_board_member");
        client.spriteName = SpriteDict.GetClerkSpriteName();
        client.nonShootable = true;
        client.clientFaction = "FACTION_LOWER_LEVEL";
        StoreClientFactionSetup.InitScav(client);
        client.clientIntent = StoreClient.ClientIntent.APPRAISAL_SERVICE;
        client.mainDialogue
            .SetText(client.displayName, ModHelper.GetLocalized(ModId, "appraiser_arrive"))
            .NextDialogue()
            .SetText(client.displayName, ModHelper.GetLocalized(ModId, "exam_rules"))
            .SetEndAction(delegate
            {
                // 考核用的三件从「当前等级及以下」的鉴定品池里抽——与原版 CreateAppraisalRandom 同一来源，
                // 这样原版的手、肋明治等鉴定品也会进考卷，而不是只有本模组的物件。
                List<AppraisalItemType> pool = AppraisalItemRegistry.GetPool(AppraisalRankHelper.GetRank());
                for (int i = 0; i < ExamItemCount; i++)
                {
                    Func<GameItem> factory = pool.Count > 0
                        ? pool[UnityEngine.Random.Range(0, pool.Count)].createRandom
                        : (Func<GameItem>)KnuckleItem.CreateRandom;

                    PlayerStore.Instance.AddDirectSellingItemToTable(factory());
                }
            });
        client.AddBasicDialog();
        client.CompleteClientCreation();
        ModHelper.SetClientSource(client, ModId);

        // 原版在所有物品估完后会把 allDoneDialogue 接在「估价接受」台词之后（见 OnEstimate），
        // 这里把结算对话放进这个槽位：玩家点掉接受台词，才会进收费结算。
        client.allDoneDialogue = ExamSession.CreateSettlement();
        int before = clientManager.clientStack.Count;
        clientManager.AddNextClient(client);
        int after = clientManager.clientStack.Count;
        bool inside = clientManager.clientStack.Contains(client);

        Debug.Log($"[{ModId}] 考官已到店：队列 {before} → {after}，在队中={inside}");
    }
}
