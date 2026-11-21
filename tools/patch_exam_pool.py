"""修改 AppraiserVisit：考核件改为从原版鉴定品池抽取。

安全写法：先读入变量，再写回。
"""
import io
import os

SRC = os.path.join(r"D:\DSH_workspace\mod-create", "mod", "AppraisalExpansion", "src")
PATH = os.path.join(SRC, "AppraiserVisit.cs")

OLD_ADD = """                PlayerStore.Instance.AddDirectSellingItemToTable(KnuckleItem.CreateRandom());
                PlayerStore.Instance.AddDirectSellingItemToTable(EnvScanItem.CreateRandom());
                PlayerStore.Instance.AddDirectSellingItemToTable(WristItem.CreateRandom());
"""

NEW_ADD = """                // 考核用的三件从「当前等级及以下」的鉴定品池里抽——与原版 CreateAppraisalRandom 同一来源，
                // 这样原版的手、肋明治等鉴定品也会进考卷，而不是只有本模组的物件。
                List<AppraisalItemType> pool = AppraisalItemRegistry.GetPool(AppraisalRankHelper.GetRank());
                for (int i = 0; i < ExamItemCount; i++)
                {
                    Func<GameItem> factory = pool.Count > 0
                        ? pool[UnityEngine.Random.Range(0, pool.Count)].createRandom
                        : (Func<GameItem>)KnuckleItem.CreateRandom;

                    PlayerStore.Instance.AddDirectSellingItemToTable(factory());
                }
"""

USINGS = """using System;
using System.Collections.Generic;
using UnityEngine;
"""

CONST_OLD = '    internal const string Identifier = "appraiserGuild";\n'
CONST_NEW = ('    internal const string Identifier = "appraiserGuild";\n\n'
             '    /// <summary>考核件数，与 ExamSession 保持一致。</summary>\n'
             '    internal const int ExamItemCount = 3;\n')


def main():
    text = io.open(PATH, encoding="utf-8").read()

    assert OLD_ADD in text, "找不到三件硬编码发放的代码块"
    text = text.replace(OLD_ADD, NEW_ADD)

    if "using System;" not in text:
        text = text.replace("using UnityEngine;\n", USINGS, 1)

    if CONST_OLD in text and "ExamItemCount" not in text:
        text = text.replace(CONST_OLD, CONST_NEW, 1)

    io.open(PATH, "w", encoding="utf-8", newline="\n").write(text)
    print("patched", PATH)


if __name__ == "__main__":
    main()
