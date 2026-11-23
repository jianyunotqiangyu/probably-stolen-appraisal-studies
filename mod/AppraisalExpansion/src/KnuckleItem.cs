// 仿生指节（第 1 件鉴定品）。
//
// 差分：材质 3（铝 0 / 钢 +30 / 镀金 +70）× 品相 3（无 0 / 磨损 −25 / 受损 −50）
//       × 接口刻字 3（规格不明 −15 / EMG 0 / EMG+ +15），共 27 种外观。
// 计价：基准 85，底线 35；大图 = 底图 + 接口刻字叠层。
//
// 注：本文件在 2026-11-19 因误操作被清空，现由已部署 DLL 反编译恢复，
//     逻辑与数值以那次构建为准；方法级注释未能恢复。

using System;
using System.Collections.Generic;
using System.Reflection;
using UnityEngine;

public static class KnuckleItem
{
	public const string Id = "oddity_bio_knuckle";

	public const string GuideItemId = "knuckle_guide";

	public const string TagMaterial = "KNUCKLE_MATERIAL";

	public const string TagCondition = "KNUCKLE_CONDITION";

	public const string TagInterface = "KNUCKLE_INTERFACE";

	public const string AluminumAlloy = "ALUMINUM_ALLOY";

	public const string Steel = "STEEL";

	public const string GoldPlated = "GOLD_PLATED";

	public const string ConditionNone = "NONE";

	public const string ConditionWear = "WEAR";

	public const string ConditionDamage = "DAMAGE";

	public const string InterfaceNone = "NONE";

	public const string InterfaceEmg = "EMG";

	public const string InterfaceEmgPlus = "EMG_PLUS";

	public const int BaseValue = 120;

	public const int MinValue = 50;

	private const int AluminumBonus = 0;

	private const int SteelBonus = 45;

	private const int GoldBonus = 100;

	private const int WearPenalty = -30;

	private const int DamagePenalty = -60;

	private const int NoInterfacePenalty = -20;

	private const int EmgPlusBonus = 25;

	private static readonly (string key, int weight)[] MaterialWeights = new(string, int)[3]
	{
		("ALUMINUM_ALLOY", 65),
		("STEEL", 30),
		("GOLD_PLATED", 5)
	};

	private static readonly (string key, int weight)[] ConditionWeights = new(string, int)[3]
	{
		("NONE", 50),
		("WEAR", 35),
		("DAMAGE", 15)
	};

	private static readonly (string key, int weight)[] InterfaceWeights = new(string, int)[3]
	{
		("NONE", 30),
		("EMG", 50),
		("EMG_PLUS", 20)
	};

	public static string Name => ModHelper.GetLocalized("AppraisalExpansion", "knuckle_name", Array.Empty<object>());

	public static string Description => ModHelper.GetLocalized("AppraisalExpansion", "knuckle_desc", Array.Empty<object>());

	public static GameItem CreateBase()
	{
		GameItem created = ItemDirectory.CreateEmptyItem("oddity_bio_knuckle");
		created.name = Name;
		created.shortDescription = Description;
		created.unitValue = 85L;

		created.EnableTag("INSPECTABLE_TAG", false);
		AppraisalHelper.InitAppraisalItem(created, 85);
		created.SetSpriteAndShapeFromMod("AppraisalExpansion", IconKey("ALUMINUM_ALLOY"));
		ItemFootprint.Ensure(created);
		return created;
	}

	public static GameItem CreateRandom()
	{
		GameItem created = DirectoryMaster.Item("oddity_bio_knuckle", true);
		ApplyVariant(created, Pick(MaterialWeights), Pick(ConditionWeights), Pick(InterfaceWeights));
		return created;
	}

	public static void ApplyVariant(GameItem item, string material, string condition, string interfaceType)
	{
		SetStringTag(item, "KNUCKLE_MATERIAL", material);
		SetStringTag(item, "KNUCKLE_CONDITION", condition);
		SetStringTag(item, "KNUCKLE_INTERFACE", interfaceType);
		item.SetSpriteAndShapeFromMod("AppraisalExpansion", IconKey(material));
		ItemFootprint.Ensure(item);
	}

	public static int GetCorrectValue(GameItem item)
	{
		return IsKnuckle(item) ? CalculateValue(item) : 0;
	}

	public static bool IsKnuckle(GameItem item)
	{
		return item != null && item.IsTag("KNUCKLE_MATERIAL");
	}

	public static int CalculateValue(GameItem item)
	{
		int num = BaseValue;
		num += MaterialBonus(GetStringTag(item, "KNUCKLE_MATERIAL"));
		num += ConditionModifier(GetStringTag(item, "KNUCKLE_CONDITION"));
		num += InterfaceModifier(GetStringTag(item, "KNUCKLE_INTERFACE"));
		return Math.Max(MinValue, num);
	}

	public static string IconKey(string material)
	{
		return "knuckle_icon_" + MaterialToken(material);
	}

	public static string MagnifierBaseKey(string material, string condition)
	{
		return "knuckle_" + MaterialToken(material) + "_" + ConditionToken(condition);
	}

	public static string MagnifierOverlayKey(string interfaceType)
	{
		if (interfaceType == "EMG")
		{
			return "knuckle_overlay_emg";
		}
		if (interfaceType == "EMG_PLUS")
		{
			return "knuckle_overlay_emgplus";
		}
		return null;
	}

	private static string MaterialToken(string material)
	{
		if (material == "STEEL")
		{
			return "steel";
		}
		if (material == "GOLD_PLATED")
		{
			return "gold";
		}
		return "alu";
	}

	private static string ConditionToken(string condition)
	{
		if (condition == "WEAR")
		{
			return "wear";
		}
		if (condition == "DAMAGE")
		{
			return "damage";
		}
		return "normal";
	}

	private static int MaterialBonus(string material)
	{
		if (material == "GOLD_PLATED")
		{
			return 70;
		}
		if (material == "STEEL")
		{
			return 30;
		}
		return 0;
	}

	private static int ConditionModifier(string condition)
	{
		if (condition == "DAMAGE")
		{
			return -50;
		}
		if (condition == "WEAR")
		{
			return -25;
		}
		return 0;
	}

	private static int InterfaceModifier(string interfaceType)
	{
		if (interfaceType == "EMG_PLUS")
		{
			return 15;
		}
		if (interfaceType == "NONE")
		{
			return -15;
		}
		return 0;
	}

	public static string GetStringTag(GameItem item, string tag)
	{
		return item.GetTagReadonly(tag).GetString();
	}

	private static void SetStringTag(GameItem item, string tag, string value)
	{
		item.ModifyTag(tag, (Action<TagState>)delegate(TagState state)
		{
			state.Enable().SetString(value);
		}, false);
	}

	private static string Pick((string key, int weight)[] options)
	{
		int num = 0;
		for (int i = 0; i < options.Length; i++)
		{
			(string key, int weight) tuple = options[i];
			string item = tuple.key;
			int item2 = tuple.weight;
			num += item2;
		}
		int num2 = UnityEngine.Random.Range(0, num);
		for (int j = 0; j < options.Length; j++)
		{
			var (result, num3) = options[j];
			if (num2 < num3)
			{
				return result;
			}
			num2 -= num3;
		}
		return options[0].key;
	}
}
