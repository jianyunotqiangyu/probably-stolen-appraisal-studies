using System.Reflection;
using HarmonyLib;
using UnityEngine;

/// <summary>
/// 考核：考官带来的三件物品，玩家逐件估价，按游戏自己的「估价精度」判定；
/// 判定完收考试费（原版对话选择机制），缴费且合格才发证书。
///
/// 规则（2026-11-17 用户定）：
///   三件里过两件算及格；考试费 150¢ 在考完、考官离开前统一收；
///   不缴费不发证，只能重考；不扣进度；考完当天不能再约（次日可重约）。
///
/// 结算挂在 <c>StoreClient.allDoneDialogue</c> 上——这是原版的「全部物品处理完」对话槽：
/// <c>AppraisalServiceHelper.OnEstimate</c> 在最后一件估完时会把 <c>client.allDoneDialogue</c>
/// 接在「估价接受」台词后面（见原版 29080–29099 行），所以玩家点掉接受台词后，
/// 自然就进我们的结算，不用另外抢屏幕。
///
/// [非规范实现] 用 Postfix 旁听 <c>AppraisalServiceHelper.OnEstimate</c>。
/// 依据：没有「估价完成」的公开事件；该方法正是玩家提交估价的落点。
/// 风险：方法改名/改签名时补丁失效 → 考核不会自动判定（物品与顾客照常，不会崩）。
/// 回退：删掉本文件，改成考官到场即付钱发证（原版行为）。
/// </summary>
internal static class ExamSession
{
    /// <summary>考核件数：与考官放入柜台的数量保持一致（见 AppraiserVisit.ExamItemCount）。</summary>
    private const int TotalItems = AppraiserVisit.ExamItemCount;
    private const int NeededPasses = 2;
    private const int ExamFee = 150;

    private const string LastExamDayKey = "exam_last_day";

    private static bool _active;

    /// <summary>是否已进入考核（考官已站到柜台）。</summary>
    internal static bool IsActive => _active;
    private static int _judged;
    private static int _passed;
    private static Dialogue _settlement;
    private static int _feeSkips;

    private static readonly MethodInfo PrecisionMethod =
        AccessTools.Method(typeof(AppraisalServiceHelper), "GetEstimatePrecision");

    private static string ModId => AppraisalExpansionMod.ModId;

    private static string Loc(string key)
    {
        return ModHelper.GetLocalized(ModId, key);
    }

    /// <summary>
    /// 考官入队时调用：只建一个空的结算对话占位，**不打开计费拦截**。
    /// 原版 OnEstimate 要用 client.allDoneDialogue 这个槽位，所以必须提前挂上；
    /// 但这会挂一整天，期间可能还有普通鉴定顾客，所以不能在这里就 `_active = true`。
    /// </summary>
    internal static Dialogue CreateSettlement()
    {
        _settlement = new Dialogue();
        return _settlement;
    }

    /// <summary>
    /// 考官被叫到柜台时调用：此刻起才计入考核、才拦截鉴定费。
    /// 这样考官前面排着普通顾客时，那些顾客的鉴定费照收。
    /// </summary>
    internal static void Begin()
    {
        _active = true;
        _judged = 0;
        _passed = 0;
        _feeSkips = 0;

        if (_settlement == null)
        {
            _settlement = new Dialogue();
        }

        Debug.Log($"[{ModId}] 考核开始：{TotalItems} 件，需 {NeededPasses} 件合格，考试费 {ExamFee}");
    }

    /// <summary>
    /// 考核作废：考官被赶走、或还没到柜台就被移除时调用。
    /// 不清状态的话，下一次别的顾客来估价也会被算进考卷，数到三件就在别人面前弹结算。
    /// </summary>
    internal static void Cancel(string reason)
    {
        if (!_active)
        {
            return;
        }

        _active = false;
        _judged = 0;
        _passed = 0;
        _settlement = null;
        Debug.Log($"[{ModId}] 考核作废（{reason}）：已重置计数，未产生结算");
    }

    /// <summary>调试用：清掉「当天不能再约」的冷却。</summary>
    internal static void ResetCooldown()
    {
        ModHelper.SetModDataInt(ModId, LastExamDayKey, -1);
        Debug.Log($"[{ModId}] 调试：已清除考核冷却");
    }

