using System.Collections.Generic;
using UnityEngine;
using Alexandria.VisualAPI;

namespace PlutoTheCat
{
    /// <summary>Custom effects: a puff of fur (Nine Lives, tail whip) and a burst of hearts and a gravy splat (Wet Food Can).</summary>
    public static class PlutoVFX
    {
        public static VFXPool FurPuff;
        public static VFXPool LoveBurst;
        public static VFXPool AngerMarks;
        public static VFXPool BlockSpark;
        public static VFXPool GravyBurst;
        public static VFXPool Bonito;
        public static VFXPool Jingle;   // 2.17 Jingle Bell Collar ring
        public static VFXPool Catnip;   // 2.17 Catnip Pouch leaves

        public static void Init()
        {
            FurPuff = VFXBuilder.CreateVFXPool("PlutoFurPuff", Frames("furpuff", 4), 12, new IntVector2(16, 16),
                tk2dBaseSprite.Anchor.MiddleCenter, false, 0f);
            LoveBurst = VFXBuilder.CreateVFXPool("PlutoLoveBurst", Frames("loveburst", 4), 8, new IntVector2(16, 16),
                tk2dBaseSprite.Anchor.MiddleCenter, false, 0f);
            AngerMarks = VFXBuilder.CreateVFXPool("PlutoAngerMarks", Frames("anger", 4), 10, new IntVector2(12, 12),
                tk2dBaseSprite.Anchor.MiddleCenter, false, 0f);
            BlockSpark = VFXBuilder.CreateVFXPool("PlutoBlockSpark", Frames("spark", 3), 16, new IntVector2(12, 12),
                tk2dBaseSprite.Anchor.MiddleCenter, false, 0f);
            GravyBurst = VFXBuilder.CreateVFXPool("PlutoGravyBurst", Frames("gravyburst", 4), 10, new IntVector2(20, 20),
                tk2dBaseSprite.Anchor.MiddleCenter, false, 0f);
            Bonito = VFXBuilder.CreateVFXPool("PlutoBonito", Frames("bonito", 4), 12, new IntVector2(16, 16),
                tk2dBaseSprite.Anchor.MiddleCenter, false, 0f);
            Jingle = VFXBuilder.CreateVFXPool("PlutoJingle", Frames("jingle", 4), 14, new IntVector2(24, 24),
                tk2dBaseSprite.Anchor.MiddleCenter, false, 0f);
            Catnip = VFXBuilder.CreateVFXPool("PlutoCatnip", Frames("catnip", 4), 8, new IntVector2(12, 12),
                tk2dBaseSprite.Anchor.MiddleCenter, false, 0f);
        }

        private static List<string> Frames(string prefix, int count)
        {
            List<string> paths = new List<string>();
            for (int i = 1; i <= count; i++) paths.Add(Plugin.VFX_ROOT + "/" + prefix + "_" + i.ToString("000") + ".png");
            return paths;
        }

        public static void Spawn(VFXPool pool, Vector2 position)
        {
            if (pool == null) return;
            pool.SpawnAtPosition(new Vector3(position.x, position.y, position.y));
        }
    }
}
