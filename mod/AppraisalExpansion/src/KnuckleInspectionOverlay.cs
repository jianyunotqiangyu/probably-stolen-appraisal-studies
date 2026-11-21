using System.Collections.Generic;
using HarmonyLib;
using UnityEngine;
using UnityEngine.UI;

/// <summary>
/// 指节的“鉴定大图”：在鉴定面板上叠两层精灵（底图 + 接口标记），模拟原版
/// <c>AppHandUILarge</c> 那种按 Tag 开关叠层 GameObject 的大图。
///
/// [非规范实现] 用 Harmony 补丁 + 新建 GameObject 改动了内置鉴定界面。
/// 依据：官方指南《已支持与不支持的模组功能》把“改动现有 UI：重构或替换内置界面”列为**不支持**，
///       并建议“改为添加你自己的窗口”。但原版鉴定大图是预制体（CigaretteUI / FuelUI / StampUI /
///       InjectorUI / RibwichUI / AppHandUI / InsBerryUI），模组没有注册预制体的 API，
///       而鉴定玩法的核心就是“凑近看大图找特征”，没有等价的原生路径。
///
/// 原版放大镜的结构（从 level1 资源包里 dump 出来的，不是猜的）：
/// <code>
/// _InspectionUI (912×804)
/// ├─ _App1Hand            scale 1   ← 面板里的原尺寸大图
/// ├─ ...
/// └─ MagnifiyingGlasse (484×456) [MagnifyingGlassMono]
///    └─ Mask               ← UI Mask，裁剪成镜片形状
///       ├─ BlockerTray     挡住点击
///       ├─ _App1Hand        scale 2   ← 同一套大图的 2 倍复制品，只有它在镜片里可见
///       └─ ...             （每个物品块都有一份 2 倍复制品，挂 CounterMoveChild 做视差）
/// </code>
/// 所以“透过镜片看到东西”的条件是：**内容必须是 Mask 的子节点**。挂在面板里的图只会出现在镜片外。
///
/// 风险：<c>InspectionUIManager.OnInspectItem</c> 改名/改签名、<c>panel</c>/<c>magnifyingGlass</c>
///       字段变动，或预制体里 <c>Mask</c> 改名时补丁失效；失效表现是“大图不显示/镜片里空着”，
///       不影响鉴定流程与定价。
/// 回退：删掉本文件即可退回“只有小图标”的原版表现。
/// </summary>
internal static class KnuckleInspectionOverlay
{
    private const string OverlayName = "ODDITY_KnuckleMagnifier";
    private const string MaskNodeName = "Mask";

    /// 面板里大图的显示尺寸。
    /// 256 原图 × 1.72（原 512，用户反馈偏大，缩到 440 ≈ 0.86 倍）。
    /// [待确认] 原版义肢手各层的图幅是 812×704、肋明治是 530×208，尺寸基准尚未逐分辨率核对。
    private static readonly Vector2 OverlaySize = new Vector2(440f, 440f);

    private static readonly Vector2 OverlayOffset = Vector2.zero;

    /// <summary>
    /// 面板显示倍率：统一按「原图最长边 × 此倍率」，再受 <see cref="MaxOverlaySize"/> 封顶。
    /// 这样裁过留白的图不会被固定框过度放大（之前裁切后指节被拉到 3.6× 就是这个原因）。
    /// 1.7 沿用最早的观感；原版是 1:1 显示，此处属于放大显示，属于观感折中。
    /// </summary>
    private const float PanelZoom = 1.7f;

    /// <summary>面板最大边长，避免大图撑满整个鉴定面板。</summary>
    private static readonly Vector2 MaxOverlaySize = new Vector2(440f, 440f);

    /// <summary>底图边长：字符偏移 dx 是在这个坐标系里量的（美术导出按 256 画的）。</summary>
    private const float BaseImageSize = 256f;

