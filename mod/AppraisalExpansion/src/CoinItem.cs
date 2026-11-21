// 第九环港开港纪念币（第 4 件鉴定品）。
//
// 差分：材质 3（铜 0 / 镀银 +30 / 镀金 +60）× 版别 3（普通 0 / 稀有 +80 / 珍藏 +200）
//       × 防伪编号（五位数字 + 材质字母 G/S/C）。
//   豹子号（去掉前导 0 后 ≥2 位且全同）+100；测试币（各号段起始 9 个号）+600。
//   赝品：号段与版别图案不符，或字母与材质不符 → 固定 40，任何加成不计。
//   无品质轴：纪念币一般不流通，基本不出现品相差。
//
// 编号由代码按 5px 步进叠在底图刻字位上（首字在 256 空间的 54,123），不画进贴图。
//
// 注：本文件在 2026-11-19 因误操作被清空，现由已部署 DLL 反编译恢复，
//     逻辑与数值以那次构建为准；方法级注释未能恢复。

using System;
using System.Collections.Generic;
using System.Reflection;
using UnityEngine;

public static class CoinItem
{
	public const string Id = "oddity_coin";

	public const string GuideItemId = "coin_guide";

	public const string TagMaterial = "COIN_MATERIAL";

	public const string TagEdition = "COIN_EDITION";

	public const string TagSerial = "COIN_SERIAL";

	public const string TagFake = "COIN_FAKE";

	public const string MaterialGold = "GOLD";

	public const string MaterialSilver = "SILVER";

	public const string MaterialCopper = "COPPER";

	public const string EditionNormal = "NORMAL";

	public const string EditionRare = "RARE";

	public const string EditionCollector = "COLLECTOR";

	public const int BaseValue = 100;

	public const int MinValue = 40;

	public const int FakeValue = 40;

	private const int GoldBonus = 60;

	private const int SilverBonus = 30;

	private const int CopperBonus = 0;

	private const int RareBonus = 80;

	private const int CollectorBonus = 200;

	private const int JaguarBonus = 100;

	private const int TestCoinBonus = 600;

	private const int FakeChancePercent = 10;

	private const int NormalMin = 10000;

	private const int NormalMax = 99999;

	private const int RareMin = 1000;

	private const int RareMax = 9999;

	private const int CollectorMin = 1;

	private const int CollectorMax = 999;

	private static readonly (string key, int weight)[] MaterialWeights = new(string, int)[3]
	{
		("COPPER", 60),
		("SILVER", 30),
		("GOLD", 10)
	};

	private static readonly (string key, int weight)[] EditionWeights = new(string, int)[3]
	{
		("NORMAL", 70),
		("RARE", 25),
		("COLLECTOR", 5)
	};

	public const int SerialStep = 5;

	public static string Name => ModHelper.GetLocalized("AppraisalExpansion", "coin_name", Array.Empty<object>());

	public static string Description => ModHelper.GetLocalized("AppraisalExpansion", "coin_desc", Array.Empty<object>());

	public static GameItem CreateBase()
	{
		GameItem created = ItemDirectory.CreateEmptyItem("oddity_coin");
		created.name = Name;
		created.shortDescription = Description;
		created.unitValue = 100L;

		created.EnableTag("INSPECTABLE_TAG", false);
		AppraisalHelper.InitAppraisalItem(created, 100);
		created.SetSpriteAndShapeFromMod("AppraisalExpansion", IconKey("COPPER"));
		ItemFootprint.Ensure(created);
		return created;
	}

	public static GameItem CreateRandom()
	{
		GameItem created = DirectoryMaster.Item("oddity_coin", true);
		if (created == null)
		{
			Debug.LogError((object)"[AppraisalExpansion] 纪念币工厂返回 null：目录里没有注册 oddity_coin");
			return null;
		}
		string text = Pick(MaterialWeights);
		string text2 = Pick(EditionWeights);
		bool flag = UnityEngine.Random.Range(0, 100) < 10;
		string edition = text2;
		string material = text;
		string text3 = "";
		if (flag)
		{
			if (UnityEngine.Random.Range(0, 2) == 0)
			{
				edition = DifferentEdition(text2);
				text3 = "号段不符";
			}
			else
			{
				material = DifferentMaterial(text);
				text3 = "材质字母不符";
			}
		}
		string text4 = UnityEngine.Random.Range(RangeMin(edition), RangeMax(edition) + 1).ToString("D5") + LetterOf(material);
		ApplyVariant(created, text, text2, text4, flag);
		Debug.Log((object)("[AppraisalExpansion] coin random: " + text + "/" + text2 + " 编号=" + text4 + (flag ? (" 赝品(" + text3 + ")") : "") + $" value={CalculateValue(created)}"));
		return created;
	}