    /// <summary>考试当天不许再约，次日恢复。</summary>
    internal static bool CooldownActive()
    {
        int last = ModHelper.GetModDataInt(ModId, LastExamDayKey);
        int today = StoreStation.Instance?.dayCounter ?? 0;
        return today <= last;
    }

    /// <summary>三件估完：把结果与收费填进结算对话。</summary>
    private static void Finish()
    {
        _active = false;
        bool pass = _passed >= NeededPasses;
        ModHelper.SetModDataInt(ModId, LastExamDayKey, StoreStation.Instance?.dayCounter ?? 0);
        Debug.Log($"[{ModId}] 考核结束：{_judged} 件已估，{_passed} 件合格 → {(pass ? "通过" : "未通过")}，"
            + $"跳过鉴定费 {_feeSkips} 次，现金 {PlayerStore.Instance.playerCash}");

        if (_settlement == null)
        {
            Debug.LogWarning($"[{ModId}] 结算对话缺失，跳过结算");
            return;
        }

        FillSettlement(_settlement, pass);
    }

    /// <summary>
    /// 结算对话：先报结果，再收考试费。
    /// 选项的显示文字取自「下一个节点正文」（DialogUIManager 的行为与电话界面一致）。
    /// </summary>
    private static void FillSettlement(Dialogue root, bool pass)
    {
        string speaker = LocHelper.GetLocalizedClientName("name_appraiser_board_member");
        GameItem moneyIcon = DirectoryMaster.Item("$");
        GameItem cancelIcon = DirectoryMaster.Item("cancel");

        root.SetText(speaker, pass ? Loc("exam_pass") : Loc("exam_fail"));

        // 缴费：扣钱；合格才发证。钱不够时用 choiceEnabled 置灰（照搬原版晋升做法）
        Dialogue payOption = new Dialogue();
        payOption.SetText("PLAYER", Loc("exam_pay_choice"));
        Dialogue paid = payOption.NextDialogue();
        paid.SetText(speaker, pass ? Loc("exam_cert") : Loc("exam_paid_fail")).SetEndAction(delegate
        {
            if (pass)
            {
                AppraisalRankHelper.Promote();
                Debug.Log($"[{ModId}] 考核通过且已缴费：已发证书");
            }

            Leave();
        });

        root.AddChoice(moneyIcon, "", "", payOption, delegate
        {
            if (PlayerStore.Instance.playerCash < ExamFee)
            {
                return;
            }

            PlayerStore.Instance.ModCash(-ExamFee);
            Debug.Log($"[{ModId}] 已收考试费 {ExamFee}");
        }, () => PlayerStore.Instance.playerCash >= ExamFee);

        // 不缴：不发证，可以重考
        Dialogue skipOption = new Dialogue();
        skipOption.SetText("PLAYER", Loc("exam_skip_choice"));
        Dialogue skipped = skipOption.NextDialogue();
        skipped.SetText(speaker, Loc("exam_skip_reply")).SetEndAction(Leave);
        root.AddChoice(cancelIcon, "", "", skipOption);
    }

    private static void Leave()
    {
        PlayerStore.Instance?.DismissCurrentClient(callNextWhenPossible: false);
    }

    /// <summary>
    /// 考核期间不计鉴定费。
    ///
    /// 原版每次估价都会走 <c>AppraisalServiceHelper.GiveAppraisalFee</c>：加钱、播收银声、并生成一张鉴定纸条。
    /// 考核是考试不是做生意，所以整段跳过——考生这三次估价不该再收钱，考试费另算 150¢。
    ///
    /// [非规范实现] 前置补丁，条件跳过（仅考核进行时）。
    /// 依据：没有「本次估价是否计费」的开关；这是对游戏代码打补丁（能力免费）。
    /// 风险：方法改名/改签名时补丁失效 → 考核期间又会发鉴定费（不会崩）。
    /// 回退：删掉这个内部类。
    /// </summary>
    [HarmonyPatch(typeof(AppraisalServiceHelper), nameof(AppraisalServiceHelper.GiveAppraisalFee))]
    internal static class FeePatch
    {
        private static bool Prefix()
        {
            if (!_active)
            {
                return true;
            }

            _feeSkips++;
            Debug.Log($"[{ModId}] 考核中：跳过鉴定费（第 {_feeSkips} 次）");
            return false;
        }
    }
    /// <summary>按原版口径给一次估价打精度分。</summary>
    private static int Precision(GameItem item, int value)
    {
        if (PrecisionMethod == null)
        {
            return 5;
        }

        int correct = AppraisalHelper.GetCorrectBaseValue(item);
        return (int)PrecisionMethod.Invoke(null, new object[] { correct, value });
    }

