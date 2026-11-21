using System.Collections;
using System.Reflection;
using HarmonyLib;

/// <summary>
/// 只把**本模组手册**的页码文本改写成 "1/5"。
///
/// 原版逻辑（PaperUI.ShowPage）：
/// <code>
/// string text = PageCount > 0
///     ? LocHelper.GetLocalizedUIOrDefault("ui_page_indicator", "{0}/{1}", CurrentPage + 1, PageCount)
///     : "";
/// foreach (Binding pageIndicator in pageIndicators) pageIndicator.text.text = text;
/// </code>
/// 玩家语言是中文时这条键在 zh 表里有条目，显示成「第1/5页」；模组的
/// Localization/*.csv 是按模组分表的（LoadedMod.Localization），覆盖不了全局表。
///
/// 实现方式：ShowPage 执行完之后，直接改它自己那份 pageIndicators 里的 TMP 文本。
/// （最早那版是去拦 LocHelper 的返回值，全局影响面大；后来测试发现不稳，改成直接写组件。）
/// pageIndicators 是 private，这里用 AccessTools 取字段；它是游戏自己的类型，不需要能力声明。
///
/// [非规范实现] 直接改原版手册的页码文本。
/// 风险：PaperUI.ShowPage / pageIndicators 字段 / Binding.text 任一改名就失效；
///       失效表现是页码回到「第1/5页」，不影响翻页与内容。
/// 回退：删掉本文件即可。
/// </summary>
[HarmonyPatch(typeof(PaperUI), "ShowPage")]
internal static class PaperPageNumberScope
{
    private static readonly FieldInfo IndicatorsField =
        AccessTools.Field(typeof(PaperUI), "pageIndicators");

    private static void Postfix(PaperUI __instance)
    {
        if (__instance == null || __instance.Id == null || !__instance.Id.Contains("knuckle_guide"))
        {
            return;
        }

        if (IndicatorsField == null)
        {
            return;
        }

        IList indicators = IndicatorsField.GetValue(__instance) as IList;
        if (indicators == null || indicators.Count == 0)
        {
            return;
        }

        string text = (__instance.CurrentPage + 1) + "/" + __instance.PageCount;
        foreach (object entry in indicators)
        {
            PaperUI.Binding binding = entry as PaperUI.Binding;
            if (binding != null && binding.text != null)
            {
                binding.text.text = text;
            }
        }
    }
}