    /// <summary>
    /// 镜片倍数：**相对面板 2 倍**，与原版一致。
    /// 依据（2026-11-19 从游戏 level1 预制体实测）：
    ///   面板侧 `_InspectionUI → _App1Hand / _Ribwich / …` 的 localScale 全是 1；
    ///   镜片侧 `MagnifiyingGlasse → Mask → 同名块` 的 localScale 全是 2。
    /// 注意这是「相对面板」的比值，不是「相对原图像素」：
    ///   原版面板是 1:1（812px 原图就画 812px），镜片 2× → 屏幕上是 2 倍原生像素；
    ///   我们的面板把 256 画成 440（1.72×），镜片再乘 2 → 屏幕上是 3.44 倍原生像素。
    ///   观感（相对面板放大 2 倍）与原版相同，代价是低分辨率图更糊——
    ///   根治办法是美术出 512 或更大的底图，而不是把倍数压小。
    /// </summary>
    private const float VanillaLensFactor = 2f;

    private static GameObject _overlay;
    private static Image _baseImage;
    private static readonly List<Image> _markImages = new List<Image>();
    private static readonly List<Image> _glyphImages = new List<Image>();

    private static GameObject _lensCopy;
    private static Image _lensBase;
    private static readonly List<Image> _lensMarks = new List<Image>();
    private static readonly List<Image> _lensGlyphs = new List<Image>();
    private static Vector3 _lensInitialLocalPosition;

    private static bool _loggedGlassFallback;

    internal static void Show(InspectionUIManager ui, GameItem item)
    {
        if (ui == null || ui.panel == null)
        {
            return;
        }

        Transform parent = OverlayParent(ui);
        bool ours = KnuckleItem.IsKnuckle(item) || EnvScanItem.IsEnvScan(item) || WristItem.IsWrist(item) || CoinItem.IsCoin(item);

        if (_overlay != null && (!ours || _overlay.transform.parent != parent))
        {
            Destroy();
        }

        if (!ours)
        {
            return;
        }

        if (_overlay == null)
        {
            Build(ui);
        }

        // 放大镜是面板里的最后一个子节点（镜片永远画在图上面），
        // 这里把叠层压到它前面，避免大图把镜片盖住。
        PlaceUnderMagnifier(ui);

        Sprite baseSprite = GetSprite(ResolveBaseKey(item));

        if (baseSprite == null)
        {
            _overlay.SetActive(false);
            SetLensVisible(false);
            return;
        }

        ApplyPanelSize(_overlay, baseSprite);

        List<Sprite> markSprites = ResolveMarks(item);
        List<(Sprite Sprite, int Dx)> glyphs = ResolveGlyphs(item);

        _baseImage.sprite = baseSprite;
        _baseImage.enabled = true;

        SyncPanelMarks(markSprites.Count);
        for (int i = 0; i < markSprites.Count; i++)
        {
            _markImages[i].sprite = markSprites[i];
            _markImages[i].enabled = true;
        }
        HideUnused(_markImages, markSprites.Count);

        SyncPanelGlyphs(glyphs.Count);
        for (int i = 0; i < glyphs.Count; i++)
        {
            _glyphImages[i].sprite = glyphs[i].Sprite;
            ApplyGlyphOffset(_glyphImages[i], glyphs[i].Dx);
            _glyphImages[i].enabled = true;
        }
        HideUnused(_glyphImages, glyphs.Count);

        _overlay.SetActive(true);

        // 镜片里的 2 倍复制品：没有它，玩家把镜片拖到图上只会看到一片空白。
        EnsureLensCopy(ui);
        if (_lensCopy != null)
        {
            // 关键：每次打开面板都要复位。
            // CounterMoveChild 是“拖动时反向补偿”，每拖一次都会在复制品上留下位移；
            // 原版 OpenUI() 也是这么处理的（cigaretteUILarge / appHandUILarge … 全部
            // localPosition 复位回 *InitialPosition），否则第二次打开就会错位、几次之后漂出蒙版。
            ResetLensPosition();
            ApplyLensScale(baseSprite);

            _lensBase.sprite = baseSprite;
            _lensBase.enabled = true;

            SyncLensMarks(markSprites.Count);
            for (int i = 0; i < markSprites.Count; i++)
            {
                _lensMarks[i].sprite = markSprites[i];
                _lensMarks[i].enabled = true;
            }
            HideUnused(_lensMarks, markSprites.Count);

            SyncLensGlyphs(glyphs.Count);
            for (int i = 0; i < glyphs.Count; i++)
            {
                _lensGlyphs[i].sprite = glyphs[i].Sprite;
                ApplyGlyphOffset(_lensGlyphs[i], glyphs[i].Dx);
                _lensGlyphs[i].enabled = true;
            }
            HideUnused(_lensGlyphs, glyphs.Count);

            SetLensVisible(true);
        }
    }