    [HarmonyPatch(typeof(AppraisalServiceHelper), nameof(AppraisalServiceHelper.OnEstimate))]
    internal static class OnEstimatePatch
    {
        private static void Postfix(GameItem gameItem, int value)
        {
            if (!_active)
            {
                return;
            }

            StoreClient blueprint = PlayerStore.Instance?.currentClientInstance?.GetClientBlueprint();
            if (blueprint == null || blueprint.identifier != AppraiserVisit.Identifier)
            {
                // 不是考官在场时的估价，一律不计入考核
                return;
            }

            string who = blueprint.identifier;

            _judged++;
            bool good = AppraisalRankHelper.IsGradeAccepted(Precision(gameItem, value));
            if (good)
            {
                _passed++;
            }

            Debug.Log($"[{ModId}] 考核记分：第 {_judged} 件，估价 {value}，现金 {PlayerStore.Instance.playerCash}，"
                + $"{(good ? "合格" : "不合格")}，客户端 {who}");

            if (_judged >= TotalItems)
            {
                Finish();
            }
        }
    }
}

/// <summary>
/// 考官被赶走（或中途离场）时作废考核。
/// 原版 <c>PlayerStore.DismissCurrentClient</c> 会顺手销毁柜台上的非自有物品（考卷），
/// 但不会通知模组，所以这里补一个 Postfix 清掉考核状态。
/// </summary>
[HarmonyPatch(typeof(PlayerStore), nameof(PlayerStore.DismissCurrentClient))]
internal static class ExamDismissPatch
{
    private static bool _wasAppraiser;

    /// <summary>
    /// 必须先记下「要走的是不是考官」——方法体里会把 currentClientInstance 置空，
    /// Postfix 时就查不到身份了。不是考官离场就不能作废考核（否则普通顾客离店会把考核清掉）。
    /// </summary>
    private static void Prefix()
    {
        StoreClient client = PlayerStore.Instance?.currentClientInstance?.GetClientBlueprint();
        _wasAppraiser = client != null && client.identifier == AppraiserVisit.Identifier;
    }

    private static void Postfix()
    {
        if (_wasAppraiser)
        {
            ExamSession.Cancel("考官离场");
        }
    }
}

/// <summary>考官还排在队列里就被移除时同样作废。</summary>
[HarmonyPatch(typeof(StoreClientManager), nameof(StoreClientManager.RemoveClientById))]
internal static class ExamRemovePatch
{
    private static void Postfix()
    {
        ExamSession.Cancel("考官被移出队列");
    }
}

/// <summary>
/// 考官被叫到柜台（<c>PlayerStore.GetNextClient</c> 把队首变成 currentClientInstance）时开考。
/// 只有这一刻才 `_active = true`：考官入队到被叫号之间可能排着普通鉴定顾客，
/// 若提前拦截，那些顾客的鉴定费会被白吞。
/// </summary>
[HarmonyPatch(typeof(PlayerStore), nameof(PlayerStore.GetNextClient))]
internal static class ExamBeginPatch
{
    private static void Postfix()
    {
        StoreClient client = PlayerStore.Instance?.currentClientInstance?.GetClientBlueprint();
        if (client != null && client.identifier == AppraiserVisit.Identifier)
        {
            AppraiserVisit.MarkServed();
            ExamSession.Begin();
        }
    }
}

/// <summary>
/// 诊断：队列被整体清空时打一行日志，确认考官是不是被这里清掉的。
/// </summary>
[HarmonyPatch(typeof(StoreClientManager), nameof(StoreClientManager.DismissClientStack))]
internal static class ExamStackClearPatch
{
    private static void Prefix(StoreClientManager __instance)
    {
        int count = __instance.clientStack?.Count ?? 0;
        bool hasAppraiser = false;
        if (__instance.clientStack != null)
        {
            foreach (StoreClient c in __instance.clientStack)
            {
                if (c != null && c.identifier == AppraiserVisit.Identifier)
                {
                    hasAppraiser = true;
                    break;
                }
            }
        }

        if (hasAppraiser)
        {
            Debug.Log($"[{AppraisalExpansionMod.ModId}] 队列被清空时考官在队中（{count} 人），确认是否已到柜台");
        }
    }
}