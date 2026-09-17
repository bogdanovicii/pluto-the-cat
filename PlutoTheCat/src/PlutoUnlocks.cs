using System;
using System.Collections.Generic;

namespace PlutoTheCat
{
    /// <summary>
    /// Per-save unlock store for the Shrine Stall's ten cat items. Each item gets an extended
    /// GungeonFlags value (per-save, but its numeric id drifts if other flag-extending mods are
    /// added or removed) mirrored by a string key via ForceUnlock/IsForceUnlocked (stable, also
    /// per-save). ShrineStallRules.Unlocked treats the mirror as authoritative.
    /// </summary>
    public static class PlutoUnlocks
    {
        /// <summary>The ten gated item ids, in the order of the config price table.</summary>
        public static readonly string[] Ids = new[]
        {
            BallOfYarnItem.ID,
            CatnipPouchItem.ID,
            HairballItem.ID,
            ScratchingPostItem.ID,
            ToiletPaperRollItem.ID,
            CoffeeMugItem.ID,
            JingleBellCollarItem.ID,
            ConeOfShameItem.ID,
            SprayBottleGun.ID,
            FeatherTeaserGun.ID,
        };

        private static readonly Dictionary<string, GungeonFlags> Flags = new Dictionary<string, GungeonFlags>();

        /// <summary>Registers one extended GungeonFlags value per id. Safe to call once (a second call is a no-op).</summary>
        public static void Init()
        {
            if (Flags.Count > 0) return;
            foreach (string id in Ids)
            {
                try
                {
                    Flags[id] = ETGModCompatibility.ExtendEnum<GungeonFlags>(Plugin.GUID, ShrineStallRules.FlagName(id));
                }
                catch (Exception e)
                {
                    Plugin.Log("unlock flag registration failed for " + id + ": " + e);
                }
            }
        }

        /// <summary>The extended GungeonFlags value for an item id, for building prerequisites. Default(GungeonFlags) if unregistered.</summary>
        public static GungeonFlags Flag(string itemId)
        {
            GungeonFlags flag;
            return Flags.TryGetValue(itemId, out flag) ? flag : default(GungeonFlags);
        }

        public static bool IsUnlocked(string itemId)
        {
            if (GameStatsManager.Instance == null) return false;
            bool flag = Flags.ContainsKey(itemId) && GameStatsManager.Instance.GetFlag(Flags[itemId]);
            bool mirror = GameStatsManager.Instance.IsForceUnlocked(ShrineStallRules.MirrorKey(itemId));
            return ShrineStallRules.Unlocked(flag, mirror, PlutoConfig.StallUnlocksDisabled);
        }

        /// <summary>Sets the flag, writes the mirror, and flushes the save.</summary>
        public static void Unlock(string itemId)
        {
            if (GameStatsManager.Instance == null) return;
            if (Flags.ContainsKey(itemId)) GameStatsManager.Instance.SetFlag(Flags[itemId], true);
            GameStatsManager.Instance.ForceUnlock(ShrineStallRules.MirrorKey(itemId));
            GameStatsManager.Save();
        }
    }
}
