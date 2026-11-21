using System;
using System.Collections.Generic;
using UnityEngine;

/// <summary>
/// 鉴定行会的电话接线：把 <see cref="Number"/>（名片上印的 0347）登记进游戏的号码簿，
/// 拨通后用游戏原生的 <see cref="DialoguePhoneUIManager"/> 播放对话，选「预约考官上门」
/// 就让考官到店。
///
/// [非规范实现] 往原版号码簿里登记一行。
/// 依据：官方指南《已支持与不支持的模组功能》没有电话相关的 API；
///       <see cref="StorePhoneClient"/> 与 <c>PhoneClientList.DialogFuncs</c> 都是游戏类型，
///       按《能力声明与扫描器》属于「反射/使用游戏类型免费」，不需要声明能力。
/// 风险：<c>PhoneClientDict</c> 是 ES3 序列化的存档字段。玩家**停用**模组时我们在 <see cref="Unregister"/>
///       里删掉这一行；但若玩家直接把模组文件夹**删了**，存档里会留下一行孤儿号码——
///       拨过去只会停在拨号状态（不崩溃、不报错），按红色挂断键即可退出。
/// 回退：删掉本文件与 <c>AppraisalExpansionMod</c> 里的两处调用，名片上的号码就只是一串数字。
/// </summary>
public static class GuildPhone
{
    /// <summary>
    /// 名片上印的预约号：<c>1717</c>，致敬《彼方的她》。
    /// **不用 0 开头**——电话键盘按 0 时 <c>currentNumber</c> 仍是 0，屏幕不显示前导零。
    /// </summary>
    public const long Number = 1717L;

    /// <summary>早期版本用过的号码，读档时清掉，避免存档里留一串拨不通的号。</summary>
    private static readonly long[] LegacyNumbers = { 347L, 8347L };

    private const string DialogFuncId = "AppraiserGuild";

    private static bool _dialogueRegistered;

    /// <summary>往 <c>DialogFuncs</c> 注册对话构造器（静态表，注册一次即可）。</summary>
    internal static void RegisterDialogue()
    {
        if (_dialogueRegistered)
        {
            return;
        }

        PhoneClientList.DialogFuncs[DialogFuncId] = _ => BuildCallDialogue();
        _dialogueRegistered = true;
        Debug.Log($"[{AppraisalExpansionMod.ModId}] 电话：已注册行会对话 {DialogFuncId}");
    }

    /// <summary>读档后 / 开店时调用：号码簿里没有行会就补一行。</summary>
    internal static void EnsureRegistered()
    {
        RegisterDialogue();

        PlayerStore store = PlayerStore.Instance;
        if (store == null || store.PhoneClientDict == null)
        {
            return;
        }

        foreach (long legacy in LegacyNumbers)
        {
            if (store.PhoneClientDict.Remove(legacy))
            {
                Debug.Log($"[{AppraisalExpansionMod.ModId}] 电话：清掉旧号码 {legacy}");
            }
        }

        if (store.PhoneClientDict.ContainsKey(Number))
        {
            return;
        }

        store.PhoneClientDict[Number] = new StorePhoneClient
        {
            displayName = ModHelper.GetLocalized(AppraisalExpansionMod.ModId, "phone_guild_speaker"),
            dialogFuncId = DialogFuncId,
            phoneState = StorePhoneClient.PhoneState.Regular,
            cooldownDuration = 0,
            // 照原版规矩：dialedBefore 由 StartPhoneDialog 在第一次接通时置真，
            // 在此之前联系人不会出现在电话簿里（StorePhoneClient.ShownInPhoneBook）。
            // 所以第一次要手输 1717，之后就能在电话簿里一键拨通。
            dialedBefore = false,
        };

        Debug.Log($"[{AppraisalExpansionMod.ModId}] 电话：号码簿补登行会 {Number}");
    }

    /// <summary>停用模组时清掉登记，避免存档里留一行拨不通的号。</summary>
    internal static void Unregister()
    {
        PhoneClientList.DialogFuncs.Remove(DialogFuncId);
        _dialogueRegistered = false;

        PlayerStore store = PlayerStore.Instance;
        if (store != null && store.PhoneClientDict != null)
        {
            store.PhoneClientDict.Remove(Number);
        }
    }

    private static string Loc(string key)
    {
        return ModHelper.GetLocalized(AppraisalExpansionMod.ModId, key);
    }

    /// <summary>
    /// 拨通行会时的对话树。
    ///
    /// 注意选项气泡的实现：<c>DialoguePhoneUIManager.DisplayChoice</c> 显示的是
    /// <c>choices[i].Item2.plainText</c>，也就是**下一个对话节点的正文**，不是 AddChoice 的 name。
    /// 所以每个选项都要有自己的一格节点，节点正文就是玩家读到的选项文字。
    ///
    /// 预约门槛：必须 <c>AppraisalRankHelper.IsPromotionReady()</c>（进度到 100%）才行，
    /// 否则只回一句「尚未满足晋升条件」，不进预约。
    /// </summary>
    private static Dialogue BuildCallDialogue()
    {
        string speaker = Loc("phone_guild_speaker");
        bool ready = AppraisalRankHelper.IsPromotionReady();
        bool booked = ModHelper.GetModDataBool(AppraisalExpansionMod.ModId, "appraiser_visit_pending");

        // 选项节点：正文 = 选项卡上的字；点下去后先播这句，再进对应的应答节点
        Dialogue bookOption = new Dialogue();
        bookOption.SetText("PLAYER", Loc("phone_guild_book"));
        Dialogue answer = bookOption.NextDialogue();

        if (booked)
        {
            answer.SetText(speaker, Loc("phone_already_booked")).SetEndAction(EndCall);
        }
        else if (ExamSession.CooldownActive())
        {
            answer.SetText(speaker, Loc("phone_cooldown")).SetEndAction(EndCall);
        }
        else if (!ready)
        {
            string text = ModHelper.GetLocalized(
                AppraisalExpansionMod.ModId, "phone_not_ready",
                AppraisalRankHelper.GetProgressPercent());
            answer.SetText(speaker, text).SetEndAction(EndCall);
        }
        else
        {
            answer.SetText(speaker, Loc("phone_guild_booked")).SetEndAction(delegate
            {
                AppraiserVisit.Book();
                EndCall();
            });
        }

        Dialogue byeOption = new Dialogue();
        byeOption.SetText("PLAYER", Loc("phone_guild_bye_choice"));
        Dialogue bye = byeOption.NextDialogue();
        bye.SetText(speaker, Loc("phone_guild_bye")).SetEndAction(EndCall);

        Dialogue root = new Dialogue();
        root.SetText(speaker, Loc("phone_guild_greeting"))
            .AddChoice(DirectoryMaster.Item("question"), "", "", bookOption)
            .AddChoice(DirectoryMaster.Item("cancel"), "", "", byeOption);

        return root;
    }

    private static void EndCall()
    {
        PhoneUIManager.Instance?.OnPhoneDialogEnd();
    }
}