    /// <summary>模组禁用或场景重建时清掉叠层，避免留下悬空引用。</summary>
    internal static void Reset()
    {
        Destroy();
    }


    /// <summary>原图坐标 → 面板坐标的换算系数（按底图实际尺寸与面板实际尺寸算，裁图后仍然对）。</summary>
    private static float CurrentScale()
    {
        if (_overlay == null || _baseImage == null || _baseImage.sprite == null)
        {
            return OverlaySize.x / BaseImageSize;
        }

        Vector2 shown = ((RectTransform)_overlay.transform).sizeDelta;
        Rect sprite = _baseImage.sprite.rect;
        return Mathf.Min(shown.x / sprite.width, shown.y / sprite.height);
    }

    // ---------------- 面板里的那份 ----------------

    private static void Build(InspectionUIManager ui)
    {
        _overlay = new GameObject(OverlayName, typeof(RectTransform));
        _overlay.transform.SetParent(OverlayParent(ui), false);

        RectTransform rect = (RectTransform)_overlay.transform;
        rect.anchorMin = new Vector2(0.5f, 0.5f);
        rect.anchorMax = new Vector2(0.5f, 0.5f);
        rect.pivot = new Vector2(0.5f, 0.5f);
        rect.sizeDelta = OverlaySize;
        rect.anchoredPosition = OverlayOffset;

        _baseImage = NewLayer(_overlay.transform, "base");
        SyncPanelMarks(0);
    }

    /// <summary>
    /// 叠层挂在放大镜的同一个父节点下，并插到放大镜**前面**（sibling index 更小 = 先绘制 = 在下面）。
    /// </summary>
    private static void PlaceUnderMagnifier(InspectionUIManager ui)
    {
        if (_overlay == null || ui.magnifyingGlass == null)
        {
            return;
        }

        Transform glass = ui.magnifyingGlass.transform;
        if (glass.parent == null || _overlay.transform.parent != glass.parent)
        {
            return;
        }

        int glassIndex = glass.GetSiblingIndex();
        if (_overlay.transform.GetSiblingIndex() >= glassIndex)
        {
            _overlay.transform.SetSiblingIndex(glassIndex);
        }
    }

    private static Transform OverlayParent(InspectionUIManager ui)
    {
        if (ui.magnifyingGlass != null && ui.magnifyingGlass.transform.parent != null)
        {
            return ui.magnifyingGlass.transform.parent;
        }

        if (!_loggedGlassFallback)
        {
            _loggedGlassFallback = true;
            Debug.LogWarning($"[{AppraisalExpansionMod.ModId}] 找不到 magnifyingGlass，叠层退回到 panel 根节点；" +
                             "如果这时镜片挡住了大图或大图盖住了镜片，就是这里。");
        }
        return ui.panel.transform;
    }

    // ---------------- 镜片里的那份 ----------------

    private static void EnsureLensCopy(InspectionUIManager ui)
    {
        Transform mask = FindMask(ui);
        if (mask == null)
        {
            return;
        }

        if (_lensCopy != null && _lensCopy.transform.parent == mask)
        {
            return;
        }

        if (_lensCopy != null)
        {
            Object.Destroy(_lensCopy);
        }

        _lensCopy = new GameObject(OverlayName + "_Lens", typeof(RectTransform));
        _lensCopy.transform.SetParent(mask, false);

        RectTransform rect = (RectTransform)_lensCopy.transform;
        rect.anchorMin = new Vector2(0.5f, 0.5f);
        rect.anchorMax = new Vector2(0.5f, 0.5f);
        rect.pivot = new Vector2(0.5f, 0.5f);
        rect.sizeDelta = OverlaySize;
        rect.anchoredPosition = OverlayOffset;
        rect.localScale = Vector3.one;
        _lensInitialLocalPosition = rect.localPosition;

        // 原版每个 2 倍复制品都挂这个组件：镜片被拖动时，内容反着走、留在原处，
        // 看上去才是“镜片滑过一张不会动的图”，而不是“连图一起被拖走”。
        _lensCopy.AddComponent<CounterMoveChild>();

        _lensBase = NewLayer(_lensCopy.transform, "base");
        SyncLensMarks(0);
    }