	public static void ApplyVariant(GameItem item, string material, string edition, string serial, bool fake)
	{
		SetStringTag(item, "COIN_MATERIAL", material);
		SetStringTag(item, "COIN_EDITION", edition);
		SetStringTag(item, "COIN_SERIAL", serial);
		SetStringTag(item, "COIN_FAKE", fake ? "1" : "0");
		item.SetSpriteAndShapeFromMod("AppraisalExpansion", IconKey(material));
		ItemFootprint.Ensure(item);
	}

	public static int GetCorrectValue(GameItem item)
	{
		return IsCoin(item) ? CalculateValue(item) : 0;
	}

	public static bool IsCoin(GameItem item)
	{
		return item != null && item.IsTag("COIN_MATERIAL");
	}

	public static bool IsFakeTagged(GameItem item)
	{
		return IsCoin(item) && GetStringTag(item, "COIN_FAKE") == "1";
	}

	public static int CalculateValue(GameItem item)
	{
		if (IsFakeTagged(item))
		{
			return 40;
		}
		string stringTag = GetStringTag(item, "COIN_MATERIAL");
		string stringTag2 = GetStringTag(item, "COIN_EDITION");
		string stringTag3 = GetStringTag(item, "COIN_SERIAL");
		int num = 100;
		num += MaterialBonus(stringTag);
		num += EditionBonus(stringTag2);
		if (IsJaguarSerial(stringTag3))
		{
			num += 100;
		}
		if (IsTestCoinSerial(stringTag3))
		{
			num += 600;
		}
		return Math.Max(40, num);
	}

	public static bool IsJaguarSerial(string serial)
	{
		string text = DigitsOf(serial).TrimStart('0');
		if (text.Length < 2)
		{
			return false;
		}
		string text2 = text;
		foreach (char c in text2)
		{
			if (c != text[0])
			{
				return false;
			}
		}
		return true;
	}

	public static bool IsTestCoinSerial(string serial)
	{
		if (!int.TryParse(DigitsOf(serial), out var result))
		{
			return false;
		}
		bool flag = result >= 10001 && result <= 10009;
		bool flag2 = result >= 1001 && result <= 1009;
		bool flag3 = result >= 1 && result <= 9;
		return flag || flag2 || flag3;
	}

	private static string DigitsOf(string serial)
	{
		if (string.IsNullOrEmpty(serial))
		{
			return "00000";
		}
		return (serial.Length >= 6) ? serial.Substring(0, serial.Length - 1) : serial;
	}

	public static string IconKey(string material)
	{
		return "coin_icon_" + MaterialToken(material);
	}

	public static string MagnifierBaseKey(string material, string edition)
	{
		return "coin_" + MaterialToken(material) + "_" + EditionToken(edition);
	}

	public static List<(string key, int dx)> SerialGlyphs(GameItem item)
	{
		List<(string, int)> list = new List<(string, int)>();
		if (!IsCoin(item))
		{
			return list;
		}
		string stringTag = GetStringTag(item, "COIN_MATERIAL");
		string stringTag2 = GetStringTag(item, "COIN_SERIAL");
		if (string.IsNullOrEmpty(stringTag2))
		{
			return list;
		}
		for (int i = 0; i < stringTag2.Length; i++)
		{
			list.Add(("coin_ch_" + MaterialToken(stringTag) + "_" + stringTag2[i], i * 5));
		}
		return list;
	}

	private static string MaterialToken(string material)
	{
		if (material == "GOLD")
		{
			return "gold";
		}
		return (material == "SILVER") ? "silver" : "copper";
	}

	private static string EditionToken(string edition)
	{
		if (edition == "RARE")
		{
			return "rare";
		}
		return (edition == "COLLECTOR") ? "collector" : "normal";
	}

	private static string LetterOf(string material)
	{
		if (material == "GOLD")
		{
			return "G";
		}
		return (material == "SILVER") ? "S" : "C";
	}

	private static string DifferentEdition(string edition)
	{
		if (!(edition == "NORMAL"))
		{
			if (edition == "RARE")
			{
				return "COLLECTOR";
			}
			return "NORMAL";
		}
		return "RARE";
	}

	private static string DifferentMaterial(string material)
	{
		if (!(material == "GOLD"))
		{
			if (material == "SILVER")
			{
				return "COPPER";
			}
			return "GOLD";
		}
		return "SILVER";
	}

	private static int RangeMin(string edition)
	{
		if (!(edition == "RARE"))
		{
			if (edition == "COLLECTOR")
			{
				return 1;
			}
			return 10000;
		}
		return 1000;
	}

	private static int RangeMax(string edition)
	{
		if (!(edition == "RARE"))
		{
			if (edition == "COLLECTOR")
			{
				return 999;
			}
			return 99999;
		}
		return 9999;
	}

	private static int MaterialBonus(string material)
	{
		if (material == "GOLD")
		{
			return 60;
		}
		return (material == "SILVER") ? 30 : 0;
	}

	private static int EditionBonus(string edition)
	{
		if (edition == "COLLECTOR")
		{
			return 200;
		}
		return (edition == "RARE") ? 80 : 0;
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
