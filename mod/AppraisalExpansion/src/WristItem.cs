// 腕式通讯终端（第 3 件鉴定品）。
//
// 差分：品相 3（全新 0 / 磨损 −20 / 损坏 −40）× 材质 2（铸铁 0 / 镀金 +200）
//       × 支持服务 4（未开通 0 / 中继 +40 / 加密 +50 / 双服务 +120）；
//       全新 + 镀金 + 含中继 → 轻奢套装 +200。
// 计价：基准 100，底线 40；服务图标为单张整图叠层。
//
// 注：本文件在 2026-11-19 因误操作被清空，现由已部署 DLL 反编译恢复，
//     逻辑与数值以那次构建为准；方法级注释未能恢复。

using System;
using System.Collections.Generic;
using System.Reflection;
using UnityEngine;

public static class WristItem
{
	public const string Id = "oddity_tech_wrist";

	public const string GuideItemId = "wrist_guide";

	public const string TagCondition = "WRIST_CONDITION";

	public const string TagMaterial = "WRIST_MATERIAL";

	public const string TagService = "WRIST_SERVICE";

	public const string ConditionNew = "NEW";

	public const string ConditionWorn = "WORN";

	public const string ConditionDamaged = "DAMAGED";

	public const string MaterialIron = "IRON";

	public const string MaterialGold = "GOLD";

	public const string ServiceNone = "NONE";

	public const string ServiceRelay = "RELAY";

	public const string ServiceCrypt = "CRYPT";

	public const string ServiceBoth = "BOTH";

	public const int BaseValue = 100;

	public const int MinValue = 40;

	private const int ConditionWornPenalty = -20;

	private const int ConditionDamagedPenalty = -40;

	private const int MaterialGoldBonus = 200;

	private const int ServiceRelayBonus = 40;

	private const int ServiceCryptBonus = 50;

	private const int ServiceBothBonus = 120;

	public const int LuxeSetBonus = 200;

	private static readonly (string key, int weight)[] ConditionWeights = new(string, int)[3]
	{
		("NEW", 65),
		("WORN", 25),
		("DAMAGED", 10)
	};

	private static readonly (string key, int weight)[] MaterialWeights = new(string, int)[2]
	{
		("IRON", 80),
		("GOLD", 20)
	};

	private static readonly (string key, int weight)[] ServiceWeights = new(string, int)[4]
	{
		("NONE", 15),
		("RELAY", 35),
		("CRYPT", 30),
		("BOTH", 20)
	};

	public static string Name => ModHelper.GetLocalized("AppraisalExpansion", "wrist_name", Array.Empty<object>());

	public static string Description => ModHelper.GetLocalized("AppraisalExpansion", "wrist_desc", Array.Empty<object>());

	public static GameItem CreateBase()
	{
		GameItem created = ItemDirectory.CreateEmptyItem("oddity_tech_wrist");
		created.name = Name;
		created.shortDescription = Description;
		created.unitValue = 100L;

		created.EnableTag("INSPECTABLE_TAG", false);
		AppraisalHelper.InitAppraisalItem(created, 100);
		created.SetSpriteAndShapeFromMod("AppraisalExpansion", IconKey("IRON"));
		ItemFootprint.Ensure(created);
		return created;
	}

	public static GameItem CreateRandom()
	{
		GameItem created = DirectoryMaster.Item("oddity_tech_wrist", true);
		if (created == null)
		{
			Debug.LogError((object)"[AppraisalExpansion] 腕式终端工厂返回 null：目录里没有注册 oddity_tech_wrist");
			return null;
		}
		ApplyVariant(created, Pick(ConditionWeights), Pick(MaterialWeights), Pick(ServiceWeights));
		return created;
	}

	public static void ApplyVariant(GameItem item, string condition, string material, string service)
	{
		SetStringTag(item, "WRIST_CONDITION", condition);
		SetStringTag(item, "WRIST_MATERIAL", material);
		SetStringTag(item, "WRIST_SERVICE", service);
		item.SetSpriteAndShapeFromMod("AppraisalExpansion", IconKey(material));
		ItemFootprint.Ensure(item);
	}

	public static int GetCorrectValue(GameItem item)
	{
		return IsWrist(item) ? CalculateValue(item) : 0;
	}

	public static bool IsWrist(GameItem item)
	{
		return item != null && item.IsTag("WRIST_CONDITION");
	}

	public static bool IsLuxeSet(GameItem item)
	{
		if (!IsWrist(item))
		{
			return false;
		}
		return IsLuxeSet(GetStringTag(item, "WRIST_CONDITION"), GetStringTag(item, "WRIST_MATERIAL"), GetStringTag(item, "WRIST_SERVICE"));
	}

	public static bool IsLuxeSet(string condition, string material, string service)
	{
		bool flag = service == "RELAY" || service == "BOTH";
		return condition == "NEW" && material == "GOLD" && flag;
	}

	public static int CalculateValue(GameItem item)
	{
		string stringTag = GetStringTag(item, "WRIST_CONDITION");
		string stringTag2 = GetStringTag(item, "WRIST_MATERIAL");
		string stringTag3 = GetStringTag(item, "WRIST_SERVICE");
		int num = 100;
		num += ConditionModifier(stringTag);
		num += MaterialModifier(stringTag2);
		num += ServiceModifier(stringTag3);
		if (IsLuxeSet(stringTag, stringTag2, stringTag3))
		{
			num += 200;
		}
		return Math.Max(40, num);
	}

	public static string IconKey(string material)
	{
		return "wrist_icon_" + MaterialToken(material);
	}

	public static string MagnifierBaseKey(string condition, string material)
	{
		return "wrist_" + MaterialToken(material) + "_" + ConditionToken(condition);
	}

	public static string ServiceKey(string service)
	{
		return service switch
		{
			"BOTH" => "wrist_service_both", 
			"CRYPT" => "wrist_service_crypt", 
			"RELAY" => "wrist_service_relay", 
			_ => null, 
		};
	}

	private static string MaterialToken(string material)
	{
		return (material == "GOLD") ? "gold" : "iron";
	}

	private static string ConditionToken(string condition)
	{
		if (condition == "WORN")
		{
			return "worn";
		}
		if (condition == "DAMAGED")
		{
			return "damaged";
		}
		return "new";
	}

	private static int ConditionModifier(string condition)
	{
		if (condition == "DAMAGED")
		{
			return -40;
		}
		return (condition == "WORN") ? (-20) : 0;
	}

	private static int MaterialModifier(string material)
	{
		return (material == "GOLD") ? 200 : 0;
	}

	private static int ServiceModifier(string service)
	{
		int result;
		switch (service)
		{
		case "BOTH":
			return 120;
		case "CRYPT":
			return 50;
		default:
			result = 0;
			break;
		case "RELAY":
			result = 40;
			break;
		}
		return result;
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