    /// <summary>
    /// 把镜片复制品复位到建出来时的位置。
    /// 对应原版 <c>InspectionUIManager.OpenUI()</c> 里的那串
    /// <c>cigaretteUILarge.transform.localPosition = cigaretteInitialPosition;</c>
    /// （以及 fuelUILarge / stampUILarge / injectorUILarge / ribwichUILarge / appHandUILarge / insBerryUILarge）。
    /// </summary>
    private static void ResetLensPosition()
    {
        if (_lensCopy != null)
        {
            _lensCopy.transform.localPosition = _lensInitialLocalPosition;
        }
    }

    private static Transform FindMask(InspectionUIManager ui)
    {
        if (ui.magnifyingGlass == null)
        {
            return null;
        }

        Transform glass = ui.magnifyingGlass.transform;
        Transform mask = glass.Find(MaskNodeName);
        return mask != null ? mask : glass;
    }

    private static void SetLensVisible(bool visible)
    {
        if (_lensCopy != null)
        {
            _lensCopy.SetActive(visible);
        }
    }

    // ---------------- 通用 ----------------

    private static void Destroy()
    {
        if (_overlay != null)
        {
            Object.Destroy(_overlay);
        }
        if (_lensCopy != null)
        {
            Object.Destroy(_lensCopy);
        }

        _overlay = null;
        _baseImage = null;
        _markImages.Clear();
        _lensCopy = null;
        _lensBase = null;
        _lensMarks.Clear();
        _lensGlyphs.Clear();
    }

    // ---------------- 物品 → 贴图键 ----------------

    /// <summary>底图键：指节按 材质×状态，检测仪按 机身×传感器，终端按 材质×品相。</summary>
    private static string ResolveBaseKey(GameItem item)
    {
        if (item == null)
        {
            return null;
        }

        if (EnvScanItem.IsEnvScan(item))
        {
            return EnvScanItem.MagnifierBaseKey(
                EnvScanItem.GetStringTag(item, EnvScanItem.TagBody),
                EnvScanItem.GetStringTag(item, EnvScanItem.TagSensor));
        }

        if (CoinItem.IsCoin(item))
        {
            return CoinItem.MagnifierBaseKey(
                CoinItem.GetStringTag(item, CoinItem.TagMaterial),
                CoinItem.GetStringTag(item, CoinItem.TagEdition));
        }

        if (WristItem.IsWrist(item))
        {
            return WristItem.MagnifierBaseKey(
                WristItem.GetStringTag(item, WristItem.TagCondition),
                WristItem.GetStringTag(item, WristItem.TagMaterial));
        }

        return KnuckleItem.MagnifierBaseKey(
            KnuckleItem.GetStringTag(item, KnuckleItem.TagMaterial),
            KnuckleItem.GetStringTag(item, KnuckleItem.TagCondition));
    }

    /// <summary>
    /// 叠层键（按绘制顺序）：指节最多 1 层（接口刻字）；
    /// 检测仪最多 3 层（空气插件 / 病菌插件 / 厂商标），双插件时前两层同时叠；
    /// 终端最多 2 层（卫星中继 / 加密通信），双服务时两层同时叠。
    /// </summary>
    private static List<Sprite> ResolveMarks(GameItem item)
    {
        List<Sprite> list = new List<Sprite>();
        if (item == null)
        {
            return list;
        }

        if (EnvScanItem.IsEnvScan(item))
        {
            string plugin = EnvScanItem.GetStringTag(item, EnvScanItem.TagPlugin);
            AddIfPresent(list, EnvScanItem.PluginKey(plugin, EnvScanItem.PluginAir));
            AddIfPresent(list, EnvScanItem.PluginKey(plugin, EnvScanItem.PluginBio));
            AddIfPresent(list, EnvScanItem.VendorKey(EnvScanItem.GetStringTag(item, EnvScanItem.TagVendor)));
            return list;
        }

        if (WristItem.IsWrist(item))
        {
            AddIfPresent(list, WristItem.ServiceKey(WristItem.GetStringTag(item, WristItem.TagService)));
            return list;
        }

        AddIfPresent(list, KnuckleItem.MagnifierOverlayKey(
            KnuckleItem.GetStringTag(item, KnuckleItem.TagInterface)));
        return list;
    }

