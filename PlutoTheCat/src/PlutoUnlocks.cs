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

        /// <summary>
        /// True once Init() has registered a real flag for this id. Flag(itemId) cannot tell this apart from a
        /// genuine flag value of 0 (default(GungeonFlags)), so callers that build a prerequisite from Flag(...)
        /// must check this first and skip the id when it is false.
        /// </summary>
        public static bool IsRegistered(string itemId)
        {
            return Flags.ContainsKey(itemId);
        }

        /// <summary>The raw GungeonFlags value for this id, ignoring the mirror and the config toggle.</summary>
        public static bool FlagSet(string itemId)
        {
            if (GameStatsManager.Instance == null) return false;
            return Flags.ContainsKey(itemId) && GameStatsManager.Instance.GetFlag(Flags[itemId]);
        }

        /// <summary>The raw string mirror for this id, ignoring the flag and the config toggle.</summary>
        public static bool MirrorSet(string itemId)
        {
            if (GameStatsManager.Instance == null) return false;
            return GameStatsManager.Instance.IsForceUnlocked(ShrineStallRules.MirrorKey(itemId));
        }

        public static bool IsUnlocked(string itemId)
        {
            if (GameStatsManager.Instance == null) return false;
            return ShrineStallRules.Unlocked(FlagSet(itemId), MirrorSet(itemId), PlutoConfig.StallUnlocksDisabled);
        }

        /// <summary>
        /// Brings the flag and the string mirror back into agreement, in both directions, and flushes the
        /// save only if something actually changed. Two real cases need this:
        ///
        /// - mirror set, flag clear: the flag-id drift scenario the mirror exists for. IsUnlocked() is true
        ///   (so the item drops again) but the item's FLAG prerequisite reads the *flag*, so
        ///   PrerequisitesMet() stays false: the stall re-stocks and re-charges an item the player already
        ///   owns, and its Ammonomicon page reverts to "???".
        /// - flag set, mirror clear: what a purchase actually leaves behind. Alexandria's foyer meta-shop
        ///   path never assigns the OnPurchase delegate at all (CustomShopController.DoSetup only wires
        ///   customCanBuy/removeCurrency/customPrice/OnPurchase/OnSteal in its NON-blueprint branch; the
        ///   `baseShopType == 6 &amp;&amp; ExampleBlueprintPrefab != null` branch jumps straight past that block to
        ///   the m_itemControllers.Add - verified in the Alexandria 0.5.10 IL). The game's own pickup path
        ///   still sets PickupObject.SaveFlagToSetOnAcquisition, which DoSetup copies from our FLAG
        ///   prerequisite onto the blueprint clone, so the flag lands even though our callback never runs.
        ///   This is the only thing that then writes the mirror.
        ///
        /// Deliberately reads FlagSet/MirrorSet rather than IsUnlocked: IsUnlocked honours
        /// PlutoConfig.StallUnlocksDisabled, and reconciling through it would burn all ten unlocks
        /// permanently into the save the first time someone flipped the testing toggle on.
        /// </summary>
        public static void Reconcile()
        {
            if (GameStatsManager.Instance == null) return;
            bool changed = false;
            foreach (string id in Ids)
            {
                bool flag = FlagSet(id);
                bool mirror = MirrorSet(id);
                if (flag == mirror) continue;

                if (mirror && Flags.ContainsKey(id))
                {
                    GameStatsManager.Instance.SetFlag(Flags[id], true);
                    changed = true;
                    Plugin.Log("unlocks: mirror said unlocked but the flag did not, flag set for " + id);
                }
                else if (flag)
                {
                    GameStatsManager.Instance.ForceUnlock(ShrineStallRules.MirrorKey(id));
                    changed = true;
                    Plugin.Log("unlocks: flag said unlocked but the mirror did not, mirror written for " + id);
                }
            }
            if (changed) GameStatsManager.Save();
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
