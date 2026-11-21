// 个人环境检测仪（第 2 件鉴定品）。
//
// 差分：传感器 3 × 机身 3 × 插件 4 × 厂商 3 = 108 种外观；
//       正常 + 良好 + 双插件 + 有厂商标 → 顶配套装 +100。
// 计价：基准 100，底线 40。
//
// 注：本文件在 2026-11-19 因误操作被清空，现由已部署 DLL 反编译恢复，
//     逻辑与数值以那次构建为准；方法级注释未能恢复。

using System;
using System.Collections.Generic;
using System.Reflection;
using UnityEngine;

public static class EnvScanItem
{
	public const string Id = "oddity_tech_envscan";

	public const string GuideItemId = "envscan_guide";

	public const string TagSensor = "ENVSCAN_SENSOR";

	public const string TagBody = "ENVSCAN_BODY";

	public const string TagPlugin = "ENVSCAN_PLUGIN";

	public const string TagVendor = "ENVSCAN_VENDOR";

	public const string SensorOk = "OK";

	public const string SensorDrift = "DRIFT";

	public const string SensorDead = "DEAD";

	public const string BodyGood = "GOOD";

	public const string BodyWorn = "WORN";

	public const string BodyBroken = "BROKEN";

	public const string PluginNone = "NONE";

	public const string PluginAir = "AIR";

	public const string PluginBio = "BIO";

	public const string PluginBoth = "BOTH";

	public const string VendorNone = "NONE";

	public const string VendorSteam = "STEAM";

	public const string VendorLuban = "LUBAN";

	public const int BaseValue = 100;

	public const int MinValue = 40;

	private const int SensorDriftPenalty = -20;

	private const int SensorDeadPenalty = -40;

	private const int BodyWornPenalty = -5;

	private const int BodyBrokenPenalty = -20;

	private const int PluginAirBonus = 10;

	private const int PluginBioBonus = 15;

	private const int PluginBothBonus = 30;

	private const int VendorSteamBonus = 10;

	private const int VendorLubanBonus = 20;

	public const int FullSetBonus = 100;

	private static readonly (string key, int weight)[] SensorWeights = new(string, int)[3]
	{
		("OK", 70),
		("DRIFT", 25),
		("DEAD", 5)
	};

	private static readonly (string key, int weight)[] BodyWeights = new(string, int)[3]
	{
		("GOOD", 65),
		("WORN", 28),
		("BROKEN", 7)
	};

	private static readonly (string key, int weight)[] PluginWeights = new(string, int)[4]
	{
		("NONE", 30),
		("AIR", 30),
		("BIO", 25),
		("BOTH", 15)
	};

	private static readonly (string key, int weight)[] VendorWeights = new(string, int)[3]
	{
		("NONE", 55),
		("STEAM", 25),
		("LUBAN", 20)
	};

	public static string Name => ModHelper.GetLocalized("AppraisalExpansion", "envscan_name", Array.Empty<object>());

	public static string SetName => ModHelper.GetLocalized("AppraisalExpansion", "envscan_set_name", Array.Empty<object>());

	public static string Description => ModHelper.GetLocalized("AppraisalExpansion", "envscan_desc", Array.Empty<object>());

	public static GameItem CreateBase()
	{
		GameItem created = ItemDirectory.CreateEmptyItem("oddity_tech_envscan");
		created.name = Name;
		created.shortDescription = Description;
		created.unitValue = 100L;

		created.EnableTag("INSPECTABLE_TAG", false);
		AppraisalHelper.InitAppraisalItem(created, 100);
		created.SetSpriteAndShapeFromMod("AppraisalExpansion", IconKey());
		ItemFootprint.Ensure(created);
		return created;
	}

	public static GameItem CreateRandom()
	{
		GameItem created = DirectoryMaster.Item("oddity_tech_envscan", true);
		if (created == null)
		{
			Debug.LogError((object)"[AppraisalExpansion] 环境检测仪工厂返回 null：目录里没有注册 oddity_tech_envscan");
			return null;
		}
		string text = Pick(BodyWeights);
		string text2 = Pick(SensorWeights);
		string text3 = Pick(PluginWeights);
		string text4 = Pick(VendorWeights);
		ApplyVariant(created, text, text2, text3, text4);
		Debug.Log((object)("[AppraisalExpansion] envscan random: body=" + text + " sensor=" + text2 + " " + $"plugin={text3} vendor={text4} value={CalculateValue(created)}"));
		return created;
	}

