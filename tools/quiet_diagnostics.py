"""发布前把诊断日志收敛：只保留与考核相关的行。

背景：排查「考官不来」时加了三行诊断（每次叫号、每次清队列、每次生成顾客），
发布版每接待一位普通顾客都会刷屏，所以改成只在真与考官有关时才打。
"""
import io
import os
import sys

SRC = os.path.join(r"D:\DSH_workspace\mod-create", "mod", "AppraisalExpansion", "src")
EXAM = os.path.join(SRC, "ExamSession.cs")

OLD_BEGIN = """        StoreClient client = PlayerStore.Instance?.currentClientInstance?.GetClientBlueprint();
        Debug.Log($"[{AppraisalExpansionMod.ModId}] 叫号到场：{(client == null ? "null" : client.identifier)}");

        if (client != null && client.identifier == AppraiserVisit.Identifier)
        {"""

NEW_BEGIN = """        StoreClient client = PlayerStore.Instance?.currentClientInstance?.GetClientBlueprint();
        if (client != null && client.identifier == AppraiserVisit.Identifier)
        {"""

OLD_CLEAR = """        Debug.Log($"[{AppraisalExpansionMod.ModId}] 队列被清空：{count} 人，其中考官={hasAppraiser}");"""

NEW_CLEAR = """        if (hasAppraiser)
        {
            Debug.Log($"[{AppraisalExpansionMod.ModId}] 队列被清空时考官在队中（{count} 人），确认是否已到柜台");
        }"""


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    text = io.open(EXAM, encoding="utf-8").read()

    if OLD_BEGIN in text:
        text = text.replace(OLD_BEGIN, NEW_BEGIN)
        print("叫号日志：只在考官时打印")
    else:
        print("叫号日志：未命中（可能已改）")

    if OLD_CLEAR in text:
        text = text.replace(OLD_CLEAR, NEW_CLEAR)
        print("清队日志：只在考官在队时打印")
    else:
        print("清队日志：未命中（可能已改）")

    # Prefix 里用不到的 count 变量保留（hasAppraiser 分支要用）
    io.open(EXAM, "w", encoding="utf-8", newline="\n").write(text)


if __name__ == "__main__":
    main()