    /// <summary>编号叠层：把字符 sprite 与它在原图里的横向偏移一起返回。</summary>
    private static List<(Sprite Sprite, int Dx)> ResolveGlyphs(GameItem item)
    {
        List<(Sprite Sprite, int Dx)> list = new List<(Sprite Sprite, int Dx)>();
        if (item == null || !CoinItem.IsCoin(item))
        {
            return list;
        }

        foreach ((string key, int dx) in CoinItem.SerialGlyphs(item))
        {
            Sprite sprite = GetSprite(key);
            if (sprite != null)
            {
                list.Add((sprite, dx));
            }
        }

        return list;
    }

    /// <summary>保证面板里的编号层数量足够。</summary>
    private static void SyncPanelGlyphs(int count)
    {
        while (_glyphImages.Count < count)
        {
            _glyphImages.Add(NewLayer(_overlay.transform, "glyph" + _glyphImages.Count));
        }
    }

    /// <summary>保证镜片复制品里的编号层数量足够。</summary>
    private static void SyncLensGlyphs(int count)
    {
        if (_lensCopy == null)
        {
            return;
        }

        while (_lensGlyphs.Count < count)
        {
            _lensGlyphs.Add(NewLayer(_lensCopy.transform, "glyph" + _lensGlyphs.Count));
        }
    }

    /// <summary>
    /// 字符偏移：dx 是「原图 256 空间」里的像素，换算到面板显示尺寸。
    /// 字符图本身是 256×256 的整层，所以只需要横向平移。
    /// </summary>
    /// <summary>按精灵最长边 × 固定倍率设定面板尺寸，受上限封顶。</summary>
    private static void ApplyPanelSize(GameObject overlay, Sprite sprite)
    {
        if (overlay == null || sprite == null)
        {
            return;
        }

        ((RectTransform)overlay.transform).sizeDelta = PanelSizeFor(sprite);
    }

    /// <summary>面板边长：原图最长边 × 倍率，封顶于 <see cref="MaxOverlaySize"/>。</summary>
    private static Vector2 PanelSizeFor(Sprite sprite)
    {
        if (sprite == null)
        {
            return OverlaySize;
        }

        float longest = Mathf.Max(sprite.rect.width, sprite.rect.height);
        float side = Mathf.Min(longest * PanelZoom, MaxOverlaySize.x);
        return new Vector2(side, side);
    }

    /// <summary>
    /// 隐藏本轮没用到的层。
    /// 层是按需增长的（只增不减），若不主动关掉，换成叠层更少的物品时
    /// 上一件的编号/标记会留在屏幕上——这就是「纪念币的数字、手表的服务残留」的原因。
    /// </summary>
    private static void HideUnused(List<Image> layers, int used)
    {
        for (int i = used; i < layers.Count; i++)
        {
            layers[i].sprite = null;
            layers[i].enabled = false;
        }
    }

    /// <summary>关闭鉴定界面时把叠层收起来，避免退出后残留在屏幕上。</summary>
    internal static void Hide()
    {
        if (_overlay != null)
        {
            _overlay.SetActive(false);
        }

        SetLensVisible(false);
    }

    /// <summary>
    /// 镜片复制品固定为面板的 2 倍（原版比值），并打日志便于核对。
    /// </summary>
    private static void ApplyLensScale(Sprite sprite)
    {
        if (_lensCopy == null)
        {
            return;
        }

        // 镜片复制品的长宽必须与面板一致，否则镜片与面板的比例会失真。
        Vector2 panel = PanelSizeFor(sprite);
        ((RectTransform)_lensCopy.transform).sizeDelta = panel;
        _lensCopy.transform.localScale = new Vector3(VanillaLensFactor, VanillaLensFactor, 1f);

        float native = sprite != null ? sprite.rect.width : BaseImageSize;
        Debug.Log($"[{AppraisalExpansionMod.ModId}] 镜片倍数 {VanillaLensFactor:0.00}"
            + $"（面板 {panel.x:0}px × {VanillaLensFactor:0} → {panel.x * VanillaLensFactor:0}px；"
            + $"原图 {native:0}px，有效放大 {panel.x * VanillaLensFactor / native:0.00}× 原生像素）");
    }

