using UnityEngine;

/// <summary>
/// 按「格子内是否有任何像素」重算占格形状，修掉模组贴图的不规则轮廓。
///
/// 原版与模组两条路的采样方式**不一样**（从游戏代码里读出来的）：
/// <list type="bullet">
/// <item>原版 <c>BuildShapeFromSprite</c> 用 <c>GetPixel(x, y, mipLevel)</c>，mip 级别 = √gridSize = 4，
///       等于把 16×16 的格子**降采样后**再判 alpha —— 只要格子里有墨就算占格。</item>
/// <item>模组 <c>SetSpriteAndShapeFromMod</c> 用 <c>GetPixel(x, y)</c> 取**格子中心那一个像素**。
///       图标中心透明就判空：纪念币因此整枚不占格，检测仪 3×3 因此变成不规则形状。</item>
/// </list>
/// 所以这里按原版语义重算：逐格扫一遍像素，有墨就置 1，再 <c>SetShape</c> 覆盖。
/// </summary>
internal static class ItemFootprint
{
    internal static void Ensure(GameItem item)
    {
        if (item == null)
        {
            return;
        }

        string key = item.spritePath;
        string modId = item.spriteAtlasPath;
        if (string.IsNullOrEmpty(key) || string.IsNullOrEmpty(modId))
        {
            return;
        }

        LoadedMod mod = ModLoader.Mods.Find(m => m.Manifest.ID == modId);
        if (mod == null || !mod.Sprites.TryGetValue(key, out Sprite sprite) || sprite == null)
        {
            return;
        }

        int grid = UISettings.current.gridSize;
        int cols = Mathf.Max(1, (int)(sprite.rect.width / grid));
        int rows = Mathf.Max(1, (int)(sprite.rect.height / grid));

        byte[] data = new byte[cols * rows];
        bool anyCell = false;

        for (int row = 0; row < rows; row++)
        {
            for (int col = 0; col < cols; col++)
            {
                bool ink = false;
                for (int y = 0; y < grid && !ink; y++)
                {
                    for (int x = 0; x < grid && !ink; x++)
                    {
                        // 纹理坐标自下而上：row 0 对应最上面一行
                        int px = (int)sprite.rect.xMin + col * grid + x;
                        int py = (int)sprite.rect.yMin + (rows - 1 - row) * grid + y;
                        if (sprite.texture.GetPixel(px, py).a > 0f)
                        {
                            ink = true;
                        }
                    }
                }

                if (ink)
                {
                    data[row * cols + col] = 1;
                    anyCell = true;
                }
            }
        }

        if (!anyCell)
        {
            byte[] single = { 1 };
            item.SetShape(new GridShapeBuilder().SetData(single, 1));
            Debug.LogWarning($"[{AppraisalExpansionMod.ModId}] {item.identifier}: 贴图整张透明，占格兜底为 1×1");
            return;
        }

        item.SetShape(new GridShapeBuilder().SetData(data, cols));
    }
}
