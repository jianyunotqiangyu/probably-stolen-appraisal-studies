using HarmonyLib;

/// <summary>
/// 让模组登记的电话联系人显示自己的名字。
///
/// 原版 <c>StorePhoneClient.GetLocalizedDisplayName()</c> 只查游戏自带的 "ClientName" 字符串表
/// （<c>LocHelper.GetLocalizedClientName(locID)</c>），完全忽略 <c>displayName</c> 字段。
/// 模组没法往那张表里加键，于是 <c>locID</c> 为空的条目名字永远是空的。
///
/// [非规范实现] 前置补丁：只在 <c>locID</c> 为空时改用 <c>displayName</c>，
/// 其余条目（原版联系人都有 locID）照走原逻辑，不会把原版名字变成英文。
/// 风险：游戏改动该方法签名时补丁失效 → 名字退化为空（其余功能不受影响）。
/// 回退：删掉本文件即可。
/// </summary>
[HarmonyPatch(typeof(StorePhoneClient), nameof(StorePhoneClient.GetLocalizedDisplayName))]
internal static class PhoneClientNamePatch
{
    private static bool Prefix(StorePhoneClient __instance, ref string __result)
    {
        if (__instance == null || !string.IsNullOrEmpty(__instance.locID))
        {
            return true;
        }

        __result = string.IsNullOrEmpty(__instance.displayName) ? string.Empty : __instance.displayName;
        return false;
    }
}