    private static void ApplyGlyphOffset(Image image, int dx)
    {
        if (image == null || _baseImage == null || _baseImage.sprite == null)
        {
            return;
        }

        RectTransform rect = (RectTransform)image.transform;
        RectTransform parent = rect.parent as RectTransform;
        if (parent == null)
        {
            return;
        }

        // 关键：偏移要按「这一层所在的父节点尺寸」换算，不能统一用面板尺寸。
        // 镜片复制品的 rect 与面板不同（且整体还有 LensScale 缩放），用面板尺寸会让字距被放大。
        Rect sprite = _baseImage.sprite.rect;
        Vector2 shown = parent.sizeDelta;
        float scale = Mathf.Min(shown.x / sprite.width, shown.y / sprite.height);
        rect.anchoredPosition = new Vector2(dx * scale, 0f);
    }

    private static void AddIfPresent(List<Sprite> list, string key)
    {
        Sprite sprite = GetSprite(key);
        if (sprite != null)
        {
            list.Add(sprite);
        }
    }

    /// <summary>保证面板里的叠层数量足够（多退少补）。</summary>
    private static void SyncPanelMarks(int count)
    {
        while (_markImages.Count < count)
        {
            _markImages.Add(NewLayer(_overlay.transform, "mark" + _markImages.Count));
        }
    }

    /// <summary>保证镜片复制品里的叠层数量足够（多退少补）。</summary>
    private static void SyncLensMarks(int count)
    {
        if (_lensCopy == null)
        {
            return;
        }

        while (_lensMarks.Count < count)
        {
            _lensMarks.Add(NewLayer(_lensCopy.transform, "mark" + _lensMarks.Count));
        }
    }

    private static Sprite GetSprite(string key)
    {
        if (string.IsNullOrEmpty(key))
        {
            return null;
        }

        LoadedMod mod = ModLoader.Mods.Find(m => m.Manifest.ID == AppraisalExpansionMod.ModId);
        if (mod == null)
        {
            return null;
        }

        Sprite sprite;
        return mod.Sprites.TryGetValue(key, out sprite) ? sprite : null;
    }

    private static Image NewLayer(Transform parent, string name)
    {
        GameObject go = new GameObject(name, typeof(RectTransform));
        go.transform.SetParent(parent, false);

        RectTransform rect = (RectTransform)go.transform;
        rect.anchorMin = Vector2.zero;
        rect.anchorMax = Vector2.one;
        rect.offsetMin = Vector2.zero;
        rect.offsetMax = Vector2.zero;

        Image image = go.AddComponent<Image>();
        image.preserveAspect = true;
        image.raycastTarget = false;
        return image;
    }
}

/// <summary>
/// 挂到原版鉴定入口上的补丁：游戏原本只在物品带 <c>HAND_TAG</c> 等原版 Tag 时才显示对应大图，
/// 模组物品没有自己的大图，所以在 <c>OnInspectItem</c> 之后补一层。
/// 补丁由加载器统一 PatchAll（见指南《Harmony 补丁》），这里不自己 new Harmony。
/// </summary>
[HarmonyPatch(typeof(InspectionUIManager), nameof(InspectionUIManager.OnInspectItem))]
internal static class KnuckleInspectionPatch
{
    private static void Postfix(InspectionUIManager __instance, GameItem gameItem)
    {
        KnuckleInspectionOverlay.Show(__instance, gameItem);
    }
}

/// <summary>
/// 关闭鉴定界面时收起叠层。
/// 原版 <c>InspectionUIManager.CloseUI()</c> 只把 panel 关掉，我们自己 new 出来的
/// 叠层节点（以及镜片里的复制品）不在它的管理范围里，之前退出后会留在屏幕上。
/// </summary>
[HarmonyPatch(typeof(InspectionUIManager), nameof(InspectionUIManager.CloseUI))]
internal static class KnuckleInspectionClosePatch
{
    private static void Postfix()
    {
        KnuckleInspectionOverlay.Hide();
    }
}