	public static void ApplyVariant(GameItem item, string body, string sensor, string plugin, string vendor)
	{
		SetStringTag(item, "ENVSCAN_BODY", body);
		SetStringTag(item, "ENVSCAN_SENSOR", sensor);
		SetStringTag(item, "ENVSCAN_PLUGIN", plugin);
		SetStringTag(item, "ENVSCAN_VENDOR", vendor);
		item.SetSpriteAndShapeFromMod("AppraisalExpansion", IconKey());
		ItemFootprint.Ensure(item);
	}

	public static int GetCorrectValue(GameItem item)
	{
		return IsEnvScan(item) ? CalculateValue(item) : 0;
	}

	public static bool IsEnvScan(GameItem item)
	{
		return item != null && item.IsTag("ENVSCAN_BODY");
	}

	public static bool IsFullSet(GameItem item)
	{
		if (!IsEnvScan(item))
		{
			return false;
		}
		return IsFullSet(GetStringTag(item, "ENVSCAN_BODY"), GetStringTag(item, "ENVSCAN_SENSOR"), GetStringTag(item, "ENVSCAN_PLUGIN"), GetStringTag(item, "ENVSCAN_VENDOR"));
	}

	public static bool IsFullSet(string body, string sensor, string plugin, string vendor)
	{
		return body == "GOOD" && sensor == "OK" && plugin == "BOTH" && vendor != "NONE";
	}

	public static int CalculateValue(GameItem item)
	{
		string stringTag = GetStringTag(item, "ENVSCAN_BODY");
		string stringTag2 = GetStringTag(item, "ENVSCAN_SENSOR");
		string stringTag3 = GetStringTag(item, "ENVSCAN_PLUGIN");
		string stringTag4 = GetStringTag(item, "ENVSCAN_VENDOR");
		int num = 100;
		num += SensorModifier(stringTag2);
		num += BodyModifier(stringTag);
		num += PluginModifier(stringTag3);
		num += VendorModifier(stringTag4);
		if (IsFullSet(stringTag, stringTag2, stringTag3, stringTag4))
		{
			num += 100;
		}
		return Math.Max(40, num);
	}

	public static string IconKey()
	{
		return "envscan_icon";
	}

	public static string MagnifierBaseKey(string body, string sensor)
	{
		return "envscan_" + BodyToken(body) + "_" + SensorToken(sensor);
	}

	public static string PluginKey(string plugin, string which)
	{
		bool flag = plugin == "AIR" || plugin == "BOTH";
		bool flag2 = plugin == "BIO" || plugin == "BOTH";
		if (which == "AIR" && flag)
		{
			return "envscan_plugin_air";
		}
		if (which == "BIO" && flag2)
		{
			return "envscan_plugin_bio";
		}
		return null;
	}

	public static string VendorKey(string vendor)
	{
		if (vendor == "STEAM")
		{
			return "envscan_vendor_steam";
		}
		if (vendor == "LUBAN")
		{
			return "envscan_vendor_luban";
		}
		return null;
	}

	private static string BodyToken(string body)
	{
		if (body == "WORN")
		{
			return "worn";
		}
		if (body == "BROKEN")
		{
			return "broken";
		}
		return "good";
	}

	private static string SensorToken(string sensor)
	{
		if (sensor == "DRIFT")
		{
			return "drift";
		}
		if (sensor == "DEAD")
		{
			return "dead";
		}
		return "ok";
	}

	private static int SensorModifier(string sensor)
	{
		if (sensor == "DEAD")
		{
			return -40;
		}
		return (sensor == "DRIFT") ? (-20) : 0;
	}

	private static int BodyModifier(string body)
	{
		if (body == "BROKEN")
		{
			return -20;
		}
		return (body == "WORN") ? (-5) : 0;
	}

	private static int PluginModifier(string plugin)
	{
		int result;
		switch (plugin)
		{
		case "BOTH":
			return 30;
		case "BIO":
			return 15;
		default:
			result = 0;
			break;
		case "AIR":
			result = 10;
			break;
		}
		return result;
	}

	private static int VendorModifier(string vendor)
	{
		if (vendor == "LUBAN")
		{
			return 20;
		}
		return (vendor == "STEAM") ? 10 : 0;
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
